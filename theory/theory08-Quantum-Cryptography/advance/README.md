# 量子密码 · Advance

先完成 [Basic](../basic/README.md)。本阶段的具体目标和验收以 [完整任务书](../README.md) 为主。

## 项目结构与材料定位

- [quantum_crypto/basic_circuits.py](quantum_crypto/basic_circuits.py)：Basic 电路基线。
- [quantum_crypto/grover_experiment.py](quantum_crypto/grover_experiment.py)：Grover 小规模实验。
- [quantum_crypto/order_demo.py](quantum_crypto/order_demo.py)：N=15 阶查找演示。
- [tests/test_experiments.py](tests/test_experiments.py)：可复现实验检查。
- [../docs/](../docs/) 与 [../src/](../src/)：知识清单、报告模板及旧 QKD/模拟器材料，作为阅读参考。

## 建议阅读与使用顺序

1. 先读根目录 README 的 Advance 要求及 docs/ 中的知识清单和实验指南。
2. 从 basic_circuits.py 复核相位干涉，再读 grover_experiment.py 的 oracle、扩散和迭代次数。
3. 运行 order_demo.py 核对 N=15、a=2 的经典阶查找演示；不要把它称作完整 Shor 电路。
4. 跑测试并保存种子、shot 数、曲线、理论比较与密码方案分析。

## 本地起步

从项目根目录运行，量子密码示例先进入 advance 目录：

    cd advance
    python -m unittest discover -s tests -v
    python -m quantum_crypto.basic_circuits --shots 1000 --seed 20260929
    python -m quantum_crypto.grover_experiment --qubits 2 3 4 --target 0 --shots 2000 --seed 20260929
    python -m quantum_crypto.order_demo --modulus 15 --base 2



## 原有实验说明

这些模块刻意保持小规模、无外部依赖，适合学习与检查。所有状态向量都显式保存在内存中，默认实验最多四个量子比特。

```sh
python -m unittest discover -s tests -v
python -m quantum_crypto.basic_circuits --shots 1000 --seed 20260929
python -m quantum_crypto.grover_experiment --qubits 2 3 4 --target 0 --shots 2000 --seed 20260929
python -m quantum_crypto.order_demo --modulus 15 --base 2
```

可为 Grover 指定多个目标，例如 `--target 1 6`。报告必须记录目标数、随机种子、shot 数和迭代次数；多目标情形的理论成功概率使用 \(\theta=\arcsin\sqrt{M/N}\)。
