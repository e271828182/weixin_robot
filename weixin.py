#! python3.6
# -*- coding=utf-8 -*-

from flask import Flask, request
from xml.etree import ElementTree as ET
from flask import render_template
import requests
from json import loads
from basic import Basic
import cv2
import random
from aip import AipSpeech

app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        echostr = request.args.get(key='echostr')
        return echostr
    else:
        data = request.get_data()
        print(data)
        xml = ET.fromstring(data)
        kwargs = dict(
            ToUserName=xml.findtext('.//ToUserName'),
            FromUserName=xml.findtext('.//FromUserName'),
            CreateTime=xml.findtext('.//CreateTime'),
            MsgType=xml.findtext('.//MsgType'),
            MsgId=xml.findtext('.//MsgId'),

            Content=xml.findtext('.//Content'),

            MediaId=xml.findtext('.//MediaId'),
            Format=xml.findtext('.//Format'),
            Recognition=xml.findtext('.//Recognition'),

            PicUrl=xml.findtext('.//PicUrl'),
        )
        if kwargs['MsgType'] == 'text':
            return handle_text(kwargs)
        if kwargs['MsgType'] == 'image':
            return handle_pic(kwargs)

        if kwargs['MsgType'] == 'voice':
            return handle_voice(kwargs)


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
    if img.status_code == 200:
        with open('123.jpg', 'wb') as f:
            f.write(img.content)
    accessToken = Basic().get_access_token()
    postUrl = "https://api.weixin.qq.com/cgi-bin/media/upload?access_token=%s&type=%s" % (accessToken, "image")
    generate_pic()
    files = {'file': open('123.jpg', 'rb')}
    r = requests.post(postUrl, files=files)
    if r.status_code == 200:
        resp = loads(r.text)
        MediaID = resp.get('media_id')
        return render_template(
            'pic.html',
            ToUserName=kwargs['ToUserName'],
            FromUserName=kwargs['FromUserName'],
            CreateTime=kwargs['CreateTime'],
            MsgType='image',
            MediaID=MediaID,
        )



def handle_voice(kwargs):
    accessToken = Basic().get_access_token()
    get_url = "https://api.weixin.qq.com/cgi-bin/media/get?access_token=%s&type=%s" % (accessToken, "image")
    r = requests.get(url=get_url)
    voice = r.content
    APP_ID = '11052668'
    API_KEY = 'lir2iuuDuVgcCSx82MAS0vEk'
    SECRET_KEY = 'dKZxNhEUdGDPxGbFrCZHYXAtGC6rDYmV'

    client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

    resp = client.asr(voice, 'amr', 16000, {
        'dev_pid': '1536',
    })

    if resp['err_no'] == 0:
        content = ','.join(resp['result'])
    else:
        content = resp['err_msg']

    return render_template(
        'text.html',
        ToUserName=kwargs['ToUserName'],
        FromUserName=kwargs['FromUserName'],
        CreateTime=kwargs['CreateTime'],
        MsgType='text',
        Content=content,
    )



def generate_pic():
    tar = "123.jpg"
    sample_image = cv2.imread(tar)

    # OpenCv人脸检测
    face_patterns = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
    faces = face_patterns.detectMultiScale(sample_image, scaleFactor=1.1, minNeighbors=8, minSize=(50, 50))
    # 圣诞帽
    hats = []
    for i in range(4):
        hats.append(cv2.imread('img/hat%d.png' % i, -1))

    for face in faces:
        # 随机一顶帽子
        hat = random.choice(hats)
        # 调整帽子尺寸
        scale = face[3] / hat.shape[0] * 1.25
        hat = cv2.resize(hat, (0, 0), fx=scale, fy=scale)
        # 根据人脸坐标调整帽子位置
        x_offset = int(face[0] + face[2] / 2 - hat.shape[1] / 2)
        y_offset = int(face[1] - hat.shape[0] / 2)
        # 计算贴图位置，注意防止超过边界的情况
        x1, x2 = max(x_offset, 0), min(x_offset + hat.shape[1], sample_image.shape[1])
        y1, y2 = max(y_offset, 0), min(y_offset + hat.shape[0], sample_image.shape[0])
        hat_x1 = max(0, -x_offset)
        hat_x2 = hat_x1 + x2 - x1
        hat_y1 = max(0, -y_offset)
        hat_y2 = hat_y1 + y2 - y1
        # 透明部分的处理
        alpha_h = hat[hat_y1:hat_y2, hat_x1:hat_x2, 3] / 255
        alpha = 1 - alpha_h
        # 按3个通道合并图片
        for c in range(0, 3):
            sample_image[y1:y2, x1:x2, c] = (
            alpha_h * hat[hat_y1:hat_y2, hat_x1:hat_x2, c] + alpha * sample_image[y1:y2, x1:x2, c])
    # 保存最终结果
    cv2.imwrite('123.jpg', sample_image)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True)
    # generate_pic()
