"""大模型回复的解析工具。

修复前：7 处用 `re.search(r'\\{[\\s\\S]*\\}', response)` 从回复里抠 JSON。
这个正则是贪婪的，会从第一个 `{` 一直吃到最后一个 `}`；只要模型在 JSON
前后写了带花括号的说明文字，切出来的片段就不是合法 JSON，解析直接失败，
然后落到硬编码的兜底假报告上。
"""

import json
import logging
import re

logger = logging.getLogger("interview.llm")

_FENCE = re.compile(r"```(?:json)?\s*(.*?)```", re.DOTALL | re.IGNORECASE)


def _balanced_slices(text, opening="{", closing="}"):
    """依次产出所有括号配平的顶层片段，跳过字符串字面量里的括号。

    必须遍历全部候选而不是只取第一个：模型常写「例如 {占位} 这样」这类
    带花括号的说明文字，第一个配平片段可能只是散文里的括号。
    """
    depth = 0
    start = -1
    in_string = False
    escaped = False
    for i, ch in enumerate(text):
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            if depth > 0:
                in_string = True
        elif ch == opening:
            if depth == 0:
                start = i
            depth += 1
        elif ch == closing:
            if depth > 0:
                depth -= 1
                if depth == 0 and start != -1:
                    yield text[start:i + 1]
                    start = -1


def _balanced_slice(text, opening="{", closing="}"):
    for chunk in _balanced_slices(text, opening, closing):
        return chunk
    return None


def extract_json(response, expect=dict):
    """从模型回复里取出 JSON 对象；取不到或不合法时返回 None。

    调用方必须处理 None —— 不要再用编造的默认内容顶上去。
    """
    if not response:
        return None
    if isinstance(response, (dict, list)):
        return response if isinstance(response, expect) else None

    text = str(response).strip()

    candidates = []
    fenced = _FENCE.search(text)
    if fenced:
        candidates.append(fenced.group(1).strip())
    candidates.append(text)
    # 所有配平片段都试一遍，取第一个能解析成目标类型的
    candidates.extend(_balanced_slices(text, "{", "}"))
    candidates.extend(_balanced_slices(text, "[", "]"))

    for candidate in candidates:
        if not candidate:
            continue
        try:
            parsed = json.loads(candidate)
        except (ValueError, TypeError):
            continue
        if isinstance(parsed, expect):
            return parsed

    logger.warning("无法从模型回复中解析 JSON，前 120 字: %s", text[:120])
    return None
