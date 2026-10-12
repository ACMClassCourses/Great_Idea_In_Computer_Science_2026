"""svmswarm: GA / hybrid-PSO driven RBF-SVM with feature selection.

Course project "基于元启发式算法优化的支持向量机解决有噪声的高维二分类问题".
Sub-packages:
  datasets.py    – Iris (binary pair) and MADELON loaders
  naive_svm.py   – teaching SMO SVM compared against sklearn on Iris
  pso.py         – continuous PSO and hybrid (continuous + binary) PSO
  ga.py          – real-coded GA and hybrid-chromosome GA
  objective.py   – leak-free stratified-K-fold CV objective + feature penalty
  baselines.py   – default SVM and random-search baselines
  evaluation.py  – final validation metrics on the sealed MADELON validation set
  viz.py         – convergence / box / feature-frequency figures
  config.py      – experiment configurations (quick / full)
  experiment.py  – multi-seed runner, result persistence, Markdown report
"""

__version__ = "0.1.0"
