import time
import random
from typing import List

import requests

from .header import make_header
from .typing_ import VideoInfo, Tag, Page, VideoDetails, SubtitleData, BVID_PATTERN

api_view_url = 'https://api.bilibili.com/x/web-interface/view'
api_tag_url = 'https://api.bilibili.com/x/web-interface/view/detail/tag'
api_pagelist_url = 'https://api.bilibili.com/x/player/pagelist?bvid={}'
api_video_details = 'https://api.bilibili.com/x/player/v2?bvid={}&cid={}'
api_search = 'https://api.bilibili.com/x/space/arc/search'
api_user = 'https://space.bilibili.com/{}'


def random_sleep(func, mu=2, sigma=0.3):
    def wrapper(*args, **kwargs):
        t = random.normalvariate(mu, sigma)
        time.sleep(max(t, 0))
        return func(*args, **kwargs)
    return wrapper


@random_sleep
def get_info(bvid: str, cookie=None) -> VideoInfo:
    """
    获取视频基本信息
    :param bvid: 视频bv号
    :param cookie:
    :return: 参见`response_demo/video_info.py`
    """
    assert BVID_PATTERN.match(bvid), f"Invalid BVID format: {bvid}"
    response = requests.get(api_view_url, params={'bvid': bvid}, headers=make_header(cookie))   # code, message, ttl, data
    assert response.status_code == 200, f"failed to get info, status code: {response.status_code}"
    return response.json()['data']


@random_sleep
def get_video_tags(bvid: str, cookie=None) -> List[Tag]:
    """
    获取视频标签信息
    :param bvid: 视频bv号
    :param cookie:
    :return: 参见`response_demo/video_tags.py`
    """
    assert BVID_PATTERN.match(bvid), f"Invalid BVID format: {bvid}"
    response = requests.get(api_tag_url, params={"bvid": bvid}, headers=make_header(cookie))  # code, message, ttl, data
    assert response.status_code == 200, f"failed to get tags, status code: {response.status_code}"
    return response.json()['data']


@random_sleep
def get_video_pages(bvid: str, cookie=None) -> List[Page]:
    """
    获取视频所有分P信息
    :param bvid: 视频bv号
    :param cookie:
    :return: 参见`response_demo/video_pages.py`
    """
    assert BVID_PATTERN.match(bvid), f"Invalid BVID format: {bvid}"
    response = requests.get(api_pagelist_url.format(bvid), headers=make_header(cookie))  # code, message, ttl, data
    assert response.status_code == 200, f"Failed to get video pages, status code: {response.status_code}"
    return response.json()['data']


@random_sleep
def get_user_access_details(bvid: str, cid: int, cookie=None) -> VideoDetails:
    """

    :param bvid: 视频bvid
    :param cid: 视频每一P的cid
    :param cookie:
    :return: 参见`response_demo/user_access_details.py`
    """
    assert BVID_PATTERN.match(bvid), f"Invalid BVID format: {bvid}"
    response = requests.get(api_video_details.format(bvid, cid), headers=make_header(cookie))  # code, message, ttl, data
    assert response.status_code == 200, f"Failed to get Bilibili video details, status code: {response.status_code}"
    return response.json()['data']


@random_sleep
def get_subtitles_from_url(subtitle_url, cookie=None) -> SubtitleData:
    """
    获取视频字幕
    :param subtitle_url: 字幕url，可以通过get_user_access_details获取
    :param cookie:
    :return: 参见`response_demo/subtitles.py`
    """
    response = requests.get(subtitle_url, headers=make_header(cookie))
    assert response.status_code == 200, f"failed to get subtitles, status code: {response.status_code}"
    return response.json()


def get_subtitles(bvid: str, cookie=None) -> SubtitleData:
    """
    获取某个bvid第一P的字幕
    :param bvid: 视频bvid
    :param cookie:
    :return:
    """
    pages = get_video_pages(bvid)

    cid = pages[0]['cid']  # 第一个分P的cid
    details = get_user_access_details(bvid, cid, cookie=cookie)

    subtitle_url = "https:" + details["subtitle"]["subtitles"][0]['subtitle_url']
    subtitles = get_subtitles_from_url(subtitle_url)
    return subtitles

