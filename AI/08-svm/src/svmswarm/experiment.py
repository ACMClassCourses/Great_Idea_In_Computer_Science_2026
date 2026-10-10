"""Multi-seed experiment runner: persistence, summary tables, figures, report.

Each (method, seed) run is a budget-limited optimisation over MADELON:
  main methods  – GA, hybrid PSO, random search on the full space (mask + u, v)
  default       – sklearn-default SVM on all features (no search)
  ablation A1   – joint feature selection vs ALL features (same budget)
  ablation A2   – PSO with linearly decreasing inertia weight w
  ablation A3   – GA feature-penalty (lambda) sensitivity
  ablation A4   – GA screening-prior warm start vs uniform masks

After a candidate is found the model is refitted on the full training set and
evaluated once on the sealed validation set (README: validation never used
inside the search).
"""
from __future__ import annotations

import csv
import json
import statistics as st
import time
from pathlib import Path

import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from .baselines import RandomSearchContinuous, RandomSearchHybrid
from .config import ExperimentConfig
from .datasets import REPO_ROOT, load_madelon
from .evaluation import default_svm_evaluate, final_evaluate
from .ga import GA, HybridGA
from .objective import (CONT_BOUNDS, CVObjective, decode, make_cv_only_objective,
                        screening_prior)
from .pso import HybridPSO, PSO
from .viz import (convergence_by_method, convergence_plot, feature_count_bar,
                  feature_frequency_plot, score_boxplot)

LABELS = {"ga": "GA", "pso": "PSO", "random": "RandomSearch"}

_DATA: dict | None = None


def load_data() -> dict:
    global _DATA
    if _DATA is None:
        _DATA = load_madelon()
    return _DATA


def get_objective(data: dict, cfg: ExperimentConfig, penalty: float) -> CVObjective:
    """Create an independent objective for one optimisation run.

    ``CVObjective`` still caches duplicate candidates *within* a run.  Keeping
    that cache local prevents a later method, seed, or ablation from receiving
    free cache hits, so ``n_fits_run`` and wall-clock comparisons stay honest.
    """
    return CVObjective(data["X_train"], data["y_train"],
                       n_splits=cfg.n_splits, cv_seed=cfg.cv_seed,
                       penalty=penalty, cv_jobs=cfg.cv_jobs)


def _make_optimizer(method: str, cfg: ExperimentConfig, seed: int,
                    all_features: bool = False, pso_w_end: float | None = None):
    if all_features:
        if method == "ga":
            return GA(dim=2, bounds=CONT_BOUNDS, n_pop=cfg.n_pop,
                      tournament=cfg.ga_tournament, pc=cfg.ga_pc,
                      pm_cont=cfg.ga_pm_cont, mut_scale=cfg.ga_mut_scale,
                      elite=cfg.ga_elite, seed=seed)
        if method == "pso":
            return PSO(n_particles=cfg.n_particles, bounds=CONT_BOUNDS, w=cfg.pso_w,
                       c1=cfg.pso_c1, c2=cfg.pso_c2, w_end=pso_w_end,
                       v_max_frac=cfg.pso_v_max_frac, random_state=seed)
        return RandomSearchContinuous(random_state=seed)

    if method == "ga":
        return HybridGA(n_cont=2, n_bin=cfg.n_feat, bounds=CONT_BOUNDS,
                        n_pop=cfg.n_pop, tournament=cfg.ga_tournament, pc=cfg.ga_pc,
                        pm_cont=cfg.ga_pm_cont, mut_scale=cfg.ga_mut_scale,
                        pm_bin=1.0 / cfg.n_feat, elite=cfg.ga_elite, seed=seed)
    if method == "pso":
        return HybridPSO(n_particles=cfg.n_particles, n_cont=2, n_bin=cfg.n_feat,
                         bounds=CONT_BOUNDS, w=cfg.pso_w, c1=cfg.pso_c1,
                         c2=cfg.pso_c2, w_end=pso_w_end,
                         v_max_frac=cfg.pso_v_max_frac, v_bin_max=cfg.pso_v_bin_max,
                         random_state=seed)
    return RandomSearchHybrid(n_feat=cfg.n_feat, p_mask=cfg.rs_p_mask,
                              random_state=seed)


