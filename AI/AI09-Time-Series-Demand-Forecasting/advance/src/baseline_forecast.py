"""Advance TODO 1–2：三基线 + 一个特征模型，并用滚动起点评价。

复用 Basic 的 ``ts9.baselines`` 与 ``ts9.features``。学生需要完成：
  TODO 1（G3）：选一个模型（岭回归 / 随机森林 / HGB 之一），在 train 上拟合，
                特征用 features.build_features 的滞后 + 日历特征。
  TODO 2（G2/G3）：用"滚动起点、只向前"的协议评价，输出点预测与同批小时的可比指标；
                  保证模型与基线用完全一致的信息边界。

运行：``python -m src.baseline_forecast``
"""

from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "src"))

import pandas as pd  # noqa: E402
import yaml  # noqa: E402

from ts9.ingest import load_and_split  # noqa: E402
from ts9.baselines import run_all_baselines, NaiveForecaster, SeasonalNaiveForecaster, RollingMeanForecaster  # noqa: E402
from ts9.features import build_features, feature_matrix  # noqa: E402
from ts9.metrics import evaluate  # noqa: E402


def fit_feature_model(train_df, lags):  # TODO 1（G3）
    """训练一个特征模型（示例：岭回归）。替换为你选的模型即可。

    TODO：在 train 上拟合；不要在 dev/test 上拟合（保持时间协议）。
          也可在 dev 上用滚动起点选少量超参数，冻结后再用于测试。
    """
    from sklearn.linear_model import Ridge

    feats = build_features(train_df, lags)
    X, y = feature_matrix(feats, lags)
    model = Ridge(alpha=1.0)
    model.fit(X, y)
    return model


def forecast_feature_model(model, history, test_df, lags):  # TODO 1
    """用特征模型对 test 逐个目标小时做点预测（只使用过去特征）。

    TODO：为每个目标小时 t 构造 t 之前的滞后/日历特征；缺失滞后回退到历史均值。
          本示例用最近可用的全局滞后近似，学生应改为严格的滚动构造。
    """
    feats = build_features(history, lags)
    last = feats.iloc[-1]
    X_row = [last.get(f"lag_{l}", last["value"]) for l in lags] + \
            [test_df.iloc[0]["timestamp"].hour,
             test_df.iloc[0]["timestamp"].dayofweek,
             int(test_df.iloc[0]["timestamp"].dayofweek >= 5)]
    preds = [float(model.predict([X_row])[0]) for _ in range(len(test_df))]
    return preds


def main() -> None:
    cfg_path = os.path.join(ROOT, "configs", "default.yaml")
    with open(cfg_path) as f:
        cfg = yaml.safe_load(f)
    sample = os.path.join(ROOT, cfg["data"]["sample"])
    split = load_and_split(sample, cfg["data"]["value_col"],
                           cfg["split"]["train_frac"], cfg["split"]["dev_frac"])
    history = pd.concat([split.train, split.dev], ignore_index=True)

    # 三基线
    baselines = run_all_baselines(history, split.test,
                                  cfg["season"]["lags"], cfg["rolling"]["window"])
    print("=== 三基线（测试集）===")
    for name, fc in baselines.items():
        yt = [t for (_, t, p) in fc if p is not None]
        yp = [p for (_, t, p) in fc if p is not None]
        print(f"{name:12s}", evaluate(yt, yp))

    # 特征模型
    lags = cfg["features"]["lags"]
    model = fit_feature_model(split.train, lags)  # TODO 1
    preds = forecast_feature_model(model, history, split.test, lags)  # TODO 1
    yt = split.test["value"].to_numpy(dtype=float)
    # 简单对齐：仅演示指标，学生应做严格滚动构造后再比
    print("=== 特征模型（示例对齐，TODO 2 需严格化）===")
    print("feature_model", evaluate(yt, preds))


if __name__ == "__main__":
    main()
