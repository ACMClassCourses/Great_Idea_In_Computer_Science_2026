"""
Shor算法步骤3：量子模幂运算

此文件实现了Shor算法的第三步：量子模幂运算。
应用受控模幂运算U_a：|x⟩|y⟩ = |x⟩|y ⊕ a^x mod N⟩
执行后的状态：|ψ₂⟩ = (1/√Q) ∑_{x=0}^{Q-1} |x⟩|a^x mod N⟩
"""

import math
from typing import List
from shor_definitions import QuantumRegister, QuantumGate
from shor_step2 import verify_superposition

class ModularExponentiationGate:
    """
    模幂运算量子门（无矩阵版）
    
    实现受控模幂运算 U_a: |x⟩|y⟩ → |x⟩|y ⊕ a^x mod N⟩
    
    属性:
        a: 底数
        N: 模数
        m: 第一寄存器量子比特数
        n: 第二寄存器量子比特数
    """
    
    def __init__(self, a: int, N: int, m: int, n: int):
        """
        初始化模幂运算门（无矩阵版）
        
        参数:
            a: 底数
            N: 模数
            m: 第一寄存器量子比特数
            n: 第二寄存器量子比特数
        """
        self.a = a
        self.N = N
        self.m = m
        self.n = n
        self.num_qubits = m + n
        self.name = f"ModularExponentiation(a={a}, N={N})"
        
        # 预计算映射关系，而不是构建完整的矩阵
        self.input_to_output = {}
        
        # 计算所有非零元素的映射关系
        for x in range(2 ** m):
            for y in range(2 ** n):
                # 计算输入索引 |x⟩|y⟩
                input_idx = (x << n) | y
                
                # 计算输出索引 |x⟩|y ⊕ a^x mod N⟩
                a_pow_x = pow(a, x, N)
                output_y = y ^ a_pow_x  # 使用异或运算
                output_idx = (x << n) | output_y
                
                # 存储映射关系
                self.input_to_output[input_idx] = output_idx
    
    def apply_to_register(self, register: 'QuantumRegister', target_qubits: List[int]) -> 'QuantumRegister':
        """
        对量子寄存器的指定量子比特应用模幂运算门（优化版）
        
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
        
        # 使用预计算的映射关系，只处理非零元素
        for input_idx, amplitude in enumerate(register.state):
            if abs(amplitude) < 1e-10:
                continue
            
            # 使用预计算的映射关系
            if input_idx in self.input_to_output:
                output_idx = self.input_to_output[input_idx]
                new_state[output_idx] += amplitude
        
        # 创建新的量子寄存器
        new_register = QuantumRegister(n)
        new_register.set_state(new_state)
        return new_register

def apply_modular_exponentiation(state: QuantumRegister, a: int, N: int, m: int, n: int) -> QuantumRegister:
    """
    应用模幂运算 U_a: |x⟩|y⟩ → |x⟩|y ⊕ a^x mod N⟩
    
    参数:
        state: 当前量子态 (1/√Q) ∑|x⟩|0⟩
        a: 底数
        N: 模数
        m: 第一寄存器的量子比特数
        n: 第二寄存器的量子比特数
        
    返回:
        QuantumRegister: 应用模幂运算后的量子态 (1/√Q) ∑|x⟩|a^x mod N⟩
        
    异常:
        ValueError: 如果输入状态不正确或参数无效
    """
    # 输入验证
    if state.num_qubits != m + n:
        raise ValueError(f"量子寄存器大小不匹配，期望{m+n}，实际{state.num_qubits}")
    
    # 验证叠加态
    if not verify_superposition(state, m, n):
        raise ValueError("输入状态不是有效的叠加态 (1/√Q) ∑|x⟩|0⟩")
    
    # 验证a和N的有效性
    if not (1 < a < N):
        raise ValueError(f"底数a必须满足1 < a < N，得到a={a}, N={N}")
    
    # 验证a和N互质
    if math.gcd(a, N) != 1:
        raise ValueError(f"底数a和模数N必须互质，gcd({a}, {N}) = {math.gcd(a, N)}")
    
    # 创建模幂运算门
    mod_exp_gate = ModularExponentiationGate(a, N, m, n)
    
    # 应用模幂运算门
    result_state = mod_exp_gate.apply_to_register(state, list(range(m + n)))
    
    return result_state

def verify_modular_exponentiation(state: QuantumRegister, a: int, N: int, m: int, n: int) -> bool:
    """
    验证模幂运算是否正确应用
    
    参数:
        state: 量子寄存器状态
        a: 底数
        N: 模数
        m: 第一寄存器的量子比特数
        n: 第二寄存器的量子比特数
        
    返回:
        bool: 如果模幂运算正确返回True，否则返回False
    """
    # 检查归一化
    norm = math.sqrt(sum(abs(x)**2 for x in state.state))
    if not abs(norm - 1.0) < 1e-10:
        print(f"错误：量子态未归一化，范数为{norm}")
        return False
    
    # 检查非零元素的数量和值
    non_zero_indices = [i for i, x in enumerate(state.state) if abs(x) > 1e-10]
    expected_count = 2 ** m  # 应该有2^m个非零元素
    
    if len(non_zero_indices) != expected_count:
        print(f"错误：应有{expected_count}个非零元素，实际有{len(non_zero_indices)}个")
        return False
    
    # 验证模幂运算结果
    expected_amplitude = 1 / math.sqrt(2 ** m)
    
    for idx in non_zero_indices:
        # 分离第一和第二寄存器的值
        x = idx >> n  # 第一寄存器的值
        y = idx & ((1 << n) - 1)  # 第二寄存器的值
        
        # 计算期望的第二寄存器值
        expected_y = pow(a, x, N)
        
        if y != expected_y:
            print(f"错误：状态|{x}⟩|{y}⟩的第二寄存器值不正确，应为|{x}⟩|{expected_y}⟩")
            return False
        
        # 检查振幅
        if not abs(abs(state.state[idx]) - expected_amplitude) < 1e-10:
            print(f"错误：状态|{x}⟩|{y}⟩的振幅不正确，应为{expected_amplitude}，实际为{abs(state.state[idx])}")
            return False
    
    return True

def print_modular_exponentiation_info(state: QuantumRegister, a: int, N: int, m: int, n: int) -> None:
    """
    打印模幂运算后的量子态信息
    
    参数:
        state: 量子态向量
        a: 底数
        N: 模数
        m: 第一寄存器的量子比特数
        n: 第二寄存器的量子比特数
    """
    print(f"模幂运算后的量子态信息:")
    print(f"  底数 a: {a}")
    print(f"  模数 N: {N}")
    print(f"  第一寄存器位数 (m): {m}")
    print(f"  第二寄存器位数 (n): {n}")
    print(f"  理论振幅 (1/√2^m): {1/math.sqrt(2**m):.6f}")
    
    # 显示前几个和最后几个非零元素
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

def create_modular_exponentiation_circuit(initial_state, a: int, N: int, m: int, n: int) -> QuantumRegister:
    """
    创建模幂运算的完整电路实现
    
    参数:
        initial_state: 初始叠加态 (1/√Q) ∑|x⟩|0⟩
        a: 底数
        N: 模数
        m: 第一寄存器的量子比特数
        n: 第二寄存器的量子比特数
        
    返回:
        QuantumRegister: 应用模幂运算后的量子态
    """
    # 步骤1：验证初始状态
    print(f"步骤1：验证初始叠加态")
    if not verify_superposition(initial_state, m, n):
        raise RuntimeError("初始叠加态验证失败")
    
    # 步骤2：应用模幂运算
    print(f"步骤2：应用模幂运算 U_a: |x⟩|y⟩ → |x⟩|y ⊕ a^x mod N⟩")
    print(f"  底数 a = {a}")
    print(f"  模数 N = {N}")
    print(f"  变换: (1/√{2**m}) ∑_{{x=0}}^{{2**{m}-1}} |x⟩|0⟩ → (1/√{2**m}) ∑_{{x=0}}^{{2**{m}-1}} |x⟩|a^x mod {N}⟩")
    
    result_state = apply_modular_exponentiation(initial_state, a, N, m, n)
    
    # 验证结果
    if not verify_modular_exponentiation(result_state, a, N, m, n):
        raise RuntimeError("模幂运算应用失败")
    
    print(f"✓ 成功应用模幂运算 (1/√{2**m}) ∑_{{x=0}}^{{2**{m}-1}} |x⟩|a^x mod {N}⟩")
    
    return result_state

if __name__ == "__main__":
    # 此文件不包含演示代码，演示代码请参考 shor_main.py
    pass