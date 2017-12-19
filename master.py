#!/usr/bin/env python
# encoding=utf-8

import requests
import json
from pymongo import MongoClient
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

DB = MongoClient('127.0.0.1', 27017)['zhihu_user']['collection']

BASE_URL = 'https://www.zhihu.com/api/v4/members/'

USER_INFO_URL = '?include=locations%2Cemployments%2Cgender%2Ceducations%2Cbusiness%2Cvoteup_count%2Cthanked_Count%2Cfollower_count%2Cfollowing_count%2Ccover_url%2Cfollowing_topic_count%2Cfollowing_question_count%2Cfollowing_favlists_count%2Cfollowing_columns_count%2Cavatar_hue%2Canswer_count%2Carticles_count%2Cpins_count%2Cquestion_count%2Ccolumns_count%2Ccommercial_question_count%2Cfavorite_count%2Cfavorited_count%2Clogs_count%2Cincluded_answers_count%2Cincluded_articles_count%2Cincluded_text%2Cmessage_thread_token%2Caccount_status%2Cis_active%2Cis_bind_phone%2Cis_force_renamed%2Cis_bind_sina%2Cis_privacy_protected%2Csina_weibo_url%2Csina_weibo_name%2Cshow_sina_weibo%2Cis_blocking%2Cis_blocked%2Cis_following%2Cis_followed%2Cis_org_createpin_white_user%2Cmutual_followees_count%2Cvote_to_count%2Cvote_from_count%2Cthank_to_count%2Cthank_from_count%2Cthanked_count%2Cdescription%2Chosted_live_count%2Cparticipated_live_count%2Callow_message%2Cindustry_category%2Corg_name%2Corg_homepage%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics'

FOLLOW_URL = '/followees?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&limit=20&'

MAX_DEPTH = 5

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Host': 'www.zhihu.com',
    'Referer': 'https://www.zhihu.com/people/zhao-finger/activities',
    'X-Requested-With': 'XMLHttpRequest',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Connection': 'close',
    'authorization': '打开浏览器F12获取',
    'Cookie': '打开浏览器F12获取',
    'X-UDID': 'ACDCrznFAAyPTjLJ_cwueRWmiX48eUpHRWY=',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.36',
}

def get_user_info(url_token):
    """
        获取用户信息以及存储
    """
    if DB.find_one({'url_token': url_token}) is None:
        url = BASE_URL + url_token + USER_INFO_URL
        user_json = json.loads(requests.get(url, headers=HEADERS).text)
        # 存储数据
        DB.update_one(
            filter={'_id': user_json.get('id')},
            update={'$set': user_json},
            upsert=True
        )
        print(user_json.get('name') + ' 存储完毕!')
    else:
        print('已经存储过了，jump!')
        return False


user_2d_list = [None] * MAX_DEPTH
for i in range(0, MAX_DEPTH): user_2d_list[i] = set()

now_depth = 0

def get_follow_user(url):
    """
    某个用户的所有关注者信息
    """

    follow_json = json.loads(requests.get(url, headers=HEADERS).text)
    follow_list = follow_json.get('data')

    if len(follow_list):
        for item in follow_list:
            url_token = item.get('url_token')
            user_2d_list[now_depth].add(url_token)
            get_user_info(url_token)
    else:
        pass

     # 获取下一页关注者
    if not follow_json.get('paging').get('is_end'):
        get_follow_user(follow_json.get('paging').get('next'))
    else:
        pass


def each_follow_user():
    """
    遍历已经抓取的用户
    """
    global now_depth, user_2d_list

    for index in range(0, MAX_DEPTH):
        now_depth += 1
        print('正在抓取第' + str(index) + '层用户数据！')
        for item in user_2d_list[index]:
            get_follow_user(BASE_URL + item + FOLLOW_URL)

    print('抓取完成，总共' + str(MAX_DEPTH) + '层')
    exit()

def main():
    user_2d_list[0].add('zhao-finger')
    each_follow_user()


if __name__ == '__main__':
    main()
