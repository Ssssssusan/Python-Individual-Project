#!/usr/bin/env python
# -*- coding: utf-8 -*
"""
- File name: machine_translation.py
- Author: 苏珊（201511680148）
- Date: 07/20/2018
- Description:
    1. 逐行读取 LocaleResource_en_US.properties 文件中的内容，并判断该行内容是否需要翻译。
    2. 需要翻译则提取待翻译内容，调用有道翻译API进行翻译，将结果写入命名为 LocaleResource_zh_CN.properties 的文件。
    3. 无需翻译则直接将原文写入命名为 LocaleResource_zh_CN.properties 的文件
"""

import urllib.request, json, time, hashlib, re


class Youdao():
    ''' Description: 有道翻译API '''
    def __init__(self, in_Lang, out_Lang):
        '''
        :description: 构造函数，初始化有道翻译所需参数
        :param str langFrom: 源语言
        :param str langTo: 目标语言
        :param str url: 有道翻译 api 的链接
        :param str appKey: 有道翻译 API 用户ID
        :param str appSecret: 有道翻译 API 用户密钥
        '''

        langFrom = in_Lang
        if (langFrom == 'zh-CHS'):
            langFrom = 'zh'
        elif (langFrom == 'en_US'):
            langFrom = 'EN'
        elif (langFrom == 'es_ES'):
            langFrom = 'es'
        langTo = out_Lang
        if (langTo == 'zh_CN'):
            langTo = 'zh-CHS'
        elif (langTo == 'en_US'):
            langTo = 'EN'
        elif (langTo == 'es_ES'):
            langTo = 'es'
        self.url = 'https://openapi.youdao.com/api/'
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.109 Safari/537.36",
        }
        self.appKey = '08d00a94ef3ac62f'  # 应用id
        self.appSecret = 'oRqukWQZni4iof6X0uhfHj9z0pXponZa'  # 应用密钥
        self.langFrom = langFrom  # 翻译前文字语言,auto为自动检查
        self.langTo = langTo  # 翻译后文字语言,auto为自动检查

    def getUrlEncodedData(self, queryText):
        '''
        :description:将数据进行url编码，并返回编码后的数据
        :param str queryText: 待翻译的文字
        :param str salt: 加密值
        :param str sign: 发送请求的所有数据
        :return str data: 返回url编码后的数据
        '''
        salt = str(int(round(time.time() * 1000)))  # 生成随机数
        sign_str = self.appKey + queryText + salt + self.appSecret
        sign = hashlib.md5(sign_str.encode("utf8")).hexdigest()  # 对sign.str进行统一编码，否则报错
        payload = {
            'q': queryText,
            'from': self.langFrom,
            'to': self.langTo,
            'appKey': self.appKey,
            'salt': salt,
            'sign': sign
        }

        data = urllib.parse.urlencode(payload)
        return (data)

    def parseHtml(self, html):
        '''
        :description: 解析页面，输出翻译结果
        :param str html: 翻译返回的页面内容
        :return str translationResult: 返回翻译结果
        '''
        data = json.loads(html.decode('utf-8'))
        translationResult = data['translation']
        if isinstance(translationResult, list):
            translationResult = translationResult[0]
        return translationResult

    def translate(self, queryText):
        '''
        :description: 连接 getUrlEncodedData 和 parseHtml
        :return str self.parseHtml: 返回翻译结果
        '''
        if queryText.strip():
            data = self.getUrlEncodedData(queryText)  # 获取url编码过的数据
            target_url = self.url + '?' + data  # 构造目标url
            request = urllib.request.Request(target_url, headers=self.headers)  # 构造请求
            response = urllib.request.urlopen(request)  # 发送请求
            return self.parseHtml(response.read())  # 解析，显示翻译结果
        else:
            return queryText


test_filename = "test.properties"                  # 测试文件
# en_filename = "LocaleResource_en_US.properties"    # 待翻译文件整体
zh_filename = "LocaleResource_zh_CN.properties"  # 生成文件名称

pattern = '([\s\S]*)(=)([\s\S]*)'  # 正则表达式匹配：以“=”为界两侧
p_except = '.+\.(css|gif|htm)$'    # 正则表达式匹配：css/gif/htm 字符串
strinfo = re.compile(' ')            # 正则表达式匹配：空格

youdao = Youdao('EN', 'zh')  # 实例化机器翻译类，参数：源语言，目标语言

with open(test_filename, "r")as en, open(zh_filename, "a") as zh:  # a 代表的文件读写模式为追加写
    lines = en.readlines()
    for line in lines:
        if line.strip() and line[0] != '#':               # 排除空行、以“#”开头的注释行
            match = re.match(pattern, line)                    # 匹配“=”及其两侧
            match_except = re.match(p_except, match.group(3))  # 匹配 css/gif/htm 字符串
            if match_except is None:                          # 如果未匹配到 css/gif/htm ，则调用翻译API
                trans = youdao.translate(match.group(3))            # 翻译“=”右侧内容
                line = match.group(1)+match.group(2)+trans          # 组合为原文格式
            else:                                              # 如果匹配到 css/gif/htm ，则移除字符串头尾空格
                line = line.strip()
            line = strinfo.sub('', line)                       # 删除字符串中多余空格字符，确保\n等标签格式正确
            zh.write(line+'\n')                                # 行尾添加换行符，并写入输出文件
            # print(line)                                      # 输出所有翻译结果，可用于监控进度
        else:                                             # 如为空行、注释行，则直接写入输出文件
            zh.write(line)

