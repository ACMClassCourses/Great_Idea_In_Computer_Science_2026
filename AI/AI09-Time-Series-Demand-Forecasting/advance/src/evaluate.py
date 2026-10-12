"""Advance TODO 6–7：场景分组评价与失败案例收集。

复用 ``ts9.evaluate.group_metrics`` 与 ``advance.src.utils.classify_scenario``。
学生需要完成：
  TODO 6（G5）：按工作日/周末、高峰/低谷（及可选天气、测试前七天）分组，
                每组报告 MAE/RMSE 与组大小；高峰定义须预先或只用训练数据确定。
  TODO 7（G7）：收集 ≥5 个失准片段，区分点预测偏差 / 需求突变 / 区间过窄，
                并据此写一份短报告与 presentation 要点。

运行：``python -m src.evaluate``
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
from ts9.evaluate import group_metrics  # noqa: E402
from .utils import classify_scenario  # noqa: E402


def main() -> None:
    cfg_path = os.path.join(ROOT, "configs", "default.yaml")
    with open(cfg_path) as f:
        cfg = yaml.safe_load(f)
    sample = os.path.join(ROOT, cfg["data"]["sample"])
    split = load_and_split(sample, cfg["data"]["value_col"],
                           cfg["split"]["train_frac"], cfg["split"]["dev_frac"])
    history = pd.concat([split.train, split.dev], ignore_index=True)

    model = SeasonalNaiveForecaster(cfg["season"]["lags"][1]).fit(history)
    fc = model.forecast(split.test)
    yt, yp = [], []
    groups = []
    for (t, y_true, y_pred) in fc:
        if y_pred is None:
            continue
        yt.append(y_true)
        yp.append(y_pred)
        sc = classify_scenario(t, y_true)
        groups.append(f"{sc['weekday_weekend']}/{sc['peak_offpeak']}")

    # TODO 6：分场景指标
    print("=== 分场景 MAE/RMSE（上一周同小时）===")
    gm = group_metrics(yt, yp, groups)
    for g, m in sorted(gm.items()):
        print(f"{g:18s} n={int(m['n']):4d}  MAE={m['mae']:7.3f}  RMSE={m['rmse']:7.3f}")

    # TODO 7：失败案例收集（示例：绝对误差最大的若干小时）
    errs = np.abs(np.array(yt) - np.array(yp))
    top = np.argsort(errs)[-5:][::-1]
    print("\n=== 失准片段 Top5（TODO 7 需分类：点偏差/突变/区间过窄）===")
    for i in top:
        print(f"  idx={i}  true={yt[i]:.0f}  pred={yp[i]:.0f}  "
              f"abs_err={errs[i]:.1f}  group={groups[i]}")


if __name__ == "__main__":
    main()
