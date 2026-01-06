"""
Community-contributed analyzer: String Analysis Plugin

This plugin analyzes strings in binaries for security-relevant patterns.
Contributed by the community.
"""

from ghidrainsight.plugins import BaseAnalyzer, AnalysisResult
from typing import Dict, Any, Optional, List
import time
import re


class StringAnalyzer(BaseAnalyzer):
    """
    Analyzes strings in binaries for security-relevant patterns.
    
    Detects:
    - API keys and tokens
    - URLs and endpoints
    - File paths
    - Suspicious strings
    """
    
    def __init__(self):
        super().__init__(
            name="community_string_analyzer",
            version="1.0.0"
        )
        self.config = {
            "min_string_length": 4,
            "check_api_keys": True,
            "check_urls": True,
            "check_paths": True,
        }
    
    def analyze(self, binary_data: bytes, context: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """Analyze strings in binary."""
        start_time = time.time()
        findings: List[Dict[str, Any]] = []
        
        # Extract strings
        strings = self._extract_strings(binary_data)
        
        # Check for API keys
        if self.config.get("check_api_keys", True):
            api_key_findings = self._check_api_keys(strings)
            findings.extend(api_key_findings)
        
        # Check for URLs
        if self.config.get("check_urls", True):
            url_findings = self._check_urls(strings)
            findings.extend(url_findings)
        
        # Check for file paths
        if self.config.get("check_paths", True):
            path_findings = self._check_paths(strings)
            findings.extend(path_findings)
        
        # Check for suspicious strings
        suspicious_findings = self._check_suspicious(strings)
        findings.extend(suspicious_findings)
        
        execution_time = (time.time() - start_time) * 1000
        
        return self._create_result(
            findings=findings,
            metadata={
                "total_strings": len(strings),
                "strings_analyzed": len(strings),
            },
            execution_time_ms=execution_time,
            confidence=0.80
        )
    
    def _extract_strings(self, binary_data: bytes) -> List[str]:
        """Extract printable strings from binary."""
        strings = []
        current_string = b""
        
        for byte in binary_data:
            if 32 <= byte <= 126:  # Printable ASCII
                current_string += bytes([byte])
            else:
                if len(current_string) >= self.config.get("min_string_length", 4):
                    try:
                        strings.append(current_string.decode('ascii', errors='ignore'))
                    except:
                        pass
                current_string = b""
        
        # Add last string if exists
        if len(current_string) >= self.config.get("min_string_length", 4):
            try:
                strings.append(current_string.decode('ascii', errors='ignore'))
            except:
                pass
        
        return strings
    
    def _check_api_keys(self, strings: List[str]) -> List[Dict[str, Any]]:
        """Check for API keys and tokens."""
        findings = []
        
        # Common API key patterns
        patterns = {
            "aws_key": r"AKIA[0-9A-Z]{16}",
            "github_token": r"ghp_[a-zA-Z0-9]{36}",
            "slack_token": r"xox[baprs]-[0-9a-zA-Z-]{10,}",
            "jwt": r"eyJ[A-Za-z0-9-_=]+\.eyJ[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*",
        }
        
        for string in strings:
            for key_type, pattern in patterns.items():
                if re.search(pattern, string, re.IGNORECASE):
                    findings.append({
                        "type": "api_key_detected",
                        "key_type": key_type,
                        "severity": "high",
                        "description": f"Potential {key_type} found in binary",
                        "location": "strings",
                    })
        
        return findings
    
    def _check_urls(self, strings: List[str]) -> List[Dict[str, Any]]:
        """Check for URLs."""
        findings = []
        
        url_pattern = r"https?://[^\s<>\"{}|\\^`\[\]]+"
        
        for string in strings:
            urls = re.findall(url_pattern, string)
            for url in urls:
                # Check for suspicious URLs
                if any(domain in url.lower() for domain in ["pastebin.com", "paste.ee", "hastebin.com"]):
                    findings.append({
                        "type": "suspicious_url",
                        "url": url,
                        "severity": "medium",
                        "description": f"Suspicious URL found: {url}",
                        "location": "strings",
                    })
                elif "api" in url.lower() or "endpoint" in url.lower():
                    findings.append({
                        "type": "api_endpoint",
                        "url": url,
                        "severity": "low",
                        "description": f"API endpoint found: {url}",
                        "location": "strings",
                    })
        
        return findings
    
    def _check_paths(self, strings: List[str]) -> List[Dict[str, Any]]:
        """Check for file paths."""
        findings = []
        
        # Windows paths
        windows_path_pattern = r"[A-Za-z]:\\(?:[^\\/:*?\"<>|\r\n]+\\)*[^\\/:*?\"<>|\r\n]*"
        # Unix paths
        unix_path_pattern = r"/(?:[^/\0]+/)*[^/\0]+"
        
        for string in strings:
            # Check for sensitive paths
            sensitive_paths = [
                "/etc/passwd", "/etc/shadow", "/etc/hosts",
                "C:\\Windows\\System32", "C:\\Windows\\Temp",
                "/tmp/", "/var/log/", ".ssh/", ".aws/",
            ]
            
            for path_pattern in [windows_path_pattern, unix_path_pattern]:
                paths = re.findall(path_pattern, string)
                for path in paths:
                    if any(sensitive in path.lower() for sensitive in sensitive_paths):
                        findings.append({
                            "type": "sensitive_path",
                            "path": path,
                            "severity": "medium",
                            "description": f"Sensitive file path found: {path}",
                            "location": "strings",
                        })
        
        return findings
    
    def _check_suspicious(self, strings: List[str]) -> List[Dict[str, Any]]:
        """Check for suspicious strings."""
        findings = []
        
        suspicious_keywords = [
            "password", "secret", "key", "token", "credential",
            "backdoor", "trojan", "malware", "exploit",
            "cmd.exe", "/bin/sh", "powershell",
        ]
        
        for string in strings:
            lower_string = string.lower()
            for keyword in suspicious_keywords:
                if keyword in lower_string:
                    findings.append({
                        "type": "suspicious_string",
                        "keyword": keyword,
                        "severity": "low",
                        "description": f"Suspicious keyword found: {keyword}",
                        "location": "strings",
                    })
        
        return findings
    
    def validate(self) -> bool:
        """Validate plugin configuration."""
        return self.config.get("min_string_length", 0) > 0
