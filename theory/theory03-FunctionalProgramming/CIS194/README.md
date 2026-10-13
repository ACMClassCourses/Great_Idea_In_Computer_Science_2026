# 函数式编程

这个项目二次改编自宾夕法尼亚大学的经典课程 CIS 194。其中，你需要通过完成编程作业，体会函数式编程的基本思想。

本项目使用 Haskell 作为程序设计语言，如果你之前没有接触过，你需要先进行集成开发环境（IDE）配置。推荐使用 VsCode 和 Haskell 插件开发，GHCup 管理 Haskell 编译器。安装 GHCup 的时候，推荐使用国内镜像源。

在完成环境配置之后，进入项目跟目录。项目根目录下，存在 `pdfs` 文件夹放置教学资料，`src` 放置作业代码，`test` 放置测试代码，根目录下还有一些其他辅助文件。

在项目根目录执行 `stack init` 进行项目初始化，此过程可能需要花费 30 分钟，你可以通过在 VsCode 中打开任意一个 `.hs` 文件同时初始化 IDE。如果成功，运行 `stack test`，你应该能看到每个测试是否通过，此后 stack 会报出错误 `Test suite failure for package cis194-0.1.0.0`，这是正常现象。然后运行 `stack test --file-watch --test-arguments '-m toDigits/'`，应该能看到第一次作业的 `toDigits` 函数的三个测试，并且进入测试循环，输入 `quit` 可以退出。你可以类似地进行后续测试。注意，`-m` 匹配的是 `*Spec.hs` 里 `describe` 后面跟的名字。
