#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@Author         : yanyongyu
@Date           : 2021-03-09 16:45:25
@LastEditors    : yanyongyu
@LastEditTime   : 2021-04-02 14:50:56
@Description    : None
@GitHub         : https://github.com/yanyongyu
"""
__author__ = "yanyongyu"

from pathlib import Path
from typing import List, Optional

import markdown

from src.libs import html2img
from src.libs.github import Github
from ... import github_config as config
from src.libs.github.models import Issue
from src.libs.playwright import get_new_page


async def get_issue(owner: str,
                    repo_name: str,
                    number: int,
                    token: Optional[str] = None) -> Issue:
    if token:
        g = Github(token)
    elif config.github_client_id and config.github_client_secret:
        g = Github(config.github_client_id, config.github_client_secret)
    else:
        g = Github()

    try:
        repo = await g.get_repo(f"{owner}/{repo_name}", True)
        issue = await repo.get_issue(number)
    finally:
        await g.close()
    return issue


HEADER = """
# {title} <font color=#8b949e>{type}#{number}</font>

<span class="State State--{status}">{status}</span> <small><font color=#8b949e>{comments} comments</font></small>
"""
COMMENT_HEADER = """
### **{login}** <small><font color=#8b949e>{updated_at}</font></small>
"""
DIFF_CONTENT = """
````diff
{diff_content}
````
"""
OPTIONS: dict = {"encoding": "utf-8"}
if config.xvfb_installed:
    OPTIONS["xvfb"] = ""
CSS_FILES: List[str] = [
    str(Path(__file__).parent / "github.css"),
    str(Path(__file__).parent / "status.css")
]


async def issue_diff_to_image(issue: Issue,
                              width: int = 800,
                              wkhtmltoimage: bool = False) -> Optional[bytes]:
    if not issue.is_pull_request:
        return

    diff_url = issue.pull_request.diff_url
    try:
        response = await issue.requester.request("GET", diff_url)
    finally:
        await issue.close()
    diff_content = response.text
    html = '<article class="markdown-body">' + markdown.markdown(
        HEADER.format(title=issue.title,
                      type="pr",
                      number=issue.number,
                      status=issue.state,
                      comments=issue.comments) +
        DIFF_CONTENT.format(diff_content=diff_content),
        extensions=["fenced_code", "codehilite"],
        extension_configs={"codehilite": {
            "noclasses": True
        }}) + "</article>"

    OPTIONS["width"] = width
    imgkit = await html2img.IMGKit(html,
                                   "string",
                                   options=OPTIONS,
                                   css=CSS_FILES)
    if not wkhtmltoimage:
        imgkit._prepend_css(CSS_FILES)
        html: str = imgkit.source.get_source()  # type: ignore
        async with get_new_page(viewport={
                "width": width,
                "height": 300
        }) as page:
            await page.set_content(html)
            img = await page.screenshot(full_page=True)
            return img
    else:
        return await imgkit.to_img()


async def issue_to_image(issue: Issue,
                         width: int = 800,
                         wkhtmltoimage: bool = False) -> Optional[bytes]:
    CONTENT = HEADER + COMMENT_HEADER
    if issue.body_html:
        html = '<article class="markdown-body">' + markdown.markdown(
            CONTENT.format(
                title=issue.title,
                type="pr" if issue.is_pull_request else "issue",
                number=issue.number,
                status=issue.state,
                comments=issue.comments,
                login=issue.user.login,
                updated_at=issue.updated_at.strftime(
                    "%Y-%m-%d %H:%M:%S"))) + issue.body_html + "</article>"
    elif issue.body:
        html = '<article class="markdown-body">' + markdown.markdown(
            CONTENT.format(
                title=issue.title,
                type="pr" if issue.is_pull_request else "issue",
                number=issue.number,
                status=issue.state,
                comments=issue.comments,
                login=issue.user.login,
                updated_at=issue.updated_at.strftime("%Y-%m-%d %H:%M:%S")) +
            issue.body,
            extensions=["fenced_code", "codehilite"],
            extension_configs={"codehilite": {
                "noclasses": True
            }}) + "</article>"
    else:
        html = '<article class="markdown-body">' + markdown.markdown(
            CONTENT.format(title=issue.title,
                           type="pr" if issue.is_pull_request else "issue",
                           number=issue.number,
                           status=issue.state,
                           comments=issue.comments,
                           login=issue.user.login,
                           updated_at=issue.updated_at.strftime(
                               "%Y-%m-%d %H:%M:%S")) +
            "_No description provided._\n") + "</article>"

    try:
        comments = await issue.get_comments()
        async for comment in comments:
            if comment.body_html:
                html += markdown.markdown(
                    COMMENT_HEADER.format(
                        login=comment.user.login,
                        updated_at=comment.updated_at)) + comment.body_html
            elif comment.body:
                html += markdown.markdown(
                    COMMENT_HEADER.format(login=comment.user.login,
                                          updated_at=comment.updated_at) +
                    comment.body,
                    extensions=["fenced_code", "codehilite"],
                    extension_configs={"codehilite": {
                        "noclasses": True
                    }})
            else:
                html += markdown.markdown(
                    COMMENT_HEADER.format(login=comment.user.login,
                                          updated_at=comment.updated_at) +
                    "_No description provided._\n")
    finally:
        await issue.close()

    OPTIONS["width"] = width
    imgkit = await html2img.IMGKit(html,
                                   "string",
                                   options=OPTIONS,
                                   css=CSS_FILES)
    if not wkhtmltoimage:
        imgkit._prepend_css(CSS_FILES)
        html: str = imgkit.source.get_source()  # type: ignore
        async with get_new_page(viewport={
                "width": width,
                "height": 300
        }) as page:
            await page.set_content(html)
            img = await page.screenshot(full_page=True)
            return img
    else:
        return await imgkit.to_img()
