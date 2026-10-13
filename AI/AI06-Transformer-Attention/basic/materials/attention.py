# 运行：python attention.py
import numpy as np


def project(X, W_Q, W_K, W_V):
    # 线性投影：检查维度后计算 Q、K、V
    assert X.shape[1] == W_Q.shape[0] == W_K.shape[0] == W_V.shape[0]
    return X @ W_Q, X @ W_K, X @ W_V


def softmax_rows(S):
    # 逐行 softmax，先减每行最大值避免指数溢出
    S = S - S.max(axis=1, keepdims=True)
    e = np.exp(S)
    return e / e.sum(axis=1, keepdims=True)


def causal_mask(n):
    # 因果掩码：第 i 行屏蔽 j > i 的位置
    mask = np.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            mask[i, j] = -np.inf
    return mask


def attention(Q, K, V, causal=False):
    # 缩放点积注意力，返回权重 A 与输出 O
    d_k = Q.shape[1]
    S = Q @ K.T / np.sqrt(d_k)
    if causal:
        S = S + causal_mask(Q.shape[0])
    A = softmax_rows(S)
    return A, A @ V


def show(name, M):
    # 打印名称、形状与数值
    print(name, "shape =", M.shape)
    print(np.round(M, 6))
    print()


def main():
    # 1. 手工核对：X 与三个投影矩阵都是二阶单位阵
    print("== 1. 手工核对的例子 ==")
    I = np.eye(2)
    Q, K, V = project(I, I, I, I)
    show("Q(=K=V)", Q)
    A, O = attention(Q, K, V)
    show("A 无掩码", A)
    print("每行权重之和:", A.sum(axis=1))
    print()
    A, O = attention(Q, K, V, causal=True)
    show("A 因果掩码", A)
    print("每行权重之和:", A.sum(axis=1))
    print()

    # 2. 只有一个位置时，输出等于该位置的 V
    print("== 2. 只有一个位置 ==")
    X = np.array([[2.0, 3.0]])
    W = np.eye(2)
    Q, K, V = project(X, W, W, W)
    A, O = attention(Q, K, V)
    show("A", A)
    print("输出等于 V:", np.allclose(O, V))
    print()

    # 3. 因果掩码下只改后面的输入，前面输出不变
    print("== 3. 因果掩码：只改后面的输入 ==")
    X = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    W = np.eye(2)
    Q, K, V = project(X, W, W, W)
    A, O1 = attention(Q, K, V, causal=True)
    X2 = X.copy()
    X2[2] = [9.0, 9.0]
    Q, K, V = project(X2, W, W, W)
    A, O2 = attention(Q, K, V, causal=True)
    show("O 原输入", O1)
    show("O 改后输入", O2)
    print("前两行输出不变:", np.allclose(O1[:2], O2[:2]))
    print()

    # 4. 无掩码时打乱输入顺序，输出按同样方式重排
    print("== 4. 打乱输入顺序 ==")
    order = [2, 0, 1]
    Q, K, V = project(X, W, W, W)
    A, O1 = attention(Q, K, V)
    Q, K, V = project(X[order], W, W, W)
    A, O2 = attention(Q, K, V)
    show("O 原顺序", O1)
    show("O 打乱后", O2)
    print("输出按同样方式重排:", np.allclose(O1[order], O2))


if __name__ == "__main__":
    main()
