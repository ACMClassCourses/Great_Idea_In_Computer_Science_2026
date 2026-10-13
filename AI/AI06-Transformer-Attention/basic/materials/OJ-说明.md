# Transformer（Basic 单头注意力）

## 题目描述

完成一次缩放点积注意力：

$$Q=XW_Q,\ K=XW_K,\ V=XW_V,$$
$$S=QK^T/\sqrt{d_k},\ A=softmax(S+mask),\ O=AV.$$

softmax 按行计算，必须先减去该行最大值。开启因果掩码时，在 softmax 前屏蔽 $j>i$ 的位置，保留对角线。

## 输入格式

第一行为 `n d_model d_k d_v causal`，`causal` 为 0 或 1。后续浮点数依次为：

1. $X$，共 $n\times d_{model}$ 个；
2. $W_Q$，共 $d_{model}\times d_k$ 个；
3. $W_K$，共 $d_{model}\times d_k$ 个；
4. $W_V$，共 $d_{model}\times d_v$ 个。

所有矩阵均按行优先排列。

## 输出格式

仅输出浮点数，依次为 $Q,K,V,S,A,O$，各矩阵按行优先排列。数值误差容限为绝对 $10^{-6}$ 加相对 $2\times10^{-5}$。

## 完整 Basic 提交

除 OJ 结果外，还需提交源码、矩阵日志、权重热力图和 Q1-Q5；验收时还会检查行和、非负性、单位置及修改未来输入的因果性。

## 数据范围

$1\le n,d_{model},d_k,d_v\le32$。
