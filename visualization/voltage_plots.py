# visualization/voltage_plots.py

from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


def plot_bus_voltage_comparison(
    base_v: pd.DataFrame,
    disturbed_v: pd.DataFrame,
    scenario_id: str,
    save_path: str | Path
) -> None:
    """
    绘制扰动前后节点电压对比图。
    """
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    df = base_v.merge(
        disturbed_v,
        on=["pp_bus", "mp_bus"],
        suffixes=("_base", "_new")
    ).sort_values("mp_bus")

    plt.figure(figsize=(10, 5))
    plt.plot(df["mp_bus"], df["vm_pu_base"], marker="o", label="Base")
    plt.plot(df["mp_bus"], df["vm_pu_new"], marker="s", label="Disturbed")
    plt.xlabel("Bus Number")
    plt.ylabel("Voltage Magnitude (p.u.)")
    plt.title(f"Voltage Profile Comparison - {scenario_id}")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=200)
    plt.close()


def plot_delta_voltage_bar(
    delta_bus_df: pd.DataFrame,
    scenario_id: str,
    save_path: str | Path
) -> None:
    """
    绘制节点电压变化柱状图。
    """
    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    df = delta_bus_df.sort_values("mp_bus")

    plt.figure(figsize=(10, 5))
    plt.bar(df["mp_bus"], df["delta_vm_pu"])
    plt.xlabel("节点编号")
    plt.ylabel("电压变化量 (p.u.)")
    plt.title(f"节点电压变化 - {scenario_id}")
    plt.grid(True, axis="y")
    plt.tight_layout()
    plt.savefig(save_path, dpi=200)
    plt.close()