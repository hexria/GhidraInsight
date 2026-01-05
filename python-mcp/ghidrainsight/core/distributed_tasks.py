"""Celery tasks for distributed analysis."""

import logging
from typing import Dict, Any, List

try:
    from celery import Celery
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

from .analysis import analysis_engine

logger = logging.getLogger(__name__)

# Create Celery app instance (will be configured by DistributedAnalysisManager)
if CELERY_AVAILABLE:
    app = Celery('ghidrainsight')
else:
    app = None


@app.task(bind=True, name='ghidrainsight.core.distributed_tasks.analyze_binary_chunk')
def analyze_binary_chunk(self, binary_chunk: bytes, offset: int,
                        features: List[str]) -> Dict[str, Any]:
    """
    Analyze a chunk of binary data.

    This task runs on distributed worker nodes.
    """
    try:
        logger.info(f"Analyzing binary chunk at offset {offset}, size {len(binary_chunk)}")

        # Run analysis on this chunk
        # Note: This is a simplified version - real implementation would need
        # to handle offset-aware analysis
        result = analysis_engine._run_feature_analysis(features[0], binary_chunk)

        return {
            "offset": offset,
            "chunk_size": len(binary_chunk),
            "features": features,
            "results": {features[0]: result},
            "success": True
        }

    except Exception as e:
        logger.error(f"Chunk analysis failed: {e}")
        return {
            "offset": offset,
            "error": str(e),
            "success": False
        }


@app.task(bind=True, name='ghidrainsight.core.distributed_tasks.analyze_binary_parallel')
def analyze_binary_parallel(self, binary_data: bytes,
                           features: List[str]) -> Dict[str, Any]:
    """
    Analyze binary data with specific features in parallel.

    This task runs feature-specific analysis on distributed nodes.
    """
    try:
        logger.info(f"Running parallel analysis for features: {features}")

        # Run analysis for the specified features
        results = {}
        for feature in features:
            try:
                result = analysis_engine._run_feature_analysis(feature, binary_data)
                results[feature] = result
            except Exception as e:
                logger.error(f"Feature {feature} analysis failed: {e}")
                results[feature] = {"error": str(e)}

        return {
            "features_analyzed": features,
            "results": results,
            "success": True,
            "binary_size": len(binary_data)
        }

    except Exception as e:
        logger.error(f"Parallel analysis failed: {e}")
        return {
            "error": str(e),
            "success": False
        }


@app.task(bind=True, name='ghidrainsight.core.distributed_tasks.health_check')
def health_check(self) -> Dict[str, Any]:
    """Health check task for worker nodes."""
    return {
        "status": "healthy",
        "worker_id": self.request.hostname,
        "timestamp": self.request.eta
    }


@app.task(bind=True, name='ghidrainsight.core.distributed_tasks.get_worker_stats')
def get_worker_stats(self) -> Dict[str, Any]:
    """Get statistics from worker node."""
    import psutil
    import platform

    try:
        return {
            "hostname": self.request.hostname,
            "platform": platform.platform(),
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "disk_usage": psutil.disk_usage('/').percent,
            "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        }
    except ImportError:
        # psutil not available
        return {
            "hostname": self.request.hostname,
            "platform": platform.platform(),
            "error": "psutil not available for detailed stats"
        }
