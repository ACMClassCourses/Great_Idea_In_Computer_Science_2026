"""
Shor算法基础定义

此文件包含了Shor算法所需的基础定义，包括量子比特、量子寄存器、量子门等。
"""

import math
import random
from typing import List, Tuple

# ===== 量子计算基础 =====

### 量子比特定义

class Qubit:
    """
    量子比特类定义
    
    属性:
        alpha: |0⟩态的复数振幅
        beta: |1⟩态的复数振幅
    """
    def __init__(self, alpha=1+0j, beta=0+0j):
        """
        初始化量子比特
        
        参数:
            alpha: |0⟩态的振幅，默认为1
            beta: |1⟩态的振幅，默认为0
        """
        # 归一化处理
        norm = math.sqrt(abs(alpha)**2 + abs(beta)**2)
        if norm > 0:
            self.alpha = alpha / norm
            self.beta = beta / norm
        else:
            self.alpha = 1+0j
            self.beta = 0+0j
    
    def measure(self) -> int:
        """
        测量量子比特，返回0或1
        
        返回:
            int: 测量结果0或1
        """
        prob_zero = abs(self.alpha)**2
        return 0 if random.random() < prob_zero else 1
    
    def __str__(self) -> str:
        """返回量子比特的字符串表示"""
        return f"{self.alpha:.3f}|0⟩ + {self.beta:.3f}|1⟩"

### 量子寄存器定义

class QuantumRegister:
    """
    量子寄存器类定义
    
    属性:
        num_qubits: 量子比特数
        state: 量子态向量，长度为2^num_qubits
    """
    def __init__(self, num_qubits: int):
        """
        初始化量子寄存器
        
        参数:
            num_qubits: 量子比特数
        """
        self.num_qubits = num_qubits
        self.state = [0j] * (2**num_qubits)
        self.state[0] = 1+0j  # 初始化为|0⟩⊗n
    
    def set_state(self, state_vector: List[complex]) -> None:
        """
        设置量子寄存器的状态
        
        参数:
            state_vector: 新的量子态向量
        """
        if len(state_vector) != len(self.state):
            raise ValueError("状态向量长度不匹配")
        
        # 归一化
        norm = math.sqrt(sum(abs(x)**2 for x in state_vector))
        if norm > 0:
            self.state = [x / norm for x in state_vector]
        else:
            raise ValueError("不能设置全零状态")
    
    def measure(self) -> int:
        """
        测量量子寄存器，返回一个整数
        
        返回:
            int: 测量结果，范围0到2^num_qubits-1
        """
        probabilities = [abs(x)**2 for x in self.state]
        return random.choices(range(len(self.state)), weights=probabilities)[0]
    
    def get_amplitude(self, index: int) -> complex:
        """
        获取指定基态的振幅
        
        参数:
            index: 基态索引
            
        返回:
            complex: 振幅值
        """
        return self.state[index]
    
    def __str__(self) -> str:
        """返回量子寄存器的字符串表示"""
        non_zero = [(i, amp) for i, amp in enumerate(self.state) if abs(amp) > 1e-10]
        if len(non_zero) <= 5:
            return " + ".join([f"{amp:.3f}|{i}⟩" for i, amp in non_zero])
        else:
            return f"量子寄存器({self.num_qubits}量子比特, {len(non_zero)}个非零分量)"

# ===== 量子门定义 =====

