# 计算机伟大思想大作业—量子密钥
组员：谢家烨 付长睿 任德厚


## 代码结构
```
GREAT-IDEA-LAB-QKD/
├── src/
├── quantum_lib/        #量子相关功能
│   ├── Qubit.h
│   └── Qubit.cpp
├── actors/             #模拟密文发送过程的人员
│   ├── sender.h
│   ├── sender.cpp 
│   ├── receiver.h 
│   ├── receiver.cpp
│   ├── listener.h
│   └── listener.cpp
├── CMakeLists.txt
├── build
├── main.cpp            #实现总的模拟过程和展示
└── tests/              #测试
    └── test_quantum_lib.cpp
```
## 使用说明
将终端目录切换到build文件夹，输入make即可编译和链接，此时会在build文件夹下生成 qkd 可执行文件，输入 ./qkd 即可执行

