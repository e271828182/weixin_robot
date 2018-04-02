#!/usr/bin python
# -*- coding=utf-8 -*-

from flask import Flask, request
from xml.etree import ElementTree as ET
from flask import render_template
import requests
from json import loads

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        echostr = request.args.get(key='echostr')
        print(echostr)
        return echostr
    else:
        data = request.get_data()
        xml = ET.fromstring(data)
        ToUserName = xml.findtext('.//ToUserName')
        FromUserName = xml.findtext('.//FromUserName')
        CreateTime = xml.findtext('.//CreateTime')
        Content = xml.findtext('.//Content')
        MsgId = xml.findtext('.//MsgId')
        if u'你是谁' in Content:
            Content = u'我是star'
        else:
            json_resp = requests.get(url='http://op.juhe.cn/robot/index?info=%s&key=a6593d8af4adb1ff0164dbd215d07f3c'%Content.encode('utf-8')).text
            result = loads(json_resp)
            Content = result['result']['text']
        resp = render_template(
            'index.html',
            ToUserName=ToUserName,
            FromUserName=FromUserName,
            CreateTime=CreateTime,
            MsgType='text',
            Content=Content,
        )
        return resp



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=False)

