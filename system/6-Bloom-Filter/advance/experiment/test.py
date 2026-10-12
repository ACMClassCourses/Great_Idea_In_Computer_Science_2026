#!/usr/bin/env python3

import subprocess
import sys
import unicodedata


EXPECTED_FALSE_POSITIVES = [
    2259, 1583, 2855,
    1236, 216, 251,
    818, 60, 36,
    23, 239, 1583, 5812,
]


def display_width(text):
    width = 0
    for character in text:
        if unicodedata.east_asian_width(character) in ("W", "F"):
            width += 2
        else:
            width += 1
    return width


def pad_left(text, width):
    return " " * (width - display_width(text)) + text


def pad_right(text, width):
    return text + " " * (width - display_width(text))


def print_table(title, headers, rows):
    widths = [display_width(header) for header in headers]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], display_width(value))

    separator = "+" + "+".join("-" * (width + 2) for width in widths) + "+"
    print(title)
    print(separator)
    print("|" + "|".join(
        " " + pad_right(header, widths[index]) + " "
        for index, header in enumerate(headers)
    ) + "|")
    print(separator)
    for row in rows:
        print("|" + "|".join(
            " " + pad_left(value, widths[index]) + " "
            for index, value in enumerate(row)
        ) + "|")
    print(separator)


def main():
    if len(sys.argv) != 2:
        print("用法：test.py <experiment-program>")
        return 2

    result = subprocess.run(
        [sys.argv[1]],
        text=True,
        capture_output=True,
        timeout=10,
    )
    if result.returncode != 0:
        print(f"实验程序运行失败，退出码 {result.returncode}。")
        return 1

    lines = result.stdout.splitlines()
    expected_header = (
        "group,n,m,k,string_bytes,bloom_bytes,negative_queries,"
        "false_positives,false_positive_rate,false_negatives"
    )
    if len(lines) != 14 or lines[0] != expected_header:
        print("实验输出的行数或表头错误。")
        return 1

    parameter_pairs = set()
    saturation_counts = set()
    actual_false_positives = []
    parameter_rows = []
    saturation_rows = []

    for line in lines[1:]:
        fields = line.split(",")
        if len(fields) != 10:
            print("实验输出的列数错误。")
            return 1

        group = fields[0]
        n = int(fields[1])
        m = int(fields[2])
        hashes = int(fields[3])
        string_bytes = int(fields[4])
        bloom_bytes = int(fields[5])
        negative_queries = int(fields[6])
        false_positives = int(fields[7])
        rate = float(fields[8])
        false_negatives = int(fields[9])

        if string_bytes != n * 29:
            print("字符串内容字节数错误。")
            return 1
        if bloom_bytes != (m + 7) // 8:
            print("内存代理报告的字节数错误。")
            return 1
        if negative_queries != 10000 or false_negatives != 0:
            print("查询数量或假阴性数量错误。")
            return 1
        expected_rate = 100.0 * false_positives / negative_queries
        if abs(rate - expected_rate) > 0.0001:
            print("假阳性率计算错误。")
            return 1

        actual_false_positives.append(false_positives)
        if group == "parameters":
            parameter_pairs.add((m // n, hashes))
            parameter_rows.append([
                str(m // n), str(n), str(m), str(hashes),
                str(string_bytes), str(bloom_bytes), str(false_positives),
                f"{rate:.4f}%", str(false_negatives),
            ])
        elif group == "saturation":
            saturation_counts.add(n)
            saturation_rows.append([
                str(n), str(m), str(hashes), str(bloom_bytes),
                str(false_positives), f"{rate:.4f}%", str(false_negatives),
            ])
        else:
            print("实验分组名称错误。")
            return 1

    expected_pairs = {
        (bits, hashes)
        for bits in (4, 8, 12)
        for hashes in (1, 4, 8)
    }
    if parameter_pairs != expected_pairs:
        print("参数组合不完整。")
        return 1
    if saturation_counts != {500, 1000, 2000, 4000}:
        print("饱和实验不完整。")
        return 1
    if actual_false_positives != EXPECTED_FALSE_POSITIVES:
        print("固定数据下的假阳性数量与参考答案不一致。")
        return 1

    print_table(
        "参数对比",
        [
            "每元素位数", "元素数 n", "位数 m", "哈希数 k",
            "字符串/字节", "布隆过滤器/字节", "假阳性数", "假阳性率",
            "假阴性数",
        ],
        parameter_rows,
    )
    print()
    print_table(
        "饱和实验（m=8000, k=4）",
        [
            "元素数 n", "位数 m", "哈希数 k", "布隆过滤器/字节",
            "假阳性数", "假阳性率", "假阴性数",
        ],
        saturation_rows,
    )
    print()
    print("PASS：存储、哈希、9 组参数实验和 4 组饱和实验均正确。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
