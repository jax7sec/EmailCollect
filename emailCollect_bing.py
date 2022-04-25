# -*- coding:utf-8 -*-
import codecs
import csv
import os
import sys
import time
from bs4 import BeautifulSoup    #处理抓到的页面
import requests
import urllib
import re
 
def geturlfromBing(word,p):
    header = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, compress',
        'Accept-Language': 'en-us;q=0.5,en;q=0.3',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'
    }  # 定义头文件，伪装成浏览器
    timeOut = 4

    filename =  re.sub(r'[/\\:*?"<>|]', '', word) + ".txt"
    url = 'https://cn.bing.com/search?q=%22' + urllib.parse.quote(word) +'%22&first='  # word为关键词，first是bing用来分页的
    for k in range(1, p):
        time.sleep(2)
        path = url + str((k - 1) * 10 + 1)
        print(path)
        response = requests.get(path, headers=header, timeout=timeOut)
        page = response.content
        soup = BeautifulSoup(page, 'lxml')
        #print(soup)
        tagh2 = soup.find_all('h2')
        for h2 in tagh2:
            try:
                a = h2.find('a')
                target_url = a['href']
                print(target_url)
                with open(filename, "a+") as f:
                    try:
                        f.writelines(target_url + '\n')
                    except Exception as e:
                        print(e)
            except Exception as e:
                print(e)

def url2csv(word):
    csv_name = re.sub(r'[/\\:*?"<>|]', '', word) + ".csv"
    filename = re.sub(r'[/\\:*?"<>|]', '', word) + ".txt"
    csvfile = open(csv_name , 'a+', newline='', encoding="utf-8")  # python3
    csvfile.write(codecs.BOM_UTF8.decode())
    writer = csv.writer(csvfile, delimiter=',')
    keys = ['Email', 'URL', 'title', 'sensitive_pass', 'sensitive_pass_cn']
    writer.writerow(keys)

    list_url = ['']
    with open(filename, "r") as f:
        for line in f:
            try:
                list_url.append(line)
            except Exception as e:
                print(e)
    f.close()
    list_url = list(set(list_url)) #将文件中的url转成list去重

    for i in list_url:
        header = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, compress',
            'Accept-Language': 'en-us;q=0.5,en;q=0.3',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) Gecko/20100101 Firefox/97.0'
        }  # 定义头文件，伪装成浏览器
        timeOut = 4
        time.sleep(2)
        print(i.strip())
        if(i.strip()==''):
            continue
        url = str(i).strip()
        try:
            response = requests.get(url, headers=header, timeout=timeOut)
            page_content = response.text
            pattern = re.compile(r'[0-9a-zA-Z_]{0,19}'+word)
            title = re.findall('<title>(.+)</title>', page_content) #标题
            title = str(title)

            #敏感词匹配
            s_pass = "密码"
            sensitive_pass = re.search('password|pass|pw|key', page_content)
            sensitive_pass_cn =  re.search(s_pass, page_content)
            Email = re.findall(pattern, page_content)
            Email = list(set(Email)) #list去重
            '\n'.join(Email) #将list转为字符组并用换行符隔开
            print(Email)
            writer.writerow([Email, url, title, sensitive_pass, sensitive_pass_cn])
        except Exception as e:
            print(e)
    csvfile.close()


if __name__ == '__main__':
    try:
        word = sys.argv[1]
        p = sys.argv[2]
        p = int(p)
        print("正在收集后缀为%s的邮箱，将爬取前%s页"%(word,p))
        filename = re.sub(r'[/\\:*?"<>|]', '', word) + ".txt"
        csvname = re.sub(r'[/\\:*?"<>|]', '', word) + ".csv"
        try:
            if(os.path.exists(filename)):
                os.remove(filename)
                print("warning! rm ：'" + filename + "'")
            if (os.path.exists(csvname)):
                os.remove(csvname)
                print("warning! rm ：'" + csvname + "'")
        except Exception as r:
            print('未知错误 %s' %(r))
        geturlfromBing(word,p)
        url2csv(word)
    except:
        print("[-]输入参数有误，请检查！")
        print("[+]要爬取的邮箱后缀和爬取页数")
        print("[+]For example: python3 emailCollect_bing.py @qq.com 3")
    