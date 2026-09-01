"""Golden test vectors for SSE delta parsing.

These tests pin the contract that SSE streams are parsed correctly,
[DONE] terminates iteration, empty lines and comments are skipped,
and non-data SSE fields are ignored.
Tests load fixture files containing input lines and expected parsed deltas.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import pytest

from ogentic_adapter_sdk._sse import aiter_sse_deltas

# Regression gate constant — if this changes, the tests fail.
_DONE_SENTINEL_REGRESSION = "[DONE]"


class _FakeResponse:
    """Minimal stand-in for ``httpx.Response`` exposing ``aiter_lines``.

    The parser only calls ``aiter_lines``; constructing a real
    ``httpx.Response`` for these unit tests would be overkill (and would
    drag the test into httpx_mock territory unnecessarily).
    """

    def __init__(self, lines: list[str]) -> None:
        self._lines = lines

    async def aiter_lines(self) -> AsyncIterator[str]:
        for line in self._lines:
            yield line


@pytest.fixture
def fixture_dir() -> Path:
    """Return the path to the sse_streams fixtures directory."""
    return Path(__file__).parent / "fixtures" / "sse_streams"


def _load_fixture(fixture_path: Path) -> dict[str, Any]:
    """Load a JSON fixture file."""
    with open(fixture_path, encoding="utf-8") as f:
        data = json.load(f)
        assert isinstance(data, dict)
        return data


async def _collect(it: AsyncIterator[dict[str, object]]) -> list[dict[str, object]]:
    """Helper — consume an async iterator into a list for assertions."""
    return [x async for x in it]


@pytest.mark.asyncio
async def test_sse_single_delta(fixture_dir: Path) -> None:
    """Verify a single SSE delta is parsed correctly."""
    fixture = _load_fixture(fixture_dir / "single_delta.json")

    response = _FakeResponse(fixture["input"])
    deltas = await _collect(aiter_sse_deltas(response))

    assert deltas == fixture["expected_deltas"]


@pytest.mark.asyncio
async def test_sse_multiple_deltas(fixture_dir: Path) -> None:
    """Verify multiple SSE deltas are parsed in order."""
    fixture = _load_fixture(fixture_dir / "multiple_deltas.json")

    response = _FakeResponse(fixture["input"])
    deltas = await _collect(aiter_sse_deltas(response))

    assert deltas == fixture["expected_deltas"]


@pytest.mark.asyncio
async def test_sse_done_sentinel(fixture_dir: Path) -> None:
    """Verify [DONE] sentinel stops iteration and filters out trailing data.

    This test regression-gates the [DONE] sentinel behavior.
    If the sentinel changes, this test must fail.
    """
    fixture = _load_fixture(fixture_dir / "done_sentinel.json")

    response = _FakeResponse(fixture["input"])
    deltas = await _collect(aiter_sse_deltas(response))

    assert deltas == fixture["expected_deltas"]

    # Regression gate: verify the expected input contains the sentinel
    assert any(_DONE_SENTINEL_REGRESSION in line for line in fixture["input"])
    # And verify we only got one delta (the one before [DONE])
    assert len(deltas) == 1


@pytest.mark.asyncio
async def test_sse_empty_and_comments(fixture_dir: Path) -> None:
    """Verify empty lines and SSE comment lines are skipped."""
    fixture = _load_fixture(fixture_dir / "empty_lines_and_comments.json")

    response = _FakeResponse(fixture["input"])
    deltas = await _collect(aiter_sse_deltas(response))

    assert deltas == fixture["expected_deltas"]


@pytest.mark.asyncio
async def test_sse_non_data_fields(fixture_dir: Path) -> None:
    """Verify non-data SSE fields (event, id) are ignored."""
    fixture = _load_fixture(fixture_dir / "non_data_fields.json")

    response = _FakeResponse(fixture["input"])
    deltas = await _collect(aiter_sse_deltas(response))

    assert deltas == fixture["expected_deltas"]


@pytest.mark.asyncio
async def test_sse_multiple_deltas_with_done(fixture_dir: Path) -> None:
    """Verify [DONE] stops iteration even with more data lines after it."""
    fixture = _load_fixture(fixture_dir / "multiple_deltas_with_done.json")

    response = _FakeResponse(fixture["input"])
    deltas = await _collect(aiter_sse_deltas(response))

    assert deltas == fixture["expected_deltas"]
    # Verify the sentinel is in the input but didn't produce extra deltas
    assert any(_DONE_SENTINEL_REGRESSION in line for line in fixture["input"])
    assert len(deltas) == 2


@pytest.mark.asyncio
async def test_sse_malformed_json_raises(fixture_dir: Path) -> None:
    """Verify malformed JSON raises JSONDecodeError.

    This is the failure path test per CLAUDE.md §5. Malformed JSON in a
    data: line should raise json.JSONDecodeError so the caller sees the
    real upstream error (partial buffering / chunked SSE framing is httpx's job).
    """
    fixture = _load_fixture(fixture_dir / "malformed_json.json")

    response = _FakeResponse(fixture["input"])

    with pytest.raises(json.JSONDecodeError):
        await _collect(aiter_sse_deltas(response))
