"""
Community-contributed analyzer: Entropy Analysis Plugin

This plugin analyzes binary entropy to detect encryption, compression, or obfuscation.
Contributed by the community.
"""

from ghidrainsight.plugins import BaseAnalyzer, AnalysisResult
from typing import Dict, Any, Optional, List
import time
from collections import Counter
import math


class EntropyAnalyzer(BaseAnalyzer):
    """
    Analyzes binary entropy to detect encryption, compression, or obfuscation.
    
    High entropy regions may indicate:
    - Encrypted data
    - Compressed data
    - Obfuscated code
    - Packed executables
    """
    
    def __init__(self):
        super().__init__(
            name="community_entropy_analyzer",
            version="1.0.0"
        )
        self.config = {
            "window_size": 256,
            "high_entropy_threshold": 7.5,
            "very_high_entropy_threshold": 7.9,
            "step_size": 128,
        }
    
    def analyze(self, binary_data: bytes, context: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """Analyze binary entropy."""
        start_time = time.time()
        findings: List[Dict[str, Any]] = []
        
        if len(binary_data) < self.config.get("window_size", 256):
            return self._create_result(
                findings=[],
                metadata={"error": "Binary too small for entropy analysis"},
                execution_time_ms=0.0,
                confidence=0.0
            )
        
        window_size = self.config.get("window_size", 256)
        step_size = self.config.get("step_size", 128)
        high_threshold = self.config.get("high_entropy_threshold", 7.5)
        very_high_threshold = self.config.get("very_high_entropy_threshold", 7.9)
        
        high_entropy_regions = []
        very_high_entropy_regions = []
        
        # Calculate entropy for sliding windows
        for i in range(0, len(binary_data) - window_size, step_size):
            window = binary_data[i:i + window_size]
            entropy = self._calculate_entropy(window)
            
            if entropy >= very_high_threshold:
                very_high_entropy_regions.append({
                    "offset": i,
                    "entropy": round(entropy, 2),
                    "size": window_size,
                })
            elif entropy >= high_threshold:
                high_entropy_regions.append({
                    "offset": i,
                    "entropy": round(entropy, 2),
                    "size": window_size,
                })
        
        # Create findings
        if very_high_entropy_regions:
            findings.append({
                "type": "very_high_entropy",
                "regions": very_high_entropy_regions[:10],  # Limit to 10
                "count": len(very_high_entropy_regions),
                "severity": "high",
                "description": f"Found {len(very_high_entropy_regions)} regions with very high entropy (>= {very_high_threshold}). Possible encryption or packing.",
            })
        
        if high_entropy_regions:
            findings.append({
                "type": "high_entropy",
                "regions": high_entropy_regions[:10],  # Limit to 10
                "count": len(high_entropy_regions),
                "severity": "medium",
                "description": f"Found {len(high_entropy_regions)} regions with high entropy (>= {high_threshold}). Possible compression or obfuscation.",
            })
        
        # Overall entropy
        overall_entropy = self._calculate_entropy(binary_data)
        findings.append({
            "type": "overall_entropy",
            "entropy": round(overall_entropy, 2),
            "severity": "info",
            "description": f"Overall binary entropy: {overall_entropy:.2f}",
        })
        
        execution_time = (time.time() - start_time) * 1000
        
        return self._create_result(
            findings=findings,
            metadata={
                "binary_size": len(binary_data),
                "windows_analyzed": (len(binary_data) - window_size) // step_size + 1,
                "overall_entropy": round(overall_entropy, 2),
            },
            execution_time_ms=execution_time,
            confidence=0.85
        )
    
    def _calculate_entropy(self, data: bytes) -> float:
        """Calculate Shannon entropy of data."""
        if len(data) == 0:
            return 0.0
        
        byte_counts = Counter(data)
        entropy = 0.0
        
        for count in byte_counts.values():
            probability = count / len(data)
            if probability > 0:
                entropy -= probability * math.log2(probability)
        
        return entropy
    
    def validate(self) -> bool:
        """Validate plugin configuration."""
        return (
            self.config.get("window_size", 0) > 0 and
            self.config.get("step_size", 0) > 0 and
            self.config.get("high_entropy_threshold", 0) > 0
        )
