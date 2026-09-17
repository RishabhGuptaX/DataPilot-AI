from typing import Any


# ============================================================
# CONVERSATION STATE
# ============================================================

def initialize_conversation(
    session_state: Any,
) -> None:
    """
    Initialize DataPilot conversation memory.
    """

    if "conversation" not in session_state:

        session_state.conversation = []


    if "last_plan" not in session_state:

        session_state.last_plan = None


    if "last_result" not in session_state:

        session_state.last_result = None


    if "last_question" not in session_state:

        session_state.last_question = None


    if "last_chart" not in session_state:

        session_state.last_chart = None


# ============================================================
# ADD MESSAGE
# ============================================================

def add_message(
    session_state: Any,
    role: str,
    content: str,
    plan: dict | None = None,
) -> None:
    """
    Add a message to conversation history.
    """

    message = {
        "role": role,
        "content": content,
    }


    if plan is not None:

        message["plan"] = plan


    session_state.conversation.append(
        message
    )


# ============================================================
# GET CONVERSATION
# ============================================================

def get_conversation(
    session_state: Any,
) -> list:
    """
    Return conversation history.
    """

    return session_state.conversation


# ============================================================
# CLEAR CONVERSATION
# ============================================================

def clear_conversation(
    session_state: Any,
) -> None:
    """
    Clear DataPilot conversation memory.
    """

    session_state.conversation = []

    session_state.last_plan = None

    session_state.last_result = None

    session_state.last_question = None

    session_state.last_chart = None


# ============================================================
# SAVE LAST ANALYSIS
# ============================================================

def save_last_analysis(
    session_state: Any,
    question: str,
    plan: dict,
    result: Any,
) -> None:
    """
    Save the latest analysis so follow-up questions
    can reference it.
    """

    session_state.last_question = (
        question
    )

    session_state.last_plan = (
        plan
    )

    session_state.last_result = (
        result
    )


# ============================================================
# GET LAST ANALYSIS
# ============================================================

def get_last_analysis(
    session_state: Any,
) -> dict:
    """
    Return the latest analysis context.
    """

    return {
        "question": (
            session_state.last_question
        ),
        "plan": (
            session_state.last_plan
        ),
        "result": (
            session_state.last_result
        ),
    }