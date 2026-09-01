"""ogentic-adapter-sdk — the Adapter protocol contract for LLM backends.

This package defines the contract that any LLM backend implements so that
``ogentic-router`` can call it. It has zero runtime dependencies on other
Ogentic packages; downstream libraries can depend on it without pulling in
``ogentic-shield``, ``ogentic-router``, or ``ogentic-audit``.

This is a skeleton release (OGE-1180). The protocol surface itself lands in
a follow-up ticket.
"""

__version__ = "0.1.0"

__all__ = ["__version__"]
