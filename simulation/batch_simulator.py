# simulation/batch_simulator.py

from __future__ import annotations

from typing import Dict, Any, List

from models.perturbation_models import (
    induce_voltage_sag_at_pq,
    set_voltage_at_pv,
    apply_reactive_disturbance
)
from simulation.powerflow_runner import (
    run_powerflow,
    calc_delta_bus,
    calc_delta_line,
    calc_delta_loss
)
from utils.io_utils import save_dataframe, save_json, scenario_output_dir


def _apply_disturbance(net, scenario: Dict[str, Any], cfg: Dict[str, Any]):
    node_type = scenario["node_type"]
    target_bus = scenario["target_bus"]
    disturbance_type = scenario["disturbance_type"]
    disturbance_value = scenario["disturbance_value"]

    if node_type == "PQ" and disturbance_type == "voltage_sag":
        sag_cfg = cfg["pq_voltage_sag"]
        return induce_voltage_sag_at_pq(
            net=net,
            target_bus=target_bus,
            target_vm_pu=disturbance_value,
            step_q=sag_cfg["step_q_mvar"],
            max_iter=sag_cfg["max_iter"],
            tolerance=sag_cfg["tolerance"]
        )

    if node_type == "PV" and disturbance_type == "voltage_sag":
        return set_voltage_at_pv(
            net=net,
            target_bus=target_bus,
            new_vm_pu=disturbance_value
        )

    if disturbance_type == "reactive_variation":
        return apply_reactive_disturbance(
            net=net,
            target_bus=target_bus,
            delta_q_mvar=disturbance_value,
            node_type=node_type
        )

    raise ValueError(f"不支持的场景: {scenario}")


def run_batch_simulations(
    net_base,
    net_pv,
    base_result: Dict[str, Any],
    pv_base_result: Dict[str, Any],
    scenarios: List[Dict[str, Any]],
    cfg: Dict[str, Any],
    output_dir: str
) -> List[Dict[str, Any]]:
    """
    批量运行全部场景。
    """
    sim_results = []

    for idx, scenario in enumerate(scenarios, start=1):
        scenario_id = scenario["scenario_id"]
        print(f"[RUN] ({idx}/{len(scenarios)}) {scenario_id}")

        if scenario["network_type"] == "base":
            net_ref = net_base
            ref_result = base_result
        elif scenario["network_type"] == "pv_extended":
            net_ref = net_pv
            ref_result = pv_base_result
        else:
            raise ValueError(f"未知 network_type: {scenario['network_type']}")

        try:
            net_disturbed, disturbance_info = _apply_disturbance(net_ref, scenario, cfg)
            disturbed_result = run_powerflow(net_disturbed)

            if not disturbed_result["success"]:
                sim_result = {
                    "scenario_id": scenario_id,
                    "scenario_meta": scenario,
                    "disturbance_info": disturbance_info,
                    "powerflow_result": disturbed_result,
                    "delta_result": None,
                    "success": False
                }
                sim_results.append(sim_result)
                continue

            delta_bus = calc_delta_bus(ref_result["bus_voltage"], disturbed_result["bus_voltage"])
            delta_line = calc_delta_line(ref_result["line_flow"], disturbed_result["line_flow"])
            delta_loss = calc_delta_loss(ref_result["system_loss"], disturbed_result["system_loss"])

            sim_result = {
                "scenario_id": scenario_id,
                "scenario_meta": scenario,
                "disturbance_info": disturbance_info,
                "powerflow_result": disturbed_result,
                "delta_result": {
                    "delta_bus": delta_bus,
                    "delta_line": delta_line,
                    "delta_loss": delta_loss
                },
                "success": True
            }
            sim_results.append(sim_result)

            # 保存单场景结果
            sc_dir = scenario_output_dir(output_dir, scenario_id)
            save_dataframe(disturbed_result["bus_voltage"], sc_dir / "bus_voltage.csv")
            save_dataframe(disturbed_result["line_flow"], sc_dir / "line_flow.csv")
            save_dataframe(delta_bus, sc_dir / "delta_bus.csv")
            save_dataframe(delta_line, sc_dir / "delta_line.csv")
            save_json({
                "scenario_meta": scenario,
                "disturbance_info": disturbance_info,
                "delta_loss": delta_loss,
                "success": True
            }, sc_dir / "summary.json")

        except Exception as e:
            sim_result = {
                "scenario_id": scenario_id,
                "scenario_meta": scenario,
                "error": str(e),
                "success": False
            }
            sim_results.append(sim_result)

            sc_dir = scenario_output_dir(output_dir, scenario_id)
            save_json({
                "scenario_meta": scenario,
                "error": str(e),
                "success": False
            }, sc_dir / "summary.json")

    return sim_results