import openpyxl
from openpyxl.drawing.image import Image
import os

place = 'jiangbei'
excel_file_path = './{}二手房源-2023-09-14.xlsx'.format(place)
image_name_column = 'A'
image_column = 'M'
image_path = './{}_img/'.format(place)

wb = openpyxl.load_workbook(excel_file_path)  # 打开excel工作簿
ws = wb.active  # 获取活跃工作表
for i, e in enumerate(ws[image_name_column], start=1):  # 取出第A列内容，从第二个算起
    image_file_path = os.path.join(image_path, f"{e.value}.jpg")  # 图片路径
    try:  # 因获取A列的第一行是标题，这里防止报错结束程序
        img = Image(image_file_path)  # 获取图片
        # dadukou_img.width, dadukou_img.height = (120, 120)  # 设置图片大小
        # 调整表格列宽和行高
        ws.column_dimensions[image_column].width = 30
        ws.row_dimensions[i].height = 150
        ws.add_image(img, anchor=image_column + str(i))  # 插入对应单元格
        # ws.insert_
    except Exception as e:
        print(e)
wb.save(excel_file_path)  # 保存
