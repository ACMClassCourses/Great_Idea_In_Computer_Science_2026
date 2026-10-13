"""
Shor算法主文件

此文件整合了Shor算法的各个模块，提供了完整的算法实现。
包含所有7个步骤的核心实现。
"""

import math
import random
from typing import Dict, Tuple, Optional
from shor_step1 import initialize_quantum_state
from shor_step2 import apply_hadamard_to_first_register
from shor_step3 import apply_modular_exponentiation
from shor_step4 import measure_second_register
from shor_step5 import quantum_fourier_transform
from shor_step6 import measure_first_register
from shor_step7 import classical_post_processing

def calculate_qubits_needed(N: int) -> Dict[str, int]:
    """
    计算分解N所需的量子比特数
    
    参数:
        N: 要分解的合数
        
    返回:
        包含各寄存器所需量子比特数的字典
    """
    n = math.ceil(math.log2(N))  # 表示N所需的比特数
    m = 2 * n                    # 第一寄存器比特数
    
    # 总量子比特数
    total_qubits = m + n + 3     # 包括辅助比特
    
    return {
        "n": n,                  # 第二寄存器比特数
        "m": m,                  # 第一寄存器比特数
        "total": total_qubits    # 总量子比特数
    }

def shor_algorithm(N: int, max_attempts: int = 5) -> Optional[Tuple[int, int]]:
    """
    完整的Shor算法实现
    
    参数:
        N: 要分解的合数
        max_attempts: 最大尝试次数
        
    返回:
        (p, q) N的因子，如果无法分解则返回None
    """
    print(f"=== 开始执行Shor算法分解 N = {N} ===")
    
    # 检查N是否为合数
    if N <= 1 or N % 2 == 0:
        if N == 2:
            return (1, 2)
        elif N % 2 == 0:
            return (2, N // 2)
    
    # 尝试不同的基数
    for a in range(2, min(N, 20)):  # 限制基数范围以避免过长的运行时间
        if math.gcd(a, N) != 1:
            # gcd_val = math.gcd(a, N)
            # if 1 < gcd_val < N:
            #     return (gcd_val, N // gcd_val)
            continue
        
        print(f"\n使用基数 a = {a}")
        
        # 计算所需量子比特数
        qubit_info = calculate_qubits_needed(N)
        m = qubit_info["m"]
        n = qubit_info["n"]
        Q = 2**m
        
        print(f"量子比特需求: m = {m}, n = {n}, Q = {Q}")
        
        # 尝试多次运行量子部分
        for attempt in range(1, max_attempts + 1):
            print(f"\n--- 尝试 {attempt}/{max_attempts} ---")
            
            # 步骤1：量子态初始化
            print("步骤1：初始化量子态 |0⟩⊗m |0⟩⊗n")
            initial_state = initialize_quantum_state(m, n)
            
            # 步骤2：叠加态创建
            print("步骤2：创建叠加态 (1/√Q) ∑|x⟩|0⟩")
            superposition_state = apply_hadamard_to_first_register(initial_state, m, n)
            
            # 步骤3：量子模幂运算
            print(f"步骤3：应用量子模幂运算 |x⟩|0⟩ → |x⟩|{a}^x mod {N}⟩")
            modular_exponentiation_state = apply_modular_exponentiation(superposition_state, a, N, m, n)
            
            # 步骤4：测量第二寄存器
            print("步骤4：测量第二寄存器")
            collapsed_state, measurement_result = measure_second_register(modular_exponentiation_state, m, n)
            print(f"  测量结果: y₀ = {measurement_result}")
            
            # 步骤5：量子傅里叶变换
            print("步骤5：应用量子傅里叶变换")
            qft_state = quantum_fourier_transform(collapsed_state, m)
            
            # 步骤6：测量第一寄存器
            print("步骤6：测量第一寄存器")
            measurement_c, final_state = measure_first_register(qft_state, m, n)
            print(f"  测量结果: c = {measurement_c}")
            
            # 步骤7：经典后处理
            print("步骤7：经典后处理")
            factors = classical_post_processing(measurement_c, Q, N, a)
            
            if factors:
                p, q = factors
                print(f"  ✓ 成功分解 {N} = {p} × {q}")
                print(f"=== 算法成功完成 ===")
                return factors
            else:
                print(f"  ✗ 尝试 {attempt} 未能分解 {N}")
        
        print(f"基数 a = {a} 在 {max_attempts} 次尝试后未能分解 {N}")
    
    print(f"=== 算法失败：无法分解 {N} ===")
    return None

def main():
    """
    主函数，运行Shor算法
    """
    # 设置随机种子以获得可重复的结果
    random.seed(42)
    
    print("=" * 60)
    print("Shor算法实现")
    print("=" * 60)
    
    # 选择要分解的数
    N = 15
    print(f"\n要分解的合数: N = {N}")
    
    # 计算所需量子比特数
    qubit_info = calculate_qubits_needed(N)
    print(f"\n量子比特需求:")
    print(f"  第一寄存器位数 (m = 2n): {qubit_info['m']}")
    print(f"  第二寄存器位数 (n = ⌈log₂N⌉): {qubit_info['n']}")
    print(f"  总量子比特数: {qubit_info['total']}")
    
    # 执行算法
    factors = shor_algorithm(N)
    
    if factors:
        p, q = factors
        print(f"\n🎉 成功！{N} = {p} × {q}")
        print(f"验证: {p} × {q} = {p * q} {'✓' if p * q == N else '✗'}")
    else:
        print(f"\n❌ 失败：无法分解 {N}")
        print("在实际应用中，可能需要更多尝试或不同的基数")
    
    print("\n" + "=" * 60)
    print("算法执行完成")
    print("=" * 60)

if __name__ == "__main__":
    main()