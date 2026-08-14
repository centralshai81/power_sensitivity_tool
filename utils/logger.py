from __future__ import annotations

from pathlib import Path
from datetime import datetime
from typing import Optional


class ProjectLogger:
    def __init__(self, log_dir: str | Path = "logs", run_name: Optional[str] = None):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        if run_name is None:
            run_name = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.run_name = run_name
        self.run_log = self.log_dir / f"{run_name}_run.log"
        self.warn_log = self.log_dir / f"{run_name}_warnings.log"
        self.error_log = self.log_dir / f"{run_name}_errors.log"

    def _write(self, path: Path, level: str, message: str):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{now}] [{level}] {message}\n"
        with path.open("a", encoding="utf-8") as f:
            f.write(line)

    def info(self, message: str):
        self._write(self.run_log, "INFO", message)

    def warning(self, message: str):
        self._write(self.run_log, "WARNING", message)
        self._write(self.warn_log, "WARNING", message)

    def error(self, message: str):
        self._write(self.run_log, "ERROR", message)
        self._write(self.error_log, "ERROR", message)

    def exception(self, message: str, exc: Exception):
        self.error(f"{message} | 异常: {type(exc).__name__}: {exc}")
