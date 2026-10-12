# 示例图像

`input/` 和 `expected/` 中的示例图由 `examples/run_demo.py` 确定性生成，不使用外部照片：

- `input/synthetic_hazy.png`：依据大气散射模型合成的有雾图；
- `expected/synthetic_clear_reference.png`：合成前的清晰参考图；
- `expected/synthetic_depth_normalized.png`：用于合成雾的归一化深度图。

这些文件仅用于检查程序能否运行和观察中间结果，不用于证明 DCP 在真实图像上的普遍性能。加入其他图像前，应在本文件中记录来源、许可证和用途。

