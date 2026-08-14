# visualization/summary_plots.py

from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


def plot_group_bar_comparison(
    group_stats_df: pd.DataFrame,
    value_col: str,
    title: str,
    ylabel: str,
    save_path: str | Path
) -> None:
    """
    绘制各组统计量对比柱状图。
    """
    if group_stats_df.empty or value_col not in group_stats_df.columns:
        return

    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    df = group_stats_df.copy()

    plt.figure(figsize=(9, 5))
    plt.bar(df["group_name"], df[value_col])
    plt.xticks(rotation=20)
    plt.title(title)
    plt.ylabel(ylabel)
    plt.grid(True, axis="y")
    plt.tight_layout()
    plt.savefig(save_path, dpi=220)
    plt.close()


def plot_top_bus_ranking(
    rank_df: pd.DataFrame,
    title: str,
    save_path: str | Path,
    top_k: int = 10,
    value_col: str = "mean_abs_sensitivity"
) -> None:
    """
    绘制前 top_k 个敏感节点排名图。
    """
    if rank_df.empty or value_col not in rank_df.columns:
        return

    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    df = rank_df.head(top_k).copy()

    plt.figure(figsize=(9, 5))
    plt.bar(df["obs_bus"].astype(str), df[value_col])
    plt.title(title)
    plt.xlabel("Observed Bus")
    plt.ylabel(value_col)
    plt.grid(True, axis="y")
    plt.tight_layout()
    plt.savefig(save_path, dpi=220)
    plt.close()


def plot_top_line_ranking(
    rank_df: pd.DataFrame,
    title: str,
    save_path: str | Path,
    top_k: int = 10,
    value_col: str = "combined_score"
) -> None:
    """
    绘制前 top_k 个关键线路排名图。
    """
    if rank_df.empty or value_col not in rank_df.columns:
        return

    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    df = rank_df.head(top_k).copy()

    plt.figure(figsize=(9, 5))
    plt.bar(df["line_id"].astype(str), df[value_col])
    plt.title(title)
    plt.xlabel("线路编号")
    plt.ylabel(value_col)
    plt.grid(True, axis="y")
    plt.tight_layout()
    plt.savefig(save_path, dpi=220)
    plt.close()


def plot_group_dual_metric(
    group_stats_df: pd.DataFrame,
    left_col: str,
    right_col: str,
    title: str,
    save_path: str | Path
) -> None:
    """
    绘制双指标对比图。
    """
    if group_stats_df.empty or left_col not in group_stats_df.columns or right_col not in group_stats_df.columns:
        return

    save_path = Path(save_path)
    save_path.parent.mkdir(parents=True, exist_ok=True)

    df = group_stats_df.copy()
    x = range(len(df))

    fig, ax1 = plt.subplots(figsize=(10, 5))
    ax1.bar(x, df[left_col], width=0.4)
    ax1.set_ylabel(left_col)
    ax1.set_xticks(list(x))
    ax1.set_xticklabels(df["group_name"], rotation=20)

    ax2 = ax1.twinx()
    ax2.plot(x, df[right_col], marker="o")
    ax2.set_ylabel(right_col)

    plt.title(title)
    fig.tight_layout()
    plt.savefig(save_path, dpi=220)
    plt.close()