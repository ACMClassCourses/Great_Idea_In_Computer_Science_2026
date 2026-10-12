#!/usr/bin/env python3

import re
import subprocess
import sys
import unicodedata


MASK = (1 << 64) - 1
STEP = 0x9E3779B97F4A7C15
TIME_LIMIT = 5


def hash64(text):
    value = 14695981039346656037
    for byte in text.encode("ascii"):
        value ^= byte
        value = (value * 1099511628211) & MASK
    return value


def splitmix64(value):
    value = (value + STEP) & MASK
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE4E5B9) & MASK
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & MASK
    return value ^ (value >> 31)


def positions(text, bit_count):
    first = hash64(text)
    return [splitmix64((first + number * STEP) & MASK) % bit_count
            for number in range(4)]


def add(bits, bit_count, text):
    for position in positions(text, bit_count):
        bits[position // 8] |= 1 << (position % 8)


def contains(bits, bit_count, text):
    for position in positions(text, bit_count):
        if bits[position // 8] & (1 << (position % 8)) == 0:
            return False
    return True


def build_filter(addresses, domains):
    bit_count = max(1, (len(addresses) + len(domains)) * 8)
    bits = bytearray((bit_count + 7) // 8)
    for address in addresses:
        add(bits, bit_count, "address:" + address.lower())
    for domain in domains:
        add(bits, bit_count, "domain:" + domain.lower())
    return bits, bit_count


def expected_result(case):
    address_set = {value.lower() for value in case["addresses"]}
    domain_set = {value.lower() for value in case["domains"]}
    trusted_set = {value.lower() for value in case["trusted"]}
    bits, bit_count = build_filter(case["addresses"], case["domains"])
    answers = []
    exact_queries = 0

    for original in case["queries"]:
        email = original.lower()
        domain = email.split("@", 1)[1]
        if email in trusted_set:
            answers.append("Not Spam")
            continue

        maybe_address = contains(bits, bit_count, "address:" + email)
        maybe_domain = contains(bits, bit_count, "domain:" + domain)
        if not maybe_address and not maybe_domain:
            answers.append("Not Spam")
            continue

        exact_queries += 1
        if email in address_set or domain in domain_set:
            answers.append("Spam")
        else:
            answers.append("Not Spam")

    return answers, exact_queries


def make_input(case):
    lines = [
        "%d %d %d" % (
            len(case["addresses"]),
            len(case["domains"]),
            len(case["trusted"]),
        )
    ]
    lines.extend(case["addresses"])
    lines.extend(case["domains"])
    lines.extend(case["trusted"])
    lines.append(str(len(case["queries"])))
    lines.extend(case["queries"])
    return "\n".join(lines) + "\n"


def find_false_positive(addresses, domains):
    bits, bit_count = build_filter(addresses, domains)
    address_set = {value.lower() for value in addresses}
    domain_set = {value.lower() for value in domains}
    for number in range(100000):
        email = "innocent%05d@safe%03d.org" % (number, number % 997)
        domain = email.split("@", 1)[1]
        if email in address_set or domain in domain_set:
            continue
        if (contains(bits, bit_count, "address:" + email)
                or contains(bits, bit_count, "domain:" + domain)):
            return email
    raise RuntimeError("未能构造假阳性测试数据")


def make_cases():
    false_addresses = [
        "blocked%02d@list%02d.com" % (number, number % 7)
        for number in range(20)
    ]
    false_domains = ["deny%02d.net" % number for number in range(10)]
    false_positive = find_false_positive(false_addresses, false_domains)

    large_addresses = [
        "offer%04d@promo%03d.com" % (number, number % 173)
        for number in range(500)
    ]
    large_domains = ["junk%03d.net" % number for number in range(200)]
    large_trusted = [
        "teacher%03d@junk%03d.net" % (number, number)
        for number in range(50)
    ]
    large_queries = []
    for number in range(1000):
        if number % 10 == 0:
            large_queries.append(large_addresses[number % len(large_addresses)])
        elif number % 10 == 1:
            large_queries.append(
                "visitor%04d@junk%03d.net" % (number, number % 200))
        elif number % 10 == 2:
            large_queries.append(large_trusted[number % len(large_trusted)])
        else:
            large_queries.append(
                "friend%04d@safe%03d.org" % (number, number % 251))

    return [
        {
            "name": "空输入",
            "addresses": [], "domains": [], "trusted": [], "queries": [],
        },
        {
            "name": "空黑名单",
            "addresses": [], "domains": [], "trusted": [],
            "queries": ["one@safe.org", "Two@Safe.org", "three@example.com"],
        },
        {
            "name": "地址黑名单",
            "addresses": ["offer@shop.com", "blocked@same.com"],
            "domains": [], "trusted": [],
            "queries": ["OFFER@SHOP.COM", "friend@shop.com", "other@safe.org"],
        },
        {
            "name": "域名与白名单",
            "addresses": [], "domains": ["badmail.com"],
            "trusted": ["Teacher@BadMail.com"],
            "queries": [
                "visitor@BADMAIL.COM", "teacher@badmail.com", "friend@safe.org"
            ],
        },
        {
            "name": "地址域名同时命中",
            "addresses": ["both@blocked.com"], "domains": ["blocked.com"],
            "trusted": [],
            "queries": ["both@blocked.com", "another@blocked.com"],
        },
        {
            "name": "假阳性确认",
            "addresses": false_addresses, "domains": false_domains,
            "trusted": [],
            "queries": [false_positive, false_addresses[0], "clear@outside.org"],
        },
        {
            "name": "较大规模",
            "addresses": large_addresses, "domains": large_domains,
            "trusted": large_trusted, "queries": large_queries,
        },
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


def print_table(headers, rows):
    widths = [display_width(header) for header in headers]
    for row in rows:
        for index, value in enumerate(row):
            widths[index] = max(widths[index], display_width(value))
    separator = "+" + "+".join("-" * (width + 2) for width in widths) + "+"
    print(separator)
    print("|" + "|".join(
        " " + pad_right(header, widths[index]) + " "
        for index, header in enumerate(headers)
    ) + "|")
    print(separator)
    for row in rows:
        print("|" + "|".join(
            " " + (
                pad_right(value, widths[index])
                if index == 0 or index == len(row) - 1
                else pad_left(value, widths[index])
            ) + " "
            for index, value in enumerate(row)
        ) + "|")
    print(separator)


def main():
    if len(sys.argv) != 2:
        print("用法：test.py <application-program>")
        return 2

    rows = []
    failed = False
    for case in make_cases():
        expected_answers, expected_queries = expected_result(case)
        try:
            result = subprocess.run(
                [sys.argv[1]],
                input=make_input(case),
                text=True,
                capture_output=True,
                timeout=TIME_LIMIT,
            )
        except subprocess.TimeoutExpired:
            rows.append([
                case["name"], str(len(case["queries"])), "-", "-", "-", "超时"
            ])
            failed = True
            continue

        lines = result.stdout.splitlines()
        actual_answers = lines[:-1] if lines else []
        count_match = re.fullmatch(r"Exact Queries: (\d+)", lines[-1]) if lines else None
        actual_queries = int(count_match.group(1)) if count_match else -1
        correct = (
            result.returncode == 0
            and actual_answers == expected_answers
            and actual_queries == expected_queries
        )
        failed = failed or not correct
        total = len(case["queries"])
        skipped = total - expected_queries
        reduction = 0.0 if total == 0 else 100.0 * skipped / total
        rows.append([
            case["name"], str(total), str(expected_queries), str(skipped),
            "%.2f%%" % reduction, "通过" if correct else "失败",
        ])

    print("黑名单预筛应用")
    print_table(
        [
            "测试名称", "查询总数", "精确查询数",
            "跳过精确查询数", "减少比例", "结果",
        ],
        rows,
    )
    if failed:
        print("FAIL：最终判断或精确查询次数不正确。")
        return 1
    print("PASS：最终判断全部正确，精确查询次数符合预筛流程。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
