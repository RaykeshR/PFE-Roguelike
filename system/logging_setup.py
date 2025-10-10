import json
import logging
import logging.handlers
import os
from datetime import datetime


class JsonFormatter(logging.Formatter):
    """Formatteur JSON simple et robuste pour logs applicatifs."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "pathname": record.pathname,
            "lineno": record.lineno,
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            # Merge extra structured data
            payload.update(record.extra)
        return json.dumps(payload, ensure_ascii=False)


def ensure_logs_dir(base_dir: str = None) -> str:
    """Crée le dossier logs s'il n'existe pas et renvoie son chemin."""
    if base_dir is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logs_dir = os.path.join(base_dir, "logs")
    try:
        os.makedirs(logs_dir, exist_ok=True)
    except Exception:
        # Dernier recours: dossier courant
        logs_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(logs_dir, exist_ok=True)
    return logs_dir


def setup_json_logging(app_logger_name: str = "pfe_roguelike", level: int = logging.INFO) -> logging.Logger:
    """Configure un logger racine de l'app au format JSON avec rotation journalière."""
    logger = logging.getLogger(app_logger_name)
    if logger.handlers:
        return logger  # déjà configuré

    logger.setLevel(level)

    logs_dir = ensure_logs_dir()
    log_file = os.path.join(logs_dir, "app.jsonl")

    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_file, when="midnight", backupCount=7, encoding="utf-8"
    )
    file_handler.setFormatter(JsonFormatter())
    file_handler.setLevel(level)

    # Console handler (utile en dev)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JsonFormatter())
    console_handler.setLevel(level)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False

    logger.info("Logging JSON initialisé", extra={"extra": {"logs_dir": logs_dir}})
    return logger


