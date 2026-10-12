"""
Shor算法步骤4：测量第二寄存器

此文件实现了Shor算法的第四步：测量第二寄存器。
对第二寄存器进行测量，得到某个函数值y₀ = a^x₀ mod N。
测量后，量子态坍缩为：|ψ₃⟩ = (1/√M) ∑_{k=0}^{M-1} |x₀ + kr⟩ |y₀⟩
"""

import math
import random
from typing import List, Tuple
from shor_definitions import QuantumRegister
from shor_step3 import verify_modular_exponentiation

def measure_second_register(state: QuantumRegister, m: int, n: int) -> Tuple[QuantumRegister, int]:
    """
    测量第二寄存器，根据概率随机选择一个状态
    
    参数:
        state: 当前量子态 (1/√Q) ∑|x⟩|a^x mod N⟩
        m: 第一寄存器的量子比特数
        n: 第二寄存器的量子比特数
        
    返回:
        Tuple[QuantumRegister, int]: 
            - 测量后的量子态 (1/√M) ∑|x₀ + kr⟩|y₀⟩
            - 测量结果 y₀
            
    异常:
        ValueError: 如果输入状态不正确或参数无效
    """
    # 输入验证
    if state.num_qubits != m + n:
        raise ValueError(f"量子寄存器大小不匹配，期望{m+n}，实际{state.num_qubits}")
    
    # 计算第二寄存器各值的概率
    probabilities = calculate_measurement_probabilities(state, m, n)
    
    # 根据概率随机选择测量结果
    measurement_result = random.choices(range(2**n), weights=probabilities)[0]
    
    # 量子态坍缩
    collapsed_state = collapse_quantum_state(state, m, n, measurement_result)
    
    return collapsed_state, measurement_result

def calculate_measurement_probabilities(state: QuantumRegister, m: int, n: int) -> List[float]:
    """
    计算第二寄存器各值的测量概率
    
    参数:
        state: 量子寄存器状态
        m: 第一寄存器的量子比特数
        n: 第二寄存器的量子比特数
        
    返回:
        List[float]: 第二寄存器各值的概率列表
    """
    # 初始化概率数组
    probabilities = [0.0] * (2 ** n)
    
    # 计算每个y值的概率
    for idx, amplitude in enumerate(state.state):
        if abs(amplitude) < 1e-10:
            continue
            
        # 分离第一和第二寄存器的值
        x = idx >> n  # 第一寄存器的值
        y = idx & ((1 << n) - 1)  # 第二寄存器的值
        
        # 将振幅的平方概率加到对应的y值上
        probabilities[y] += abs(amplitude) ** 2
    
    return probabilities

def collapse_quantum_state(state: QuantumRegister, m: int, n: int, measurement_result: int) -> QuantumRegister:
    """
    根据测量结果坍缩量子态
    
    参数:
        state: 原始量子态
        m: 第一寄存器的量子比特数
        n: 第二寄存器的量子比特数
        measurement_result: 第二寄存器的测量结果
        
    返回:
        QuantumRegister: 坍缩后的量子态
    """
    # 创建新的量子态向量
    new_state = [0j] * len(state.state)
    
    # 保留与测量结果匹配的分量
    matching_indices = []
    for idx, amplitude in enumerate(state.state):
        if abs(amplitude) < 1e-10:
            continue
            
        # 分离第一和第二寄存器的值
        y = idx & ((1 << n) - 1)  # 第二寄存器的值
        
        # 如果第二寄存器的值等于测量结果，保留该分量
        if y == measurement_result:
            new_state[idx] = amplitude
            matching_indices.append(idx)
    
    # 重新归一化
    norm = math.sqrt(sum(abs(x)**2 for x in new_state))
    if norm > 1e-10:
        new_state = [x / norm for x in new_state]
    else:
        raise ValueError("测量后没有匹配的量子态分量")
    
    # 创建新的量子寄存器
    collapsed_register = QuantumRegister(m + n)
    collapsed_register.set_state(new_state)
    
    return collapsed_register