def run_search(method: str, cfg: ExperimentConfig, obj: CVObjective, seed: int,
               budget: int, all_features: bool = False,
               pso_w_end: float | None = None,
               label: str | None = None,
               use_prior: bool = True) -> tuple[dict, np.ndarray]:
    """One budget-limited search.  Returns (record dict, history in best-J)."""
    opt = _make_optimizer(method, cfg, seed, all_features=all_features,
                          pso_w_end=pso_w_end)
    # warm-start GA / PSO hybrid masks from the univariate screen prior
    if (not all_features and use_prior and cfg.use_screening_prior
            and hasattr(opt, "mask_prior") and opt.mask_prior is None):
        opt.mask_prior = screening_prior(obj.X, obj.y, top=cfg.prior_top,
                                         p_top=cfg.prior_p_top,
                                         p_rest=cfg.prior_p_rest)
    loss_obj = make_cv_only_objective(obj) if all_features else obj.loss
    fits_before = obj.n_fits

    t0 = time.time()
    res = opt.optimize(loss_obj, budget)
    wall = time.time() - t0

    best_x = np.asarray(res.best_x, dtype=float)
    if all_features:
        best_u, best_v = float(best_x[0]), float(best_x[1])
        sel = np.arange(obj.n_feat)
        best_full = np.concatenate([best_x, np.ones(obj.n_feat)])
        C, gamma = 10.0 ** best_u, 10.0 ** best_v
    else:
        C, gamma, sel = decode(best_x)
        best_u, best_v = float(np.log10(C)), float(np.log10(gamma))
        best_full = best_x

    history = np.asarray(res.history, dtype=float).copy()
    if history.size:
        history[:, 1] = -history[:, 1]          # convert to best-J (maximised)

    display = label or LABELS[method] + ("-noFS" if all_features else "")
    record = {
        "method": method,
        "label": display,
        "seed": int(seed),
        "budget": int(budget),
        "all_features": bool(all_features),
        "pso_w_end": pso_w_end,
        "best_j": float(-res.best_value),
        "best_loss": float(res.best_value),
        "n_evals_used": int(res.n_evals),
        "n_iter": int(res.n_iter),
        "n_fits_run": int(obj.n_fits - fits_before),
        "best_u": float(best_u), "best_v": float(best_v),
        "C": float(C), "gamma": float(gamma),
        "n_features": int(sel.size),
        "selected": [int(s) for s in sel],
        "cv_acc_raw": float(obj.raw_cv_accuracy(best_full)),
        "wall_seconds": float(wall),
    }
    return record, history


def _default_run(data: dict, cfg: ExperimentConfig) -> dict:
    obj = get_objective(data, cfg, cfg.penalty)
    pipe = make_pipeline(StandardScaler(), SVC())
    cv_mean = float(np.mean(cross_val_score(pipe, data["X_train"], data["y_train"],
                                            cv=obj.folds, scoring="accuracy",
                                            n_jobs=cfg.cv_jobs)))
    val = default_svm_evaluate(data["X_train"], data["y_train"],
                               data["X_valid"], data["y_valid"])
    return {"method": "default", "label": "Default", "seed": -1, "budget": 0,
            "n_evals_used": 0, "n_iter": 0, "n_fits_run": 0,
            "cv_acc_raw": cv_mean, "n_features": int(cfg.n_feat),
            "selected": [], "C": 1.0, "gamma": "scale",
            "best_j": float(cv_mean - cfg.penalty), "wall_seconds": 0.0,
            "pso_w_end": None, **val}


def _finalise(record: dict, data: dict, cfg: ExperimentConfig) -> dict:
    """Attach validation metrics: refit on full training set, evaluate once."""
    if isinstance(record["gamma"], str):          # default SVM record
        return record
    sel = record["selected"]
    mask = None
    if sel:
        m = np.zeros(cfg.n_feat)
        m[np.asarray(sel, dtype=int)] = 1.0
        mask = m
    val = final_evaluate(data["X_train"], data["y_train"],
                         data["X_valid"], data["y_valid"],
                         float(record["C"]), float(record["gamma"]), mask)
    record.update(val)
    return record


