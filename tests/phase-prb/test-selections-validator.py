"""Tests for selections.yaml schema validator."""
import pytest

from skills.photo_curation.scripts.selections_validator import validate, ValidationError


def test_valid_selections_passes():
    data = {
        "strategy_default": "bring-your-own",
        "slots": [
            {"slot_id": "hero-bg", "block_id": "ru-hero-01", "ratio": "16:9",
             "strategy": "bring-your-own", "chosen_photo_id": "photo_001",
             "ai_approved_by_user": False}
        ]
    }
    validate(data)


def test_invalid_strategy_enum_fails():
    data = {"strategy_default": "bring-your-own", "slots": [
        {"slot_id": "x", "block_id": "y", "ratio": "1:1", "strategy": "INVALID",
         "ai_approved_by_user": False}
    ]}
    with pytest.raises(ValidationError, match="strategy"):
        validate(data)


def test_generate_without_user_approval_for_identity_safe_slot_fails():
    data = {"strategy_default": "bring-your-own", "slots": [
        {"slot_id": "testimonial-1-avatar", "block_id": "x", "ratio": "1:1",
         "strategy": "generate", "chosen_photo_id": None,
         "ai_approved_by_user": False}
    ]}
    with pytest.raises(ValidationError, match="ai_approved_by_user"):
        validate(data)


def test_generate_with_approval_passes():
    data = {"strategy_default": "bring-your-own", "slots": [
        {"slot_id": "testimonial-1-avatar", "block_id": "x", "ratio": "1:1",
         "strategy": "generate", "chosen_photo_id": None,
         "ai_approved_by_user": True, "ai_prompt": "..."}
    ]}
    validate(data)


def test_bring_your_own_without_photo_id_fails():
    data = {"strategy_default": "bring-your-own", "slots": [
        {"slot_id": "x", "block_id": "y", "ratio": "1:1",
         "strategy": "bring-your-own", "chosen_photo_id": None,
         "ai_approved_by_user": False}
    ]}
    with pytest.raises(ValidationError, match="chosen_photo_id"):
        validate(data)


def test_missing_slots_field_fails():
    with pytest.raises(ValidationError, match="slots"):
        validate({"strategy_default": "bring-your-own"})


def test_missing_required_slot_field_fails():
    data = {"slots": [
        {"slot_id": "x", "ratio": "1:1", "strategy": "placeholder"}
        # missing block_id
    ]}
    with pytest.raises(ValidationError, match="block_id"):
        validate(data)


def test_generate_for_non_identity_safe_slot_without_approval_passes():
    # background, process, abstract — AI fallback ok by default
    data = {"slots": [
        {"slot_id": "hero-bg", "block_id": "x", "ratio": "16:9",
         "strategy": "generate", "chosen_photo_id": None,
         "ai_approved_by_user": False, "ai_prompt": "..."}
    ]}
    validate(data)
