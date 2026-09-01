"""Golden test vectors for OpenAI→Anthropic message translation.

These tests pin the contract that OpenAI system messages are extracted
and multiple system messages are joined with a specific delimiter.
Tests load fixture files containing input/expected pairs and verify
the translation function behavior.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from ogentic_adapter_sdk._anthropic_translate import extract_system_and_messages

# Regression gate constants — if these change, the tests fail.
_SYSTEM_JOIN_REGRESSION = "\n\n"


@pytest.fixture
def fixture_dir() -> Path:
    """Return the path to the anthropic_messages fixtures directory."""
    return Path(__file__).parent / "fixtures" / "anthropic_messages"


def _load_fixture(fixture_path: Path) -> dict[str, Any]:
    """Load a JSON fixture file."""
    with open(fixture_path, encoding="utf-8") as f:
        data = json.load(f)
        assert isinstance(data, dict)
        return data


def test_anthropic_translation_no_system(fixture_dir: Path) -> None:
    """Verify no-system case: no system messages in, none out."""
    fixture = _load_fixture(fixture_dir / "no_system_message.json")

    system, messages = extract_system_and_messages(fixture["input"])

    assert system == fixture["expected_system"]
    assert messages == fixture["expected_messages"]


def test_anthropic_translation_single_system(fixture_dir: Path) -> None:
    """Verify single system message is extracted."""
    fixture = _load_fixture(fixture_dir / "single_system_message.json")

    system, messages = extract_system_and_messages(fixture["input"])

    assert system == fixture["expected_system"]
    assert messages == fixture["expected_messages"]


def test_anthropic_translation_multiple_systems(fixture_dir: Path) -> None:
    """Verify multiple system messages are joined with newline delimiter.

    This test regression-gates the _SYSTEM_JOIN constant.
    If the join delimiter changes, this test must fail.
    """
    fixture = _load_fixture(fixture_dir / "multiple_systems_joined.json")

    system, messages = extract_system_and_messages(fixture["input"])

    assert system == fixture["expected_system"]
    assert messages == fixture["expected_messages"]

    # Regression gate: verify the expected string contains the exact delimiter
    assert _SYSTEM_JOIN_REGRESSION in system  # type: ignore[operator]
    assert system == "First instruction." + _SYSTEM_JOIN_REGRESSION + "Second instruction."


def test_anthropic_translation_content_parts(fixture_dir: Path) -> None:
    """Verify content-part lists (OpenAI style) are flattened."""
    fixture = _load_fixture(fixture_dir / "content_parts_message.json")

    system, messages = extract_system_and_messages(fixture["input"])

    assert system == fixture["expected_system"]
    assert messages == fixture["expected_messages"]

    # Regression gate: verify the parts are joined with the expected delimiter
    assert _SYSTEM_JOIN_REGRESSION in system  # type: ignore[operator]
    assert system == "Part A" + _SYSTEM_JOIN_REGRESSION + "Part B"