def _persist(record: dict, history: np.ndarray, root: Path) -> None:
    name = f"{record['label']}_s{record['seed']}"
    np.savetxt(root / "convergence" / f"{name}.csv", history, delimiter=",",
               header="n_evals,best_j", comments="")
    with open(root / "runs" / f"{name}.json", "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2, default=_json_default)


def _json_default(o):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(f"not JSON serialisable: {type(o)}")


def run_experiment(cfg: ExperimentConfig, out_root: Path | None = None,
                   with_report: bool = True) -> Path:
    """Run every experiment of ``cfg`` and persist JSON / CSV / figures / report."""
    data = load_data()
    root = Path(out_root) if out_root else REPO_ROOT / "outputs" / cfg.name
    for sub in ("runs", "convergence", "figures"):
        (root / sub).mkdir(parents=True, exist_ok=True)

    records: list[dict] = []
    histories: dict[str, list[np.ndarray]] = {}

    def execute(method: str, budget: int, seeds: list[int], all_features: bool,
                penalty: float, label: str | None = None,
                w_end: float | None = None, use_prior: bool = True) -> None:
        for seed in seeds:
            # One cache per (method, seed, condition): duplicate candidates in
            # this run are reused, but different experimental runs are isolated.
            obj = get_objective(data, cfg, penalty)
            rec, hist = run_search(method, cfg, obj, seed, budget,
                                   all_features=all_features, pso_w_end=w_end,
                                   label=label, use_prior=use_prior)
            rec = _finalise(rec, data, cfg)
            records.append(rec)
            histories.setdefault(rec["label"], []).append(hist)
            _persist(rec, hist, root)
            print(f"[{cfg.name}] {rec['label']:<16} seed {seed}: "
                  f"cv={rec['cv_acc_raw']:.4f}  val_acc={rec['accuracy']:.4f}  "
                  f"n_feat={rec['n_features']:>4}  wall={rec['wall_seconds']:6.1f}s",
                  flush=True)

    # 0) untuned default
    rec = _default_run(data, cfg)
    records.append(rec)
    print(f"[{cfg.name}] {'Default':<16} cv={rec['cv_acc_raw']:.4f}  "
          f"val_acc={rec['accuracy']:.4f}", flush=True)

    # 1) main methods: joint feature selection + hyper-parameters
    for method in ("random", "ga", "pso"):
        execute(method, cfg.budget, cfg.seeds, all_features=False,
                penalty=cfg.penalty)

    # 2) ablation A1: joint feature selection vs keep-all-features, same budget
    if cfg.run_noFS_ablation:
        # (a) feature-selection variants at the A1 budget (labels "<Method>-A1")
        for method in ("random", "ga", "pso"):
            execute(method, cfg.noFS_budget, cfg.noFS_seeds, all_features=False,
                    penalty=cfg.penalty, label=LABELS[method] + "-A1")
        # (b) keep-all-features variants at the same budget (labels "<Method>-noFS")
        for method in ("random", "ga", "pso"):
            execute(method, cfg.noFS_budget, cfg.noFS_seeds, all_features=True,
                    penalty=cfg.penalty, label=LABELS[method] + "-noFS")

    # 3) ablation A2: PSO with linearly decreasing inertia weight
    if cfg.run_wdecay_ablation:
        execute("pso", cfg.wdecay_budget, cfg.wdecay_seeds, all_features=False,
                penalty=cfg.penalty, label="PSO-wdecay", w_end=0.3)

    # 4) ablation A4: GA without the screening prior (uniform random masks)
    if cfg.run_uniform_control:
        execute("ga", cfg.budget, cfg.uniform_control_seeds, all_features=False,
                penalty=cfg.penalty, label="GA-uniform", use_prior=False)

    # 5) ablation A3: feature-penalty sensitivity with GA (full config only)
    if cfg.name == "full":
        for lam in (0.0, 0.01, 0.05):
            execute("ga", 60, [0, 1, 2], all_features=False, penalty=lam,
                    label=f"GA-lambda={lam:g}")

    _save_summary(records, root)
    _make_figures(records, histories, root, cfg)
    if with_report:
        _make_report(records, root, cfg)
    return root


def _save_summary(records: list[dict], root: Path) -> None:
    cols = ["label", "method", "seed", "budget", "n_evals_used", "n_iter",
            "n_fits_run", "best_j", "cv_acc_raw", "C", "gamma", "n_features",
            "accuracy", "precision", "recall", "f1", "wall_seconds",
            "pso_w_end"]
    with open(root / "summary.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for rec in records:
            w.writerow(rec)


def _make_figures(records: list[dict], histories: dict[str, list[np.ndarray]],
                  root: Path, cfg: ExperimentConfig) -> None:
    fig = root / "figures"
    main_hist = {k: v for k, v in histories.items() if k in ("GA", "PSO", "RandomSearch")}
    if main_hist:
        convergence_by_method(main_hist, fig / "convergence_main.png",
                              ylabel="best J (CV acc - lambda*||m||0/d)",
                              xmax=cfg.budget)
    mean_curves = {k: _mean_curve(v, cfg.budget)
                   for k, v in histories.items() if v}
    if mean_curves:
        convergence_plot(mean_curves, fig / "convergence_mean.png",
                         ylabel="best J (mean across seeds)",
                         title="Mean convergence across seeds")
    # validation accuracy per method (all records of a label)
    box: dict[str, list[float]] = {}
    for rec in records:
        if rec["label"] in ("Default", "GA", "PSO", "RandomSearch"):
            box.setdefault(rec["label"], []).append(float(rec["accuracy"]))
    if box:
        score_boxplot(box, fig / "validation_box.png",
                      ylabel="validation accuracy",
                      title="Validation accuracy across random seeds")
    # feature compression
    feat: dict[str, list[float]] = {}
    for rec in records:
        if rec["label"] in ("GA", "PSO", "RandomSearch") and rec["seed"] >= 0:
            feat.setdefault(rec["label"], []).append(float(rec["n_features"]))
    if feat:
        feature_count_bar([(k, float(np.mean(v))) for k, v in feat.items()],
                          fig / "features_bar.png")
    sel_sets = [np.asarray(r["selected"], dtype=int) for r in records
                if r["label"] in ("GA", "PSO") and r["selected"]]
    if sel_sets:
        feature_frequency_plot(sel_sets, cfg.n_feat,
                               fig / "feature_frequency.png",
                               title="MADELON feature selection frequency (GA + PSO runs)")


def _mean_curve(curves: list[np.ndarray], budget: int) -> np.ndarray:
    """Average best-so-far curves on the common evaluation grid 1..budget."""
    evals = np.arange(1, budget + 1)
    mats = []
    for c in curves:
        if c.shape[0] == 0:
            continue
        mats.append(np.interp(evals, c[:, 0], c[:, 1],
                              left=c[0, 1], right=c[-1, 1]))
    if not mats:
        return np.zeros((0, 2))
    return np.column_stack([evals, np.mean(mats, axis=0)])


# ------------------------------------------------------------------ report --
def _fmt_stats(values: list[float]) -> str:
    vals = [float(v) for v in values]
    if not vals:
        return "-"
    m = st.mean(vals)
    s = st.pstdev(vals) if len(vals) > 1 else 0.0
    return f"{m:.4f} ± {s:.4f}"


def _grp(records: list[dict], label: str) -> list[dict]:
    return [r for r in records if r["label"] == label]


def _make_report(records: list[dict], root: Path, cfg: ExperimentConfig) -> None:
    lines: list[str] = []
    add = lines.append

    add(f"# MADELON 实验结果报告（{cfg.name} 配置）\n")
    add(f"- 训练集 2000×500，验证集 600×500（官方划分）；Test 集无公开标签，不使用。")
    add(f"- 内部交叉验证：分层 K={cfg.n_splits} 折（random_state={cfg.cv_seed}），"
        f"StandardScaler 在每一折管道内拟合（无泄漏）。")
    add(f"- 主实验候选评价预算 B={cfg.budget}，随机种子 {cfg.seeds}；"
        f"消融实验预算见各节。")
    add(f"- 目标 J = S_CV − λ·‖m‖₀/d（λ={cfg.penalty:g}），"
        f"u=log₁₀C∈[−3,3]，v=log₁₀γ∈[−4,1]，C=10^u，γ=10^v。")
    add("")

    def stat(records_, key):
        return _fmt_stats([r[key] for r in records_ if key in r])

    add("## 1. 主实验（联合特征选择 + 超参数优化）\n")
    add("| 方法 | Best CV 准确率 | Val 准确率 | Val F1 | 特征数 | 单次耗时(s) | 预算使用 |")
    add("|---|---|---|---|---|---|---|")
    for label in ("Default", "RandomSearch", "GA", "PSO"):
        rs = _grp(records, label)
        if not rs:
            continue
        if label == "Default":
            nf, time_s, ev = "500 (all)", "-", "-"
        else:
            nf = stat(rs, "n_features")
            time_s = f"{st.mean([r['wall_seconds'] for r in rs]):.1f}"
            ev = f"{st.mean([r['n_evals_used'] for r in rs]):.0f}/{cfg.budget}"
        add(f"| {label} | {stat(rs, 'cv_acc_raw')} | {stat(rs, 'accuracy')} "
            f"| {stat(rs, 'f1')} | {nf} | {time_s} | {ev} |")
    add("")

    add("## 2. 收敛分析\n")
    add("`figures/convergence_main.png` 给出各方法每次种子运行的 best-J 曲线，"
        "`figures/convergence_mean.png` 给出跨种子均值曲线。"
        "GA（精英保留）与 PSO（全局最优记录）曲线单调不降；横轴为候选评价次数，"
        "所有方法共享同一预算。\n")
    add(f"**初始化披露**：GA/PSO 的特征掩码以一次性单变量筛选（仅在 Training 集上"
        f"计算一次，top-{cfg.prior_top} 特征高激活先验）热启动；随机搜索保持"
        f"无引导均匀采样。消融 A4（GA-uniform）在相同预算与种子下去掉该先验，"
        f"用于分离“算法本身”与“先验帮助”的贡献。\n")

    if cfg.run_noFS_ablation:
        add("## 3. 消融 A1：联合特征选择 vs 固定全部特征（预算对齐）\n")
        add(f"（特征选择与 noFS 两组均使用 B={cfg.noFS_budget}，种子 "
            f"{cfg.noFS_seeds}，K={cfg.n_splits}；-A1 = 联合选择，-noFS = 全特征）\n")
        add("| 方法 | Val 准确率 | Val F1 | 特征数 |")
        add("|---|---|---|---|")
        for base in ("RandomSearch", "GA", "PSO"):
            for variant in ("-A1", "-noFS"):
                label = base + variant
                rs = _grp(records, label)
                if not rs:
                    continue
                add(f"| {label} | {stat(rs, 'accuracy')} | {stat(rs, 'f1')} "
                    f"| {stat(rs, 'n_features')} |")
        add("")

    if cfg.run_wdecay_ablation:
        add("## 4. 消融 A2：PSO 惯性权重线性衰减（w: 0.7 → 0.3）\n")
        add(f"（两组均使用 B={cfg.wdecay_budget}，仅在相同种子 "
            f"{cfg.wdecay_seeds} 上比较）\n")
        add("| 配置 | Val 准确率 | Val F1 | 特征数 |")
        add("|---|---|---|---|")
        seeds = set(cfg.wdecay_seeds)
        pso_main = [r for r in _grp(records, "PSO")
                    if r["pso_w_end"] is None and r["seed"] in seeds]
        pso_dec = _grp(records, "PSO-wdecay")
        if pso_main:
            add(f"| PSO (固定 w) | {stat(pso_main, 'accuracy')} "
                f"| {stat(pso_main, 'f1')} | {stat(pso_main, 'n_features')} |")
        if pso_dec:
            add(f"| PSO-wdecay | {stat(pso_dec, 'accuracy')} "
                f"| {stat(pso_dec, 'f1')} | {stat(pso_dec, 'n_features')} |")
        add("")

    if cfg.run_uniform_control:
        add("## 5. 消融 A4：GA 是否使用筛选先验（GA vs GA-uniform）\n")
        add(f"（两者均使用 B={cfg.budget}，相同种子 {cfg.uniform_control_seeds}；"
            f"GA-uniform 以均匀随机掩码初始化）\n")
        add("| 配置 | Val 准确率 | Val F1 | 特征数 |")
        add("|---|---|---|---|")
        seeds = set(cfg.uniform_control_seeds)
        ga_main = [r for r in _grp(records, "GA") if r["seed"] in seeds]
        ga_uniform = _grp(records, "GA-uniform")
        if ga_main:
            add(f"| GA (先验) | {stat(ga_main, 'accuracy')} "
                f"| {stat(ga_main, 'f1')} | {stat(ga_main, 'n_features')} |")
        if ga_uniform:
            add(f"| GA-uniform | {stat(ga_uniform, 'accuracy')} "
                f"| {stat(ga_uniform, 'f1')} | {stat(ga_uniform, 'n_features')} |")
        add("")

    lam_recs = [r for r in records if r["label"].startswith("GA-lambda")]
    if lam_recs:
        add("## 6. 消融 A3：特征惩罚系数 λ（GA，B=60，种子 [0,1,2]）\n")
        add("| λ | Val 准确率 | Val F1 | 特征数 |")
        add("|---|---|---|---|")
        for lam in (0.0, 0.01, 0.05):
            rs = [r for r in lam_recs if r["label"] == f"GA-lambda={lam:g}"]
            if not rs:
                continue
            add(f"| {lam:.2f} | {stat(rs, 'accuracy')} | {stat(rs, 'f1')} "
                f"| {stat(rs, 'n_features')} |")
        add("")

    add("## 7. 运行时间（墙钟，本机）\n")
    seen: list[str] = []
    for rec in records:
        if rec["label"] not in seen and rec["seed"] >= 0:
            seen.append(rec["label"])
    for label in seen:
        rs = _grp(records, label)
        add(f"- {label}: 单次 {st.mean([r['wall_seconds'] for r in rs]):.1f} s，"
            f"{len(rs)} 次种子，累计 {sum(r['wall_seconds'] for r in rs):.0f} s。")
    add("")
    add("## 8. 说明\n")
    add("- 本文件由实验脚本自动生成，仅汇总测量数据；结论解读见项目报告正文。\n")

    (root / "report.md").write_text("\n".join(lines), encoding="utf-8")
