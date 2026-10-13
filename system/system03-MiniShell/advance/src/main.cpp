#include <iostream>
#include <string>
#include <vector>

// ---------------------------------------------------------------------------
// Mini Shell - Advance 学生起点
//
// 单文件工程：所有代码都写在 src/main.cpp 里。本地 CMake 只编译这一个文件，
// 提交到 OJ 的也只需要这一个自包含的 .cpp，不需要 #include 任何本地头文件。
//
// 下面给出的目录树表示只是起点，可以自由改动：
//   nodes[0] 是根目录 "/"，它的父目录是它自己。
// ---------------------------------------------------------------------------

enum class NodeType { File, Directory };

struct Node {
    std::string name;           // 条目名；非空，且不是 "." 或 ".."
    NodeType type = NodeType::File;
    int parent = 0;             // 父目录的下标
    std::vector<int> children;  // 直接子条目的下标（仅目录使用）
    std::string content;        // 文件内容（仅文件使用）
};

// 整个模拟器的状态：节点池 + 当前工作目录。
struct Shell {
    std::vector<Node> nodes;  // nodes[0] 是根目录
    int cwd = 0;              // 当前目录的下标

    Shell() {
        Node root;
        root.name = "/";
        root.type = NodeType::Directory;
        root.parent = 0;
        nodes.push_back(root);
    }
};

// TODO: 实现
//   - 路径解析（绝对路径、相对路径、"."、".."；根目录的 ".." 仍是根目录）
//   - mkdir / cd / pwd / ls / touch / cat / echo / tee
//   - "<"、">" 重定向与多级管道，以及它们的错误处理
//
// 命令行为与 ERROR 格式见 README.md。

int main() {
    Shell shell;
    (void)shell;

    // TODO: 从 std::cin 逐行读取命令，直到 "exit" 或输入结束；
    //       对每一行先完整检查组合语法，再从左到右执行。

    return 0;
}
