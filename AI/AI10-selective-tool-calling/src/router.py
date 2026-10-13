"""A safe, cost-capped routing baseline for calculator use."""

from __future__ import annotations

import argparse
import ast
import json
import operator
import re
from pathlib import Path


OPERATIONS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
              ast.Div: operator.truediv, ast.Pow: operator.pow}


def calculate(expression: str) -> str:
    def evaluate(node: ast.AST) -> float:
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in OPERATIONS:
            return OPERATIONS[type(node.op)](evaluate(node.left), evaluate(node.right))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -evaluate(node.operand)
        raise ValueError("unsupported expression")
    return str(evaluate(ast.parse(expression, mode="eval").body)).removesuffix(".0")


def needs_calculator(question: str) -> bool:
    return bool(re.search(r"\d", question) and re.search(r"[+*/-]", question))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--budget", type=float, default=0.5)
    parser.add_argument("--output", type=Path, default=Path("outputs/results.jsonl"))
    args = parser.parse_args()
    samples = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line]
    allowance = round(len(samples) * args.budget)
    calls = 0
    results = []
    for sample in samples:
        route = "calculator" if needs_calculator(sample["question"]) and calls < allowance else "direct"
        if route == "calculator":
            calls += 1
            expression = re.search(r"[\d.\s+*/()-]+", sample["question"])[0]
            answer = calculate(expression)
        else:
            answer = "I don't know"
        results.append({**sample, "route": route, "prediction": answer,
                        "correct": answer.strip() == str(sample["answer"]).strip()})
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(json.dumps(row, ensure_ascii=False) for row in results) + "\n", encoding="utf-8")
    print(json.dumps({"accuracy": sum(row["correct"] for row in results) / len(results), "tool_calls": calls}, indent=2))


if __name__ == "__main__":
    main()
