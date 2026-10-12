"""
Shor算法步骤1：量子态初始化

此文件实现了Shor算法的第一步：量子态初始化。
初始时，所有量子比特都处于|0⟩状态：|ψ₀⟩ = |0⟩⊗m |0⟩⊗n
"""

import math
from shor_definitions import QuantumRegister

def initialize_quantum_state(m: int, n: int) -> QuantumRegister:
    """
    初始化量子态为|0⟩⊗m |0⟩⊗n
    
    参数:
        m: 第一寄存器的量子比特数
        n: 第二寄存器的量子比特数
        
    返回:
        QuantumRegister: 初始化的量子寄存器
    """
    # 输入验证
    if not isinstance(m, int) or m <= 0:
        raise ValueError(f"第一寄存器量子比特数m必须是正整数，得到: {m}")
    
    if not isinstance(n, int) or n <= 0:
        raise ValueError(f"第二寄存器量子比特数n必须是正整数，得到: {n}")
    
    # 创建总量子寄存器
    total_qubits = m + n
    quantum_register = QuantumRegister(total_qubits)
    
    # 验证初始状态
    assert abs(quantum_register.state[0] - 1.0) < 1e-10, "初始状态不正确"
    assert all(abs(quantum_register.state[i]) < 1e-10 for i in range(1, len(quantum_register.state))), "初始状态不正确"
    
    return quantum_register

def verify_initialization(state: QuantumRegister, m: int, n: int) -> bool:
    """
    验证量子态初始化是否正确
    
    参数:
        state: 量子寄存器状态
        m: 第一寄存器的量子比特数
        n: 第二寄存器的量子比特数
        
    返回:
        bool: 如果初始化正确返回True，否则返回False
    """
    # 检查状态向量维度
    expected_dimension = 2**(m + n)
    if len(state.state) != expected_dimension:
        print(f"错误：状态向量维度应为{expected_dimension}，实际为{len(state.state)}")
        return False
    
    # 检查归一化
    norm = math.sqrt(sum(abs(x)**2 for x in state.state))
    if not abs(norm - 1.0) < 1e-10:
        print(f"错误：量子态未归一化，范数为{norm}")
        return False
    
    # 检查是否只有第一个元素非零
    non_zero_indices = [i for i, x in enumerate(state.state) if abs(x) > 1e-10]
    if len(non_zero_indices) != 1 or non_zero_indices[0] != 0:
        print(f"错误：应有且仅有|0⟩状态非零，实际非零索引为{non_zero_indices}")
        return False
    
    return True

def print_quantum_state_info(state: QuantumRegister, m: int, n: int) -> None:
    """
    打印量子态信息
    
    参数:
        state: 量子态向量
        m: 第一寄存器的量子比特数
        n: 第二寄存器的量子比特数
    """
    print(f"量子态维度: {len(state.state)}")
    print(f"第一寄存器位数 (m): {m}")
    print(f"第二寄存器位数 (n): {n}")
    print(f"总量子比特数: {m + n}")
    norm = math.sqrt(sum(abs(x)**2 for x in state.state))
    print(f"量子态归一化检查: {norm:.6f} (应为1.0)")
    
    # 显示前几个非零元素（初始化后只有第一个元素非零）
    non_zero_indices = [i for i, x in enumerate(state.state) if abs(x) > 1e-10]
    print(f"非零元素索引: {non_zero_indices}")
    print(f"非零元素值: {[state.state[i] for i in non_zero_indices]}")

if __name__ == "__main__":
    # 此文件不包含演示代码，演示代码请参考 shor_main.py
    pass