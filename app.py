import time
import hashlib
import os
from flask import Flask, request, jsonify
from lxml import etree
import requests
from log import logger
from chatgpt import ChatGPT, Robot_Thread

app = Flask(__name__)

# wechat
TOKEN = os.environ['token']
# openai
api_key = os.environ['api_key']
model = os.environ.get('model', 'gpt-3.5-turbo')
preset = os.environ.get('preset', '')
memory_length = int(os.environ.get('memory_length', 100))

robot = ChatGPT(api_key, model, preset, memory_length)

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        # 请在此处选择api
        return handle_receive_auto(request.data)
        # handle_receive(request.data)
        # return ''
    elif request.method == 'GET':
        return check_signature(request.args)
    else:
        message = 'Bad request.\n'
        logger(message)
        return message

# 绑定服务器时用于验证
def check_signature(args):
    signature = args.get('signature')
    timestamp = args.get('timestamp')
    nonce = args.get('nonce')
    echostr = args.get('echostr')

    signature_list = [TOKEN, timestamp, nonce]
    signature_list.sort()
    # 组成字符串
    signature_str = "".join(signature_list)
    # 进行sha1算法加密
    sha1 = hashlib.sha1()
    # python3.x后的算法写法
    sha1.update(signature_str.encode("utf-8"))
    # 返回加密后的签名
    signature_sha1 = sha1.hexdigest()

    try:
        if signature == signature_sha1:
            logger('Authorization succeeded.\n')
            return echostr
        else:
            logger('Authorization failed.\nTOKEN: %s\ntimestamp: %s\nnonce: %s\nechostr: %s\n'%(TOKEN, timestamp, nonce, echostr))
            return jsonify({
                "message": "Authorization failed."
            })
    except Exception as e:
        logger(e)

# 请在main()中自行选择回复所使用的api

# 使用人工回复api
# 如果已经通过微信认证，强烈建议使用人工回复api，否则只能退而求其次使用自动回复api
def handle_receive(data):
    xml = etree.XML(data)

    from_user_name = xml.find('FromUserName').text
    to_user_name = xml.find('ToUserName').text
    content = xml.find('Content').text

    logger('received message:\nfrom: %s\nto: %s\ncontent:%s\n'%(from_user_name, to_user_name, content))

    access_token = get_access_token()
    robot_thread = Robot_Thread(robot, from_user_name, content, access_token)
    robot_thread.start()

# 获取access_token
def get_access_token():
    app_id = os.environ['app_id']
    app_secret = os.environ['app_secret']
    url = 'https://api.weixin.qq.com/cgi-bin/token'
    params = {
        'grant_type': 'client_credential',
        'appid': app_id,
        'secret': app_secret,
    }
    try:
        res = requests.get(url, params=params)
        access_token = res.json()['access_token']
        logger('receieved access token: %s\n'%access_token)
        return access_token
    except Exception as e:
        logger(e)

# 使用自动回复api
# 由于微信有5秒等待时间，若chatgpt在5秒内没说完，则可能造成重复回答或不回答，因此若已通过微信认证，请使用人工回复api进行异步回复
def handle_receive_auto(data):
    xml = etree.XML(data)

    from_user_name = xml.find('FromUserName').text
    to_user_name = xml.find('ToUserName').text
    content = xml.find('Content').text

    logger('received message:\nfrom: %s\nto: %s\ncontent:%s\n'%(from_user_name, to_user_name, content))

    reply = robot.reply(content)

    reply_dict = {
        'ToUserName': from_user_name,
        'FromUserName':  to_user_name,
        'CreateTime': int(time.time()),
        'Content': reply
    }

    logger('replied message:\n%s\n'%reply)

    xml = """
        <xml>
            <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
            <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
            <CreateTime>{CreateTime}</CreateTime>
            <MsgType><![CDATA[text]]></MsgType>
            <Content><![CDATA[{Content}]]></Content>
        </xml>
    """

    return xml.format(**reply_dict)