class QuantumGate:
    """
    量子门类定义
    
    量子门是对量子态进行线性变换的酉矩阵。此类提供了创建和应用量子门的基础框架。
    
    属性:
        matrix: 量子门的酉矩阵表示
        num_qubits: 量子门作用的量子比特数
        name: 量子门的名称
    """
    def __init__(self, matrix: List[List[complex]], num_qubits: int, name: str = "Unknown"):
        """
        初始化量子门
        
        参数:
            matrix: 量子门的酉矩阵表示
            num_qubits: 量子门作用的量子比特数
            name: 量子门的名称
        """
        self.matrix = matrix
        self.num_qubits = num_qubits
        self.name = name
        
        # 验证矩阵维度
        expected_size = 2 ** num_qubits
        if len(matrix) != expected_size or any(len(row) != expected_size for row in matrix):
            raise ValueError(f"矩阵维度不匹配，期望{expected_size}×{expected_size}")
        
        # 验证酉性 (U†U = I)
        if not self._is_unitary():
            raise ValueError("矩阵不是酉矩阵")
    
    def _is_unitary(self) -> bool:
        """
        检查矩阵是否为酉矩阵
        
        返回:
            bool: 如果是酉矩阵返回True，否则返回False
        """
        # 计算U†U
        n = len(self.matrix)
        identity = [[0j] * n for _ in range(n)]
        
        # 计算共轭转置 U†
        conjugate_transpose = [[complex(0, 0) for _ in range(n)] for _ in range(n)]
        for i in range(n):
            for j in range(n):
                conjugate_transpose[i][j] = complex(self.matrix[j][i].real, -self.matrix[j][i].imag)
        
        # 计算 U†U
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    identity[i][j] += conjugate_transpose[i][k] * self.matrix[k][j]
        
        # 检查是否为单位矩阵
        for i in range(n):
            for j in range(n):
                expected = 1.0 if i == j else 0.0
                if abs(identity[i][j].real - expected) > 1e-10 or abs(identity[i][j].imag) > 1e-10:
                    return False
        
        return True
    
    def apply_to_qubit(self, qubit: 'Qubit') -> 'Qubit':
        """
        对单个量子比特应用量子门
        
        参数:
            qubit: 目标量子比特
            
        返回:
            Qubit: 应用量子门后的新量子比特
        """
        if self.num_qubits != 1:
            raise ValueError(f"此量子门作用于{self.num_qubits}个量子比特，不能应用于单个量子比特")
        
        # 应用矩阵变换
        new_alpha = self.matrix[0][0] * qubit.alpha + self.matrix[0][1] * qubit.beta
        new_beta = self.matrix[1][0] * qubit.alpha + self.matrix[1][1] * qubit.beta
        
        return Qubit(new_alpha, new_beta)
    
    def apply_to_register(self, register: 'QuantumRegister', target_qubits: List[int]) -> 'QuantumRegister':
        """
        对量子寄存器的指定量子比特应用量子门
        
        参数:
            register: 目标量子寄存器
            target_qubits: 目标量子比特的索引列表
            
        返回:
            QuantumRegister: 应用量子门后的新量子寄存器
        """
        if len(target_qubits) != self.num_qubits:
            raise ValueError(f"量子门作用量子比特数({self.num_qubits})与目标量子比特数({len(target_qubits)})不匹配")
        
        n = register.num_qubits
        new_state = [0j] * len(register.state)
        
        # 对每个基态应用量子门
        for i in range(len(register.state)):
            # 获取当前基态的振幅
            amplitude = register.state[i]
            if abs(amplitude) < 1e-10:
                continue
            
            # 确定目标量子比特的状态
            target_state = 0
            for idx, qubit_idx in enumerate(target_qubits):
                if (i >> (n - 1 - qubit_idx)) & 1:
                    target_state |= (1 << (self.num_qubits - 1 - idx))
            
            # 对目标量子比特的所有可能状态应用量子门
            for j in range(2 ** self.num_qubits):
                # 计算矩阵元素
                matrix_element = self.matrix[j][target_state]
                
                # 构建新的基态索引
                new_index = i
                for idx, qubit_idx in enumerate(target_qubits):
                    # 清除原目标量子比特的值
                    new_index &= ~(1 << (n - 1 - qubit_idx))
                    # 设置新的值
                    if (j >> (self.num_qubits - 1 - idx)) & 1:
                        new_index |= (1 << (n - 1 - qubit_idx))
                
                # 添加振幅贡献
                new_state[new_index] += matrix_element * amplitude
        
        # 创建新的量子寄存器
        new_register = QuantumRegister(n)
        new_register.set_state(new_state)
        return new_register
    
    def __str__(self) -> str:
        """返回量子门的字符串表示"""
        return f"QuantumGate({self.name}, {self.num_qubits} qubits)"

# 常用量子门定义

def create_hadamard_gate() -> QuantumGate:
    """
    创建Hadamard门
    
    H = 1/√2 * [[1, 1],
                [1, -1]]
    
    返回:
        QuantumGate: Hadamard门对象
    """
    inv_sqrt2 = 1 / math.sqrt(2)
    matrix = [
        [inv_sqrt2, inv_sqrt2],
        [inv_sqrt2, -inv_sqrt2]
    ]
    return QuantumGate(matrix, 1, "Hadamard")