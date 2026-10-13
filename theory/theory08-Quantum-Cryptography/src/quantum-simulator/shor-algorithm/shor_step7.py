"""
Shor算法步骤7：经典后处理 - 连分数算法

此文件实现了Shor算法第七步：经典后处理。
使用连分数算法从测量结果c推断周期r，并最终分解合数N。
"""

import math
from typing import List, Tuple, Optional


def continued_fraction_algorithm(c: int, Q: int, N: int, a: Optional[int] = None) -> Optional[int]:
    """
    连分数算法，从测量结果c推断周期r
    
    参数:
        c: 第一寄存器的测量结果
        Q: 第一寄存器的状态数 (Q = 2^m)
        N: 要分解的合数
        a: 基数（可选，用于周期验证）
        
    返回:
        Optional[int]: 推断的周期r，如果无法推断则返回None
        
    异常:
        ValueError: 如果输入参数无效
    """
    # 1. 输入验证
    if Q <= 0 or N <= 0 or c < 0 or c >= Q:
        raise ValueError("输入参数无效")
    
    # 2. 计算c/Q的连分数展开
    coefficients = continued_fraction_expansion(c, Q)
    
    # 3. 尝试不同的收敛子找到可能的r
    for i in range(1, len(coefficients) + 1):
        # 计算第i个收敛子
        numerator, denominator = compute_convergent(coefficients[:i])
        
        # 检查是否为可能的周期
        if denominator > 0 and denominator < N:
            # 验证周期
            if verify_period(denominator, N, a):
                return denominator
    
    # 4. 如果没有找到有效周期，返回None
    return None


def continued_fraction_expansion(numerator: int, denominator: int, max_depth: int = 20) -> List[int]:
    """
    计算连分数展开
    
    参数:
        numerator: 分子
        denominator: 分母
        max_depth: 最大展开深度，防止无限循环
        
    返回:
        List[int]: 连分数展开的系数列表 [a₀, a₁, a₂, ...]
        
    异常:
        ValueError: 如果分母为0
    """
    # 1. 输入验证
    if denominator == 0:
        raise ValueError("分母不能为0")
    
    # 2. 初始化结果列表
    coefficients = []
    
    # 3. 执行欧几里得算法
    a = numerator
    b = denominator
    
    for _ in range(max_depth):
        if b == 0:
            break
        
        # 计算商和余数
        q = a // b
        r = a % b
        
        # 添加商到系数列表
        coefficients.append(q)
        
        # 更新a和b
        a, b = b, r
    
    return coefficients


def compute_convergent(coefficients: List[int]) -> Tuple[int, int]:
    """
    计算连分数的收敛子
    
    参数:
        coefficients: 连分数展开的系数列表
        
    返回:
        Tuple[int, int]: (分子, 分母) 表示的收敛子
        
    异常:
        ValueError: 如果系数列表为空
    """
    # 1. 输入验证
    if not coefficients:
        return 0, 1
    
    # 2. 初始化前两个收敛子
    p_minus2, p_minus1 = 0, 1  # p_{-2} = 0, p_{-1} = 1
    q_minus2, q_minus1 = 1, 0  # q_{-2} = 1, q_{-1} = 0
    
    # 3. 递推计算收敛子
    for a in coefficients:
        p = a * p_minus1 + p_minus2
        q = a * q_minus1 + q_minus2
        
        # 更新前两个收敛子
        p_minus2, p_minus1 = p_minus1, p
        q_minus2, q_minus1 = q_minus1, q
    
    return p_minus1, q_minus1


def verify_period(r: int, N: int, a: Optional[int] = None) -> bool:
    """
    验证r是否为函数f(x) = a^x mod N的周期
    
    参数:
        r: 待验证的周期
        N: 模数
        a: 基数（可选）
        
    返回:
        bool: 如果r是有效周期返回True，否则返回False
        
    异常:
        ValueError: 如果r或N不是正整数
    """
    # 1. 输入验证
    if r <= 1 or N <= 1:
        return False
    
    # 2. 如果没有提供a，无法验证
    if a is None:
        return False
    
    # 3. 检查a和N是否互质
    if math.gcd(a, N) != 1:
        return False
    
    # 4. 检查a^r mod N是否等于1
    try:
        return pow(a, r, N) == 1
    except (ValueError, OverflowError):
        return False


def find_factors_from_period(N: int, a: int, r: int) -> Optional[Tuple[int, int]]:
    """
    从周期r找出N的因子
    
    参数:
        N: 要分解的合数
        a: 基数
        r: 周期
        
    返回:
        Optional[Tuple[int, int]]: (p, q) N的因子，如果无法找出则返回None
        
    异常:
        ValueError: 如果输入参数无效
    """
    # 1. 输入验证
    if N <= 1 or a <= 0 or r <= 1:
        return None
    
    # 2. 检查周期是否为偶数
    if r % 2 != 0:
        return None
    
    try:
        # 3. 计算候选因子
        gcd1 = math.gcd(pow(a, r // 2) - 1, N)
        gcd2 = math.gcd(pow(a, r // 2) + 1, N)
        
        # 4. 检查是否为有效因子
        if 1 < gcd1 < N and 1 < gcd2 < N:
            return gcd1, gcd2
        elif 1 < gcd1 < N:
            return gcd1, N // gcd1
        elif 1 < gcd2 < N:
            return gcd2, N // gcd2
        
        return None
    except (ValueError, OverflowError):
        return None


def classical_post_processing(c: int, Q: int, N: int, a: int) -> Optional[Tuple[int, int]]:
    """
    完整的经典后处理流程
    
    参数:
        c: 第一寄存器的测量结果
        Q: 第一寄存器的状态数
        N: 要分解的合数
        a: 基数
        
    返回:
        Optional[Tuple[int, int]]: (p, q) N的因子，如果无法找出则返回None
        
    异常:
        ValueError: 如果输入参数无效
    """
    # 1. 输入验证
    if Q <= 0 or N <= 0 or c < 0 or c >= Q or a <= 0:
        raise ValueError("输入参数无效")
    
    # 2. 检查a和N是否互质
    if math.gcd(a, N) != 1:
        raise ValueError(f"a={a}与N={N}不互质")
    
    # 3. 使用连分数算法推断周期
    r = continued_fraction_algorithm(c, Q, N, a)
    
    # 4. 如果无法推断周期，返回None
    if r is None:
        return None
    
    # 5. 从周期找出因子
    return find_factors_from_period(N, a, r)