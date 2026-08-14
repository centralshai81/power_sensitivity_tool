from __future__ import annotations

from pathlib import Path
from typing import Dict, Any

from input.adapters import load_networks_by_adapter
from simulation.pipeline_runner import run_full_sensitivity_pipeline
from model.network_builder import export_mapping_tables

from reporting.excel_exporter_legacy_v6 import export_all_results_to_excel_legacy
from reporting.paper_packager import package_paper_figures
from reporting.report_bundle import export_full_report_bundle

from visualization.heatmaps import plot_sensitivity_heatmap

from utils.io_utils import ensure_dir
from utils.chinese_mapper import save_dataframe_chinese
from utils.logger import ProjectLogger
from utils.config_manager import export_runtime_config
from utils.config_validator import validate_project_config
from utils.advanced_validator import validate_runtime_environment
from utils.result_layout import create_standard_result_layout


class ProjectService:
    """
    面向 GUI / API / 前端 的统一服务层。
    外部只需要调用 run_project(cfg)。
    """

    def __init__(self, logger: ProjectLogger | None = None):
        self.logger = logger

    def _log_info(self, msg: str):
        if self.logger:
            self.logger.info(msg)

    def _log_error(self, msg: str):
        if self.logger:
            self.logger.error(msg)

    def run_project(self, cfg: Dict[str, Any]) -> Dict[str, Any]:
        output_dir_name = cfg.get("output_dir", "results")
        # 确保输出目录相对于脚本所在目录
        from pathlib import Path
        script_dir = Path(__file__).parent.parent
        output_dir = script_dir / output_dir_name
        layout = create_standard_result_layout(output_dir)

        proj_errors = validate_project_config(cfg)
        env_errors = validate_runtime_environment(cfg)
        errors = proj_errors + env_errors
        if errors:
            for err in errors:
                self._log_error(err)
            raise ValueError("项目配置/环境校验失败:\n" + "\n".join(errors))

        export_runtime_config(cfg, layout["runtime"] / "runtime_config.json")
        self._log_info("已导出运行时配置")

        network_bundle = load_networks_by_adapter(cfg)
        self._log_info("网络加载完成")

        if network_bundle.get("meta"):
            export_mapping_tables(network_bundle["meta"], str(layout["root"] / "mapping_tables.xlsx"))
            self._log_info("已导出 mapping_tables.xlsx")

        result = run_full_sensitivity_pipeline(network_bundle["net_base"], network_bundle["net_pv"], cfg, output_dir)
        self._log_info("灵敏度分析主链执行完成")

        save_dataframe_chinese(result["summary_df"], layout["tables"] / "全部场景汇总.csv")
        save_dataframe_chinese(result["sensitivity_results"]["vv_matrix"], layout["tables"] / "电压-电压灵敏度矩阵.csv")
        save_dataframe_chinese(result["sensitivity_results"]["qv_matrix"], layout["tables"] / "无功-电压灵敏度矩阵.csv")
        save_dataframe_chinese(result["sensitivity_results"]["flow_matrix"], layout["tables"] / "潮流灵敏度矩阵.csv")
        save_dataframe_chinese(result["impact_results"]["impact_summary"], layout["tables"] / "影响指标汇总.csv")
        self._log_info("已导出核心 CSV")

        export_all_results_to_excel_legacy(
            output_path=layout["tables"] / "IEEE33灵敏度分析汇总.xlsx",
            base_result=result["base_result"],
            pv_base_result=result["pv_base_result"],
            summary_df=result["summary_df"],
            sensitivity_results=result["sensitivity_results"],
            impact_results=result["impact_results"],
            group_tables=result["group_tables"],
            overall_tables=result["overall_tables"],
        )
        self._log_info("已导出兼容旧项目的 Excel 汇总")

        plot_sensitivity_heatmap(
            result["sensitivity_results"]["vv_matrix"],
            "电压-电压灵敏度热力图",
            layout["figures_heatmaps"] / "vv_sensitivity_heatmap.png",
        )
        plot_sensitivity_heatmap(
            result["sensitivity_results"]["qv_matrix"],
            "无功-电压灵敏度热力图",
            layout["figures_heatmaps"] / "qv_sensitivity_heatmap.png",
        )
        self._log_info("已导出基础热力图")

        report_bundle = export_full_report_bundle(layout["reports"], cfg, network_bundle, result)
        self._log_info(f"已导出报告包: {report_bundle}")

        package_paper_figures(layout["root"])
        self._log_info("已整理 paper_figures")

        return {
            "layout": {k: str(v) for k, v in layout.items()},
            "network_bundle": network_bundle,
            "result": result,
            "report_bundle": report_bundle,
        }
