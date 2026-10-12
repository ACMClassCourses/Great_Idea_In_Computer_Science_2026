"""
Shor算法步骤2：叠加态创建

此文件实现了Shor算法的第二步：叠加态创建。
对第一寄存器应用Hadamard门，创建均匀叠加态：|ψ₁⟩ = (1/√Q) ∑_{x=0}^{Q-1} |x⟩ |0⟩
"""

import math
from shor_definitions import QuantumRegister, create_hadamard_gate
from shor_step1 import initialize_quantum_state, verify_initialization

def apply_hadamard_to_first_register(state: QuantumRegister, m: int, n: int) -> QuantumRegister:
    """
    对第一寄存器应用Hadamard门，创建均匀叠加态
    
    参数:
        state: 当前量子态
        m: 第一寄存器的量子比特数
        n: 第二寄存器的量子比特数
        
    返回:
        QuantumRegister: 应用Hadamard门后的量子态
    """
    # 输入验证
    if state.num_qubits != m + n:
        raise ValueError(f"量子寄存器大小不匹配，期望{m+n}，实际{state.num_qubits}")
    
    # 验证初始状态
    if not verify_initialization(state, m, n):
        raise ValueError("输入状态不是有效的|0⟩⊗m |0⟩⊗n状态")
    
    # 创建Hadamard门
    hadamard = create_hadamard_gate()
    
    # 对第一寄存器的每个量子比特应用Hadamard门
    current_register = state
    for i in range(m):
        current_register = hadamard.apply_to_register(current_register, [i])
    
    return current_register

def verify_superposition(state: QuantumRegister, m: int, n: int) -> bool:
    """
    验证叠加态是否正确创建
    
    参数:
        state: 量子寄存器状态
        m: 第一寄存器的量子比特数
        n: 第二寄存器的量子比特数
        
    返回:
        bool: 如果叠加态正确返回True，否则返回False
    """
    # 计算第一寄存器的状态数
    Q = 2**m
    
    # 检查归一化
    norm = math.sqrt(sum(abs(x)**2 for x in state.state))
    if not abs(norm - 1.0) < 1e-10:
        print(f"错误：量子态未归一化，范数为{norm}")
        return False
    
    # 检查非零元素的数量和值
    non_zero_indices = [i for i, x in enumerate(state.state) if abs(x) > 1e-10]
    expected_amplitude = 1 / math.sqrt(Q)
    
    # 应该有Q个非零元素（对应第一寄存器的所有可能状态）
    if len(non_zero_indices) != Q:
        print(f"错误：应有{Q}个非零元素，实际有{len(non_zero_indices)}个")
        return False
    
    # 检查所有非零元素的振幅是否正确
    for i in non_zero_indices:
        if not abs(abs(state.state[i]) - expected_amplitude) < 1e-10:
            print(f"错误：状态{i}的振幅不正确，应为{expected_amplitude}，实际为{abs(state.state[i])}")
            return False
    
    # 检查非零元素是否都在第二寄存器为|0⟩的位置
    for i in non_zero_indices:
        # 索引i应该满足 i % 2^n == 0（第二寄存器为|0⟩）
        if i % (2**n) != 0:
            print(f"错误：状态{i}的第二寄存器不为|0⟩")
            return False
    
    return True

def print_superposition_info(state: QuantumRegister, m: int, n: int) -> None:
    """
    打印叠加态信息
    
    参数:
        state: 量子态向量
        m: 第一寄存器的量子比特数
        n: 第二寄存器的量子比特数
    """
    Q = 2**m
    expected_amplitude = 1 / math.sqrt(Q)
    
    print(f"叠加态信息:")
    print(f"  第一寄存器状态数 (Q = 2^m): {Q}")
    print(f"  理论振幅 (1/√Q): {expected_amplitude:.6f}")
    
    # 显示前几个和最后几个非零元素
    non_zero_indices = [i for i, x in enumerate(state.state) if abs(x) > 1e-10]
    print(f"  非零元素数量: {len(non_zero_indices)}")
    
    if len(non_zero_indices) > 0:
        print(f"  前5个非零元素:")
        for i in range(min(5, len(non_zero_indices))):
            idx = non_zero_indices[i]
            first_reg = idx // (2**n)
            second_reg = idx % (2**n)
            print(f"    |{first_reg}⟩|{second_reg}⟩: {state.state[idx]}")
        
        if len(non_zero_indices) > 5:
            print(f"    ...")
            print(f"  最后5个非零元素:")
            for i in range(max(0, len(non_zero_indices) - 5), len(non_zero_indices)):
                idx = non_zero_indices[i]
                first_reg = idx // (2**n)
                second_reg = idx % (2**n)
                print(f"    |{first_reg}⟩|{second_reg}⟩: {state.state[idx]}")

def create_superposition_circuit(m: int, n: int) -> QuantumRegister:
    """
    创建叠加态的完整电路实现
    
    参数:
        m: 第一寄存器的量子比特数
        n: 第二寄存器的量子比特数
        
    返回:
        QuantumRegister: 创建的叠加态
    """
    # 步骤1：初始化量子态
    print(f"步骤1：初始化量子态 |0⟩⊗{m} |0⟩⊗{n}")
    initial_state = initialize_quantum_state(m, n)
    
    # 验证初始化
    if not verify_initialization(initial_state, m, n):
        raise RuntimeError("量子态初始化失败")
    
    # 步骤2：应用Hadamard门到第一寄存器
    print(f"步骤2：对第一寄存器应用Hadamard门")
    print(f"  使用Hadamard门酉矩阵: H = 1/√2 * [[1, 1], [1, -1]]")
    print(f"  H^(⊗{m}) |0⟩⊗{m} = (1/√{2**m}) ∑_{{x=0}}^{{2**{m}-1}} |x⟩")
    superposition_state = apply_hadamard_to_first_register(initial_state, m, n)
    
    # 验证叠加态
    if not verify_superposition(superposition_state, m, n):
        raise RuntimeError("叠加态创建失败")
    
    print(f"✓ 成功创建叠加态 (1/√{2**m}) ∑_{{x=0}}^{{2**{m}-1}} |x⟩ |0⟩")
    
    return superposition_state

if __name__ == "__main__":
    # 此文件不包含演示代码，演示代码请参考 shor_main.py
    pass