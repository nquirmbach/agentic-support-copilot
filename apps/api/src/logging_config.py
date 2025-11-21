import json
import logging
import sys
import uuid
from contextvars import ContextVar
from datetime import datetime
from typing import Optional

_request_id_var: ContextVar[Optional[str]
                            ] = ContextVar("request_id", default=None)


class JsonFormatter(logging.Formatter):
    # type: ignore[override]
    def format(self, record: logging.LogRecord) -> str:
        log = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        request_id = getattr(record, "request_id",
                             None) or _request_id_var.get()
        if request_id:
            log["request_id"] = request_id

        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)

        return json.dumps(log, ensure_ascii=False)


def setup_logging() -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.handlers.clear()
    root.addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"support_copilot.{name}")


def set_request_id(request_id: Optional[str] = None) -> str:
    rid = request_id or str(uuid.uuid4())
    _request_id_var.set(rid)
    return rid


def get_request_id() -> Optional[str]:
    return _request_id_var.get()
