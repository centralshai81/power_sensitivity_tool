from __future__ import annotations

import argparse
import json
from pathlib import Path

from main import main as run_main


def parse_args():
    parser = argparse.ArgumentParser(description="配电网灵敏度分析平台")
    parser.add_argument("--system-config", default="config/system_config_v7.json", help="系统配置文件")
    parser.add_argument("--network-config", default="config/network_config_v7.json", help="网络配置文件")
    parser.add_argument("--analysis-config", default="config/analysis_config_v7.json", help="分析配置文件")
    parser.add_argument("--mode", default=None, choices=["quick", "full"], help="覆盖 quick_test")
    parser.add_argument("--network-source", default=None, choices=["excel", "matpower"], help="覆盖 network_source")
    parser.add_argument("--output-dir", default=None, help="覆盖 output_dir")
    return parser.parse_args()


def _patch_json(path: Path, patch: dict):
    with path.open("r", encoding="utf-8") as f:
        cfg = json.load(f)
    cfg.update({k: v for k, v in patch.items() if v is not None})
    with path.open("w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    args = parse_args()

    if args.mode is not None:
        _patch_json(Path(args.analysis_config), {"quick_test": args.mode == "quick"})

    if args.network_source is not None or args.output_dir is not None:
        _patch_json(
            Path(args.network_config),
            {"network_source": args.network_source, "output_dir": args.output_dir}
        )

    if args.output_dir is not None:
        _patch_json(Path(args.system_config), {"output_dir": args.output_dir})

    run_main()
