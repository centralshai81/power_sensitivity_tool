from __future__ import annotations

import matplotlib as mpl

def setup_chinese_font():
    mpl.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'STHeiti', 'WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'sans-serif']
    mpl.rcParams['axes.unicode_minus'] = False

setup_chinese_font()
