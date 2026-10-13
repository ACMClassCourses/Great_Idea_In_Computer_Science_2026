#!/usr/bin/env python3
"""Selective Tool Calling (Basic) — Safe Calculator & Budgeted Router.
Online Judge submission framework.

An agent answers questions either directly or by calling a tool. This problem
covers the two deterministic cores of that project:

  CALC  -- a whitelist arithmetic calculator (the tool). It must evaluate an
           integer expression or report a structured error, and must NEVER
           eval arbitrary code.
  ROUTE -- an offline-batch router: given a batch of questions, each with a
           precomputed "tool-need score", and a call budget (integer
           percent), choose AT MOST floor(N * b / 100) questions to call the
           tool on, then account for the resulting accuracy and call rate.

Only fill in the two TODO functions below. The I/O parsing, result accounting
and printing in main() are already provided — do NOT modify them.

Run locally:  python3 tool_router.py < input.txt
"""

import math
import sys
from typing import List, Tuple

# Structured error codes the calculator must print (already used by main).
ERR_EMPTY = "ERR_EMPTY"          # empty / whitespace-only expression
ERR_TOO_LONG = "ERR_TOO_LONG"    # raw expression longer than 200 characters
ERR_SYNTAX = "ERR_SYNTAX"        # illegal character, malformed number,
                                 # unbalanced or misplaced parentheses,
                                 # missing operand, trailing operator, ...
ERR_NESTING = "ERR_NESTING"      # parenthesis nesting deeper than 16
ERR_DIV_ZERO = "ERR_DIV_ZERO"    # division by zero
ERR_OVERFLOW = "ERR_OVERFLOW"    # any literal / intermediate / final value
                                 # with absolute value > 10**18

VALUE_LIMIT = 10**18
MAX_LEN = 200
MAX_DEPTH = 16


# TODO 1: The safe calculator.
#
# Evaluate `expr` and return the result AS A STRING: either the decimal
# integer result, or exactly one of the error codes above.
#
# Grammar (expressions follow the usual arithmetic precedence):
#   expr   := term (('+' | '-') term)*
#   term   := factor (('*' | '/') factor)*
#   factor := integer | '(' expr ')' | '-' factor
# Notes on the grammar:
#   - integer literals are non-negative decimal integers (negative numbers
#     arise only via the unary minus); unary minus may repeat ("--3" == 3);
#     unary PLUS is not in the grammar ("1++2" is a syntax error);
#   - spaces and tabs may appear anywhere and carry no meaning;
#   - '+' and '-' are LEFT-associative: 10 - 2 - 3 == (10 - 2) - 3 == 5;
#   - '/' is INTEGER DIVISION TRUNCATING TOWARD ZERO (C semantics):
#     -7/2 == -3 and 7/-2 == -3.  Careful: Python's '//' floors instead
#     (-7//2 == -4) — do not use it directly on negative operands.
#
# Error checking order (check earlier rules first):
#   1. empty/whitespace-only          -> ERR_EMPTY
#   2. raw length > MAX_LEN           -> ERR_TOO_LONG
#   3. anything not matching grammar  -> ERR_SYNTAX
#      (nesting deeper than MAX_DEPTH -> ERR_NESTING, detected while parsing)
#   4. during evaluation, in the order the evaluation reaches them:
#      literal/intermediate/final |value| > VALUE_LIMIT -> ERR_OVERFLOW,
#      division by zero -> ERR_DIV_ZERO.
#
# Security requirement: never use eval()/exec() or shell out. Parse the
# expression yourself.
#
# Hints:
#   - A tiny recursive-descent parser maps one function per grammar rule;
#     that is the classical, readable way to do this. See
#     https://en.wikipedia.org/wiki/Recursive_descent_parser
#   - Think about WHERE whitespace skipping should happen so that every
#     rule gets it for free.
#   - Truncating division on integers: work with abs() and fix the sign.
#   - Python integers never overflow physically — the VALUE_LIMIT check is
#     YOUR job, and intermediate results count too.
def calc(expr: str) -> str:
    # TODO: your code here. Replace the line below.
    return ERR_SYNTAX


# TODO 2: The budgeted offline-batch router.
#
# `items` is a list of (qid, direct_correct, tool_correct, score):
#   qid            -- question id (string)
#   direct_correct -- 1 if the direct answer is right, else 0
#   tool_correct   -- 1 if the tool-assisted answer is right, else 0
#   score          -- the router's tool-need score (integer, 0 <= s <= 10^9),
#                     computed from features available BEFORE calling anything
# `budget_percent` is an integer 0..100.
#
# Return the list of INDICES (into `items`, 0-based) of the questions the
# router decides to call the tool on. Rules:
#   - the call budget is k = floor(N * budget_percent / 100) questions;
#     use integer arithmetic — floats invite rounding bugs (and round()
#     would sometimes EXCEED the budget, which is strictly forbidden);
#   - select the k questions with the highest scores;
#   - ties in score are broken by input order (earlier question wins);
#   - return the selected indices in INCREASING order (main() prints them
#     in that order and then does the accuracy/cost accounting).
#
# Think about (no need to implement):
#   - why the router must not see direct_correct/tool_correct at decision
#     time (here they are only used afterwards, for scoring the decision);
#   - why a question where the tool HURTS (direct 1, tool 0) can still be
#     selected, and what that does to accuracy.
#
# Hint:
#   - https://docs.python.org/3/library/math.html#math.floor  (and why
#     N * budget_percent // 100 is the same thing without floats)
def route(items: List[Tuple[str, int, int, int]], budget_percent: int) -> List[int]:
    # TODO: your code here. Replace the line below.
    return []


# ---------------- provided I/O below — do not modify ----------------

def main() -> None:
    data = sys.stdin.read()
    pos = 0

    def next_line() -> str:
        nonlocal pos
        end = data.index("\n", pos)
        line = data[pos:end]
        pos = end + 1
        return line

    # Section 1: C calculator queries.
    c = int(next_line().strip())
    for _ in range(c):
        # The expression is the REST OF THE LINE, verbatim (may contain
        # spaces, may be empty).
        print(calc(next_line()))

    # Section 2: R routing batches.
    r = int(next_line().strip())
    for _ in range(r):
        n, b = map(int, next_line().split())
        items: List[Tuple[str, int, int, int]] = []
        for _ in range(n):
            qid, d, t, s = next_line().split()
            items.append((qid, int(d), int(t), int(s)))

        chosen = route(items, b)
        chosen_set = set(chosen)
        calls = len(chosen_set)
        correct = sum(
            items[i][2] if i in chosen_set else items[i][1] for i in range(n)
        )
        ids = " ".join(items[i][0] for i in chosen) if chosen else "-"
        print(f"CALL {ids}")
        print(f"RESULT {correct}/{n} {correct / n * 100:.2f}% "
              f"{calls}/{n} {calls / n * 100:.2f}%")


if __name__ == "__main__":
    main()
