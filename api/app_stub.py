from __future__ import annotations

"""
这是一个面向未来 GUI / Web 前端 / API 服务的调用示例骨架。
当前不强依赖 FastAPI / Flask，仅提供最小可复用接口。

后续如果你要做：
- Streamlit
- PySide
- FastAPI
都可以直接复用这里的 ProjectService。
"""

from utils.logger import ProjectLogger
from services.project_service import ProjectService
from utils.config_manager import load_project_config


def run_project_from_configs(
    system_config: str = "config/system_config_v7.json",
    network_config: str = "config/network_config_v7.json",
    analysis_config: str = "config/analysis_config_v7.json",
):
    cfg = load_project_config(system_config, network_config, analysis_config)
    logger = ProjectLogger(cfg.get("output_dir", "results_v7"), run_name="api_stub")
    service = ProjectService(logger=logger)
    return service.run_project(cfg)
