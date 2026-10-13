#!/usr/bin/env python3
"""N-gram Counting and Generation (Basic) — Online Judge submission framework.

A language model can be nothing more than a big counting table: "after this
context of N-1 tokens, which token followed, and how many times?" In this
problem you build such a table from a training corpus (COUNT queries) and
then use it to generate new text by weighted random sampling (GEN queries).

Read the problem statement (Input/Output format) carefully before you start.

Only fill in the three TODO functions below. The I/O parsing and main() are
already provided — do NOT modify them.

Run locally:  python3 ngram.py < 1.in
"""
import random
import sys

START = "<START>"
END = "<END>"


def build_ngram_model(tokens, n):
    """TODO 1: Build the N-gram counting model from the training corpus.

    Args:
        tokens: list of token strings from the corpus (no special symbols;
                padding is YOUR job).
        n:      the N of the N-gram model (1 <= n <= 4).

    Returns:
        A dict mapping a context to its successor counts:
            model[context][token] = number of occurrences
        where `context` is a tuple of exactly n-1 tokens (the empty tuple ()
        when n == 1) and `token` is any token that immediately followed that
        context in the (padded) corpus.

    Requirements:
      - Before counting, pad the corpus with n-1 copies of START at the front
        and exactly one END at the back. For example, with
        tokens = ["我", "爱", "北京", "爱", "你"] and n = 2, the padded
        sequence is  <START> 我 爱 北京 爱 你 <END>  and the resulting model
        must contain:
            ("<START>",)  =  {"我": 1}
            ("爱",)       =  {"北京": 1, "你": 1}
            ("你",)       =  {"<END>": 1}
      - Every maximal window of n consecutive tokens in the padded sequence
        contributes exactly one count: its first n-1 tokens form the context,
        its last token is the counted successor.
      - Do NOT special-case n == 1: with zero padding up front, every context
        is the empty tuple () and the model naturally degenerates into a
        plain unigram frequency table (including END, which appears once).
      - The corpus may be shorter than n, or even empty; the padding rule
        above must still be applied exactly as stated.

    Hints:
      - Think about why we pad n-1 STARTs rather than just one: each real
        sentence position must be predictable from a full-length context.
      - collections.defaultdict and collections.Counter save you from
        "first time seeing this key" checks:
        https://docs.python.org/3/library/collections.html
      - A plain dict of dicts works just as well if you prefer it.
    """
    # TODO: your code here.
    raise NotImplementedError("TODO 1: implement build_ngram_model")


def count_ngram(model, context, w):
    """TODO 2: Answer one COUNT query against the model.

    Args:
        model:   the dict returned by build_ngram_model.
        context: a tuple of exactly n-1 tokens (() when n == 1).
        w:       the queried successor token (a string).

    Returns:
        The number of times token `w` immediately followed `context` in the
        padded training corpus. Return 0 if the context never occurred, or if
        the context occurred but was never followed by `w`.

    Requirements:
      - Never modify the model while answering a query. In particular, beware
        that indexing a collections.defaultdict with a missing key silently
        CREATES an entry — later GEN queries would then see a phantom empty
        context. Prefer a lookup style that leaves absent keys absent.
      - Queries involving START/END are legal and must be answered from the
        table like any other token (e.g. with n == 2, COUNT <START> 我 asks
        how often 我 opened the corpus).
    """
    # TODO: your code here.
    raise NotImplementedError("TODO 2: implement count_ngram")


def generate_text(model, n, length, seed):
    """TODO 3: Generate up to `length` tokens by weighted random sampling.

    Args:
        model:  the dict returned by build_ngram_model.
        n:      the N the model was built with.
        length: maximum number of tokens to generate (>= 1).
        seed:   integer seed for the random number generator.

    Returns:
        The list of generated tokens, NOT including START or END. It may be
        empty (if END is sampled on the very first step).

    The sampling rule below is part of the problem statement — follow it
    exactly, otherwise your output will not be reproducible:

      1. Create a private generator:  rng = random.Random(seed).
         (Do NOT touch the global random module state.)
      2. Start from context = (START,) * (n - 1).
      3. At each step, look up the current context in the model.
         - The candidate list is ALL successor tokens of this context,
           sorted by Python's default string ordering (i.e. by Unicode code
           points; sorted(counter) does this).
         - The weight of each candidate is its integer count, in the same
           order as the sorted candidate list.
         - Draw the next token with exactly:
               rng.choices(candidates, weights=counts, k=1)[0]
      4. If the drawn token is END, stop immediately (END is not emitted).
      5. Otherwise append the token to the result, slide the window forward
         (the new context is the last n-1 tokens of old context + new token),
         and continue.
      6. Stop after `length` emitted tokens at the latest. If the current
         context is absent from the model (should not normally happen),
         stop as well.

    Hints:
      - random.Random / random.choices documentation:
        https://docs.python.org/3/library/random.html
      - Debug with a deterministic corpus first: with tokens = ["x", "y", "z"]
        and n = 2 every context has exactly one successor, so any seed must
        generate exactly ["x", "y", "z"] (then stop at END).
      - Same seed + same model must always give the same output. If yours
        doesn't, check the sorting of the candidate list — dict iteration
        order is NOT what the rule asks for.
    """
    # TODO: your code here.
    raise NotImplementedError("TODO 3: implement generate_text")


# ---------------- provided I/O below — do not modify ----------------

def main():
    readline = sys.stdin.readline

    first = readline().split()
    n, q = int(first[0]), int(first[1])
    tokens = readline().split()  # may be an empty corpus (empty line)

    model = build_ngram_model(tokens, n)

    out_lines = []
    for _ in range(q):
        parts = readline().split()
        if parts[0] == "COUNT":
            # COUNT c1 ... c_{n-1} w   (COUNT w when n == 1)
            context = tuple(parts[1:n])
            w = parts[n]
            out_lines.append(str(count_ngram(model, context, w)))
        else:  # GEN L seed
            length, seed = int(parts[1]), int(parts[2])
            out_lines.append(" ".join(generate_text(model, n, length, seed)))

    sys.stdout.write("\n".join(out_lines) + "\n")


if __name__ == "__main__":
    main()
