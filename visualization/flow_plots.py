# visualization/flow_plots.py

from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


def plot_line_flow_changes(
    delta_line_df: pd.DataFrame,
    scenario_id: str,
    save_path: str | Path
) -> None:
    """
    绘制线路有功潮流变化图。
    """
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    df = delta_line_df.sort_values("line_id")

    plt.figure(figsize=(11, 5))
    plt.bar(df["line_id"], df["delta_p_from_mw"])
    plt.xlabel("Line ID")
    plt.ylabel("Delta P_from (MW)")
    plt.title(f"Line Active Power Change - {scenario_id}")
    plt.grid(True, axis="y")
    plt.tight_layout()
    plt.savefig(save_path, dpi=200)
    plt.close()


def plot_line_reactive_changes(
    delta_line_df: pd.DataFrame,
    scenario_id: str,
    save_path: str | Path
) -> None:
    """
    绘制线路无功潮流变化图。
    """
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    df = delta_line_df.sort_values("line_id")

    plt.figure(figsize=(11, 5))
    plt.bar(df["line_id"], df["delta_q_from_mvar"])
    plt.xlabel("线路编号")
    plt.ylabel("无功变化量 (Mvar)")
    plt.title(f"线路无功潮流变化 - {scenario_id}")
    plt.grid(True, axis="y")
    plt.tight_layout()
    plt.savefig(save_path, dpi=200)
    plt.close()