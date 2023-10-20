import json
import os
import re
import time
from urllib import request
from bs4 import BeautifulSoup
import requests
import pandas as pd


#  获取总页数
def get_total_page(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    total_page = json.loads(soup.find('div', class_='page-box house-lst-page-box').get('page-data'))['totalPage']
    return int(total_page)


# 获取每页的房源信息
def get_house_info(url):
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')
    house_info_list = []
    print('house count :', end=' ')

    for house_info in soup.find_all('div', class_='info clear'):
        print(1 + len(house_info_list), end='\t')
        house_info_dict = {}
        # 获取标题
        title = house_info.find('div', class_='title')
        house_info_dict['标题'] = title.get_text().replace('\n', '').replace(' ', '').replace('/', '、')
        # 获取价格
        price_info = house_info.find('div', class_='priceInfo').get_text().replace('\n', '').replace(' ', '').split(
            '万')
        house_info_dict['总价（万）'] = price_info[0]
        house_info_dict['单价（元/平）'] = price_info[1].replace(',', '').replace('元/平', '')
        # 获取简要信息
        brief_info = house_info.find('div', class_='houseInfo').get_text().replace('\n', '').replace(' ', '').split('|')
        house_info_dict['楼层'] = brief_info[0]
        house_info_dict['建成时间'] = brief_info[1].replace('年建', '')
        # house_info_dict['户型'] = brief_info[2]
        house_info_dict['建筑面积（平米）'] = brief_info[3].replace('平米', '')
        house_info_dict['朝向'] = brief_info[4]
        # 获取小区名
        house_info_dict['小区'] = house_info.find('div', class_='positionInfo').get_text().replace('\n', '').replace(
            ' ', '')

        # 获取房源详细信息
        title_url = title.find('a').get('href')
        # print(title_url)
        res_fang = requests.get(title_url, headers=headers)
        res_fang_soup = BeautifulSoup(res_fang.text, 'lxml')
        info = res_fang_soup.find('div', class_='introContent').find_all('li')

        detailed_info = [i.get_text().replace(' ', '').replace('\n', '') for i in info]
        detailed_info = sorted(detailed_info)
        # 详细信息排序
        # 0 上次交易,   1 交易权属,     2 产权所属,     3 套内面积,     4 建筑类型,     5 建筑结构
        # 6 建筑面积,   7 户型结构,     8 房屋年限,     9 房屋户型,     10 房屋朝向,    11 房屋用途
        # 12 房本备件,  13 所在楼层,    14 抵押信息     15 挂牌时间,    16 梯户比例,    17 装修情况
        # 18 配备电梯
        house_info_dict['套内面积（平米）'] = detailed_info[3].replace('套内面积', '').replace('㎡', '')
        house_info_dict['户型'] = detailed_info[9].replace('房屋户型', '')
        house_info_dict['户型结构'] = detailed_info[7].replace('户型结构', '')
        house_info_dict['建筑类型'] = detailed_info[4].replace('建筑类型', '')
        house_info_dict['建筑结构'] = detailed_info[5].replace('建筑结构', '')
        house_info_dict['装修情况'] = detailed_info[17].replace('装修情况', '')
        house_info_dict['梯户比例'] = detailed_info[16].replace('梯户比例', '')
        if len(detailed_info) == 19:
            house_info_dict['配备电梯'] = detailed_info[18].replace('配备电梯', '')
        else:
            house_info_dict['配备电梯'] = '无'

        house_info_dict['房屋用途'] = detailed_info[11].replace('房屋用途', '')
        house_info_dict['房屋年限'] = detailed_info[8].replace('房屋年限', '')
        house_info_dict['挂牌时间'] = detailed_info[15].replace('挂牌时间', '')
        house_info_dict['上次交易'] = detailed_info[0].replace('上次交易', '')
        house_info_dict['交易权属'] = detailed_info[1].replace('交易权属', '')
        house_info_dict['产权所属'] = detailed_info[2].replace('产权所属', '')
        house_info_dict['抵押信息'] = detailed_info[14].replace('抵押信息', '')
        house_info_dict['房本备件'] = detailed_info[12].replace('房本备件', '')

        area_info = (res_fang_soup.find('div', class_='areaName')
                     .get_text().replace('所在区域', '')
                     .replace('\n', '').replace('\xa0', '').replace(' ', ''))
        house_info_dict['所在区域'] = area_info
        # 下载图片
        img = None  # 原户型图
        img_cut = None  # 裁剪的户型图
        img_err = None  # 无户型图
        try:
            # 获取原图
            img = res_fang_soup.find('div', class_='imgdiv').get('data-img')
        except:
            try:
                # 无原图，使用裁剪的户型图
                img_cut = res_fang_soup.find('img', alt=re.compile('-户型图')).get('src')
                img_w = img_cut[img_cut.find('w_') + 2:img_cut.find('h_') - 1]
                img_h = img_cut[img_cut.find('h_') + 2:img_cut.find('l_') - 1]
                img_cut = img_cut.replace(img_h, str(int(img_h) * 2)).replace(img_w, str(int(img_w) * 2))
            except:
                # 无户型图，用其他图片代替
                print('\n该房源无户型图：{}'.format(house_info_dict['标题']))
                img_err = 'https://s1.ljcdn.com/pegasus/redskull/images/common/default_house_detail.png?_v=20230816111335'

        # 防止重名，误用户型图
        while os.path.exists(img_dir + house_info_dict['标题'] + '.jpg'):
            print('\n该房源户型图已存在：{}'.format(house_info_dict['标题']))
            house_info_dict['标题'] += '1'

        with open(img_dir + house_info_dict['标题'] + '.jpg', 'wb') as f:
            if img is not None:
                res = request.urlopen(img)
            elif img_cut is not None:
                res = request.urlopen(img_cut)
            else:
                res = request.urlopen(img_err)
            f.write(res.read())
            f.close()

        # 留空位方便后续插图
        house_info_dict['户型图'] = img_dir + house_info_dict['标题'] + '.jpg'
        house_info_list.append(house_info_dict)
        # print(house_info_dict)
    print()
    return house_info_list


if __name__ == '__main__':
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
    url_base = 'https://cq.ke.com/ershoufang/'  # 基本链接
    url_place = 'dadukou'  # 查询地点
    url_para = 'sf1y3l1l2l3/'  # 参数配置
    # 查询参数对应的内容：
    # sf1:普通住宅
    # y1:5年以内,  y2:10年以内,   y3:15年以内,   y4:20年以内
    # l1:1室,     l2:2室,       l3:3室
    # lc1:低楼层,  lc2:中楼层,   lc3:高楼层

    # 创建图片缓存文件夹
    img_dir = './{}_img/'.format(url_place)
    os.makedirs(img_dir, exist_ok=True)

    total_pages = get_total_page(url=url_base + url_place + '/' + url_para)

    # 获取每页房源信息
    info_list = []
    for i in range(1, total_pages + 1):
        url = url_base + url_place + '/pg' + str(i) + url_para
        print('page/total pages : {}/{}'.format(i, total_pages))
        info_list.extend(get_house_info(url))

    # 保存到本地
    df = pd.DataFrame.from_records(info_list)
    order = ['标题', '所在区域', '小区', '建成时间', '总价（万）', '单价（元/平）', '建筑面积（平米）', '套内面积（平米）',
             '朝向',
             '楼层', '户型', '户型结构', '户型图', '建筑类型', '建筑结构', '装修情况', '配备电梯', '梯户比例',
             '挂牌时间',
             '上次交易', '房屋用途', '房屋年限', '交易权属', '产权所属']
    df = df[order]
    df.to_excel('./{}二手房源-{}.xlsx'.format(url_place, time.strftime('%Y-%m-%d', time.localtime())), index=False)
