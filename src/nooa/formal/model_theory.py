# SPDX-FileCopyrightText: Copyright (c) 2026, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Mini-language model theory for NOOA call boundaries.

Precision
---------
This is **not** first-order model theory of the Python heap. It defines
satisfaction for a **fixed tiny formula grammar** on a **partial carrier**
(``AgentStructure``). See ``perspectives`` / ``IMPLICATIONS.md`` for how this
relates to CT dual readings and to production validation.

Dual with CT (aligned case only)
--------------------------------
When the theory is ``{ AtomicInhabits(codomain) }`` and the CT object is
``MethodArrow(..., codomain=codomain)``, both describe the same generation
boundary the harness enforces with return-type validation. Residuals
(``AtomicField``, ``AtomicResultPred``) match postconditions that types alone
cannot express. Build the aligned pair with
``perspectives.bridge_method_arrow_to_theory``.

Relation to engineering-CL
--------------------------
``assert_satisfies`` raises ``InvariantError`` so it can ride the same
model-correctable retry channel as ``run_postconditions``. That is executable
evidence-carrying rejection — not a foundational constructive type theory.

Vocabulary (as implemented)
---------------------------
| Symbol | Implementation |
|--------|-----------------|
| Structure | ``AgentStructure`` (result, optional fields, tags) |
| Formula | ``AtomicInhabits`` / ``AtomicField`` / ``AtomicEventTag`` / ``AtomicResultPred`` |
| ``M ⊨ φ`` | ``satisfies(M, φ)`` |
| Theory | sequence / ``And`` of formulas |
| Homomorphism | ``StructureHomomorphism`` — **weak** (result type + shared fields) |

Defer
-----
Completeness, ultraproducts, full FOL, elementary embeddings for collapse
(collapse is lossy — do not call it an embedding). Sandbox-as-reduct is
metaphor unless the signature is only capability flags.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from nooa.strategy_validation import InvariantError

# ---------------------------------------------------------------------------
# Formulas (tiny contract language — not a full FOL implementation)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class AtomicInhabits:
    """Atomic formula: the distinguished result inhabits ``ty``.

    Written informally as ``result : ty``.
    """

    ty: type | Any
    name: str = "result_inhabits"


@dataclass(frozen=True, slots=True)
class AtomicField:
    """Atomic formula: ``agent.<attr>`` satisfies ``predicate``.

    Dependent residual — the ARC-style "WAIT requires submission" pattern
    is an instance of this shape (attr + predicate over live state).
    """

    attr: str
    predicate: Callable[[Any], bool]
    name: str = "agent_field"


@dataclass(frozen=True, slots=True)
class AtomicEventTag:
    """Atomic formula: event history contains tag ``tag`` (audit witness)."""

    tag: str
    name: str = "has_event_tag"


@dataclass(frozen=True, slots=True)
class AtomicResultPred:
    """Atomic formula: distinguished result satisfies ``predicate``.

    Use for residual obligations on the value itself (beyond bare type).
    """

    predicate: Callable[[Any], bool]
    name: str = "result_pred"


Formula = AtomicInhabits | AtomicField | AtomicEventTag | AtomicResultPred


@dataclass(frozen=True, slots=True)
class And:
    """Conjunction of formulas (theory fragment closed under ∧)."""

    conjuncts: tuple[Formula | And, ...]


Theory = Sequence[Formula | And]


# ---------------------------------------------------------------------------
# Structures
# ---------------------------------------------------------------------------


@dataclass
class AgentStructure:
    """First-order-ish structure for one agentic call boundary.

    The *universe* is not enumerated exhaustively (Python state is large);
    we only expose the carriers the contract language can mention: the
    result, selected agent attributes, and event tags. That is enough to
    interpret the atomic formulas above — the same observables postconditions
    already use.
    """

    result: Any = None
    agent_fields: dict[str, Any] = field(default_factory=dict)
    event_tags: frozenset[str] = field(default_factory=frozenset)
    call_name: str | None = None

    @classmethod
    def from_call(
        cls,
        agent: Any,
        result: Any,
        call: Any,
        *,
        fields: Sequence[str] = (),
        event_tags: Sequence[str] | None = None,
    ) -> AgentStructure:
        """Build a structure snapshot from harness-visible call data."""
        agent_fields: dict[str, Any] = {}
        for name in fields:
            if hasattr(agent, name):
                agent_fields[name] = getattr(agent, name)
        tags: frozenset[str]
        if event_tags is not None:
            tags = frozenset(event_tags)
        else:
            em = getattr(agent, "event_manager", None)
            if em is not None and hasattr(em, "keys"):
                try:
                    tags = frozenset(str(t) for t in em.keys())
                except Exception:
                    tags = frozenset()
            else:
                tags = frozenset()
        call_name = getattr(call, "method_name", None) or getattr(call, "name", None)
        return cls(
            result=result,
            agent_fields=agent_fields,
            event_tags=tags,
            call_name=str(call_name) if call_name else None,
        )


