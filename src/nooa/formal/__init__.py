# SPDX-FileCopyrightText: Copyright (c) 2026, NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
"""Optional residual-contract helpers for NOOA generation methods.

**Opt-in only.** Not re-exported from top-level ``nooa``. No default runtime
change when unused.

Public API::

    from nooa.formal import method_boundary_contract, method_boundary_postconditions

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
