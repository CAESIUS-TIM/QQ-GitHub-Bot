"""
@Author         : yanyongyu
@Date           : 2021-03-09 16:30:16
@LastEditors    : yanyongyu
@LastEditTime   : 2022-10-05 07:04:36
@Description    : OAuth lib
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

import json
import urllib.parse

from src.plugins.github import config
from src.plugins.github.models import User
from src.plugins.github.utils import get_github
from src.plugins.github.cache import get_state, create_state, delete_state

from .platform import UserInfo, create_or_update_user


async def create_auth_link(info: UserInfo) -> str:
    """Create oauth link"""
    query = {
        "client_id": config.github_app.client_id,
        "state": await create_state(json.dumps(info)),
    }
    return f"https://github.com/login/oauth/authorize?{urllib.parse.urlencode(query)}"


async def get_state_data(state_id: str) -> UserInfo | None:
    """Get oauth state data"""
    return json.loads(data) if (data := await get_state(state_id)) is not None else None


async def delete_state_data(state_id: str) -> None:
    """Delete oauth state data"""
    return await delete_state(state_id)


async def create_auth_user(info: UserInfo, access_token: str) -> User:
    """Create oauth user model"""
    return await create_or_update_user(info, access_token=access_token)


async def get_token_by_code(code: str) -> str:
    """Get oauth token by oauth code"""
    github = get_github()
    data = {
        "client_id": config.github_app.client_id,
        "client_secret": config.github_app.client_secret,
        "code": code,
    }
    headers = {"Accept": "application/json"}
    response = await github.arequest(
        "POST",
        "https://github.com/login/oauth/access_token",
        json=data,
        headers=headers,
    )
    return response.json()["access_token"]