# ---------------------------------------------------------------------------
# Satisfaction  M ⊨ φ
# ---------------------------------------------------------------------------


def _inhabits(value: Any, ty: type | Any) -> bool:
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
    return True


def satisfies(structure: AgentStructure, formula: Formula | And) -> bool:
    """Return whether ``structure ⊨ formula``.

    This is the model-theoretic reading of a single contract check. Raising
    is reserved for :func:`assert_satisfies` (harness-facing).
    """
    if isinstance(formula, And):
        return all(satisfies(structure, c) for c in formula.conjuncts)
    if isinstance(formula, AtomicInhabits):
        return _inhabits(structure.result, formula.ty)
    if isinstance(formula, AtomicField):
        if formula.attr not in structure.agent_fields:
            return False
        try:
            return bool(formula.predicate(structure.agent_fields[formula.attr]))
        except Exception:
            return False
    if isinstance(formula, AtomicEventTag):
        return formula.tag in structure.event_tags
    if isinstance(formula, AtomicResultPred):
        try:
            return bool(formula.predicate(structure.result))
        except Exception:
            return False
    return False  # pragma: no cover — exhaustive for Formula | And


def assert_satisfies(structure: AgentStructure, formula: Formula | And) -> None:
    """Harness-facing satisfaction: raise ``InvariantError`` if ``M ⊭ φ``."""
    if not satisfies(structure, formula):
        raise InvariantError(
            f"structure does not satisfy {formula!r} "
            f"(call={structure.call_name!r}, result={type(structure.result).__name__})"
        )


def models_theory(structure: AgentStructure, theory: Theory) -> bool:
    """``M ⊨ T`` iff every formula in the theory holds."""
    return all(satisfies(structure, phi) for phi in theory)


# ---------------------------------------------------------------------------
# Homomorphisms (structure-preserving maps under orchestration)
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class StructureHomomorphism:
    """A map ``h: M → N`` that should preserve atomic contract structure.

    For NOOA, a nested or orchestrated call induces a candidate homomorphism:
    the parent result becomes (or is computed from) a child result; event tags
    of the child embed into the parent history; typed fields that both
    structures expose must agree after the map.

    We only check **preservation of inhabitation and shared field equalities**
    — enough to state "orchestration must not drop type contracts."
    """

    source: AgentStructure
    target: AgentStructure
    # Optional rename of agent field names source → target
    field_map: Mapping[str, str] = field(default_factory=dict)

    def preserves_result_type(self, ty: type | Any) -> bool:
        """If source result : ty, target result should still inhabit ty."""
        if not _inhabits(self.source.result, ty):
            return True  # vacuous: nothing to preserve
        return _inhabits(self.target.result, ty)

    def preserves_shared_fields(self) -> bool:
        for src_name, value in self.source.agent_fields.items():
            tgt_name = self.field_map.get(src_name, src_name)
            if tgt_name in self.target.agent_fields:
                if self.target.agent_fields[tgt_name] != value:
                    return False
        return True

    def is_homomorphism_for(self, ty: type | Any) -> bool:
        return self.preserves_result_type(ty) and self.preserves_shared_fields()


def as_postcondition(
    *formulas: Formula | And,
    fields: Sequence[str] = (),
) -> Callable[[Any, Any, Any], None]:
    """Compile formulas into a CodeAct/Predict postcondition checker.

    Example::

        from nooa.config import CodeActConfig
        from nooa.formal.model_theory import AtomicInhabits, as_postcondition

        cfg = CodeActConfig(
            postconditions=[as_postcondition(AtomicInhabits(str))]
        )
    """

    def _check(agent: Any, result: Any, call: Any) -> None:
        structure = AgentStructure.from_call(agent, result, call, fields=fields)
        for phi in formulas:
            assert_satisfies(structure, phi)

    _check.__name__ = "model_theory_postcondition"
    return _check
