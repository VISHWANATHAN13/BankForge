"""
BankForge - centralized logging configuration.

Uses Python's built-in logging module.

Features:
- DEBUG by default
- LOG_LEVEL environment variable support
- JSON structured logs
- ENTER / EXIT / FAILED tracing
- Call ID and execution duration
- Safe argument and result representation
"""

from __future__ import annotations

import functools
import inspect
import json
import logging
import os
import sys
import time
import uuid
from typing import Any, Callable


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_LOG_LEVEL = "DEBUG"

LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    DEFAULT_LOG_LEVEL,
).upper()


# ---------------------------------------------------------------------------
# JSON Formatter
# ---------------------------------------------------------------------------

class JsonFormatter(logging.Formatter):
    """
    Converts every log record into one JSON object.
    """

    def format(self, record: logging.LogRecord) -> str:

        log_data: dict[str, Any] = {
            "timestamp": self.formatTime(
                record,
                datefmt="%Y-%m-%dT%H:%M:%S%z",
            ),
            "level": record.levelname,
            "service": os.getenv(
                "SERVICE_NAME",
                "bankforge",
            ),
            "logger": record.name,
            "message": record.getMessage(),
        }

        extra_fields = getattr(
            record,
            "extra_fields",
            None,
        )

        if extra_fields:
            log_data["fields"] = extra_fields

        if record.exc_info:
            log_data["exception"] = self.formatException(
                record.exc_info
            )

        return json.dumps(
            log_data,
            default=str,
        )


# ---------------------------------------------------------------------------
# Logger management
# ---------------------------------------------------------------------------

_CONFIGURED_LOGGERS: set[str] = set()


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured BankForge logger.

    Example:

        logger = get_logger(__name__)
    """

    logger = logging.getLogger(name)

    if name in _CONFIGURED_LOGGERS:
        return logger

    handler = logging.StreamHandler(
        sys.stdout
    )

    handler.setFormatter(
        JsonFormatter()
    )

    logger.addHandler(handler)

    logger.setLevel(
        getattr(
            logging,
            LOG_LEVEL,
            logging.DEBUG,
        )
    )

    logger.propagate = False

    _CONFIGURED_LOGGERS.add(name)

    return logger


def set_log_level(level: str) -> None:
    """
    Change the log level for all BankForge loggers
    that have already been created.
    """

    resolved_level = getattr(
        logging,
        level.upper(),
        None,
    )

    if resolved_level is None:
        raise ValueError(
            f"Invalid log level: {level}"
        )

    for logger_name in _CONFIGURED_LOGGERS:
        logging.getLogger(
            logger_name
        ).setLevel(resolved_level)


# ---------------------------------------------------------------------------
# Safe value representation
# ---------------------------------------------------------------------------

def _safe_repr(
    value: Any,
    max_length: int = 200,
) -> Any:
    """
    Create a safe, short representation for logging.

    This does not perform PII masking.
    PII-specific masking will be handled by the
    BankForge guardrails module.
    """

    try:
        json.dumps(value)
        result = value
    except (TypeError, ValueError):
        result = str(value)

    if isinstance(result, str) and len(result) > max_length:
        return (
            result[:max_length]
            + f"...<truncated, {len(result)} chars total>"
        )

    return result


def _bind_arguments(
    function: Callable,
    args: tuple,
    kwargs: dict,
) -> dict:
    """
    Convert positional and keyword arguments into
    a readable dictionary.
    """

    try:
        signature = inspect.signature(function)

        bound = signature.bind_partial(
            *args,
            **kwargs,
        )

        return {
            name: _safe_repr(value)
            for name, value in bound.arguments.items()
            if name != "self"
        }

    except (TypeError, ValueError):
        return {
            "args": _safe_repr(args),
            "kwargs": _safe_repr(kwargs),
        }


# ---------------------------------------------------------------------------
# Trace decorator
# ---------------------------------------------------------------------------

def trace(
    logger: logging.Logger,
    redact: Callable[[dict], dict] | None = None,
):
    """
    Trace synchronous or asynchronous functions.

    Logs:

        ENTER
        EXIT

    or:

        ENTER
        FAILED

    Example:

        logger = get_logger(__name__)

        @trace(logger)
        def get_account(account_id):
            ...
    """

    def decorator(function: Callable) -> Callable:

        is_async = inspect.iscoroutinefunction(
            function
        )

        function_name = (
            f"{function.__module__}."
            f"{function.__qualname__}"
        )

        def log_enter(
            call_id: str,
            arguments: dict,
        ) -> None:

            if redact:
                arguments = redact(arguments)

            logger.debug(
                f"ENTER {function_name}",
                extra={
                    "extra_fields": {
                        "event": "enter",
                        "call_id": call_id,
                        "function": function_name,
                        "args": arguments,
                    }
                },
            )

        def log_exit(
            call_id: str,
            start_time: float,
            result: Any,
        ) -> None:

            duration_ms = round(
                (time.perf_counter() - start_time)
                * 1000,
                3,
            )

            logger.debug(
                f"EXIT {function_name}",
                extra={
                    "extra_fields": {
                        "event": "exit",
                        "call_id": call_id,
                        "function": function_name,
                        "duration_ms": duration_ms,
                        "result_preview": _safe_repr(result),
                    }
                },
            )

        def log_failure(
            call_id: str,
            start_time: float,
            exception: Exception,
        ) -> None:

            duration_ms = round(
                (time.perf_counter() - start_time)
                * 1000,
                3,
            )

            logger.error(
                f"FAILED {function_name}",
                extra={
                    "extra_fields": {
                        "event": "failed",
                        "call_id": call_id,
                        "function": function_name,
                        "duration_ms": duration_ms,
                        "error_type": type(exception).__name__,
                    }
                },
                exc_info=True,
            )

        # ---------------------------------------------------------------
        # Async function
        # ---------------------------------------------------------------

        if is_async:

            @functools.wraps(function)
            async def async_wrapper(
                *args,
                **kwargs,
            ):

                call_id = uuid.uuid4().hex[:12]

                arguments = _bind_arguments(
                    function,
                    args,
                    kwargs,
                )

                log_enter(
                    call_id,
                    arguments,
                )

                start_time = time.perf_counter()

                try:
                    result = await function(
                        *args,
                        **kwargs,
                    )

                except Exception as exception:
                    log_failure(
                        call_id,
                        start_time,
                        exception,
                    )
                    raise

                log_exit(
                    call_id,
                    start_time,
                    result,
                )

                return result

            return async_wrapper

        # ---------------------------------------------------------------
        # Synchronous function
        # ---------------------------------------------------------------

        @functools.wraps(function)
        def sync_wrapper(
            *args,
            **kwargs,
        ):

            call_id = uuid.uuid4().hex[:12]

            arguments = _bind_arguments(
                function,
                args,
                kwargs,
            )

            log_enter(
                call_id,
                arguments,
            )

            start_time = time.perf_counter()

            try:
                result = function(
                    *args,
                    **kwargs,
                )

            except Exception as exception:
                log_failure(
                    call_id,
                    start_time,
                    exception,
                )
                raise

            log_exit(
                call_id,
                start_time,
                result,
            )

            return result

        return sync_wrapper

    return decorator


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    logger = get_logger(
        "bankforge.selftest"
    )

    @trace(logger)
    def add(a: int, b: int) -> int:
        return a + b

    @trace(logger)
    def failing_function():
        raise ValueError(
            "Intentional test failure"
        )

    print(
        f"LOG_LEVEL={LOG_LEVEL}"
    )

    add(10, 20)

    try:
        failing_function()
    except ValueError:
        pass
