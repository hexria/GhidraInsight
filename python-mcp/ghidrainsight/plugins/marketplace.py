"""Plugin marketplace for discovering and installing community plugins."""

import json
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import requests
from pathlib import Path

from .registry import PluginRegistry
from .loader import PluginLoader

logger = logging.getLogger(__name__)


@dataclass
class MarketplacePlugin:
    """Plugin information from marketplace."""
    name: str
    version: str
    author: str
    description: str
    repository: str
    download_url: str
    install_count: int = 0
    rating: float = 0.0
    tags: List[str] = None
    verified: bool = False
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class PluginMarketplace:
    """Marketplace for discovering and installing plugins."""
    
    def __init__(self, marketplace_url: Optional[str] = None, cache_dir: Optional[str] = None):
        """
        Initialize plugin marketplace.
        
        Args:
            marketplace_url: URL to marketplace API (default: GitHub-based)
            cache_dir: Directory to cache plugin metadata
        """
        self.marketplace_url = marketplace_url or "https://api.github.com/search/repositories"
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / ".ghidrainsight" / "marketplace"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.registry = PluginRegistry()
        self.loader = PluginLoader()
    
    def search(self, query: str, tags: Optional[List[str]] = None) -> List[MarketplacePlugin]:
        """
        Search for plugins in marketplace.
        
        Args:
            query: Search query
            tags: Filter by tags
            
        Returns:
            List of matching plugins
        """
        try:
            # Search GitHub for plugins with topic "ghidrainsight-plugin"
            params = {
                "q": f"{query} topic:ghidrainsight-plugin",
                "sort": "stars",
                "order": "desc"
            }
            
            response = requests.get(self.marketplace_url, params=params, timeout=10)
            response.raise_for_status()
            
            results = response.json()
            plugins = []
            
            for repo in results.get("items", [])[:20]:  # Limit to top 20
                plugin = self._parse_github_repo(repo)
                if plugin:
                    # Filter by tags if provided
                    if tags and not any(tag in plugin.tags for tag in tags):
                        continue
                    plugins.append(plugin)
            
            return plugins
            
        except Exception as e:
            logger.error(f"Failed to search marketplace: {e}")
            return []
    
    def get_popular(self, limit: int = 10) -> List[MarketplacePlugin]:
        """Get popular plugins."""
        return self.search("", tags=None)[:limit]
    
    def get_by_tag(self, tag: str) -> List[MarketplacePlugin]:
        """Get plugins by tag."""
        return self.search("", tags=[tag])
    
    def install(self, plugin: MarketplacePlugin, install_dir: Optional[str] = None) -> bool:
        """
        Install a plugin from marketplace.
        
        Args:
            plugin: Plugin to install
            install_dir: Directory to install plugin (default: ./plugins)
            
        Returns:
            True if installed successfully
        """
        try:
            install_path = Path(install_dir) if install_dir else Path("./plugins")
            install_path.mkdir(parents=True, exist_ok=True)
            
            # Download plugin file
            if plugin.download_url.endswith(".py"):
                response = requests.get(plugin.download_url, timeout=30)
                response.raise_for_status()
                
                plugin_file = install_path / f"{plugin.name}.py"
                plugin_file.write_text(response.text)
                
                # Load and register plugin
                loaded_plugin = self.loader.load_from_file(str(plugin_file))
                if loaded_plugin:
                    logger.info(f"Installed plugin: {plugin.name} v{plugin.version}")
                    return True
                else:
                    logger.error(f"Failed to load installed plugin: {plugin.name}")
                    plugin_file.unlink()  # Clean up
                    return False
            else:
                logger.error(f"Unsupported plugin format: {plugin.download_url}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to install plugin {plugin.name}: {e}")
            return False
    
    def uninstall(self, plugin_name: str, plugin_dir: Optional[str] = None) -> bool:
        """Uninstall a plugin."""
        try:
            plugin_path = Path(plugin_dir) if plugin_dir else Path("./plugins")
            plugin_file = plugin_path / f"{plugin_name}.py"
            
            if plugin_file.exists():
                plugin_file.unlink()
                self.registry.unregister(plugin_name)
                logger.info(f"Uninstalled plugin: {plugin_name}")
                return True
            else:
                logger.warning(f"Plugin file not found: {plugin_file}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to uninstall plugin {plugin_name}: {e}")
            return False
    
    def list_installed(self) -> List[Dict[str, Any]]:
        """List installed plugins."""
        return self.registry.get_info()
    
    def _parse_github_repo(self, repo: Dict[str, Any]) -> Optional[MarketplacePlugin]:
        """Parse GitHub repository into MarketplacePlugin."""
        try:
            # Look for plugin metadata in repository
            # This is a simplified version - real implementation would check for metadata file
            name = repo.get("name", "").replace("ghidrainsight-", "").replace("-plugin", "")
            
            # Try to get plugin.py or similar
            download_url = f"{repo['html_url']}/raw/main/{name}.py"
            
            # Extract tags from topics
            tags = repo.get("topics", [])
            tags = [t for t in tags if t != "ghidrainsight-plugin"]
            
            return MarketplacePlugin(
                name=name,
                version="1.0.0",  # Would parse from metadata
                author=repo.get("owner", {}).get("login", "unknown"),
                description=repo.get("description", ""),
                repository=repo.get("html_url", ""),
                download_url=download_url,
                install_count=repo.get("stargazers_count", 0),
                rating=0.0,  # Would calculate from reviews
                tags=tags,
                verified=repo.get("owner", {}).get("type") == "Organization"
            )
        except Exception as e:
            logger.debug(f"Failed to parse repository: {e}")
            return None
    
    def update_cache(self) -> None:
        """Update local plugin cache."""
        try:
            popular = self.get_popular(limit=50)
            cache_file = self.cache_dir / "plugins.json"
            
            cache_data = {
                "updated": datetime.utcnow().isoformat(),
                "plugins": [
                    {
                        "name": p.name,
                        "version": p.version,
                        "author": p.author,
                        "description": p.description,
                        "repository": p.repository,
                        "download_url": p.download_url,
                        "install_count": p.install_count,
                        "rating": p.rating,
                        "tags": p.tags,
                        "verified": p.verified
                    }
                    for p in popular
                ]
            }
            
            cache_file.write_text(json.dumps(cache_data, indent=2))
            logger.info(f"Updated plugin cache: {len(popular)} plugins")
            
        except Exception as e:
            logger.error(f"Failed to update cache: {e}")
