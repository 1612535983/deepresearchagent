"""Skill configuration policy for browser-initiated research."""

from __future__ import annotations

from dataclasses import replace

from dotenv import load_dotenv

from deepresearch.skill.config import SkillConfig


def resolve_web_skill_config(config: SkillConfig | None = None) -> SkillConfig:
    """Enable the default SkillManager for the Web catalog and Web runs.

    CLI callers retain the environment-controlled opt-in behavior. The Web UI
    is itself an explicit selection surface, so an empty selection means
    automatic matching and selected names mean forced matching.
    """

    if config is None:
        load_dotenv()
        config = SkillConfig.from_env()
    return config if config.enabled else replace(config, use="default")
