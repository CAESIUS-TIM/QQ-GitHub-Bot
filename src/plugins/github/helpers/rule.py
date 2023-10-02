"""
@Author         : yanyongyu
@Date           : 2022-10-27 04:24:58
@LastEditors    : yanyongyu
@LastEditTime   : 2023-03-30 23:24:36
@Description    : Rule helpers
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.rule import Rule
from nonebot.adapters import Event
from nonebot.matcher import Matcher
from nonebot.adapters.github import Event as GitHubEvent

from .event import GROUP_EVENT, PRIVATE_EVENT


def is_private_event(event: Event) -> bool:
    """Check if the event is a private event"""
    return isinstance(event, PRIVATE_EVENT)


def is_group_event(event: Event) -> bool:
    """Check if the event is a group event"""
    return isinstance(event, GROUP_EVENT)


async def no_github_event(event: Event):
    """Check if the event is not a github webhook event"""
    return not isinstance(event, GitHubEvent)


NO_GITHUB_EVENT = Rule(no_github_event)


async def run_when_private(event: Event, matcher: Matcher) -> None:
    """Skip the matcher if the event is not a private event"""
    if not is_private_event(event):
        matcher.skip()


async def run_when_group(event: Event, matcher: Matcher) -> None:
    """Skip the matcher if the event is not a group event"""
    if not is_group_event(event):
        matcher.skip()
