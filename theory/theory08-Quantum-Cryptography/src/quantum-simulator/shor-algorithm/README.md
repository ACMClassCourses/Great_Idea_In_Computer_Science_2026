# Shor算法模块化实现

本项目实现了完整的Shor算法，采用模块化设计，将算法分解为7个独立步骤。Shor算法是一种量子算法，可以在多项式时间内解决大整数分解问题，这对现代密码学具有重要意义。

## 目录

- [概述](#概述)
- [算法原理](#算法原理)
- [项目结构](#项目结构)
- [安装要求](#安装要求)
- [使用方法](#使用方法)
- [API文档](#api文档)
- [示例](#示例)
- [注意事项](#注意事项)
- [常见问题](#常见问题)

## 概述

Shor算法由Peter Shor于1994年提出，是量子计算领域最重要的算法之一。它展示了量子计算机在解决特定问题上的指数级优势，特别是整数分解问题，这是许多现代密码系统（如RSA）安全性的基础。

本实现采用了模块化设计，将Shor算法第二阶段（量子周期查找）分解为7个独立步骤：

1. 量子态初始化 ([`shor_step1.py`](shor_step1.py))
2. 叠加态创建 ([`shor_step2.py`](shor_step2.py))
3. 量子模幂运算 ([`shor_step3.py`](shor_step3.py))
4. 测量第二寄存器 ([`shor_step4.py`](shor_step4.py))
5. 量子傅里叶变换 ([`shor_step5.py`](shor_step5.py))
6. 测量第一寄存器 ([`shor_step6.py`](shor_step6.py))
7. 经典后处理 ([`shor_step7.py`](shor_step7.py))

核心定义和类可以在 [`shor_definitions.py`](shor_definitions.py) 中找到。

## 算法原理

### 核心思想

Shor算法的核心思想是将整数分解问题转化为周期查找问题。给定一个合数N和一个与N互质的整数a，函数f(x) = a^x mod N是一个周期函数。如果我们能找到这个函数的周期r，并且满足某些条件，就可以用r来找出N的因子。

### 算法步骤

1. **选择基数**：随机选择一个与N互质的整数a
2. **量子计算**：使用量子计算机找出函数f(x) = a^x mod N的周期r
3. **经典处理**：如果r是偶数且a^(r/2) ≠ -1 mod N，则可以计算出N的因子

### 量子周期查找

量子周期查找是Shor算法的核心，它利用量子并行性和干涉效应来高效地找到周期：

1. 创建所有可能输入x的叠加态
2. 计算函数值f(x)并存储在第二寄存器
3. 测量第二寄存器，使第一寄存器坍缩为周期性叠加态
4. 应用量子傅里叶变换将周期信息转换到频率域
5. 测量第一寄存器，得到与周期相关的信息
6. 使用连分数算法从测量结果推断周期

## 项目结构

```
.
├── README.md                           # 本文档
├── shor_definitions.py                 # 基础定义（量子比特、量子寄存器、量子门）
├── shor_main.py                        # 主程序，整合所有步骤
├── shor_step1.py                       # 步骤1：量子态初始化
├── shor_step2.py                       # 步骤2：叠加态创建
├── shor_step3.py                       # 步骤3：量子模幂运算
├── shor_step4.py                       # 步骤4：测量第二寄存器
├── shor_step5.py                       # 步骤5：量子傅里叶变换
├── shor_step6.py                       # 步骤6：测量第一寄存器
└── shor_step7.py                       # 步骤7：经典后处理
```

## 安装要求

### 系统要求

- Python 3.6 或更高版本
- 支持的操作系统：Windows、macOS、Linux

### 依赖库

本实现仅使用Python标准库，无需安装额外依赖：

- `math`：数学运算
- `random`：随机数生成
- `typing`：类型提示

## 使用方法

### 基本使用

运行完整的Shor算法演示：

```bash
python3 shor_main.py
```

这将使用默认参数（N=15）运行完整的算法演示。

### 自定义参数

你可以修改代码中的参数来分解不同的合数：

```python
# 在 shor_main.py 文件末尾修改
if __name__ == "__main__":
    # 分解不同的合数
    N = 21  # 修改这里
    main()
```

## API文档

### 主要函数

#### `shor_algorithm(N, max_attempts=5)`

完整的Shor算法实现。

**参数：**
- `N` (int): 要分解的合数
- `max_attempts` (int): 最大尝试次数，默认为5

**返回值：**
- `Tuple[int, int] | None`: 如果成功，返回N的因子(p, q)；如果失败，返回None

**示例：**
```python
from shor_main import shor_algorithm

# 分解15
factors = shor_algorithm(15)
if factors:
    p, q = factors
    print(f"15 = {p} × {q}")
```

### 步骤函数

每个步骤都有对应的函数，详见各步骤文件：

1. [`initialize_quantum_state(m, n)`](shor_step1.py:11) - 初始化量子态
2. [`apply_hadamard_to_first_register(state, m, n)`](shor_step2.py:11) - 创建叠加态
3. [`apply_modular_exponentiation(state, a, N, m, n)`](shor_step3.py:11) - 量子模幂运算
4. [`measure_second_register(state, m, n)`](shor_step4.py:11) - 测量第二寄存器
5. [`quantum_fourier_transform(register, num_qubits)`](shor_step5.py:109) - 量子傅里叶变换
6. [`measure_first_register(state, m, n)`](shor_step6.py:11) - 测量第一寄存器
7. [`classical_post_processing(measurement_c, Q, N, a)`](shor_step7.py:11) - 经典后处理

### 辅助函数

#### `calculate_qubits_needed(N)`

计算分解N所需的量子比特数。

**参数：**
- `N` (int): 要分解的合数

**返回值：**
- `Dict[str, int]`: 包含各寄存器所需量子比特数的字典

## 示例

### 示例1：分解15

```python
from shor_main import main

# 使用默认参数分解15
main()
```

输出：
```
============================================================
Shor算法实现
============================================================

要分解的合数: N = 15

量子比特需求:
  第一寄存器位数 (m = 2n): 8
  第二寄存器位数 (n = ⌈log₂N⌉): 4
  总量子比特数: 19

=== 开始执行Shor算法分解 N = 15 ===

使用基数 a = 2
量子比特需求: m = 8, n = 4, Q = 256

--- 尝试 1/5 ---
步骤1：初始化量子态 |0⟩⊗m |0⟩⊗n
步骤2：创建叠加态 (1/√Q) ∑|x⟩|0⟩
步骤3：应用量子模幂运算 |x⟩|0⟩ → |x⟩|2^x mod 15⟩
步骤4：测量第二寄存器
  测量结果: y₀ = 4
步骤5：应用量子傅里叶变换
步骤6：测量第一寄存器
  测量结果: c = 128
步骤7：经典后处理
  ✓ 成功分解 15 = 3 × 5
=== 算法成功完成 ===

🎉 成功！15 = 3 × 5
验证: 3 × 5 = 15 ✓
```

### 示例2：分解自定义数值

```python
from shor_main import shor_algorithm

# 分解21
factors = shor_algorithm(21, max_attempts=5)
if factors:
    p, q = factors
    print(f"21 = {p} × {q}")
else:
    print("无法分解21")
```
