from __future__ import annotations

from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']  # 支持中文的字体
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题


def _plot_single_heatmap(df: pd.DataFrame, title: str, save_path: str) -> None:
    if df is None or df.empty:
        return

    plt.figure(figsize=(10, 8))
    plt.imshow(df.values, aspect="auto")
    plt.colorbar()
    plt.title(title)
    plt.xlabel("扰动节点/列")
    plt.ylabel("响应节点/行")
    plt.tight_layout()
    plt.savefig(save_path, dpi=300)
    plt.close()


def plot_sensitivity_heatmaps(vv_matrix: pd.DataFrame, qv_matrix: pd.DataFrame, output_dir: str) -> None:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    _plot_single_heatmap(vv_matrix, "VV近似灵敏度热力图", str(output / "vv_heatmap.png"))
    _plot_single_heatmap(qv_matrix, "QV灵敏度热力图", str(output / "qv_heatmap.png"))
