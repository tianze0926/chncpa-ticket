from typing import TypedDict

class PushConfig(TypedDict):
    app_token: str
    topic_ids: list[str]
    uids: list[str]

class Concert(TypedDict):
    id: str
    name: str

class Config(TypedDict):
    wx_push: PushConfig
    concerts: list[Concert]