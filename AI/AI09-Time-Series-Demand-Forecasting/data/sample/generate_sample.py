"""生成离线小样本 ``bike_sample.csv``（无需下载真实 UCI 数据即可跑 Basic）。

合成规则（仅用于教学，非真实分布）：
- 日周期：小时需求呈双峰（通勤早高峰 ~8 点、晚高峰 ~18 点）。
- 周周期：工作日整体偏高、周末午后偏高。
- 噪声：乘性 + 少量随机缺失（供缺失处理演示，但默认写满网格）。
- cnt = casual + registered（与真实 UCI 字段一致，便于 Q3 演示）。

运行：``python data/sample/generate_sample.py`` -> 生成 bike_sample.csv。
"""

from __future__ import annotations

import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "bike_sample.csv")

START = "2023-01-01"
DAYS = 30  # 30 天 * 24 = 720 小时


def main(seed: int = 20240101) -> None:
    rng = np.random.default_rng(seed)
    idx = pd.date_range(START, periods=DAYS * 24, freq="h")
    hours = idx.hour.to_numpy()
    dows = idx.dayofweek.to_numpy()
    is_weekend = (dows >= 5).astype(float)

    # 双峰日周期（早 8、晚 18）
    daily = (
        40
        + 120 * np.exp(-((hours - 8) ** 2) / 8.0)
        + 140 * np.exp(-((hours - 18) ** 2) / 10.0)
        + 30 * np.cos((hours / 24.0) * 2 * np.pi)
    )
    # 周周期：工作日整体高，周末午后高
    weekly = 30 * (1 - is_weekend) + 40 * is_weekend * (
        0.5 + 0.5 * np.sin((hours / 24.0) * 2 * np.pi)
    )
    base = daily + weekly
    noise = rng.normal(0, 0.12 * base)
    registered = np.clip(base + noise, 0, None)
    casual = np.clip(0.35 * registered * rng.normal(1, 0.2, size=len(idx)), 0, None)
    # 三个整数严格满足 cnt = casual + registered（便于 Q3 数据完整性校验）
    registered_int = np.round(registered).astype(int)
    casual_int = np.round(casual).astype(int)
    cnt = registered_int + casual_int

    out = pd.DataFrame(
        {
            "dteday": idx.strftime("%Y-%m-%d"),
            "hr": hours,
            "casual": casual_int,
            "registered": registered_int,
            "cnt": cnt,
        }
    )
    out.to_csv(OUT, index=False)
    print(f"wrote {OUT}  rows={len(out)}")


if __name__ == "__main__":
    main()
