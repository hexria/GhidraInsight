"""Multi-region support for distributed GhidraInsight deployments."""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import asyncio
import aiohttp
from datetime import datetime

from ..config import Settings, RegionConfig

logger = logging.getLogger(__name__)


@dataclass
class RegionStatus:
    """Status of a region."""
    region: str
    url: str
    healthy: bool = False
    latency_ms: float = 0.0
    last_check: Optional[datetime] = None
    error: Optional[str] = None


class MultiRegionManager:
    """Manages multi-region deployments."""
    
    def __init__(self, config: Settings):
        """
        Initialize multi-region manager.
        
        Args:
            config: Application settings
        """
        self.config = config
        self.region_config = config.region
        self.regions: Dict[str, RegionStatus] = {}
        self._session: Optional[aiohttp.ClientSession] = None
        self._initialize_regions()
    
    def _initialize_regions(self) -> None:
        """Initialize region status tracking."""
        if not self.region_config.enabled:
            return
        
        for region in self.region_config.regions:
            # Construct region URL (would be configured per region)
            url = self._get_region_url(region)
            self.regions[region] = RegionStatus(
                region=region,
                url=url,
                healthy=False
            )
    
    def _get_region_url(self, region: str) -> str:
        """Get URL for a region."""
        # Default pattern: https://ghidrainsight-{region}.example.com
        # In production, this would come from configuration
        return f"https://ghidrainsight-{region}.example.com"
    
    async def initialize(self) -> None:
        """Initialize HTTP session."""
        if self.region_config.enabled:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.region_config.cross_region_timeout)
            )
    
    async def close(self) -> None:
        """Close HTTP session."""
        if self._session:
            await self._session.close()
            self._session = None
    
    async def check_region_health(self, region: str) -> bool:
        """
        Check health of a region.
        
        Args:
            region: Region name
            
        Returns:
            True if region is healthy
        """
        if not self._session or region not in self.regions:
            return False
        
        region_status = self.regions[region]
        start_time = asyncio.get_event_loop().time()
        
        try:
            async with self._session.get(f"{region_status.url}/health") as response:
                latency = (asyncio.get_event_loop().time() - start_time) * 1000
                
                if response.status == 200:
                    region_status.healthy = True
                    region_status.latency_ms = latency
                    region_status.last_check = datetime.utcnow()
                    region_status.error = None
                    return True
                else:
                    region_status.healthy = False
                    region_status.error = f"HTTP {response.status}"
                    return False
                    
        except Exception as e:
            latency = (asyncio.get_event_loop().time() - start_time) * 1000
            region_status.healthy = False
            region_status.latency_ms = latency
            region_status.error = str(e)
            logger.warning(f"Region {region} health check failed: {e}")
            return False
    
    async def check_all_regions(self) -> Dict[str, bool]:
        """Check health of all regions."""
        if not self.region_config.enabled:
            return {}
        
        tasks = {
            region: self.check_region_health(region)
            for region in self.regions.keys()
        }
        
        results = await asyncio.gather(*tasks.values(), return_exceptions=True)
        
        return {
            region: result if isinstance(result, bool) else False
            for region, result in zip(tasks.keys(), results)
        }
    
    def get_best_region(self) -> Optional[str]:
        """
        Get the best region based on health and latency.
        
        Returns:
            Best region name or None
        """
        if not self.region_config.enabled:
            return self.region_config.current_region
        
        healthy_regions = [
            (region, status.latency_ms)
            for region, status in self.regions.items()
            if status.healthy
        ]
        
        if not healthy_regions:
            # Fallback to current region
            return self.region_config.current_region
        
        # Return region with lowest latency
        best_region, _ = min(healthy_regions, key=lambda x: x[1])
        return best_region
    
    async def replicate_to_region(self, region: str, data: Dict[str, Any]) -> bool:
        """
        Replicate data to another region.
        
        Args:
            region: Target region
            data: Data to replicate
            
        Returns:
            True if successful
        """
        if not self.region_config.replication_enabled:
            return False
        
        if region not in self.regions:
            logger.error(f"Unknown region: {region}")
            return False
        
        if not self._session:
            logger.error("Session not initialized")
            return False
        
        region_status = self.regions[region]
        
        try:
            async with self._session.post(
                f"{region_status.url}/api/replicate",
                json=data,
                headers={"X-Region": self.region_config.current_region}
            ) as response:
                if response.status == 200:
                    logger.info(f"Replicated data to {region}")
                    return True
                else:
                    logger.error(f"Replication to {region} failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Replication to {region} error: {e}")
            return False
    
    async def replicate_to_all(self, data: Dict[str, Any]) -> Dict[str, bool]:
        """
        Replicate data to all replication regions.
        
        Args:
            data: Data to replicate
            
        Returns:
            Dictionary mapping region to success status
        """
        if not self.region_config.replication_enabled:
            return {}
        
        results = {}
        for region in self.region_config.replication_regions:
            results[region] = await self.replicate_to_region(region, data)
        
        return results
    
    def get_region_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all regions."""
        return {
            region: {
                "healthy": status.healthy,
                "latency_ms": status.latency_ms,
                "last_check": status.last_check.isoformat() if status.last_check else None,
                "error": status.error,
            }
            for region, status in self.regions.items()
        }
    
    def is_current_region_primary(self) -> bool:
        """Check if current region is primary."""
        if not self.region_config.enabled:
            return True
        
        return (
            self.region_config.primary_region is None or
            self.region_config.current_region == self.region_config.primary_region
        )
