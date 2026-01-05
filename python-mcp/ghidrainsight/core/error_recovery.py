"""Advanced error recovery and resilience module."""

import logging
import asyncio
import time
from typing import Dict, Any, List, Callable, Optional, Union
from dataclasses import dataclass
from enum import Enum
import traceback

logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecoveryStrategy(Enum):
    """Available recovery strategies."""
    RETRY = "retry"
    FALLBACK = "fallback"
    SKIP = "skip"
    ESCALATE = "escalate"


@dataclass
class AnalysisError:
    """Represents an analysis error with recovery information."""
    error_type: str
    message: str
    severity: ErrorSeverity
    recoverable: bool
    recovery_strategy: RecoveryStrategy
    context: Dict[str, Any]
    timestamp: float
    retry_count: int = 0
    max_retries: int = 3

    def should_retry(self) -> bool:
        """Check if error should be retried."""
        return (self.recoverable and
                self.recovery_strategy == RecoveryStrategy.RETRY and
                self.retry_count < self.max_retries)

    def increment_retry(self) -> None:
        """Increment retry count."""
        self.retry_count += 1


class ErrorRecoveryManager:
    """Advanced error recovery manager for analysis operations."""

    def __init__(self):
        self.error_handlers: Dict[str, Callable] = {}
        self.recovery_strategies: Dict[str, Callable] = {}
        self.error_history: List[AnalysisError] = []
        self.max_history_size = 1000

        self._setup_default_handlers()

    def _setup_default_handlers(self):
        """Setup default error handlers and recovery strategies."""

        # Timeout errors
        self.error_handlers["timeout"] = self._handle_timeout_error
        self.recovery_strategies["timeout"] = self._retry_with_backoff

        # Memory errors
        self.error_handlers["memory"] = self._handle_memory_error
        self.recovery_strategies["memory"] = self._reduce_complexity_fallback

        # Network errors
        self.error_handlers["network"] = self._handle_network_error
        self.recovery_strategies["network"] = self._retry_with_exponential_backoff

        # Analysis errors
        self.error_handlers["analysis"] = self._handle_analysis_error
        self.recovery_strategies["analysis"] = self._fallback_to_simpler_analysis

        # Database errors
        self.error_handlers["database"] = self._handle_database_error
        self.recovery_strategies["database"] = self._retry_with_jitter

    async def execute_with_recovery(self, operation: Callable,
                                  operation_name: str,
                                  *args, **kwargs) -> Any:
        """
        Execute an operation with automatic error recovery.

        Args:
            operation: The operation to execute
            operation_name: Name of the operation for logging
            *args, **kwargs: Arguments for the operation

        Returns:
            Operation result or fallback result
        """
        start_time = time.time()

        try:
            result = await operation(*args, **kwargs)
            logger.info(f"Operation {operation_name} completed successfully")
            return result

        except Exception as e:
            error = self._create_error_from_exception(e, operation_name, args, kwargs)
            self._log_error(error)

            # Try recovery
            recovery_result = await self._attempt_recovery(error, operation, args, kwargs)

            if recovery_result is not None:
                execution_time = time.time() - start_time
                logger.info(f"Operation {operation_name} recovered successfully in {execution_time:.2f}s")
                return recovery_result
            else:
                # Recovery failed, re-raise original error
                raise e

    def _create_error_from_exception(self, exception: Exception,
                                   operation_name: str,
                                   args: tuple,
                                   kwargs: dict) -> AnalysisError:
        """Create AnalysisError from exception."""
        error_type = type(exception).__name__.lower()

        # Determine severity and recoverability
        if "timeout" in error_type:
            severity = ErrorSeverity.HIGH
            recoverable = True
            strategy = RecoveryStrategy.RETRY
        elif "memory" in error_type:
            severity = ErrorSeverity.CRITICAL
            recoverable = True
            strategy = RecoveryStrategy.FALLBACK
        elif "network" in error_type or "connection" in error_type:
            severity = ErrorSeverity.MEDIUM
            recoverable = True
            strategy = RecoveryStrategy.RETRY
        elif "database" in error_type:
            severity = ErrorSeverity.HIGH
            recoverable = True
            strategy = RecoveryStrategy.RETRY
        else:
            severity = ErrorSeverity.MEDIUM
            recoverable = False
            strategy = RecoveryStrategy.ESCALATE

        return AnalysisError(
            error_type=error_type,
            message=str(exception),
            severity=severity,
            recoverable=recoverable,
            recovery_strategy=strategy,
            context={
                "operation": operation_name,
                "args_count": len(args),
                "kwargs_keys": list(kwargs.keys()),
                "traceback": traceback.format_exc()
            },
            timestamp=time.time()
        )

    async def _attempt_recovery(self, error: AnalysisError,
                              operation: Callable,
                              args: tuple,
                              kwargs: dict) -> Optional[Any]:
        """Attempt to recover from an error."""
        if not error.recoverable:
            return None

        strategy_name = error.recovery_strategy.value
        strategy_func = self.recovery_strategies.get(strategy_name)

        if not strategy_func:
            logger.warning(f"No recovery strategy found for {strategy_name}")
            return None

        try:
            logger.info(f"Attempting recovery for {error.error_type} using {strategy_name}")
            return await strategy_func(error, operation, args, kwargs)
        except Exception as recovery_error:
            logger.error(f"Recovery failed for {error.error_type}: {recovery_error}")
            return None

    async def _retry_with_backoff(self, error: AnalysisError,
                                operation: Callable,
                                args: tuple,
                                kwargs: dict) -> Optional[Any]:
        """Retry operation with exponential backoff."""
        if not error.should_retry():
            return None

        base_delay = 1.0
        max_delay = 30.0

        for attempt in range(error.retry_count, error.max_retries):
            delay = min(base_delay * (2 ** attempt), max_delay)

            logger.info(f"Retrying {error.error_type} in {delay}s (attempt {attempt + 1})")
            await asyncio.sleep(delay)

            try:
                result = await operation(*args, **kwargs)
                logger.info(f"Retry successful for {error.error_type}")
                return result
            except Exception as e:
                logger.warning(f"Retry {attempt + 1} failed: {e}")
                error.increment_retry()

        return None

    async def _retry_with_exponential_backoff(self, error: AnalysisError,
                                            operation: Callable,
                                            args: tuple,
                                            kwargs: dict) -> Optional[Any]:
        """Retry with exponential backoff and jitter."""
        if not error.should_retry():
            return None

        import random
        base_delay = 1.0
        max_delay = 60.0
        jitter_factor = 0.1

        for attempt in range(error.retry_count, error.max_retries):
            delay = min(base_delay * (2 ** attempt), max_delay)
            jitter = delay * jitter_factor * random.uniform(-1, 1)
            total_delay = delay + jitter

            logger.info(f"Retrying {error.error_type} in {total_delay:.2f}s (attempt {attempt + 1})")
            await asyncio.sleep(total_delay)

            try:
                result = await operation(*args, **kwargs)
                logger.info(f"Retry successful for {error.error_type}")
                return result
            except Exception as e:
                logger.warning(f"Retry {attempt + 1} failed: {e}")
                error.increment_retry()

        return None

    async def _reduce_complexity_fallback(self, error: AnalysisError,
                                        operation: Callable,
                                        args: tuple,
                                        kwargs: dict) -> Optional[Any]:
        """Fallback by reducing analysis complexity."""
        # For memory errors, try with reduced features
        if "features" in kwargs:
            original_features = kwargs["features"]
            if len(original_features) > 1:
                # Try with fewer features
                reduced_features = original_features[:len(original_features)//2]
                kwargs["features"] = reduced_features
                logger.info(f"Falling back with reduced features: {reduced_features}")

                try:
                    result = await operation(*args, **kwargs)
                    return {
                        "fallback_applied": True,
                        "reason": "memory_error",
                        "reduced_features": reduced_features,
                        "result": result
                    }
                except Exception as e:
                    logger.warning(f"Fallback failed: {e}")

        return None

    async def _fallback_to_simpler_analysis(self, error: AnalysisError,
                                          operation: Callable,
                                          args: tuple,
                                          kwargs: dict) -> Optional[Any]:
        """Fallback to simpler analysis method."""
        # Try basic analysis instead of advanced
        if "features" in kwargs:
            original_features = kwargs["features"]
            simple_features = ["basic_info", "strings"]

            # Replace complex features with simple ones
            kwargs["features"] = simple_features
            logger.info(f"Falling back to simple analysis: {simple_features}")

            try:
                result = await operation(*args, **kwargs)
                return {
                    "fallback_applied": True,
                    "reason": "analysis_error",
                    "simple_features": simple_features,
                    "result": result
                }
            except Exception as e:
                logger.warning(f"Simple analysis fallback failed: {e}")

        return None

    async def _retry_with_jitter(self, error: AnalysisError,
                               operation: Callable,
                               args: tuple,
                               kwargs: dict) -> Optional[Any]:
        """Retry with jitter to avoid thundering herd."""
        import random

        if not error.should_retry():
            return None

        for attempt in range(error.retry_count, error.max_retries):
            # Jittered delay between 1-5 seconds
            delay = 1.0 + random.uniform(0, 4.0)

            logger.info(f"Retrying {error.error_type} with jitter in {delay:.2f}s (attempt {attempt + 1})")
            await asyncio.sleep(delay)

            try:
                result = await operation(*args, **kwargs)
                logger.info(f"Jitter retry successful for {error.error_type}")
                return result
            except Exception as e:
                logger.warning(f"Jitter retry {attempt + 1} failed: {e}")
                error.increment_retry()

        return None

    def _handle_timeout_error(self, error: AnalysisError) -> None:
        """Handle timeout errors."""
        logger.warning(f"Timeout error in {error.context.get('operation')}: {error.message}")

    def _handle_memory_error(self, error: AnalysisError) -> None:
        """Handle memory errors."""
        logger.error(f"Memory error in {error.context.get('operation')}: {error.message}")

    def _handle_network_error(self, error: AnalysisError) -> None:
        """Handle network errors."""
        logger.warning(f"Network error in {error.context.get('operation')}: {error.message}")

    def _handle_analysis_error(self, error: AnalysisError) -> None:
        """Handle analysis errors."""
        logger.error(f"Analysis error in {error.context.get('operation')}: {error.message}")

    def _handle_database_error(self, error: AnalysisError) -> None:
        """Handle database errors."""
        logger.error(f"Database error in {error.context.get('operation')}: {error.message}")

    def _log_error(self, error: AnalysisError) -> None:
        """Log error and add to history."""
        log_level = {
            ErrorSeverity.LOW: logging.DEBUG,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }.get(error.severity, logging.ERROR)

        logger.log(log_level, f"Analysis error: {error.error_type} - {error.message}")

        # Add to history
        self.error_history.append(error)
        if len(self.error_history) > self.max_history_size:
            self.error_history.pop(0)

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics."""
        if not self.error_history:
            return {"total_errors": 0}

        error_types = {}
        severities = {}
        recoveries = {"successful": 0, "failed": 0}

        for error in self.error_history:
            error_types[error.error_type] = error_types.get(error.error_type, 0) + 1
            severities[error.severity.value] = severities.get(error.severity.value, 0) + 1

            # Note: In real implementation, track recovery success
            recoveries["failed"] += 1  # Simplified

        return {
            "total_errors": len(self.error_history),
            "error_types": error_types,
            "severities": severities,
            "recovery_stats": recoveries,
            "most_common_error": max(error_types, key=error_types.get) if error_types else None
        }

    def clear_error_history(self) -> None:
        """Clear error history."""
        self.error_history.clear()


# Global error recovery manager
error_recovery_manager = ErrorRecoveryManager()
