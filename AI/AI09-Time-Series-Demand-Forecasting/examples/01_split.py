"""时间切分与数据卡（Basic；对应 TODO 2 与提交验收中的"时间审计"）。

输出：
- 切分日期范围（train/dev/test），证明测试集严格晚于训练。
- 数据卡：总行数、时间跨度、缺失小时数、目标列统计。

运行：``python examples/01_split.py``
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))

import pandas as pd  # noqa: E402
import yaml  # noqa: E402

from ts9.ingest import load_series, find_missing_hours, time_split  # noqa: E402


def data_card(df: pd.DataFrame) -> None:
    ts = df["timestamp"]
    missing = find_missing_hours(ts, df["value"])
    print("=== 数据卡 ===")
    print(f"行数            : {len(df)}")
    print(f"时间跨度        : {ts.iloc[0]}  ~  {ts.iloc[-1]}")
    print(f"目标列统计      : mean={df['value'].mean():.2f}  "
          f"min={df['value'].min()}  max={df['value'].max()}")
    print(f"缺失小时数      : {len(missing)}")
    if missing:
        print(f"  缺失示例      : {missing[:5]}")


def main() -> None:
    cfg_path = os.path.join(ROOT, "configs", "default.yaml")
    with open(cfg_path) as f:
        cfg = yaml.safe_load(f)
    sample = os.path.join(ROOT, cfg["data"]["sample"])
    value_col = cfg["data"]["value_col"]

    df = load_series(sample, value_col=value_col)
    data_card(df)

    split = time_split(df, cfg["split"]["train_frac"], cfg["split"]["dev_frac"])
    print("\n=== 时间切分（禁随机）===")
    print(split.summary())

    ok = split.test["timestamp"].iloc[0] > split.train["timestamp"].iloc[-1]
    print("\n测试集晚于训练末端（无未来泄漏）:", ok)


if __name__ == "__main__":
    main()
