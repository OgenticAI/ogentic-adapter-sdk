# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Golden test vectors for OpenAI→Anthropic message translation (4 test cases)
- Golden test vectors for SSE stream parsing with [DONE] sentinel handling (7 test cases)
- `ogentic_adapter_sdk._anthropic_translate` module with `extract_system_and_messages()` function
- `ogentic_adapter_sdk._sse` module with `aiter_sse_deltas()` async function
- Regression gates on `_SYSTEM_JOIN` constant and `[DONE]` sentinel parsing logic

## [0.1.0] - 2026-09-01

### Added

- Initial release of ogentic-adapter-sdk
- Skeleton release with core package structure and tooling
- Python 3.11+ support with strict type hints
- Pydantic v2 for data model validation

### Documentation

- README with overview and quick-start
- Contributing guidelines and code of conduct
- Apache 2.0 license
