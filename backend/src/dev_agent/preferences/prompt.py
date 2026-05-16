from dev_agent.database.models.user_preferences import UserPreferencesPublic


_MAX_AGENT_INSTRUCTIONS = 4000


def build_agent_system_preamble(prefs: UserPreferencesPublic) -> str:
    display_name = (prefs.display_name or "Developer").strip()
    instructions = (prefs.agent_instructions or "").strip()
    if len(instructions) > _MAX_AGENT_INSTRUCTIONS:
        instructions = instructions[:_MAX_AGENT_INSTRUCTIONS] + "…"

    instructions_block = f"\n{instructions}" if instructions else ""

    return (
        f"You are AYANAMI AGENT. The user's name is {display_name}. "
        f"Address them by this name naturally throughout the conversation."
        f"{instructions_block}\n"
        "Be concise. Give short, direct answers. Do not elaborate unless the user "
        "explicitly asks for more detail. Never use formal closing phrases like "
        '"Atenciosamente" or sign off messages.'
    )
