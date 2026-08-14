from __future__ import annotations

from pathlib import Path

import visualization  # noqa: F401

from services.project_service import ProjectService
from utils.logger import ProjectLogger
from utils.config_manager import load_project_config
from utils.pv_config_sync import sync_pv_config_from_excel


def main():
    script_dir = Path(__file__).parent
    sync_info = sync_pv_config_from_excel(
        script_dir,
        script_dir / "config/network_config_v7.json",
        script_dir / "config/analysis_config_v7.json",
    )
    if sync_info.get("synced"):
        print(f"[PV_SYNC] 已同步 PV 节点: {sync_info.get('pv_nodes')}")

    cfg = load_project_config(
        script_dir / "config/system_config_v7.json",
        script_dir / "config/network_config_v7.json",
        script_dir / "config/analysis_config_v7.json",
    )

    output_dir_name = cfg.get("output_dir", "results")
    output_dir = script_dir / output_dir_name
    logger = ProjectLogger(output_dir / "logs", run_name="main")
    logger.info("执行开始")

    try:
        service = ProjectService(logger=logger)
        service.run_project(cfg)

        logger.info("执行完成")
        print("=" * 72)
        print("[DONE] 执行完成。")
        print(f"结果目录: {output_dir.resolve()}")
        print("=" * 72)

    except Exception as e:
        logger.exception("执行失败", e)
        raise


if __name__ == "__main__":
    main()
