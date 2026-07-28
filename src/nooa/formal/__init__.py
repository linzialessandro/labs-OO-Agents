# SPDX-FileCopyrightText: Copyright (c) 2026, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Optional residual-contract helpers for NOOA generation methods.

**Opt-in only.** Not re-exported from top-level ``nooa``. No default runtime
change when unused.

**Public API** (this package)::

    from nooa.formal import method_boundary_contract, method_boundary_postconditions

``model_theory`` is **private support** for :mod:`nooa.formal.application`
(formula builders + ``as_postcondition``). Do not treat it as a stable public
surface in reviews or docs — import residual contracts from this package or
from ``nooa.formal.application``.

See ``APPLICATION.md``.
"""

from nooa.formal.application import (
    MethodBoundaryContract,
    method_boundary_contract,
    method_boundary_postconditions,
)

__all__ = [
    "MethodBoundaryContract",
    "method_boundary_contract",
    "method_boundary_postconditions",
]
