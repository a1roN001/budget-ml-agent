import pytest
from agent.agent import Agent

class FailingProvider:
    def chat_completion(self, messages, model):
        raise RuntimeError("boom")


def test_failed_request_does_not_corrupt_history():
    provider = FailingProvider()
    agent = Agent(provider=provider, model="test-model", max_history_messages=10)

    with pytest.raises(RuntimeError):
        agent.send("hello")

    assert agent.history() == []

class FakeProvider:
    def __init__(self, response="ok"):
        self.response = response
        self.calls = []

    def chat_completion(self, messages, model):
        self.calls.append({"messages": messages, "model": model})
        return self.response


def test_agent_remembers_history():
    provider = FakeProvider(response="Nice to meet you, Alex.")
    agent = Agent(provider=provider, model="test-model", max_history_messages=10)

    agent.send("My name is Alex.")
    agent.send("What is my name?")

    assert len(agent.history()) == 4
    assert agent.history()[0]["role"] == "user"
    assert agent.history()[1]["role"] == "assistant"
    assert agent.history()[2]["content"] == "What is my name?"


def test_reset_clears_history():
    provider = FakeProvider()
    agent = Agent(provider=provider, model="test-model", max_history_messages=10)

    agent.send("Hello")
    agent.reset()

    assert agent.history() == []


def test_history_trim_preserves_order():
    provider = FakeProvider(response="ok")
    agent = Agent(provider=provider, model="test-model", max_history_messages=2)

    agent.send("one")
    agent.send("two")

    payload = agent._payload_messages()

    assert payload[0]["role"] == "system"
    assert payload[1]["content"] == "two"
    assert payload[2]["content"] == "ok"
    assert payload[3]["content"] == ""  # если send добавляет assistant пустой? лучше не так

def test_trim_keeps_last_messages_in_order():
    provider = FakeProvider(response="answer")
    agent = Agent(provider=provider, model="test-model", max_history_messages=2)

    agent.messages = [
        {"role": "user", "content": "first"},
        {"role": "assistant", "content": "second"},
        {"role": "user", "content": "third"},
    ]

    trimmed = agent._trimmed_history()

    assert trimmed == [
        {"role": "assistant", "content": "second"},
        {"role": "user", "content": "third"},
    ]

def test_max_history_zero_returns_empty_history():
    provider = FakeProvider()
    agent = Agent(provider=provider, model="test-model", max_history_messages=0)

    agent.messages = [
        {"role": "user", "content": "should not be sent"},
    ]

    assert agent._trimmed_history() == []

