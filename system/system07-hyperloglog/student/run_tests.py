#!/usr/bin/env python3
from __future__ import annotations

import argparse
import math
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / ".test_build"


def fail(message: str) -> None:
    print(f"\n[FAIL] {message}")
    raise SystemExit(1)


def compile_target(target: str) -> Path:
    gxx = shutil.which("g++")
    if not gxx:
        fail("未找到 g++。请先安装支持 C++17 的编译器。")

    src_dir = ROOT / target
    sources = sorted(
        p for p in src_dir.rglob("*.cpp")
        if "tests" not in p.parts and ".test_build" not in p.parts
    )
    if not sources:
        fail(f"{target}/ 下没有找到 .cpp 文件。请把你的实现放在该目录中。")

    BUILD.mkdir(exist_ok=True)
    exe = BUILD / target
    cmd = [
        gxx, "-std=c++17", "-O2", "-Wall", "-Wextra", "-pedantic",
        *map(str, sources), "-o", str(exe),
    ]
    print(f"[build] {target}: {len(sources)} 个源文件")
    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.returncode != 0:
        print(result.stdout, end="")
        print(result.stderr, end="")
        fail(f"{target} 编译失败。")
    return exe


def run_case(exe: Path, input_path: Path, timeout: float = 8.0) -> list[str]:
    try:
        result = subprocess.run(
            [str(exe)],
            input=input_path.read_text(encoding="utf-8"),
            text=True,
            capture_output=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        fail(f"{input_path.name} 运行超时。")

    if result.returncode != 0:
        print(result.stderr, end="")
        fail(f"{input_path.name} 程序异常退出，返回码 {result.returncode}。")

    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def expected_lines(output_path: Path) -> list[str]:
    return [line.strip() for line in output_path.read_text(encoding="utf-8").splitlines() if line.strip()]


def first_difference(actual: list[str], expected: list[str]):
    length = min(len(actual), len(expected))
    for i in range(length):
        if actual[i] != expected[i]:
            return i, actual[i], expected[i]
    if len(actual) != len(expected):
        i = length
        a = actual[i] if i < len(actual) else "<缺失>"
        e = expected[i] if i < len(expected) else "<不应有额外输出>"
        return i, a, e
    return None


def run_exact_tests(target: str, exe: Path) -> None:
    test_dir = ROOT / target / "tests" / "exact"
    cases = sorted(test_dir.glob("*.in"))
    print(f"\n[{target}] 必须精确通过的测试：{len(cases)} 个")
    for input_path in cases:
        output_path = input_path.with_suffix(".out")
        actual = run_case(exe, input_path)
        expected = expected_lines(output_path)
        diff = first_difference(actual, expected)
        if diff is not None:
            line_no, got, want = diff
            print(f"  ✗ {input_path.stem}")
            print(f"    第 {line_no + 1} 个输出错误")
            print(f"    expected: {want}")
            print(f"    actual:   {got}")
            fail("遇到第一个确定性错误，测试已停止。请先修复这个测试点。")
        print(f"  ✓ {input_path.stem}")


def relative_error(actual: int, truth: int) -> float:
    if truth == 0:
        return 0.0 if actual == 0 else math.inf
    return abs(actual - truth) / truth


def run_quality_tests(target: str, exe: Path) -> list[float]:
    test_dir = ROOT / target / "tests" / "quality"
    cases = sorted(test_dir.glob("*.in"))
    all_errors: list[float] = []
    print(f"\n[{target}] 近似质量测试：{len(cases)} 个")
    print("这些测试不会因为误差较大而提前停止；.out 中保存的是真实基数。")

    for input_path in cases:
        output_path = input_path.with_suffix(".out")
        actual_text = run_case(exe, input_path, timeout=15.0)
        truth_text = expected_lines(output_path)
        if len(actual_text) != len(truth_text):
            fail(
                f"{input_path.stem} 输出数量错误：应有 {len(truth_text)} 行，"
                f"实际 {len(actual_text)} 行。"
            )

        errors: list[float] = []
        for index, (got, want) in enumerate(zip(actual_text, truth_text), start=1):
            try:
                actual = int(got)
                truth = int(want)
            except ValueError:
                fail(f"{input_path.stem} 第 {index} 行不是整数输出。")
            if actual < 0:
                fail(f"{input_path.stem} 第 {index} 行输出了负数。")
            errors.append(relative_error(actual, truth))

        all_errors.extend(errors)
        mean = sum(errors) / len(errors) if errors else 0.0
        worst = max(errors) if errors else 0.0
        print(
            f"  • {input_path.stem:<24} "
            f"mean={mean * 100:7.3f}%  max={worst * 100:7.3f}%  "
            f"queries={len(errors)}"
        )

    if all_errors:
        mean = sum(all_errors) / len(all_errors)
        worst = max(all_errors)
        print(f"  -> 合计 mean={mean * 100:.3f}%  max={worst * 100:.3f}%")
    return all_errors


def write_line(pipe, text: str) -> None:
    pipe.write(text)
    pipe.write("\n")


def run_hard_stress(exe: Path) -> None:
    # 这个测试不落盘。每个时间桶由一组全局重复用户和一组桶内独有用户构成，
    # 因而窗口真值可以直接由公式计算，不需要测试器维护巨大的 set。
    buckets = 160
    global_users = 600
    local_users = 700
    query_every = 20
    windows = (1, 8, 32, 64, 128)

    expected: list[int] = []
    print("\n[hard] 在线压力测试（不生成巨大输入文件）")
    print(
        f"  buckets={buckets}, 每桶 distinct≈{global_users + local_users}, "
        f"ADD≈{buckets * (global_users + local_users):,}"
    )

    start = time.perf_counter()
    proc = subprocess.Popen(
        [str(exe)], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, bufsize=1,
    )
    assert proc.stdin is not None

    try:
        for t in range(buckets):
            for i in range(global_users):
                write_line(proc.stdin, f"ADD {t} {1_000_000 + i}")
            local_base = 10_000_000_000 + t * 1_000_000
            for i in range(local_users):
                write_line(proc.stdin, f"ADD {t} {local_base + i}")
            # 少量重复请求，验证重复元素不会改变基数。
            for i in range(20):
                write_line(proc.stdin, f"ADD {t} {1_000_000 + i}")

            if (t + 1) % query_every == 0:
                for window in windows:
                    if window <= t + 1:
                        write_line(proc.stdin, f"QUERY {t} {window}")
                        expected.append(global_users + local_users * window)
        write_line(proc.stdin, "QUIT")
        proc.stdin.close()
        stdout = proc.stdout.read() if proc.stdout else ""
        stderr = proc.stderr.read() if proc.stderr else ""
        code = proc.wait(timeout=25)
    except (BrokenPipeError, subprocess.TimeoutExpired):
        proc.kill()
        fail("在线压力测试运行失败或超时。")

    if code != 0:
        print(stderr, end="")
        fail(f"在线压力测试程序异常退出，返回码 {code}。")

    outputs = [line.strip() for line in stdout.splitlines() if line.strip()]
    if len(outputs) != len(expected):
        fail(f"在线压力测试应输出 {len(expected)} 行，实际 {len(outputs)} 行。")

    errors: list[float] = []
    for i, (got, truth) in enumerate(zip(outputs, expected), start=1):
        try:
            actual = int(got)
        except ValueError:
            fail(f"在线压力测试第 {i} 个输出不是整数。")
        errors.append(relative_error(actual, truth))

    elapsed = time.perf_counter() - start
    mean = sum(errors) / len(errors) if errors else 0.0
    worst = max(errors) if errors else 0.0
    print(f"  mean error={mean * 100:.3f}%  max error={worst * 100:.3f}%")
    print(f"  wall time={elapsed:.3f}s")
    print("  注：本地压力测试只用于自查；正式大规模评测的数据范围和资源限制见 README。")


def run_target(target: str, stress: bool) -> None:
    exe = compile_target(target)
    run_exact_tests(target, exe)
    run_quality_tests(target, exe)
    if target == "hard" and stress:
        run_hard_stress(exe)
    print(f"\n[PASS] {target} 的必须精确测试全部通过。")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="编译并运行 Hard 时间窗口任务的公开测试。Basic 请在 OJ 提交。"
    )
    parser.add_argument("target", choices=["hard"])
    parser.add_argument(
        "--stress", action="store_true",
        help="Hard 额外运行在线生成的中等规模压力测试。",
    )
    args = parser.parse_args()

    run_target("hard", args.stress)


if __name__ == "__main__":
    main()
