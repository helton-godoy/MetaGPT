from pathlib import Path

import chainlit as cl
from init_setup import ChainlitEnv

from metagpt.actions import UserRequirement
from metagpt.roles import (
    Architect,
    Engineer,
    ProductManager,
    ProjectManager,
    QaEngineer,
)
from metagpt.team import Team


def _ensure_watch(role, actions):
    """RoleZero subclasses only register `_watch` when `use_fixed_sop=True`.

    With the default `use_fixed_sop=False` their `rc.watch` stays empty, so the
    role is never triggered by an incoming message: `_observe()` finds no news,
    `_think()` returns early on `if not self.rc.todo`, and the LLM is never
    called. The whole team looks idle and the UI appears unresponsive.
    """
    if not role.rc.watch:
        role._watch(actions)
    return role


# https://docs.chainlit.io/concepts/starters
@cl.set_chat_profiles
async def chat_profile() -> list[cl.ChatProfile]:
    """Generates a chat profile containing starter messages which can be triggered to run MetaGPT

    Returns:
        list[chainlit.ChatProfile]: List of Chat Profile
    """
    return [
        cl.ChatProfile(
            name="MetaGPT",
            icon="/public/MetaGPT-new-log.jpg",
            markdown_description="It takes a **one line requirement** as input and outputs **user stories / competitive analysis / requirements / data structures / APIs / documents, etc.**, But `everything in UI`.",
            starters=[
                cl.Starter(
                    label="Create a 2048 Game",
                    message="Create a 2048 game",
                    icon="/public/2048.jpg",
                ),
                cl.Starter(
                    label="Write a cli Blackjack Game",
                    message="Write a cli Blackjack Game",
                    icon="/public/blackjack.jpg",
                ),
            ],
        )
    ]


# https://docs.chainlit.io/concepts/message
@cl.on_message
async def startup(message: cl.Message) -> None:
    """On Message in UI, Create a MetaGPT software company

    Args:
        message (chainlit.Message): message by chainlist
    """
    idea = message.content
    company = Team(env=ChainlitEnv())

    await cl.Message(
        content=(
            f"**Ideia recebida:** {idea}\n\n"
            "Montando a software company "
            "(`ProductManager → Architect → ProjectManager → Engineer → QaEngineer`)...\n\n"
            "*Nota: o modelo (`qwen3.6-35b-a3b`) roda localmente em CPU/GPU e pode "
            "levar vários minutos por fase. A saída aparece conforme é gerada.*"
        )
    ).send()

    # Similar to software_company.py
    company.hire(
        [
            _ensure_watch(ProductManager(), [UserRequirement]),
            _ensure_watch(Architect(), [UserRequirement]),
            _ensure_watch(ProjectManager(), [UserRequirement]),
            _ensure_watch(Engineer(n_borg=5, use_code_review=True), [UserRequirement]),
            _ensure_watch(QaEngineer(), [UserRequirement]),
        ]
    )

    company.invest(investment=3.0)
    company.run_project(idea=idea)

    await company.run(n_round=5)

    workdir = Path(company.env.context.config.project_path)
    files = [file.name for file in workdir.iterdir() if file.is_file()]
    files = "\n".join([f"{workdir}/{file}" for file in files if not file.startswith(".git")])

    await cl.Message(
        content=f"""
Codes can be found here:
{files}

---

Total cost: `{company.cost_manager.total_cost}`
"""
    ).send()
