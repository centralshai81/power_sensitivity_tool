from __future__ import annotations

from pathlib import Path
from typing import Dict, Any
import pandas as pd


def _safe_head(df: pd.DataFrame, n: int = 10) -> str:
    if df is None or df.empty:
        return "无\n"
    return df.head(n).to_string(index=False) + "\n"


def generate_markdown_report(
    output_path: str | Path,
    cfg: Dict[str, Any],
    network_bundle: Dict[str, Any],
    result: Dict[str, Any],
) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    net_base = network_bundle["net_base"]
    net_pv = network_bundle["net_pv"]

    summary_df = result["summary_df"]
    group_stats = result["group_tables"].get("group_statistics", pd.DataFrame())
    vv_rank = result["overall_tables"].get("overall_vv_bus_rank", pd.DataFrame())
    qv_rank = result["overall_tables"].get("overall_qv_bus_rank", pd.DataFrame())
    line_rank = result["overall_tables"].get("overall_line_rank", pd.DataFrame())

    lines = []
    lines.append("# 配电网灵敏度分析报告")
    lines.append("")
    lines.append("## 1. 项目概况")
    lines.append(f"- 网络来源: {network_bundle.get('network_source', '')}")
    lines.append(f"- 输入文件: {network_bundle.get('input_file', '')}")
    lines.append(f"- 基础网络节点数: {len(net_base.bus)}")
    lines.append(f"- 基础网络线路数: {len(net_base.line)}")
    lines.append(f"- 基础网络负荷数: {len(net_base.load)}")
    lines.append(f"- 基础网络变压器数: {len(net_base.trafo)}")
    lines.append(f"- 基础网络分布式电源数(sgen): {len(net_base.sgen)}")
    lines.append(f"- PV扩展网络发电机数(gen): {len(net_pv.gen)}")
    lines.append("")

    lines.append("## 2. 分析配置")
    lines.append(f"- quick_test: {cfg.get('quick_test')}")
    lines.append(f"- PQ测试节点: {cfg.get('pq_test_nodes')}")
    lines.append(f"- PV测试节点: {cfg.get('pv_test_nodes')}")
    lines.append(f"- 电压暂降等级: {cfg.get('voltage_sag_levels')}")
    lines.append(f"- 无功扰动等级: {cfg.get('reactive_disturbance_levels')}")
    lines.append(f"- 电压影响阈值: {cfg.get('voltage_impact_threshold')}")
    lines.append("")

    lines.append("## 3. 场景汇总")
    lines.append(f"- 场景总数: {len(result.get('scenarios', []))}")
    if summary_df is not None and not summary_df.empty:
        success_num = int(summary_df['success'].fillna(False).sum()) if 'success' in summary_df.columns else len(summary_df)
        lines.append(f"- 成功场景数: {success_num}")
        lines.append(f"- 失败场景数: {len(summary_df) - success_num}")
    lines.append("")

    lines.append("## 4. 分组统计")
    lines.append("```")
    lines.append(_safe_head(group_stats, 20))
    lines.append("```")
    lines.append("")

    lines.append("## 5. 全局关键节点排名（VV）")
    lines.append("```")
    lines.append(_safe_head(vv_rank, 10))
    lines.append("```")
    lines.append("")

    lines.append("## 6. 全局关键节点排名（QV）")
    lines.append("```")
    lines.append(_safe_head(qv_rank, 10))
    lines.append("```")
    lines.append("")

    lines.append("## 7. 全局关键线路排名")
    lines.append("```")
    lines.append(_safe_head(line_rank, 10))
    lines.append("```")
    lines.append("")

    lines.append("## 8. 自动摘要")
    lines.append(result.get("text_summary", ""))
    lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def generate_text_report(
    output_path: str | Path,
    cfg: Dict[str, Any],
    network_bundle: Dict[str, Any],
    result: Dict[str, Any],
) -> None:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    net_base = network_bundle["net_base"]
    summary_df = result["summary_df"]

    lines = []
    lines.append("配电网灵敏度分析报告")
    lines.append("=" * 40)
    lines.append(f"网络来源: {network_bundle.get('network_source', '')}")
    lines.append(f"输入文件: {network_bundle.get('input_file', '')}")
    lines.append(f"节点数: {len(net_base.bus)}")
    lines.append(f"线路数: {len(net_base.line)}")
    lines.append(f"负荷数: {len(net_base.load)}")
    lines.append(f"场景数: {len(result.get('scenarios', []))}")
    if summary_df is not None and not summary_df.empty and "success" in summary_df.columns:
        lines.append(f"成功场景数: {int(summary_df['success'].fillna(False).sum())}")
    lines.append("")
    lines.append("摘要:")
    lines.append(result.get("text_summary", ""))

    output_path.write_text("\n".join(lines), encoding="utf-8")
