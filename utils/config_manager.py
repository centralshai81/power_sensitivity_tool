from __future__ import annotations

from pathlib import Path
from typing import Dict, Any
import json


def _deep_merge_dict(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(a)
    for k, v in b.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge_dict(out[k], v)
        else:
            out[k] = v
    return out


def load_json_file(path: str | Path) -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"配置文件不存在: {p}")
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_project_config(
    system_config: str | Path,
    network_config: str | Path,
    analysis_config: str | Path,
) -> Dict[str, Any]:
    """
    读取并合并三层配置：
    1. system_config
    2. network_config
    3. analysis_config

    后者覆盖前者。
    """
    cfg_system = load_json_file(system_config)
    cfg_network = load_json_file(network_config)
    cfg_analysis = load_json_file(analysis_config)

    cfg = _deep_merge_dict(cfg_system, cfg_network)
    cfg = _deep_merge_dict(cfg, cfg_analysis)

    # 恢复 int key
    if "pv_node_settings" in cfg and isinstance(cfg["pv_node_settings"], dict):
        try:
            cfg["pv_node_settings"] = {int(k): v for k, v in cfg["pv_node_settings"].items()}
        except Exception:
            pass

    return cfg


def export_runtime_config(cfg: Dict[str, Any], output_path: str | Path) -> None:
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
