"""generator.py — 调用 LLM 生成带引用的回答（TODO 6；stub 后端可离线跑通）。

返回 (answer_text, citation_ids)。Hard 的 Evidence-bound 流程会在调用本函数
之前先拆断言、绑证据。
"""

from __future__ import annotations

import os
import re

from .prompts import build_prompt


def parse_citations(answer: str) -> list[int]:
    """从回答文本中解析 [1] [2] 形式的引用编号（已提供，一般不需修改）。"""
    return sorted({int(m) for m in re.findall(r"\[(\d+)\]", answer)})


def generate(
    prompt: str,
    *,
    backend: str = "stub",
    model: str = "gpt-4o-mini",
    base_url: str = "https://api.openai.com/v1",
    api_key: str = "",
    temperature: float = 0.0,
    max_tokens: int = 512,
) -> tuple[str, list[int]]:
    """TODO 6：调用 LLM，返回 (answer, citation_ids)。

    - backend="stub"：无 API 时离线占位，仅用于打通检索→生成链路（不计入提交结果）；
    - backend="openai" / "ollama"：接入真实模型（见下方 TODO）。
    """
    if backend == "stub":
        cited = sorted({int(i) for i in re.findall(r"\[(\d+)\]", prompt)})
        answer = (
            "（stub 生成）根据提供的证据，参见引用 "
            + " ".join(f"[{i}]" for i in cited)
            + "。"
        )
        return answer, parse_citations(answer)

    # TODO 6（真实 LLM，以 OpenAI 兼容接口为例）：
    # from openai import OpenAI
    # client = OpenAI(base_url=base_url, api_key=api_key or os.environ.get("OPENAI_API_KEY", ""))
    # resp = client.chat.completions.create(
    #     model=model, temperature=temperature, max_tokens=max_tokens,
    #     messages=[{"role": "user", "content": prompt}],
    # )
    # answer = resp.choices[0].message.content
    # return answer, parse_citations(answer)
    raise NotImplementedError("TODO 6: 实现真实 LLM 调用并解析 citation_ids")
