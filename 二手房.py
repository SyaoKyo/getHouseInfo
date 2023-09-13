import json
import os
import re
from urllib import request
from bs4 import BeautifulSoup
import requests
import time
import csv

# sf1 : 普通住宅
# y1 : 5年以内
# l1 : 1室，l2 : 2室，l3 : 3室
url_base = 'https://cq.ke.com/ershoufang/dadukou/sf1y1l1l2l3/'

# 请求头
headers = {
    'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
    'Origin': "https://cq.ke.com/",
    'Referer': "https://cq.ke.com/",
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/91.0.4472.106 '
                  'Safari/537.36',
}


#  获取总页数
def get_total_page(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    total_page = json.loads(soup.find('div', class_='page-box house-lst-page-box').get('page-data'))['totalPage']
    print(total_page)
    return int(total_page)


total_pages = get_total_page(url_base)


# 获取每页的房源信息
def get_house_info(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    house_info_list = []
    for house_info in soup.find_all('div', class_='info clear'):
        house_info_dict = {}
        house_info_dict['title'] = house_info.find('div', class_='title').get_text()
        house_info_dict['price'] = house_info.find('div', class_='priceInfo').get_text()
        house_info_dict['area'] = house_info.find('div', class_='houseInfo').get_text()
        house_info_dict['position'] = house_info.find('div', class_='positionInfo').get_text()
        house_info_list.append(house_info_dict)
        print(house_info_dict)
    return house_info_list


url_base = 'https://cq.ke.com/ershoufang/dadukou/'
url_para = 'sf1y1l1l2l3/'

# 获取每页房源信息
for i in range(1, total_pages + 1):
    url = url_base + 'pg' + str(i) + url_para
    print('page:{}'.format(i))
    info_list = get_house_info(url)
