#! python3.6
# -*- coding=utf-8 -*-

from flask import Flask, request
from xml.etree import ElementTree as ET
from flask import render_template
import requests
from json import loads
from basic import Basic

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
        print(data)
        kwargs = dict(
            ToUserName=xml.findtext('.//ToUserName'),
            FromUserName=xml.findtext('.//FromUserName'),
            CreateTime=xml.findtext('.//CreateTime'),
            Content=xml.findtext('.//Content'),
            MsgId=xml.findtext('.//MsgId'),
            MsgType=xml.findtext('.//MsgType')
        )
        if kwargs['MsgType'] == 'text':
            return handle_text(kwargs)
        if kwargs['MsgType'] == 'image':
            kwargs['PicUrl'] = xml.findtext('.//PicUrl')
            kwargs['MediaId'] = xml.findtext('.//MediaId')
            return handle_pic(kwargs)


def handle_text(kwargs):
    if u'你是谁' in kwargs['Content']:
        content = u'我是star'
    else:
        json_resp = requests.get(
            url='http://op.juhe.cn/robot/index?info=%s&key=a6593d8af4adb1ff0164dbd215d07f3c' % kwargs['Content'].encode(
                'utf-8')).text
        result = loads(json_resp)
        content = result['result']['text']
    return render_template(
        'text.html',
        ToUserName=kwargs['ToUserName'],
        FromUserName=kwargs['FromUserName'],
        CreateTime=kwargs['CreateTime'],
        MsgType='text',
        Content=content,
    )

def handle_pic(kwargs):
    img = requests.get(kwargs['PicUrl'])
    accessToken = Basic().get_access_token()
    postUrl = "https://api.weixin.qq.com/cgi-bin/media/upload?access_token=%s&type=%s" % (accessToken, "image")
    if img.status_code == 200:
        resp_json = loads(requests.post(url=postUrl, files=img))
        MediaID = resp_json.get('MediaID')
        return render_template(
            'pic.html',
            ToUserName=kwargs['ToUserName'],
            FromUserName=kwargs['FromUserName'],
            CreateTime=kwargs['CreateTime'],
            MsgType='image',
            MediaID=MediaID,
        )





if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
