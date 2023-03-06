import time
import hashlib
import os
from flask import Flask, request, jsonify
from lxml import etree
from log import logger
import chatgpt

app = Flask(__name__)

TOKEN = os.environ['token']

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        return handle_receive(request.data)
    elif request.method == 'GET':
        return check_signature(request.args)
    else:
        message = 'Bad request.\n'
        logger(message)
        return message

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

def handle_receive(data):
    xml = etree.XML(data)

    from_user_name = xml.find('FromUserName').text
    to_user_name = xml.find('ToUserName').text
    content = xml.find('Content').text

    logger('received message:\nfrom: %s\nto: %s\ncontent:%s\n'%(from_user_name, to_user_name, content))

    reply = chatgpt.reply(content)

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


