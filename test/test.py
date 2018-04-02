#! python3.6
# -*- coding=utf-8 -*-

import requests

img_url = 'http://mmbiz.qpic.cn/mmbiz_jpg/BUslJxrfvOh5LJaQQMhLcrQs9798ql743icaOibHpVBBVxLYFhw7libKurZxKH6KBfficUbKKW4v7JBq3gaB78CP1A/0'
ir = requests.get(img_url)
if ir.status_code == 200:
    with open('logo.jpg', 'wb') as f:
        f.write(ir.content)