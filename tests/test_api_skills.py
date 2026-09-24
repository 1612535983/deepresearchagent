import asyncio

from deepresearch.agent import ResearchResult
from deepresearch.api.runs import default_run_executor
from deepresearch.api.skills import resolve_web_skill_config
from deepresearch.config import Settings
from deepresearch.skill.config import SkillConfig
from deepresearch.state import create_initial_state


def test_web_skill_config_enables_default_manager_without_losing_options() -> None:
    config = SkillConfig(
        use="",
        include_builtin=False,
        max_skills=2,
        token_budget=900,
    )

    resolved = resolve_web_skill_config(config)

    assert resolved.use == "default"
    assert resolved.include_builtin is False
    assert resolved.max_skills == 2
    assert resolved.token_budget == 900


def test_web_executor_enables_skills_and_forwards_frontend_selection(
    monkeypatch,
) -> None:  # noqa: ANN001
    received = {}
    settings = Settings(api_key="test-key", skill=SkillConfig(use=""))

    async def fake_astream(
        question,
        on_event,
        resolved_settings=None,
        **kwargs,
    ):
        received.update(
            question=question,
            settings=kwargs.get("settings") or resolved_settings,
            skill_overrides=kwargs.get("skill_overrides"),
            thread_id=kwargs.get("thread_id"),
        )
        state = create_initial_state(question)
        return ResearchResult(question, "完成", state, kwargs.get("thread_id"))

    monkeypatch.setattr(
        "deepresearch.api.runs.Settings.from_env",
        lambda: settings,
    )
    monkeypatch.setattr("deepresearch.api.runs.astream_question", fake_astream)

    async def scenario() -> None:
        async def ignore_event(event):
            return None

        await default_run_executor(
            "核验来源",
            ignore_event,
            "research-skill-web",
            ("source-verification",),
        )

    asyncio.run(scenario())

    assert received["settings"].skill.use == "default"
    assert received["skill_overrides"] == ("source-verification",)
    assert received["thread_id"] == "research-skill-web"
