"""组件自检（Basic TODO 7）。

检查三项：
1) 时间切分无未来泄漏（test 全部晚于 history 末端）。
2) 三基线可运行且产出有限预测。
3) 指标正确：用 README Q5 手算样例核对 MAE/RMSE/WAPE。

运行：``python examples/00_self_check.py``
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))

import numpy as np  # noqa: E402

from ts9.ingest import load_and_split  # noqa: E402
from ts9.baselines import run_all_baselines  # noqa: E402
from ts9.metrics import mae, rmse, wape  # noqa: E402


def check_metrics_q5() -> None:
    y_true = [10, 20, 0, 30]
    y_pred = [12, 18, 5, 25]
    got_mae = mae(y_true, y_pred)
    got_rmse = rmse(y_true, y_pred)
    got_wape = wape(y_true, y_pred)
    assert abs(got_mae - 3.5) < 1e-9, f"MAE 应为 3.5，得到 {got_mae}"
    assert abs(got_rmse - 3.807886) < 1e-4, f"RMSE 应为 ~3.8079，得到 {got_rmse}"
    assert abs(got_wape - 0.233333) < 1e-4, f"WAPE 应为 ~0.2333，得到 {got_wape}"
    # 零分母：全 0 真值 -> WAPE 应为 None
    assert wape([0, 0, 0], [1, 2, 3]) is None, "全 0 真值 WAPE 应为 None"
    print("[OK] Q5 指标手算核对通过（MAE=3.5, RMSE≈3.8079, WAPE≈23.33%）")


def check_split_and_baselines() -> None:
    cfg_path = os.path.join(ROOT, "configs", "default.yaml")
    import yaml

    with open(cfg_path) as f:
        cfg = yaml.safe_load(f)

    sample = os.path.join(ROOT, cfg["data"]["sample"])
    split = load_and_split(
        sample, cfg["data"]["value_col"], cfg["split"]["train_frac"], cfg["split"]["dev_frac"]
    )
    history = split.train  # 仅用 train 作为历史已足够晚于 test（train+dev 也行）
    full_hist = __import__("pandas").concat([split.train, split.dev], ignore_index=True)

    # 泄漏检查：test 最小时刻必须晚于 history 末端
    assert split.test["timestamp"].iloc[0] > full_hist["timestamp"].iloc[-1], \
        "时间切分存在未来泄漏！"
    print("[OK] 时间切分无泄漏")
    print(split.summary())

    results = run_all_baselines(
        full_hist, split.test, cfg["season"]["lags"], cfg["rolling"]["window"]
    )
    for name, fc in results.items():
        preds = [p for (_, _, p) in fc if p is not None]
        assert len(preds) > 0, f"{name} 没有任何可评价预测"
        assert np.all(np.isfinite(preds)), f"{name} 产出非有限预测"
        # 计算可评价部分的指标
        yt = [t for (_, t, p) in fc if p is not None]
        yp = [p for (_, t, p) in fc if p is not None]
        m = mae(yt, yp)
        assert np.isfinite(m), f"{name} MAE 非有限"
        print(f"[OK] {name:12s} 可评价样本={len(yt):4d}  MAE={m:7.3f}")
    print("[OK] 三基线可运行且产出有限预测")


def main() -> None:
    check_metrics_q5()
    check_split_and_baselines()
    print("\n全部自检通过。")


if __name__ == "__main__":
    main()
