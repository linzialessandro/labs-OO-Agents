# SPDX-FileCopyrightText: Copyright (c) 2026, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Concrete application: method_boundary_contract on real CodeAct hooks."""

from __future__ import annotations

import json

import pytest

from nooa import Agent, strategy
from nooa.config import CodeActConfig
from nooa.formal.application import (
    MethodBoundaryContract,
    method_boundary_contract,
    method_boundary_postconditions,
)
from nooa.strategies.codeact import CodeActStrategy
from nooa.strategy_validation import InvariantError, run_postconditions
from nooa.unifiedllm import FakeLLMClient, LLMResponse, ToolCall


def _rr(result: object, call_id: str = "c1") -> ToolCall:
    return ToolCall(
        id=call_id, name="return_result", arguments=json.dumps({"result": result})
    )


def _resp(calls: list[ToolCall]) -> LLMResponse:
    return LLMResponse(
        raw_response=None,
        content="",
        tool_calls=calls,
        finish_reason="tool_calls",
        assistant_message={"role": "assistant", "content": ""},
    )


def test_empty_contract_raises():
    with pytest.raises(ValueError, match="empty"):
        MethodBoundaryContract().postconditions()


def test_result_predicate_raises_via_run_postconditions():
    """Shipped postconditions + production run_postconditions path."""
    contract = method_boundary_contract(
        str,
        result_predicate=lambda s: "ok" in s,
        result_message="must contain ok",
    )
    with pytest.raises(InvariantError, match="must contain ok"):
        run_postconditions(object(), "bad", object(), contract.postconditions())


def test_describe_theory_optional():
    c = method_boundary_contract(str, result_predicate=lambda s: True, name="analyze")
    d = c.describe_theory()
    assert d["application"] == "method_boundary_residual_contract"
    assert d["enforcement"].startswith("InvariantError")
    assert d["name"] == "analyze"
    assert d["residuals"]["result_predicate"] is True


@pytest.mark.asyncio
async def test_method_boundary_retry_on_real_codeact():
    """Failing residual → InvariantError → CodeAct retries; then success."""
    posts = method_boundary_postconditions(
        str,
        result_predicate=lambda s: isinstance(s, str) and "shipping" in s.lower(),
        result_message="result must mention shipping",
        name="analyze",
    )
    cfg = CodeActConfig(postconditions=posts)

    class Ag(Agent, llm=FakeLLMClient()):
        @strategy(CodeActStrategy(config=cfg))
        async def analyze(self, text: str) -> str:
            """Analyze feedback."""
            ...

    fake = FakeLLMClient(
        scripted_responses=[
            _resp([_rr("Great product overall.", "c1")]),
            _resp([_rr("Great product, but shipping was slow.", "c2")]),
        ]
    )
    out = await Ag(llm=fake).analyze("Great product, but shipping was slow")
    assert "shipping" in out.lower()
    assert fake.call_count == 2


def test_field_messages_surface_via_run_postconditions():
    """Custom field_messages must be the InvariantError text (not generic AtomicField).

    Regression: agent_fields used to be compiled into as_postcondition first;
    run_postconditions stopped on the generic message and never reached
    method_boundary_field_* hooks.
    """
    custom = "agent.ready must be True before accepting result"
    posts = method_boundary_postconditions(
        str,
        agent_fields={"ready": lambda v: v is True},
        field_messages={"ready": custom},
        name="finish",
    )

    class Ag:
        ready = False

    with pytest.raises(InvariantError, match="agent.ready must be True before accepting") as ei:
        run_postconditions(Ag(), "done", object(), posts)
    # Must be the author message, not as_postcondition's structure does not satisfy…
    assert custom in str(ei.value)
    assert "does not satisfy" not in str(ei.value)


def test_field_messages_default_when_omitted():
    posts = method_boundary_postconditions(
        agent_fields={"flag": lambda v: v is True},
        name="x",
    )

    class Ag:
        flag = False

    with pytest.raises(InvariantError, match=r"agent\.flag failed residual"):
        run_postconditions(Ag(), "done", object(), posts)


@pytest.mark.asyncio
async def test_method_boundary_agent_field_ok_on_codeact():
    posts = method_boundary_postconditions(
        str,
        agent_fields={"ready": lambda v: v is True},
        field_messages={"ready": "agent.ready must be True before accepting result"},
        name="finish",
    )
    cfg = CodeActConfig(postconditions=posts)

    class Ag(Agent, llm=FakeLLMClient()):
        ready: bool = False

        @strategy(CodeActStrategy(config=cfg))
        async def finish(self, q: str) -> str:
            """Finish."""
            ...

    fake_ok = FakeLLMClient(scripted_responses=[_resp([_rr("done")])])
    agent_ok = Ag(llm=fake_ok)
    agent_ok.ready = True
    assert await agent_ok.finish("q") == "done"


@pytest.mark.asyncio
async def test_field_message_retry_on_real_codeact():
    """Custom field_messages text participates in CodeAct InvariantError retry.

    First return fails residual (ready False); second evaluation of the same
    field predicate passes (count-based stand-in for state fixed mid-run).
    """
    custom = "set agent.ready=True before return_result"
    count = {"n": 0}

    def _counting_ready(v: object) -> bool:
        count["n"] += 1
        if count["n"] >= 2:
            return True
        return bool(v)

    posts = method_boundary_postconditions(
        str,
        agent_fields={"ready": _counting_ready},
        field_messages={"ready": custom},
        name="finish",
    )
    cfg = CodeActConfig(postconditions=posts)

    class Ag(Agent, llm=FakeLLMClient()):
        ready: bool = False

        @strategy(CodeActStrategy(config=cfg))
        async def finish(self, q: str) -> str:
            """Finish."""
            ...

    fake = FakeLLMClient(
        scripted_responses=[
            _resp([_rr("first", "c1")]),
            _resp([_rr("second", "c2")]),
        ]
    )
    out = await Ag(llm=fake).finish("q")
    assert out == "second"
    assert fake.call_count == 2
    assert count["n"] >= 2


@pytest.mark.asyncio
async def test_codeact_config_kwargs_merge():
    contract = method_boundary_contract(
        str,
        result_predicate=lambda s: len(s) > 0,
        result_message="non-empty",
    )
    cfg = CodeActConfig(**contract.codeact_config_kwargs())
    assert len(cfg.postconditions) >= 1

    class Ag(Agent, llm=FakeLLMClient()):
        @strategy(CodeActStrategy(config=cfg))
        async def go(self, x: str) -> str:
            """Go."""
            ...

    fake = FakeLLMClient(scripted_responses=[_resp([_rr("x")])])
    assert await Ag(llm=fake).go("a") == "x"
