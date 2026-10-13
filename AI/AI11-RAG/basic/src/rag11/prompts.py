"""prompts.py — 生成用的 prompt 模板（通常无需修改）。"""

RAG_PROMPT = """\
你是一个严谨的问答助手。请只根据下面提供的【证据】回答问题，并严格遵守要求。

【证据】
{contexts}

【问题】
{question}

【要求】
1. 每个事实性断言都必须用 [i] 标注其依据的证据编号（i 对应上面的证据序号，从 1 开始）。
2. 如果证据不足以回答问题，请明确说明“根据提供的证据无法回答”，不要编造。
3. 不要输出证据之外的额外信息。

【回答】
"""


def build_prompt(question: str, contexts: list[str]) -> str:
    """把证据与问题拼成最终 prompt（已提供，一般不需修改）。"""
    numbered = "\n".join(f"[{i + 1}] {c}" for i, c in enumerate(contexts))
    return RAG_PROMPT.format(contexts=numbered, question=question)
