"""Advance TODO 3–5：滚动残差区间与覆盖/宽度评价。

复用 Basic 的 ``ts9.interval.RollingResidualInterval``。学生需要完成：
  TODO 3（G4）：对每个目标小时，先用过去样本外残差算半径 q，构造 [pred-q, pred+q]；
                真值到达后再把本次残差加入窗口（先预测后更新，不能偷看）。
  TODO 4（G5）：在 80%/90% 名义水平上报告经验覆盖率与平均宽度，记录暖启动小时数。
  TODO 5（G5）：写清使用的分位数规则（README A 节第 3 点），不把实测覆盖称为理论保证。

运行：``python -m src.interval_eval``
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "src"))

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
import yaml  # noqa: E402

from ts9.ingest import load_and_split  # noqa: E402
from ts9.baselines import SeasonalNaiveForecaster  # noqa: E402
from ts9.interval import RollingResidualInterval  # noqa: E402
from ts9.evaluate import coverage_width  # noqa: E402


def main() -> None:
    cfg_path = os.path.join(ROOT, "configs", "default.yaml")
    with open(cfg_path) as f:
        cfg = yaml.safe_load(f)
    sample = os.path.join(ROOT, cfg["data"]["sample"])
    split = load_and_split(sample, cfg["data"]["value_col"],
                           cfg["split"]["train_frac"], cfg["split"]["dev_frac"])
    history = pd.concat([split.train, split.dev], ignore_index=True)

    # 用"上一周同小时"作为点预测基线来演示区间
    season_lag = cfg["season"]["lags"][1]  # 168

    alphas = cfg["interval"]["alphas"]
    window = cfg["interval"]["window"]
    ri = RollingResidualInterval(window=window, alphas=alphas)

    # TODO 3：暖启动 —— 用 dev 的"样本外"残差初始化窗口。
    # 关键：预测 dev 时只能用 train 作为历史，不能把 dev 本身放进历史（否则偷看未来）。
    dev_model = SeasonalNaiveForecaster(season_lag).fit(split.train)
    dev_preds = dev_model.forecast(split.dev)
    warm_residuals = [abs(t - p) for (_, t, p) in dev_preds if p is not None]
    ri.warmup(warm_residuals)
    print(f"暖启动小时数（dev 样本外残差）：{len(warm_residuals)}")

    # 测试集的预测模型：用 train+dev 作为历史（dev 已结束，不算未来）
    model = SeasonalNaiveForecaster(season_lag).fit(history)

    # TODO 3：在 test 上先预测后更新
    yt_all, yp_all = [], []
    lowers, uppers = {a: [] for a in alphas}, {a: [] for a in alphas}
    for (t, y_true, y_pred) in model.forecast(split.test):
        if y_pred is None:
            continue
        yt_all.append(y_true)
        yp_all.append(y_pred)
        for a in alphas:
            q = ri.radius(a)
            lowers[a].append(y_pred - q)
            uppers[a].append(y_pred + q)
        ri.update(abs(y_true - y_pred))  # TODO 3：真值到达后再更新

    # TODO 4：覆盖/宽度
    print("=== 区间评价（上一周同小时 + 滚动残差区间）===")
    for a in alphas:
        cw = coverage_width(yt_all, yp_all, lowers[a], uppers[a])
        nominal = f"{int((1-a)*100)}%"
        print(f"名义 {nominal:>4s}  实测覆盖={cw['coverage']:.3f}  "
              f"平均宽度={cw['mean_width']:.2f}")


if __name__ == "__main__":
    main()
