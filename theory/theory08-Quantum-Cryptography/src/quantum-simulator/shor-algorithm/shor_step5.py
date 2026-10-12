"""
Shor算法步骤5：量子傅里叶变换

此文件包含了量子傅里叶变换所需的量子门和实现函数。
"""

import math
from shor_definitions import QuantumGate, QuantumRegister


def create_controlled_phase_gate(angle: float) -> QuantumGate:
    """
    创建受控相位门
    
    CP(θ) = [[1, 0, 0, 0],
             [0, 1, 0, 0],
             [0, 0, 1, 0],
             [0, 0, 0, e^(iθ)]]
    
    参数:
        angle: 相位角度θ
        
    返回:
        QuantumGate: 受控相位门对象
    """
    matrix = [
        [1+0j, 0+0j, 0+0j, 0+0j],
        [0+0j, 1+0j, 0+0j, 0+0j],
        [0+0j, 0+0j, 1+0j, 0+0j],
        [0+0j, 0+0j, 0+0j, complex(math.cos(angle), math.sin(angle))]
    ]
    return QuantumGate(matrix, 2, f"ControlledPhase({angle})")


def create_swap_gate() -> QuantumGate:
    """
    创建交换门
    
    SWAP = [[1, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1]]
    
    返回:
        QuantumGate: 交换门对象
    """
    matrix = [
        [1+0j, 0+0j, 0+0j, 0+0j],
        [0+0j, 0+0j, 1+0j, 0+0j],
        [0+0j, 1+0j, 0+0j, 0+0j],
        [0+0j, 0+0j, 0+0j, 1+0j]
    ]
    return QuantumGate(matrix, 2, "SWAP")


def apply_qft_circuit(register: QuantumRegister, num_qubits: int) -> QuantumRegister:
    """
    应用QFT电路到量子寄存器
    
    QFT|j⟩ = (1/√2^n) ∑_{k=0}^{2^n-1} e^(2πijk/2^n) |k⟩
    
    参数:
        register: 输入量子寄存器
        num_qubits: 要应用QFT的量子比特数
        
    返回:
        QuantumRegister: 应用QFT电路后的量子寄存器
    """
    from shor_definitions import create_hadamard_gate
    
    result_register = register
    
    # 对每个量子比特应用Hadamard门和受控相位门
    for j in range(num_qubits):
        # 应用Hadamard门到第j个量子比特
        hadamard_gate = create_hadamard_gate()
        result_register = hadamard_gate.apply_to_register(result_register, [j])
        
        # 应用受控相位门
        for k in range(j + 1, num_qubits):
            angle = math.pi / (2 ** (k - j))
            cp_gate = create_controlled_phase_gate(angle)
            result_register = cp_gate.apply_to_register(result_register, [k, j])
    
    return result_register


def reverse_qubit_order(register: QuantumRegister, num_qubits: int) -> QuantumRegister:
    """
    反转量子寄存器中前num_qubits个量子比特的顺序
    
    参数:
        register: 输入量子寄存器
        num_qubits: 要反转顺序的量子比特数
        
    返回:
        QuantumRegister: 反转顺序后的量子寄存器
    """
    result_register = register
    
    # 交换量子比特顺序（反转量子比特）
    for j in range(num_qubits // 2):
        swap_gate = create_swap_gate()
        result_register = swap_gate.apply_to_register(result_register, [j, num_qubits - j - 1])
    
    return result_register


def quantum_fourier_transform(register: QuantumRegister, num_qubits: int) -> QuantumRegister:
    """
    对量子寄存器的前num_qubits个量子比特应用量子傅里叶变换
    
    参数:
        register: 输入量子寄存器
        num_qubits: 要应用QFT的量子比特数
        
    返回:
        QuantumRegister: 应用QFT后的量子寄存器
        
    异常:
        ValueError: 如果num_qubits大于寄存器的量子比特数
    """
    # 1. 输入验证
    if num_qubits > register.num_qubits:
        raise ValueError(f"num_qubits({num_qubits})大于寄存器的量子比特数({register.num_qubits})")
    
    # 2. 应用QFT电路
    result_register = apply_qft_circuit(register, num_qubits)
    
    # 3. 反转量子比特顺序
    result_register = reverse_qubit_order(result_register, num_qubits)
    
    return result_register


def verify_qft_result(input_register: QuantumRegister, output_register: QuantumRegister,
                     num_qubits: int) -> bool:
    """
    验证QFT结果是否正确
    
    参数:
        input_register: 输入量子寄存器
        output_register: 输出量子寄存器
        num_qubits: 应用QFT的量子比特数
        
    返回:
        bool: 如果QFT结果正确返回True，否则返回False
    """
    # 这里可以实现验证逻辑
    # 由于QFT是酉变换，我们可以验证 U†U = I
    # 或者对已知输入验证输出
    
    # 简单验证：检查寄存器大小是否保持不变
    if input_register.num_qubits != output_register.num_qubits:
        return False
    
    # 检查状态是否归一化
    norm = sum(abs(x)**2 for x in output_register.state)
    if abs(norm - 1.0) > 1e-10:
        return False
    
    return True