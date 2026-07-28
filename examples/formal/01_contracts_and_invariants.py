# SPDX-FileCopyrightText: Copyright (c) 2026, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# ruff: noqa: E501
"""Demo: method-boundary residual contracts on CodeAct postconditions.

Offline (FakeLLM). No API key.

    uv run python examples/formal/01_contracts_and_invariants.py
"""

from __future__ import annotations

import json

from nooa import Agent, strategy
from nooa.config import CodeActConfig
from nooa.formal import method_boundary_contract
from nooa.strategies.codeact import CodeActStrategy
from nooa.unifiedllm import FakeLLMClient, LLMResponse, ToolCall


def _print_section(title: str) -> None:
    print(f"\n=== {title} ===")


def demo_author_api() -> None:
    _print_section("1. method_boundary_contract API")
    contract = method_boundary_contract(
        str,
        result_predicate=lambda s: "shipping" in s.lower(),
        result_message="result must mention shipping for this task",
        name="analyze",
    )
    print("  hooks:", [getattr(h, "__name__", h) for h in contract.postconditions()])
    print("  CodeActConfig keys:", list(contract.codeact_config_kwargs()))
    info = contract.describe()
    print("  application:", info["application"])
    print("  enforcement:", info["enforcement"])


async def demo_residual_retry() -> None:
    _print_section("2. Residual fails once, then CodeAct retries (FakeLLM)")
    contract = method_boundary_contract(
        str,
        result_predicate=lambda s: "shipping" in s.lower(),
        result_message="result must mention shipping for this task",
        name="analyze",
    )
    cfg = CodeActConfig(postconditions=contract.postconditions())

    def _rr(text: str, cid: str) -> ToolCall:
        return ToolCall(
            id=cid, name="return_result", arguments=json.dumps({"result": text})
        )

    def _resp(calls: list[ToolCall]) -> LLMResponse:
        return LLMResponse(
            raw_response=None,
            content="",
            tool_calls=calls,
            finish_reason="tool_calls",
            assistant_message={"role": "assistant", "content": ""},
        )

    fake = FakeLLMClient(
        scripted_responses=[
            _resp([_rr("Great product overall.", "c1")]),
            _resp([_rr("Great product, but shipping was slow.", "c2")]),
        ]
    )

    class FeedbackAgent(Agent, llm=fake):
        @strategy(CodeActStrategy(config=cfg))
        async def analyze(self, text: str) -> str:
            """Analyze feedback; mention shipping if relevant."""
            ...

    out = await FeedbackAgent().analyze("Great product, but shipping was slow")
    print(f"  final result: {out!r}")
    print(f"  LLM calls (fail + success): {fake.call_count}")
    print("  → residual beyond bare str; same InvariantError channel as production postconditions")


def main() -> None:
    import asyncio

    demo_author_api()
    asyncio.run(demo_residual_retry())
    print("\nDocs: src/nooa/formal/APPLICATION.md | Issue: #41\n")


if __name__ == "__main__":
    main()
