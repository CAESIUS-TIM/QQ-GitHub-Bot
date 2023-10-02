"""
@Author         : yanyongyu
@Date           : 2022-10-18 03:18:14
@LastEditors    : yanyongyu
@LastEditTime   : 2022-12-21 19:56:35
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from nonebot import on_command
from nonebot.log import logger
from nonebot.adapters import Event
from nonebot.params import Depends
from nonebot.typing import T_State
from nonebot.adapters.github import ActionFailed, ActionTimeout

from src.plugins.github import config
from src.plugins.github.models import User
from src.plugins.github.utils import get_github_bot
from src.plugins.github.helpers import NO_GITHUB_EVENT, get_platform
from src.plugins.github.libs.message_tag import Tag, RepoTag, create_message_tag

from . import KEY_GITHUB_REPLY
from .dependencies import get_user, is_github_reply

star = on_command(
    "star",
    rule=NO_GITHUB_EVENT & is_github_reply,
    priority=config.github_command_priority,
    block=True,
)


@star.handle()
async def handle_link(event: Event, state: T_State, user: User = Depends(get_user)):
    bot = get_github_bot()
    tag: Tag = state[KEY_GITHUB_REPLY]

    async with bot.as_user(user.access_token):
        # check starred
        message: str | None = None
        try:
            await bot.rest.activity.async_check_repo_is_starred_by_authenticated_user(
                owner=tag.owner, repo=tag.repo
            )
            message = f"你已经为 {tag.owner}/{tag.repo} 点过 star 了"
        except ActionTimeout:
            await star.finish("GitHub API 超时，请稍后再试")
        except ActionFailed as e:
            if e.response.status_code == 401:
                await star.finish("你的 GitHub 帐号授权已过期，请使用 /auth 进行刷新")
            elif e.response.status_code == 403:
                await star.finish("权限不足，请尝试使用 /auth 刷新授权")
            elif e.response.status_code != 404:
                logger.opt(exception=e).error(
                    f"Failed while checking repo in star: {e}"
                )
                await star.finish("未知错误发生，请尝试重试或联系管理员")
        except Exception as e:
            logger.opt(exception=e).error(f"Failed while checking repo in star: {e}")
            await star.finish("未知错误发生，请尝试重试或联系管理员")

        if message is None:
            try:
                await bot.rest.activity.async_star_repo_for_authenticated_user(
                    owner=tag.owner, repo=tag.repo
                )
                message = f"成功为 {tag.owner}/{tag.repo} star"
            except ActionTimeout:
                await star.finish("GitHub API 超时，请稍后再试")
            except ActionFailed as e:
                if e.response.status_code == 403:
                    await star.finish(f"权限不足，{tag.owner}/{tag.repo} 未安装 APP")
                elif e.response.status_code == 404:
                    await star.finish(f"仓库 {tag.owner}/{tag.repo} 不存在")
                logger.opt(exception=e).error(
                    f"Failed while checking repo in star: {e}"
                )
                await star.finish("未知错误发生，请尝试重试或联系管理员")
            except Exception as e:
                logger.opt(exception=e).error(
                    f"Failed while checking repo in star: {e}"
                )
                await star.finish("未知错误发生，请尝试重试或联系管理员")

    result = await star.send(message)

    tag = RepoTag(owner=tag.owner, repo=tag.repo, is_receive=False)
    match get_platform(event):
        case "qq":
            if isinstance(result, dict) and "message_id" in result:
                await create_message_tag(
                    {"type": "qq", "message_id": result["message_id"]}, tag
                )
        case _:
            logger.error(f"Unprocessed event type: {type(event)}")
