
from __future__ import annotations

OLD_SHEET_ORDER = [
    "基准节点电压",
    "基准线路潮流",
    "基准系统损耗",
    "PV基准节点电压",
    "PV基准线路潮流",
    "PV基准系统损耗",
    "全部场景汇总",
    "电压-电压灵敏度矩阵",
    "无功-电压灵敏度矩阵",
    "潮流灵敏度矩阵",
    "影响指标汇总",
    "分组统计",
    "PQ_voltage_sag_节点排名",
    "PQ_reactive_variation_节点排名",
    "PV_voltage_sag_节点排名",
    "PV_reactive_variation_节点排名",
    "PQ_voltage_sag_线路排名",
    "PQ_reactive_variation_线路排名",
    "PV_voltage_sag_线路排名",
    "PV_reactive_variation_线路排名",
    "全局电压-电压节点排名",
    "全局无功-电压节点排名",
    "全局线路排名",
]

def reorder_sheets(writer):
    """
    保证 Excel 输出 sheet 顺序与旧项目完全一致
    """
    workbook = writer.book
    sheets = workbook._sheets
    name_to_sheet = {s.title: s for s in sheets}

    ordered = []
    for name in OLD_SHEET_ORDER:
        if name in name_to_sheet:
            ordered.append(name_to_sheet[name])

    for s in sheets:
        if s.title not in OLD_SHEET_ORDER:
            ordered.append(s)

    workbook._sheets = ordered
