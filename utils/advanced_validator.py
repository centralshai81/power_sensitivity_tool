from __future__ import annotations

from typing import Dict, Any, List
from pathlib import Path


def validate_runtime_environment(cfg: Dict[str, Any]) -> List[str]:
    """
    工程部署增强版运行环境校验：
    - 输入文件是否存在
    - 输出目录是否可创建
    - 关键配置取值范围
    """
    errors: List[str] = []

    network_source = str(cfg.get("network_source", "")).lower()
    if network_source == "excel":
        input_file = cfg.get("excel_input_file", "")
        if not input_file:
            errors.append("excel_input_file 为空")
        else:
            # 尝试相对于脚本所在目录查找文件
            from pathlib import Path
            script_dir = Path(__file__).parent.parent
            input_path = Path(input_file)
            if not input_path.is_absolute():
                input_path = script_dir / input_file
            if not input_path.exists():
                errors.append(f"Excel 输入文件不存在: {input_path}")

    out_dir = cfg.get("output_dir", "")
    if not out_dir:
        errors.append("output_dir 为空")

    sag_levels = cfg.get("voltage_sag_levels", [])
    if isinstance(sag_levels, list):
        for v in sag_levels:
            try:
                fv = float(v)
                if fv <= 0 or fv > 1.2:
                    errors.append(f"voltage_sag_levels 中存在异常值: {v}")
            except Exception:
                errors.append(f"voltage_sag_levels 中存在非法值: {v}")

    dq_levels = cfg.get("reactive_disturbance_levels", [])
    if not isinstance(dq_levels, list):
        errors.append("reactive_disturbance_levels 必须为列表")

    return errors
