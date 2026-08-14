from __future__ import annotations

from typing import Dict, Any
import pandas as pd

from simulation.powerflow_runner import run_powerflow
from simulation.scenario_manager import generate_scenarios
from simulation.batch_simulator import run_batch_simulations
from analysis.sensitivity_calc import calculate_all_sensitivities
from analysis.impact_metrics import evaluate_impacts
from analysis.report_summary import (
    build_group_report_tables,
    build_overall_top_tables,
    generate_text_summary,
)


def summarize_sim_results(sim_results, cfg: Dict[str, Any]) -> pd.DataFrame:
    rows = []

    for item in sim_results:
        row = {
            "scenario_id": item.get("scenario_id"),
            "success": item.get("success", False)
        }

        meta = item.get("scenario_meta", {})
        row.update({
            "network_type": meta.get("network_type"),
            "node_type": meta.get("node_type"),
            "target_bus": meta.get("target_bus"),
            "disturbance_type": meta.get("disturbance_type"),
            "disturbance_value": meta.get("disturbance_value")
        })

        if item.get("success", False) and item.get("delta_result") is not None:
            delta_bus = item["delta_result"]["delta_bus"]
            delta_line = item["delta_result"]["delta_line"]
            delta_loss = item["delta_result"]["delta_loss"]

            row["max_abs_delta_vm_pu"] = float(delta_bus["delta_vm_pu"].abs().max())
            row["affected_bus_count"] = int((delta_bus["delta_vm_pu"].abs() >= float(cfg.get("voltage_impact_threshold", 0.005))).sum())

            if not delta_line.empty:
                row["max_abs_delta_p_from_mw"] = float(delta_line["delta_p_from_mw"].abs().max())
                row["max_abs_delta_q_from_mvar"] = float(delta_line["delta_q_from_mvar"].abs().max())
            else:
                row["max_abs_delta_p_from_mw"] = 0.0
                row["max_abs_delta_q_from_mvar"] = 0.0

            row["delta_p_loss_mw"] = float(delta_loss["delta_p_loss_mw"])
            row["delta_q_loss_mvar"] = float(delta_loss["delta_q_loss_mvar"])
        else:
            row["max_abs_delta_vm_pu"] = None
            row["affected_bus_count"] = None
            row["max_abs_delta_p_from_mw"] = None
            row["max_abs_delta_q_from_mvar"] = None
            row["delta_p_loss_mw"] = None
            row["delta_q_loss_mvar"] = None
            row["error"] = item.get("error") or item.get("powerflow_result", {}).get("error")

        rows.append(row)

    return pd.DataFrame(rows)


def run_full_sensitivity_pipeline(net_base, net_pv, cfg: Dict[str, Any], output_dir: str) -> Dict[str, Any]:
    base_result = run_powerflow(net_base)
    if not base_result["success"]:
        raise RuntimeError(f"基础网络潮流失败: {base_result.get('error')}")

    pv_base_result = run_powerflow(net_pv)
    if not pv_base_result["success"]:
        raise RuntimeError(f"PV扩展网络潮流失败: {pv_base_result.get('error')}")

    scenarios = generate_scenarios(cfg)

    sim_results = run_batch_simulations(
        net_base=net_base,
        net_pv=net_pv,
        base_result=base_result,
        pv_base_result=pv_base_result,
        scenarios=scenarios,
        cfg=cfg,
        output_dir=output_dir
    )

    summary_df = summarize_sim_results(sim_results, cfg)
    sensitivity_results = calculate_all_sensitivities(sim_results, cfg)
    impact_results = evaluate_impacts(sim_results, sensitivity_results, cfg)
    group_tables = build_group_report_tables(summary_df, sensitivity_results)
    overall_tables = build_overall_top_tables(sensitivity_results)
    text_summary = generate_text_summary(summary_df, group_tables, overall_tables)

    return {
        "base_result": base_result,
        "pv_base_result": pv_base_result,
        "scenarios": scenarios,
        "sim_results": sim_results,
        "summary_df": summary_df,
        "sensitivity_results": sensitivity_results,
        "impact_results": impact_results,
        "group_tables": group_tables,
        "overall_tables": overall_tables,
        "text_summary": text_summary,
    }
