from __future__ import annotations

from pathlib import Path
from typing import Dict


def create_standard_result_layout(output_dir: str | Path) -> Dict[str, Path]:
    """
    创建标准化 results 目录结构，便于工程部署、批处理和后续 GUI 对接。
    """
    root = Path(output_dir)
    paths = {
        "root": root,
        "tables": root / "tables",
        "figures": root / "figures",
        "figures_heatmaps": root / "figures" / "heatmaps",
        "figures_scenario_voltage": root / "figures" / "scenario_voltage",
        "figures_scenario_flow": root / "figures" / "scenario_flow",
        "figures_topology_maps": root / "figures" / "topology_maps",
        "figures_rankings": root / "figures" / "rankings",
        "figures_report_summary": root / "figures" / "report_summary",
        "paper_figures": root / "paper_figures",
        "reports": root / "reports",
        "runtime": root / "runtime",
        "logs": root / "logs",
        "scenarios": root / "scenarios",
    }

    for p in paths.values():
        p.mkdir(parents=True, exist_ok=True)

    return paths
