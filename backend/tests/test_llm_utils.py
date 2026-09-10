"""extract_json 的单元测试。

修复前用 re.search(r'\{[\s\S]*\}', response) 从模型回复里抠 JSON：
贪婪匹配，会从第一个 { 一直吃到最后一个 }，模型只要在 JSON 前后写了
带花括号的说明文字，解析就失败，然后落到硬编码的兜底假报告上。
"""

import pytest

from llm_utils import extract_json


@pytest.mark.parametrize(
    "raw, expected",
    [
        ('{"a": 1}', {"a": 1}),
        ('```json\n{"a": 2}\n```', {"a": 2}),
        ('```\n{"a": 3}\n```', {"a": 3}),
        ('好的，结果如下：\n{"a": 4}\n以上。', {"a": 4}),
        # 关键回归：散文里出现花括号
        ('例如 {占位} 这样。\n{"a": 5}\n注意 {另一个}', {"a": 5}),
        ('text {"a": {"b": [1,2]}} tail', {"a": {"b": [1, 2]}}),
        ('{"a": "值里有 } 括号", "b": 6}', {"a": "值里有 } 括号", "b": 6}),
        ('{不是json} 然后 {"ok": true}', {"ok": True}),
        ({"passthrough": 1}, {"passthrough": 1}),
    ],
)
def test_能解析出JSON(raw, expected):
    assert extract_json(raw) == expected


@pytest.mark.parametrize("raw", ["这里根本没有 json", "", None, "   ", "{未闭合"])
def test_解析不出时返回None(raw):
    assert extract_json(raw) is None


def test_旧的贪婪正则在同样输入上会失败():
    """留作对照，说明这次修复解决的是什么。"""
    import json
    import re

    raw = '例如 {占位} 这样。\n{"a": 5}\n注意 {另一个}'
    match = re.search(r"\{[\s\S]*\}", raw)
    with pytest.raises(json.JSONDecodeError):
        json.loads(match.group())

    assert extract_json(raw) == {"a": 5}
