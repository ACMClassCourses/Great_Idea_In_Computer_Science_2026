#!/usr/bin/env python3
"""
DFA Simulator -- Project 17 (Finite State Machine to Regular Expression).

A deterministic finite automaton (DFA) over the binary alphabet: {'0', '1'}
is described in the input, followed by several binary strings ("words").
For each word, decide whether the DFA accepts it.

This is the general version of Experiments 1 & 2 in the project README:
there you hand-designed machines for specific jobs (divisible-by-3,
ends-with-01); here the machine itself is part of the input.

=== Input format ===
Line 1:        n s k
               n = number of states, labeled 0 .. n-1
               s = the start state
               k = number of accepting states
Line 2:        k integers, the accepting states (an EMPTY line when k = 0)
Next n lines:  line i+3 holds two integers "z o", meaning:
               state i moves to state z on input '0', and to o on input '1'
Next line:     q, the number of query words
Next q lines:  one binary word per line.  A word may be EMPTY (the line is
               then empty); the empty word stands for the empty string.

=== Output format ===
For each query word print exactly one line:
"YES" if the DFA accepts the word, "NO" otherwise.

=== Limits ===
1 <= n <= 1000, 0 <= s < n, 0 <= k <= n, 1 <= q <= 100000,
0 <= len(word) <= 10^6, total length of all words <= 2 * 10^6.
The transition table is complete: every state has both a '0'-edge and
a '1'-edge, so you never meet an undefined transition.

Everything is already wired up except the two TODOs below.
Background reading: https://en.wikipedia.org/wiki/Deterministic_finite_automaton
"""

import sys


def build_dfa(n, start, accept_list, trans_rows):
    """TODO 1: turn the raw parsed data into your own DFA representation.

    Parameters
    ----------
    n : int
        Number of states, labeled 0 .. n-1.
    start : int
        The start state.
    accept_list : list[int]
        The accepting states; may be empty (then nothing is accepted).
    trans_rows : list[tuple[int, int]]
        trans_rows[i] = (z, o) means state i moves to z on '0', to o on '1'.

    Returns
    -------
    Whatever you choose -- the return value is passed straight to
    `simulate` as its `dfa` argument, so the representation is entirely
    up to you.  A natural choice is a tuple (start, accepts, trans).

    Hints (things to think about, not a recipe):
      * You will test "is this state accepting?" once per word, and
        "where do I go from this state on this bit?" once per character.
        Which built-in data structures make those two operations O(1)?
      * States are already numbered 0 .. n-1.  A list indexed by the
        state number is the simplest possible transition table.
      * For up to 2 * 10^6 input characters, the per-character work
        decides whether you finish in time.
    """
    # TODO: build and return your DFA representation.
    raise NotImplementedError("TODO 1: build_dfa")


def simulate(dfa, word):
    """TODO 2: run the DFA on one word; return True iff the word is accepted.

    Parameters
    ----------
    dfa : whatever your `build_dfa` returned.
    word : str
        Consists only of characters '0' and '1'.  It may be EMPTY (the
        empty string): then the machine reads nothing and stays in the
        start state, so the word is accepted exactly when the start
        state is an accepting state.  Make sure your code handles this
        without special-case crashes.

    Returns
    -------
    bool -- True if, after reading the whole word, the machine ends in
    an accepting state; False otherwise.

    Hints:
      * Keep the current state in a single variable; for each character,
        replace it with the successor state.  Never convert the word to
        an integer -- a real automaton cannot look back or "jump".
      * To see the classic example, hand-simulate the 3-state machine of
        test point 1 and watch why "current remainder mod 3" is all the
        information a state ever needs to remember.
    """
    # TODO: simulate the DFA on `word`.
    raise NotImplementedError("TODO 2: simulate")


def main():
    lines = sys.stdin.read().split("\n")
    pos = 0

    n, s, k = map(int, lines[pos].split())
    pos += 1

    accept_list = []
    if k > 0:
        accept_list = list(map(int, lines[pos].split()))
    pos += 1

    trans_rows = []
    for _ in range(n):
        z, o = map(int, lines[pos].split())
        pos += 1
        trans_rows.append((z, o))

    q = int(lines[pos])
    pos += 1
    words = [w.strip() for w in lines[pos:pos + q]]

    dfa = build_dfa(n, s, accept_list, trans_rows)
    out = []
    for w in words:
        out.append("YES" if simulate(dfa, w) else "NO")
    sys.stdout.write("\n".join(out) + "\n")


if __name__ == "__main__":
    main()
