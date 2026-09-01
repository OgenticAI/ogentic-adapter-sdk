# ogentic-adapter-sdk

**The Adapter protocol — the contract any LLM backend implements so [`ogentic-router`](https://github.com/OgenticAI/ogentic-router) can call it.**

`ogentic-adapter-sdk` is the Wave 2 OSS primitive that defines the interface between an LLM router and the backends it dispatches to (OpenAI, Anthropic, local models, or any custom provider). It ships with zero runtime dependencies on other Ogentic packages — Pydantic v2 is its only external dependency — so downstream libraries can depend on the contract layer without pulling in `ogentic-shield`, `ogentic-router`, or `ogentic-audit`.

This repository currently contains the package skeleton (build system, CI, and OSS hygiene files). The protocol surface itself (the `Adapter` interface, request/response models) lands in a follow-up release.

## Install

```bash
pip install ogentic-adapter-sdk
```

For local development:

```bash
git clone https://github.com/OgenticAI/ogentic-adapter-sdk.git
cd ogentic-adapter-sdk
pip install -e ".[dev]"
```

## Requirements

- Python 3.11+
- Pydantic >=2.0,<3

## License

Apache-2.0. See [LICENSE](./LICENSE).
