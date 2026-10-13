"""
Shor算法步骤6：测量第一寄存器

此文件包含了测量第一寄存器所需的函数和实现。
根据QFT的性质，测量结果c很可能接近kQ/r，其中k是某个整数。
"""

import math
import random
from typing import List, Tuple
from shor_definitions import QuantumRegister


def measure_first_register(state: QuantumRegister, m: int, n: int) -> Tuple[int, QuantumRegister]:
    """
    测量第一寄存器，得到一个整数c
    
    根据QFT的性质，c很可能接近kQ/r，其中k是某个整数。
    测量后，量子态坍缩为|c⟩|y₀⟩，其中c是测量结果。
    
    参数:
        state: 当前量子态，为QFT后的状态 ∑α_c|c⟩|y₀⟩
        m: 第一寄存器的量子比特数
        n: 第二寄存器的量子比特数
        
    返回:
        Tuple[int, QuantumRegister]:
            - 测量结果c，一个整数
            - 测量后的量子态，坍缩为|c⟩|y₀⟩
            
    异常:
        ValueError: 如果输入状态不正确或参数无效
    """
    # 1. 输入验证
    if state.num_qubits != m + n:
        raise ValueError(f"量子寄存器大小({state.num_qubits})与期望大小({m+n})不匹配")
    
    if m <= 0 or n <= 0:
        raise ValueError("量子比特数必须为正整数")
    
    # 2. 计算第一寄存器各值的测量概率
    probabilities = calculate_first_register_probabilities(state, m, n)
    
    # 3. 根据概率随机选择测量结果
    measurement_result = random.choices(range(len(probabilities)), weights=probabilities)[0]
    
    # 4. 量子态坍缩
    collapsed_state = collapse_to_measurement_result(state, m, n, measurement_result)
    
    return measurement_result, collapsed_state


def calculate_first_register_probabilities(state: QuantumRegister, m: int, n: int) -> List[float]:
    """
    计算第一寄存器各值的测量概率
    
    对于每个可能的c值，计算其出现的概率P(c) = ∑|α_{c,y}|²，
    其中α_{c,y}是|c⟩|y⟩的振幅
    
    参数:
        state: 量子寄存器状态
        m: 第一寄存器的量子比特数
        n: 第二寄存器的量子比特数
        
    返回:
        List[float]: 第一寄存器各值的概率列表，长度为2^m
    """
    # 1. 初始化概率数组
    probabilities = [0.0] * (2 ** m)
    
    # 2. 遍历所有基态
    for i, amplitude in enumerate(state.state):
        if abs(amplitude) < 1e-10:
            continue
            
        # 3. 提取第一寄存器值
        c = i >> n  # 右移n位，取高m位
        
        # 4. 累积概率
        probabilities[c] += abs(amplitude) ** 2
    
    return probabilities


def collapse_to_measurement_result(state: QuantumRegister, m: int, n: int, measurement_result: int) -> QuantumRegister:
    """
    根据测量结果坍缩量子态
    
    测量后，量子态坍缩为|c⟩∑α_y|y⟩，其中c是测量结果，
    保留第二寄存器的所有状态，但重新归一化
    
    参数:
        state: 原始量子态
        m: 第一寄存器的量子比特数
        n: 第二寄存器的量子比特数
        measurement_result: 第一寄存器的测量结果c
        
    返回:
        QuantumRegister: 坍缩后的量子态|c⟩∑α_y|y⟩
    """
    # 1. 验证测量结果
    if measurement_result < 0 or measurement_result >= 2 ** m:
        raise ValueError(f"测量结果{measurement_result}超出范围[0, {2**m-1}]")
    
    # 2. 创建新的量子态向量
    new_state = [0j] * len(state.state)
    
    # 3. 保留第二寄存器的所有状态
    base_index = measurement_result << n  # c左移n位
    
    # 复制所有与测量结果对应的状态
    for y in range(2 ** n):
        index = base_index | y
        new_state[index] = state.state[index]
    
    # 4. 重新归一化
    norm = math.sqrt(sum(abs(x)**2 for x in new_state))
    if norm > 0:
        new_state = [x / norm for x in new_state]
    else:
        # 如果所有振幅都为0（理论上不应该发生），随机选择一个y值
        random_y = random.randint(0, 2 ** n - 1)
        final_index = base_index | random_y
        new_state[final_index] = complex(1, 0)
    
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
    # 1. 检查归一化
    norm = sum(abs(x)**2 for x in state.state)
    if abs(norm - 1.0) > 1e-10:
        return False
    
    # 2. 检查量子态形式
    base_index = measurement_result << n
    for i, amplitude in enumerate(state.state):
        if abs(amplitude) > 1e-10:
            # 检查第一寄存器的值是否等于测量结果
            if (i >> n) != measurement_result:
                return False
    
    return True