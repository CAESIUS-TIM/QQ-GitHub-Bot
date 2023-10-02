"""
@Author         : yanyongyu
@Date           : 2022-09-14 04:34:39
@LastEditors    : yanyongyu
@LastEditTime   : 2023-03-04 15:30:25
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot.log import logger
from nonebot.matcher import Matcher
from nonebot.params import Depends, RegexDict
from githubkit.rest import Commit, Release, FullRepository
from nonebot.adapters.github import ActionFailed, ActionTimeout

from src.plugins.github.models import User
from src.plugins.github.helpers import get_current_user, get_github_context


async def check_repo(
    matcher: Matcher,
    group: dict[str, str] = RegexDict(),
    user: User | None = Depends(get_current_user),
) -> FullRepository:
    owner = group["owner"]
    repo = group["repo"]

    context = await get_github_context(owner, repo, matcher, user)

    try:
        async with context() as bot:
            resp = await bot.rest.repos.async_get(owner=owner, repo=repo)
            return resp.parsed_data
    except ActionTimeout:
        await matcher.finish("GitHub API 超时，请稍后再试")
    except ActionFailed as e:
        if e.response.status_code == 404:
            await matcher.finish()
        logger.opt(exception=e).error(f"Failed while checking repo in opengraph: {e}")
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while checking repo in opengraph: {e}")
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")


async def check_commit(
    matcher: Matcher,
    group: dict[str, str] = RegexDict(),
    check_repo=Depends(check_repo),
    user: User | None = Depends(get_current_user),
) -> Commit:
    owner = group["owner"]
    repo = group["repo"]
    ref = group["commit"]

    context = await get_github_context(owner, repo, matcher, user)

    try:
        async with context() as bot:
            resp = await bot.rest.repos.async_get_commit(
                owner=owner, repo=repo, ref=ref
            )
            return resp.parsed_data
    except ActionTimeout:
        await matcher.finish()
    except ActionFailed as e:
        if e.response.status_code == 404:
            await matcher.finish()
        logger.opt(exception=e).error(f"Failed while checking commit in opengraph: {e}")
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(f"Failed while checking commit in opengraph: {e}")
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")


async def check_release(
    matcher: Matcher,
    group: dict[str, str] = RegexDict(),
    check_repo=Depends(check_repo),
    user: User | None = Depends(get_current_user),
) -> Release:
    owner = group["owner"]
    repo = group["repo"]
    tag = group["tag"]

    context = await get_github_context(owner, repo, matcher, user)

    try:
        async with context() as bot:
            resp = await bot.rest.repos.async_get_release_by_tag(
                owner=owner, repo=repo, tag=tag
            )
            return resp.parsed_data
    except ActionTimeout:
        await matcher.finish()
    except ActionFailed as e:
        if e.response.status_code == 404:
            await matcher.finish()
        logger.opt(exception=e).error(
            f"Failed while checking release in opengraph: {e}"
        )
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")
    except Exception as e:
        logger.opt(exception=e).error(
            f"Failed while checking release in opengraph: {e}"
        )
        await matcher.finish("未知错误发生，请尝试重试或联系管理员")
