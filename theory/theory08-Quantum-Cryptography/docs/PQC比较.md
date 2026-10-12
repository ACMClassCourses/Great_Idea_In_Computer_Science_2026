# 密码影响与后量子方案比较

| 对象 | 量子影响或候选基础 | 主要用途 | 报告中不能省略的限定 |
| --- | --- | --- | --- |
| RSA、有限域/椭圆曲线 Diffie–Hellman | Shor 针对分解或离散对数 | 加密、密钥协商、签名的既有体系 | 实际攻击需要足够规模的容错量子计算；小模拟不是资源估计。 |
| 理想对称密钥穷举 | Grover 给出平方级**查询**加速 | 穷举搜索模型 | 查询数不等于实际门成本；并行性、存储和攻击模型会改变结论。 |
| ML-KEM | 模格假设 | 密钥封装，协商共享秘密 | 不是数字签名，也不等于 QKD。 |
| ML-DSA | 模格假设 | 数字签名与验证 | 不提供直接保密通信。 |
| SLH-DSA | 哈希函数安全性质 | 无状态数字签名 | 与格方案的安全基础、性能取舍不同。 |
| QKD | 量子通信、测量扰动与协议后处理 | 建立原始共享密钥 | 仍需要认证、纠错和隐私放大；不是“自动安全”。 |

PQC 不是“把经典密文换成量子态”。它通常是经典设备上执行的算法；其安全论断建立在具体的困难性假设、参数和实现上。QKD 与 PQC 可以处于同一系统，但解决问题和安全来源不同。

## 推荐引用

- Peter Shor, *Algorithms for quantum computation: discrete logarithms and factoring*, 1994/1995。
- Lov Grover, *A fast quantum mechanical algorithm for database search*, 1996。
- NIST, [FIPS 203: ML-KEM](https://csrc.nist.gov/pubs/fips/203/final)。
- NIST, [FIPS 204: ML-DSA](https://csrc.nist.gov/pubs/fips/204/final)。
- NIST, [FIPS 205: SLH-DSA](https://csrc.nist.gov/pubs/fips/205/final)。

引用实际硬件资源、攻击进展或标准部署状态时，必须注明资料日期；它们不能由本项目的小规模模拟推出。
