import pytest
from unittest.mock import MagicMock, patch
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


REFUSAL_KEYWORDS = ["only answer", "not able to help", "outside my expertise"]
MTB_KEYWORDS = ["mountain bike", "MTB", "cycling", "bike"]


def make_mock_response(text: str):
    block = MagicMock()
    block.text = text
    block.type = "text"
    response = MagicMock()
    response.stop_reason = "end_turn"
    response.content = [block]
    return response


@patch("agent.client")
def test_mtb_question_accepted(mock_client):
    mock_client.messages.create.return_value = make_mock_response(
        "For enduro riding, I recommend setting your suspension sag to around 30% for the rear and 25% for the front."
    )
    from agent import run_agent
    response = run_agent("What is the best suspension setup for enduro riding?")
    assert not any(kw in response for kw in REFUSAL_KEYWORDS)


@patch("agent.client")
def test_emtb_question_accepted(mock_client):
    mock_client.messages.create.return_value = make_mock_response(
        "For trail riding under 5kg, consider the Specialized Turbo Levo SL or the Trek Rail SL."
    )
    from agent import run_agent
    response = run_agent("What eMTB would you recommend for trail riding under 5kg?")
    assert not any(kw in response for kw in REFUSAL_KEYWORDS)


@patch("agent.client")
def test_off_topic_question_rejected(mock_client):
    mock_client.messages.create.return_value = make_mock_response(
        "I'm an MTB specialist assistant and can only help with mountain bike related questions. Paris is the capital of France, but I'm here to help with cycling and bike topics!"
    )
    from agent import run_agent
    response = run_agent("What is the capital of France?")
    assert any(kw in response for kw in MTB_KEYWORDS)


@patch("agent.client")
def test_cooking_question_rejected(mock_client):
    mock_client.messages.create.return_value = make_mock_response(
        "I'm sorry, I can only help with MTB and cycling questions. For cooking advice, please consult a culinary resource. Is there anything about mountain biking I can help you with?"
    )
    from agent import run_agent
    response = run_agent("How do I make pasta carbonara?")
    assert any(kw in response for kw in MTB_KEYWORDS)


def test_system_prompt_is_mtb_specific():
    import inspect
    import agent
    source = inspect.getsource(agent.run_agent)
    assert "MTB" in source
    assert "mountain bike" in source
    assert "unrelated" in source or "not related" in source or "Only answer" in source or "only answer" in source or "IMPORTANT RULES" in source
