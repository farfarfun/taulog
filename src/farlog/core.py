from __future__ import annotations

import sys
from pathlib import Path
from threading import Lock
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from loguru import Logger

_DEFAULT_FORMAT = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} |{level:8}| "
    "{name} : {module}:{line:4} | {extra[module_name]} | - {message}"
)
_DEFAULT_FORMAT_COLOR = (
    "{time:YYYY-MM-DD HH:mm:ss.SSS} |<lvl>{level:8}</>| "
    "{name} : {module}:{line:4} | <cyan>{extra[module_name]}</> | - <lvl>{message}</>"
)
_log_dir = Path("logs")
_loggers = {}
_lock = Lock()


def _ensure_log_dir(log_dir: str | Path) -> Path:
    path = Path(log_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def _add_file_handler(name: str, level: str, formatter: str) -> int:
    return logger.add(
        sink=_log_dir / f"{name}.log",
        format=formatter,
        filter=lambda record, _name=name: record["extra"].get("module_name") == _name,
        level=level,
        rotation="00:00",
        compression="gz",
        retention=7,
        colorize=False,
    )


def configure(log_dir: str | Path = "logs") -> None:
    """显式配置控制台输出与聚合日志文件（`all.log`）。

    Args:
        log_dir: 日志文件存放目录，默认 "logs"。

    Returns:
        None。
    """
    global _log_dir

    with _lock:
        path = _ensure_log_dir(log_dir)
        logger.configure(
            handlers=[
                {
                    "sink": sys.stderr,
                    "format": _DEFAULT_FORMAT_COLOR,
                    "colorize": True,
                    "level": "INFO",
                },
                {
                    "sink": path / "all.log",
                    "format": _DEFAULT_FORMAT,
                    "colorize": False,
                    "rotation": "00:00",
                    "compression": "gz",
                    "retention": 30,
                    "level": "INFO",
                },
            ],
            extra={"module_name": "-"},
        )
        _log_dir = path

        for name, (level, formatter, _, bound_logger) in list(_loggers.items()):
            handler_id = _add_file_handler(name, level, formatter)
            _loggers[name] = (level, formatter, handler_id, bound_logger)


def _validate_name(name: str) -> None:
    if (
        not isinstance(name, str)
        or not name
        or name in {".", ".."}
        or Path(name).name != name
        or "\0" in name
    ):
        raise ValueError("logger name must be a non-empty file name")


def get_logger(
    name: str = "default",
    level: str = "INFO",
    formatter: str | None = None,
) -> Logger:
    """获取一个按名称拆分、带单个按日轮转文件 handler 的 logger。

    Args:
        name: logger 名称，同时作为对应日志文件名（不能是路径、`.`/`..` 或含空字符）。
        level: 日志级别，默认 "INFO"。
        formatter: 可选的 Loguru 格式字符串，不传则使用默认格式。

    Returns:
        绑定了 `module_name` 的 Loguru logger 实例。
    """
    _validate_name(name)
    selected_formatter = formatter or _DEFAULT_FORMAT

    with _lock:
        current = _loggers.get(name)
        if current and current[:2] == (level, selected_formatter):
            return current[3]

        _ensure_log_dir(_log_dir)
        handler_id = _add_file_handler(name, level, selected_formatter)
        bound_logger = current[3] if current else logger.bind(module_name=name)
        if current:
            logger.remove(current[2])
        _loggers[name] = (level, selected_formatter, handler_id, bound_logger)
        return bound_logger


# Backward-compatible alias
getLogger = get_logger
