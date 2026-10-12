"""三基线端到端演示（Basic TODO 6）。

串联：时间切分 -> 三基线 -> 指标 -> 画一周预测曲线。

输出：控制台打印各基线在测试集的 MAE/RMSE/WAPE 与样本数；
      ``outputs/forecast_week.png`` 保存一周（168 小时）的真值 vs 预测曲线。

运行：``python examples/02_baseline_demo.py``
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "src"))

import pandas as pd  # noqa: E402
import yaml  # noqa: E402

from ts9.ingest import load_and_split  # noqa: E402
from ts9.baselines import run_all_baselines  # noqa: E402
from ts9.metrics import mae, rmse, wape, evaluate  # noqa: E402


def main() -> None:
    cfg_path = os.path.join(ROOT, "configs", "default.yaml")
    with open(cfg_path) as f:
        cfg = yaml.safe_load(f)
    sample = os.path.join(ROOT, cfg["data"]["sample"])

    split = load_and_split(
        sample, cfg["data"]["value_col"], cfg["split"]["train_frac"], cfg["split"]["dev_frac"]
    )
    history = pd.concat([split.train, split.dev], ignore_index=True)

    results = run_all_baselines(
        history, split.test, cfg["season"]["lags"], cfg["rolling"]["window"]
    )

    print("=== 测试集指标 ===")
    best_name, best_mae = None, float("inf")
    rows = []
    for name, fc in results.items():
        yt = [t for (_, t, p) in fc if p is not None]
        yp = [p for (_, t, p) in fc if p is not None]
        e = evaluate(yt, yp)
        rows.append((name, e))
        print(f"{name:12s} n={e['n']:4d}  MAE={e['mae']:7.3f}  "
              f"RMSE={e['rmse']:7.3f}  WAPE={e['wape']}")
        if e["mae"] < best_mae:
            best_mae, best_name = e["mae"], name
    print(f"\n测试集最强基线（按 MAE）：{best_name}")

    # 画一周曲线：真值 vs 最强基线 vs 日同小时
    plot_week(split.test, results, best_name)

    print(f"\n切分范围：\n{split.summary()}")


def plot_week(test_df, results, best_name) -> None:
    out_dir = os.path.join(ROOT, "outputs")
    os.makedirs(out_dir, exist_ok=True)
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:  # 没有 matplotlib 时跳过绘图
        print(f"[skip] 未安装 matplotlib，跳过绘图：{exc}")
        return

    week = min(168, len(test_df))
    t = test_df["timestamp"].iloc[:week]
    y_true = test_df["value"].iloc[:week].to_numpy(dtype=float)

    plt.figure(figsize=(11, 4))
    plt.plot(t, y_true, label="true", lw=2, color="black")
    for name in (best_name, "seasonal_24"):
        if name in results:
            yp = [p if p is not None else float("nan") for (_, _, p) in results[name][:week]]
            plt.plot(t, yp, label=name, lw=1.2, alpha=0.85)
    plt.title("One-week forecast (test): true vs baselines")
    plt.xlabel("timestamp")
    plt.ylabel("cnt")
    plt.legend()
    plt.tight_layout()
    out_path = os.path.join(out_dir, "forecast_week.png")
    plt.savefig(out_path, dpi=120)
    plt.close()
    print(f"[OK] 一周曲线已保存：{out_path}")


if __name__ == "__main__":
    main()