def verify_measurement_result(state: QuantumRegister, m: int, n: int, measurement_result: int) -> bool:
    """
    验证测量结果是否正确
    
    参数:
        state: 测量后的量子态
        m: 第一寄存器的量子比特数
        n: 第二寄存器的量子比特数
        measurement_result: 测量结果
        
    返回:
        bool: 如果测量结果正确返回True，否则返回False
    """
    # 检查归一化
    norm = math.sqrt(sum(abs(x)**2 for x in state.state))
    if not abs(norm - 1.0) < 1e-10:
        print(f"错误：量子态未归一化，范数为{norm}")
        return False
    
    # 检查所有非零分量的第二寄存器值是否等于测量结果
    non_zero_indices = [i for i, x in enumerate(state.state) if abs(x) > 1e-10]
    
    for idx in non_zero_indices:
        y = idx & ((1 << n) - 1)  # 第二寄存器的值
        if y != measurement_result:
            print(f"错误：状态{idx}的第二寄存器值{y}不等于测量结果{measurement_result}")
            return False
    
    return True

def print_measurement_info(state: QuantumRegister, measurement_result: int, m: int, n: int) -> None:
    """
    打印测量结果信息
    
    参数:
        state: 测量后的量子态
        measurement_result: 测量结果
        m: 第一寄存器的量子比特数
        n: 第二寄存器的量子比特数
    """
    print(f"测量结果信息:")
    print(f"  测量结果 y₀: {measurement_result}")
    print(f"  测量结果二进制: {bin(measurement_result)[2:].zfill(n)}")
    
    # 显示非零元素
    non_zero_indices = [i for i, x in enumerate(state.state) if abs(x) > 1e-10]
    print(f"  非零元素数量: {len(non_zero_indices)}")
    
    if len(non_zero_indices) > 0:
        print(f"  前5个非零元素:")
        for i in range(min(5, len(non_zero_indices))):
            idx = non_zero_indices[i]
            first_reg = idx >> n
            second_reg = idx & ((1 << n) - 1)
            print(f"    |{first_reg}⟩|{second_reg}⟩: {state.state[idx]}")
        
        if len(non_zero_indices) > 5:
            print(f"    ...")
            print(f"  最后5个非零元素:")
            for i in range(max(0, len(non_zero_indices) - 5), len(non_zero_indices)):
                idx = non_zero_indices[i]
                first_reg = idx >> n
                second_reg = idx & ((1 << n) - 1)
                print(f"    |{first_reg}⟩|{second_reg}⟩: {state.state[idx]}")
    
    # 计算测量前的概率分布
    print(f"  测量概率分析:")
    probabilities = calculate_measurement_probabilities(state, m, n)
    print(f"    测量结果的概率: {probabilities[measurement_result]:.6f}")

def create_measurement_circuit(state: QuantumRegister, m: int, n: int) -> Tuple[QuantumRegister, int]:
    """
    创建测量的完整电路实现
    
    参数:
        state: 输入量子态 (1/√Q) ∑|x⟩|a^x mod N⟩
        m: 第一寄存器的量子比特数
        n: 第二寄存器的量子比特数
        
    返回:
        Tuple[QuantumRegister, int]: 测量后的量子态和测量结果
    """
    # 步骤1：验证输入状态
    print(f"步骤1：验证输入量子态")
    # 这里我们假设输入状态已经是模幂运算后的状态
    
    # 步骤2：计算测量概率
    print(f"步骤2：计算第二寄存器各值的测量概率")
    probabilities = calculate_measurement_probabilities(state, m, n)
    
    # 显示概率分布信息
    print(f"  测量概率分布:")
    for y, prob in enumerate(probabilities):
        if prob > 1e-10:
            print(f"    P(y={y}) = {prob:.6f}")
    
    # 步骤3：执行测量
    print(f"步骤3：测量第二寄存器")
    measurement_result = random.choices(range(2**n), weights=probabilities)[0]
    print(f"  测量结果: y₀ = {measurement_result} (二进制: {bin(measurement_result)[2:].zfill(n)})")
    
    # 步骤4：量子态坍缩
    print(f"步骤4：量子态坍缩")
    collapsed_state = collapse_quantum_state(state, m, n, measurement_result)
    print(f"  量子态已坍缩为 |ψ₃⟩ = (1/√M) ∑|x₀ + kr⟩|{measurement_result}⟩")
    
    # 验证测量结果
    if not verify_measurement_result(collapsed_state, m, n, measurement_result):
        raise RuntimeError("测量结果验证失败")
    
    print(f"✓ 成功完成第二寄存器测量")
    
    return collapsed_state, measurement_result

if __name__ == "__main__":
    # 此文件不包含演示代码，演示代码请参考 shor_main.py
    pass