from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import pandas as pd


def ensure_dir(path) -> Path:
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def save_dataframe(df: pd.DataFrame, path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=False, encoding="utf-8-sig")


def save_json(obj: Any, path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)


def scenario_output_dir(output_dir, scenario_id: str) -> Path:
    return ensure_dir(Path(output_dir) / "scenarios" / scenario_id)
