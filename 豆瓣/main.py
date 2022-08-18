# -*- coding: UTF-8 -*-
# 请看下面代码
import requests
import re
from bs4 import BeautifulSoup
import xlwt     # excel操作
import matplotlib.pyplot as plt
import numpy as np
from wordcloud import WordCloud, ImageColorGenerator
import jieba.analyse
from PIL import Image
import os

if not os.path.exists('./爬取内容'):
    os.mkdir('./爬取内容')
#爬取数据  豆瓣电影排行榜豆瓣新片，推荐的前十部
url = 'https://movie.douban.com/chart'

#UA伪装   反反扒机制
header = {
'User-Agent':
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.64 Safari/537.36 Edg/101.0.1210.53'
}

request = requests.get(url=url,headers=header)
request.encoding = 'utf-8'
result = request.text
print(result)

#数据解析、持久化存储
soup = BeautifulSoup(result,'html.parser')
text_all = soup.find('div',class_='indent').find_all('tr',class_='item')#包含电影图片、连接、评论等信息的标签tag
film_data = xlwt.Workbook(encoding="utf-8", style_compression=0)#将爬取内容置入Excel中
#建立名为《豆瓣电影排行榜豆瓣新片，推荐的前十部》的sheet1
worksheet = film_data.add_sheet("豆瓣电影排行榜豆瓣新片，推荐的前十部", cell_overwrite_ok=True)
column = ("电影详情链接", "电影名称", "基本信息","评分", "评价数","电影海报")#列信息

score_list = []#用于存储电影评分
remark_num_list = []#用于存储电影评论数量
film_message = []#用于存储电影基本信息
film_name = []#用于存储电影名字

#列名写入
for index, content in enumerate(column):
    worksheet.write(0, index, column[index])

#解析text_all中影片名字、图片、评论等基本信息
for step,i in enumerate(text_all):
    #爬取电影连接、名字、基本信息、评分、评论人数、电影海报连接与图片
    i = str(i)
    href = re.findall(r'<a.*?href="(.*?)".*?>',i,re.S)[0]
    print(href)
    name = re.findall(r'<a.*?title="(.*?)">',i,re.S)[0]
    print(name)
    message = re.findall(r'<p class="pl">(.*?)</p>',i,re.S)[0]
    print(message)
    score = re.findall(r'<span class="rating_nums">(.*?)</span>',i,re.S)[0]
    print(score)
    remark_num1 = re.findall(r'<span class="pl">(.*?)</span>',i,re.S)[0]
    remark_num2 = remark_num1.replace('(','')
    remark_num3 = remark_num2.replace('人评价','')
    remark_num = remark_num3.replace(')','')
    print(remark_num)
    img = re.findall(r'<img.*?src="(.*?)".*?>',i,re.S)[0]
    print(img)

    #存储图片
    img_name1 = img.split('.')[-1]
    img_name = str(step)+'.'+img_name1
    img_result = requests.get(url=img,headers=header).content
    with open('爬取内容/'+img_name,'wb') as fp:
        fp.write(img_result)

    #将电影信息写入Excel表格中
    worksheet.write(step + 1, 0, href)
    worksheet.write(step + 1, 1, name)
    worksheet.write(step + 1, 2, message)
    worksheet.write(step + 1, 3, score)
    worksheet.write(step + 1, 4, remark_num)
    worksheet.write(step + 1, 5, img)

    #用于作图
    score_list.append(float(score))
    remark_num_list.append(int(remark_num))
    film_message.append(message)
    film_name.append(name)

#保存Excel，导出文件
film_data.save('爬取内容/豆瓣电影排行榜豆瓣新片.xlsx')

#可视化

#中文设置
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']

#选择三位评分最高的电影
score_list = sorted(score_list,reverse=True)[0:3]  #评分由高到低
score_list = sorted(score_list)

score_film_name_list = ['唐顿庄园2','万湖会议','渔港的肉子酱']

#remark_num_list = sorted(remark_num_list,reverse=True)[0:3]  #评论人数由高到低
#评分最高前三部电影  score_list

plt.subplot(111)
plt.title("评分最高前三部电影")
plt.xlabel('电影名字')
plt.ylabel('评分')
plt.ylim(7.0,8.4)#y轴->8.0~8.4
#柱状图
plt.bar(score_film_name_list,height=score_list,width=0.3,align='center')
plt.savefig("评分最高前三部电影.png")
plt.show()

#评论人数最高前三部电影  remark_num_list
fig, ax = plt.subplots()#创建子图
#plt.title('各电影评论人数占比')
explode = (0,0.1,0.2,0,0.2,0.1,0,0.3,0.1,0)
ax.pie(remark_num_list,explode=explode,labels=film_name,autopct='%1.1f%%', shadow=True, startangle=80,radius=0.9)
remark_num_sum = 0
for i in remark_num_list:
    remark_num_sum += i
ax.set(aspect="equal", title='各电影评论人数占比(总评论：'+str(remark_num_sum)+')')#设置标题以及图形的对称
plt.savefig("各电影评论人数占比.png")
plt.show()


#电影信息词云构建  film_message
img1_to_mask = np.array(Image.open(r'alice.png'))

text = ''
for i in range(0,len(film_message)):
    text = text + film_message[i]
text_keyword = jieba.analyse.textrank(text, topK=40, withWeight=True)

text_keyword_dict = {}
for i in text_keyword:
    text_keyword_dict[i[0]] = i[1]

wc = WordCloud(font_path='simhei.ttf', background_color='White', max_words=50, mask=img1_to_mask)
wc.generate_from_frequencies(text_keyword_dict)
img_to_mask = ImageColorGenerator(img1_to_mask)  # 会改变图的颜色
plt.imshow(wc)
plt.imshow(wc.recolor(color_func=img_to_mask))
plt.axis("off")
plt.show()
wc.to_file('爬取内容/电影信息词云.png')

#结束
print("完毕！")

