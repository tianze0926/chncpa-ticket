"""
Types
"""

from typing import TypedDict, Literal, Union

class PushConfig(TypedDict):
    """
    wx_push
    """
    app_token: str
    topic_ids: list[str]
    uids: list[str]

class Concert(TypedDict):
    """
    concerts
    """
    id: str
    name: str

class DurationConfigFixed(TypedDict):
    """
    duration.[inner|outer]
    """
    type: Literal['fixed']
    len: float

class DurationConfigGamma(TypedDict):
    """
    duration.[inner|outer]
    """
    type: Literal['gamma']
    k: float
    theta: float

DurationConfig = Union[
    DurationConfigFixed,
    DurationConfigGamma
]

class DurationsConfig(TypedDict):
    """
    duration
    """
    inner: DurationConfig
    outer: DurationConfig

class Config(TypedDict):
    """
    Root config
    """
    keywords: list[str]
    wx_push: PushConfig
    concerts: list[Concert]
    duration: DurationsConfig
    timeout: float
