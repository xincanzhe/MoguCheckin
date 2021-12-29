# Date：2021.12.29
# Author：Edward
# Mail：edward.xyz@qq.com
# Blog：biubiubiu.ml
# Version：2.0

import time
import hashlib
import requests

# 打卡配置
device = ""  # 设备 iOS 或 Android
ltype = ""  # 登录类型 ios 或 android
stype = ""  # 上班 START 下班 END
phone = ""  # 账号
password = ""  # 密码
city = "xx市"  # 城市
province = "xx省"  # 省份
longitude = ""  # 经度 高德地图API https://lbs.amap.com/tools/picker
latitude = ""  # 纬度
address = "xx省 · xx市 · xxx"  # 打卡位置
skey = ""  # Server酱推送服务 https://sct.ftqq.com/ 填写获取到的 send_key
UA = "gxy/3.4.1 (iPhone; iOS 14.4; Scale/3.00)"
# 苹果UA gxy/3.4.1 (iPhone; iOS 14.4; Scale/3.00)
# 安卓UA Mozilla/5.0 (Linux; U; Android 10; zh-cn; AQM-AL10 Build/HONORAQM-AL10) AppleWebKit/533.1 (KHTML, like Gecko) Version/5.0 Mobile Safari/533.1

loginUrl = "https://api.moguding.net:9000/session/user/v1/login"
saveUrl = "https://api.moguding.net:9000/attendence/clock/v2/save"
planUrl = "https://api.moguding.net:9000/practice/plan/v3/getPlanByStu"
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-CN;q=1, zh-Hans-CN;q=0.9",
    "Connection": "keep-alive",
    "Content-Type": "application/json;charset=UTF-8",
    "Host": "api.moguding.net:9000",
    "User-Agent": UA,
    "roleKey": ""
}


def push(_title, _desp):
    send_url = "https://sctapi.ftqq.com/" + skey + ".send"
    params = {"text": _title, "desp": _desp}
    try:
        _resp = requests.post(send_url, data=params).json()
        if not _resp["code"]:
            print("Server酱推送服务成功")
        else:
            print("Server酱推送服务失败")
    except Exception as e:
        print("Server酱推送服务失败")
        print(e, e.__traceback__.tb_lineno)


def getUserId():
    _loginJson = {
        "phone": phone,
        "loginType": ltype,
        "password": password
    }
    for _ in range(3):
        try:
            _resp = requests.post(
                url=loginUrl,
                headers=headers,
                json=_loginJson,
                timeout=10
            ).json()
        except Exception as e:
            print("登录失败！正在重试...")
            print(e, e.__traceback__.tb_lineno)
            time.sleep(1)
            continue
        if _resp["code"] != 200:
            print("登录失败！")
            return None
        else:
            print("登录成功！")
            headers["Authorization"] = _resp["data"]["token"]
            uid = _resp["data"]["userId"]
        return uid
    return None


def md5(word):
    hl = hashlib.md5()
    hl.update(word.encode(encoding="utf-8"))
    return hl.hexdigest()


def getPlanId(_id):
    _planJson = {
        "paramsType": "student"
    }
    headers["sign"] = md5(_id + "student" + "3478cbbc33f84bd00d75d7dfa69e0daa")
    for _ in range(3):
        try:
            _resp = requests.post(
                url=planUrl,
                headers=headers,
                json=_planJson,
                timeout=10
            ).json()
        except Exception as e:
            print("获取planId失败！正在重试...")
            print(e, e.__traceback__.tb_lineno)
            time.sleep(1)
            continue
        if _resp["code"] != 200:
            print("获取planId失败！")
            return None
        else:
            print("获取planId成功！")
            pid = _resp['data'][0]['planId']
        return pid
    return None


def main_handler(*args, **kwargs):
    print("开始登录")
    userId = getUserId()
    time.sleep(5)
    print("开始获取planId")
    planId = getPlanId(userId)
    time.sleep(5)
    print("开始打卡")
    headers["sign"] = md5(device + stype + planId + userId + address + "3478cbbc33f84bd00d75d7dfa69e0daa")
    saveJson = {
        "device": device,
        "planId": planId,
        "country": "中国",
        "state": "NORMAL",
        "attendanceType": "",
        "address": address,
        "type": stype,
        "longitude": longitude,
        "city": city,
        "province": province,
        "latitude": latitude
    }
    for _ in range(3):
        try:
            resp = requests.post(
                url=saveUrl,
                headers=headers,
                json=saveJson,
                timeout=10
            ).json()
        except Exception as e:
            print("打卡失败！正在重试...")
            print(e, e.__traceback__.tb_lineno)
            time.sleep(1)
            continue
        if resp["code"] == 200:
            print("打卡成功!")
            push("蘑菇钉打卡成功", str(resp))
            break
        else:
            print(resp)
            push("蘑菇钉打卡失败", str(resp))
