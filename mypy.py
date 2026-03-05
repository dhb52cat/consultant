from flask import Flask, request, make_response
import xml.etree.ElementTree as ET

app = Flask(__name__)

@app.route('/wechat', methods=['GET', 'POST'])
def wechat():
    if request.method == 'GET':
        # 微信服务器验证
        return request.args.get("echostr", "")
    
    elif request.method == 'POST':
        # 解析微信发送的 XML 消息
        xml_data = request.data
        root = ET.fromstring(xml_data)
        msg_type = root.find("MsgType").text
        content = root.find("Content").text
        from_user = root.find("FromUserName").text  # 用户 openid
        to_user = root.find("ToUserName").text  # 公众号 ID
        
        # 处理用户发送的 "openid"
        if msg_type == "text" and content.strip().lower() == "openid":
            return reply_text(from_user, to_user, f"您的 OpenID 是：{from_user}")

    return ""

def reply_text(to_user, from_user, content):
    """构造文本消息的 XML 回复"""
    reply = f"""
    <xml>
        <ToUserName><![CDATA[{to_user}]]></ToUserName>
        <FromUserName><![CDATA[{from_user}]]></FromUserName>
        <CreateTime> {int(time.time())} </CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{content}]]></Content>
    </xml>
    """
    return make_response(reply)

if __name__ == '__main__':
    app.run(port=8000, debug=True)
