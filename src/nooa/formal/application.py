# SPDX-FileCopyrightText: Copyright (c) 2026, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Concrete author-facing application: method-boundary residual contracts.

Why this exists
---------------
NOOA already validates return *types* and supports
``CodeActConfig(postconditions=[...])`` with ``InvariantError`` → model-correctable
retry (see ``strategy_validation`` and ARC's WAIT-requires-submission pattern).

What authors still lack is a **one-call way** to attach *residual* obligations
that types alone cannot express, without hand-rolling checkers each time:

* "string result must mention X"
* "if kind is WAIT, agent.submitted_turn must match"
* "result.evidence must be non-empty"

This module is that application — pure harness hooks, no formal-theory layer.

Usage (copy-paste)::

    from nooa import Agent, strategy
    from nooa.config import CodeActConfig
    from nooa.formal import method_boundary_contract
    from nooa.strategies import CodeActStrategy

    contract = method_boundary_contract(
        str,
        result_predicate=lambda s: "shipping" in s.lower(),
        result_message="result must mention shipping for this task",
    )

    class FeedbackAgent(Agent, llm=llm):
        @strategy(CodeActStrategy(config=CodeActConfig(
            postconditions=contract.postconditions(),
        )))
        async def analyze(self, text: str) -> str:
            \"\"\"Analyze feedback.\"\"\"
            ...
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from typing import Any

from nooa.strategy_validation import InvariantError

ResultPredicate = Callable[[Any], bool]
FieldPredicate = Callable[[Any], bool]


def _value_matches_type(value: Any, ty: type | Any) -> bool:
    """Best-effort type check aligned with common harness return types."""
    if ty is Any or ty is None:
        return True
    if hasattr(ty, "model_validate"):
        try:
            ty.model_validate(value)
            return True
        except Exception:
            return False
    if isinstance(ty, type):
        return isinstance(value, ty)
    # Generic aliases and typing constructs: leave to Pydantic/harness typing.
    return True


@dataclass(frozen=True, slots=True)
class MethodBoundaryContract:
    """A typed generation boundary plus residual obligations.

    Attach to the harness with :meth:`postconditions`::

        CodeActConfig(postconditions=contract.postconditions())

    When unused, default CodeAct/Predict behavior is unchanged (opt-in only).
    """

    return_type: type | Any | None = None
    """If set, re-check return value against this type (usually matches the
    method annotation; makes the residual package self-contained)."""

    result_predicate: ResultPredicate | None = None
    """Residual on the return *value* (beyond bare type)."""

    result_message: str | None = None
    """Human/model-facing message when ``result_predicate`` fails."""

    agent_fields: Mapping[str, FieldPredicate] = field(default_factory=dict)
    """Residuals on live ``agent.<name>`` state after the call (ARC-style)."""

    field_messages: Mapping[str, str] = field(default_factory=dict)
    """Optional per-field failure messages."""

    name: str = "method"
    """Boundary name for :meth:`describe` / debugging."""

    def postconditions(self) -> tuple[Callable[..., None], ...]:
        """Callables for ``CodeActConfig(postconditions=...)``.

        Each raises ``InvariantError`` on failure so CodeAct routes feedback
        into the validation-retry channel (same as production ARC residuals).
        """
        hooks: list[Callable[..., None]] = []

        if self.return_type is not None:
            ty = self.return_type
            message = f"result does not match expected type {ty!r}"

            def _type_hook(
                agent: Any,
                result: Any,
                call: Any,
                _ty: type | Any = ty,
                _message: str = message,
            ) -> None:
                if not _value_matches_type(result, _ty):
                    raise InvariantError(
                        f"{_message} (got {type(result).__name__})"
                    )

            _type_hook.__name__ = "method_boundary_return_type"
            hooks.append(_type_hook)

        if self.result_predicate is not None:
            pred = self.result_predicate
            message = self.result_message or "result failed residual predicate"

            def _result_hook(
                agent: Any,
                result: Any,
                call: Any,
                _pred: ResultPredicate = pred,
                _message: str = message,
            ) -> None:
                try:
                    ok = bool(_pred(result))
                except Exception as e:
                    raise InvariantError(f"{_message}: predicate error: {e}") from e
                if not ok:
                    raise InvariantError(_message)

            _result_hook.__name__ = "method_boundary_result_predicate"
            hooks.append(_result_hook)

        for attr, pred in self.agent_fields.items():
            msg = self.field_messages.get(
                attr, f"agent.{attr} failed residual predicate"
            )

            def _field_hook(
                agent: Any,
                result: Any,
                call: Any,
                _attr: str = attr,
                _pred: FieldPredicate = pred,
                _msg: str = msg,
            ) -> None:
                if not hasattr(agent, _attr):
                    raise InvariantError(f"{_msg} (agent missing {_attr!r})")
                try:
                    ok = bool(_pred(getattr(agent, _attr)))
                except Exception as e:
                    raise InvariantError(f"{_msg}: {e}") from e
                if not ok:
                    raise InvariantError(_msg)

            _field_hook.__name__ = f"method_boundary_field_{attr}"
            hooks.append(_field_hook)

        if not hooks:
            raise ValueError(
                "MethodBoundaryContract is empty: set return_type, "
                "result_predicate, and/or agent_fields"
            )
        return tuple(hooks)

    def codeact_config_kwargs(self) -> dict[str, Any]:
        """Fragment to merge into ``CodeActConfig(...)``."""
        return {"postconditions": self.postconditions()}

    def describe(self) -> dict[str, Any]:
        """Short machine-readable description (not required to attach hooks)."""
        return {
            "application": "method_boundary_residual_contract",
            "name": self.name,
            "harness": "CodeActConfig(postconditions=contract.postconditions())",
            "enforcement": "InvariantError → CodeAct validation-retry channel",
            "return_type": repr(self.return_type) if self.return_type is not None else None,
            "residuals": {
                "result_predicate": self.result_predicate is not None,
                "agent_fields": list(self.agent_fields.keys()),
            },
        }


def method_boundary_contract(
    return_type: type | Any | None = None,
    *,
    result_predicate: ResultPredicate | None = None,
    result_message: str | None = None,
    agent_fields: Mapping[str, FieldPredicate] | None = None,
    field_messages: Mapping[str, str] | None = None,
    name: str = "method",
) -> MethodBoundaryContract:
    """Build a :class:`MethodBoundaryContract` (primary author-facing entry point).

    Args:
        return_type: Optional type re-check (usually matches the method annotation).
        result_predicate: Residual on the value (e.g. non-empty evidence field).
        result_message: Model-facing retry hint when the residual fails.
        agent_fields: Map of agent attribute name → predicate (live state).
        field_messages: Optional clearer messages per agent field.
        name: Boundary label for debugging / :meth:`MethodBoundaryContract.describe`.
    """
    return MethodBoundaryContract(
        return_type=return_type,
        result_predicate=result_predicate,
        result_message=result_message,
        agent_fields=dict(agent_fields or {}),
        field_messages=dict(field_messages or {}),
        name=name,
    )


def method_boundary_postconditions(
    return_type: type | Any | None = None,
    *,
    result_predicate: ResultPredicate | None = None,
    result_message: str | None = None,
    agent_fields: Mapping[str, FieldPredicate] | None = None,
    field_messages: Mapping[str, str] | None = None,
    name: str = "method",
) -> tuple[Callable[..., None], ...]:
    """Shorthand: ``CodeActConfig(postconditions=method_boundary_postconditions(...))``."""
    return method_boundary_contract(
        return_type,
        result_predicate=result_predicate,
        result_message=result_message,
        agent_fields=agent_fields,
        field_messages=field_messages,
        name=name,
    ).postconditions()
