"""
@Author         : yanyongyu
@Date           : 2024-05-23 16:57:40
@LastEditors    : yanyongyu
@LastEditTime   : 2024-05-23 16:59:37
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""

__author__ = "yanyongyu"

from datetime import timedelta

from src.providers.redis import redis_client

IMAGE_CACHE_KEY = "cache:github:image:{type}:{identifier}"
IMAGE_CACHE_EXPIRE = timedelta(days=1)


async def save_rendered_image(type: str, identifier: str, img: bytes) -> None:
    """Save rendered image to Redis."""
    await redis_client.set(
        IMAGE_CACHE_KEY.format(type=type, identifier=identifier),
        img,
        ex=IMAGE_CACHE_EXPIRE,
    )


async def get_rendered_image(type: str, identifier: str) -> bytes | None:
    """Get rendered image from Redis."""
    return await redis_client.get(
        IMAGE_CACHE_KEY.format(type=type, identifier=identifier)
    )
