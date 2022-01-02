# Date：2022.01.01
# Author：Edward
# Mail：edward.xyz@qq.com
# Blog：biubiubiu.ml
# Version：3.0

import json
import time
import random
import hashlib
import datetime
import requests
import threading


class Mogu:
    def __init__(self, _startDate, _device, _ltype, _stype, _phone, _password, _city, _province, _longitude, _latitude,
                 _address, _skey, _ua, _content):
        self.startDate = _startDate
        self.device = _device
        self.ltype = _ltype
        self.stype = _stype
        self.phone = _phone
        self.password = _password
        self.city = _city
        self.province = _province
        self.longitude = _longitude
        self.latitude = _latitude
        self.address = _address
        self.skey = _skey
        self.ua = _ua
        self.content = random.choice(_content)
        self.userId = None
        self.token = None
        self.planId = None
        self.planSign = None
        self.sign = None
        self.saveSign = None
        self.week = None
        self.startTime = None
        self.endTime = None

    @staticmethod
    def md5(word):
        hl = hashlib.md5()
        hl.update(word.encode(encoding="utf-8"))
        return hl.hexdigest()

    @staticmethod
    def thisWeek():
        _monday, _sunday = datetime.date.today(), datetime.date.today()
        oneDay = datetime.timedelta(days=1)
        while _monday.weekday() != 0:
            _monday -= oneDay
        while _sunday.weekday() != 6:
            _sunday += oneDay
        return f"{_monday} 00:00:00", f"{_sunday} 23:59:59"

    def login(self):
        _headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-CN;q=1, zh-Hans-CN;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/json;charset=UTF-8",
            "Host": "api.moguding.net:9000",
            "User-Agent": self.ua,
            "roleKey": ""
        }
        _loginJson = {
            "phone": self.phone,
            "loginType": self.ltype,
            "password": self.password
        }
        for _ in range(3):
            try:
                _resp = requests.post(
                    url="https://api.moguding.net:9000/session/user/v1/login",
                    headers=_headers,
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
                self.token = _resp["data"]["token"]
                self.userId = _resp["data"]["userId"]
                self.planSign = self.md5(self.userId + "student" + "3478cbbc33f84bd00d75d7dfa69e0daa")
                return True
        return None

    def getPlanId(self):
        _headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-CN;q=1, zh-Hans-CN;q=0.9",
            "Connection": "keep-alive",
            "Authorization": self.token,
            "Content-Type": "application/json;charset=UTF-8",
            "Host": "api.moguding.net:9000",
            "User-Agent": self.ua,
            "roleKey": "",
            "sign": self.planSign
        }
        _planJson = {
            "paramsType": "student"
        }
        for _ in range(3):
            try:
                _resp = requests.post(
                    url="https://api.moguding.net:9000/practice/plan/v3/getPlanByStu",
                    headers=_headers,
                    json=_planJson,
                    timeout=10
                ).json()
            except Exception as e:
                print("获取planId失败！正在重试...")
                print(e, e.__traceback__.tb_lineno)
                time.sleep(1)
                continue
            if _resp["code"] != 200:
                print(_resp)
                print("获取planId失败！")
                return None
            else:
                print("获取planId成功！")
                self.planId = _resp['data'][0]['planId']
                self.sign = self.md5(
                    self.device + self.stype + self.planId + self.userId + self.address + "3478cbbc33f84bd00d75d7dfa69e0daa")
                return True
        return None

    def checkin(self):
        _headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-CN;q=1, zh-Hans-CN;q=0.9",
            "Connection": "keep-alive",
            "Authorization": self.token,
            "Content-Type": "application/json;charset=UTF-8",
            "Host": "api.moguding.net:9000",
            "User-Agent": self.ua,
            "roleKey": "",
            "sign": self.sign
        }
        _signJson = {
            "device": self.device,
            "planId": self.planId,
            "country": "中国",
            "state": "NORMAL",
            "attendanceType": "",
            "address": self.address,
            "type": self.stype,
            "longitude": self.longitude,
            "city": self.city,
            "province": self.province,
            "latitude": self.latitude
        }
        for _ in range(3):
            try:
                _resp = requests.post(
                    url="https://api.moguding.net:9000/attendence/clock/v2/save",
                    headers=_headers,
                    json=_signJson,
                    timeout=10
                ).json()
            except Exception as e:
                print("打卡失败！正在重试...")
                print(e, e.__traceback__.tb_lineno)
                time.sleep(1)
                continue
            if _resp["code"] != 200:
                print(_resp)
                self.push("蘑菇钉打卡失败", str(_resp))
                return None
            else:
                print("打卡成功!")
                self.push("蘑菇钉打卡成功", str(_resp))
                return True
        return None

    def needWeek(self):
        _today = datetime.date.today()
        # 如果今天不是周日
        if _today.weekday() != 6:
            # 不需要提交周报
            print("无需提交周报")
            return None
        # 格式化开始日期
        _start = datetime.datetime.strptime(self.startDate, '%Y%m%d')
        # 获取实习开始年份
        _startYear = _start.year
        # 获取实习开始日期是所在年的第几周
        _startWeek = int(_start.strftime('%W'))
        # 获取当前年份
        _Year = _today.year
        # 获取当前是所在年的第几周
        _todayWeek = int(_today.strftime('%W'))
        # 判断是否跨年
        if _Year - _startYear > 0:
            # 总周数 = 当前周数 + 开始实习所在年的总周数
            _totalWeeks = _todayWeek + int(datetime.datetime.strptime(f'{_startYear}1231', '%Y%m%d').strftime('%W'))
            # 当前实习周数 = 总周数 - 开始实习的周数
            _week = _totalWeeks - _startWeek + 1
        else:
            _week = _todayWeek - _startWeek + 1
        # 获取本周的起止时间 即周一 ~ 周日
        _monday, _sunday = self.thisWeek()
        print(f"第{_week}周：{_monday} ~ {_sunday}")
        self.week = str(_week)
        self.startTime = _monday
        self.endTime = _sunday
        self.saveSign = self.md5(
            self.userId + "week" + self.planId + "第" + self.week + "周总结" + "3478cbbc33f84bd00d75d7dfa69e0daa")
        return True

    def save(self):
        _headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-CN;q=1, zh-Hans-CN;q=0.9",
            "Connection": "keep-alive",
            "Authorization": self.token,
            "Content-Type": "application/json;charset=UTF-8",
            "Host": "api.moguding.net:9000",
            "User-Agent": self.ua,
            "roleKey": "",
            "sign": self.saveSign
        }
        _weekJson = {
            "weeks": "第" + self.week + "周",
            "title": "第" + self.week + "周总结",
            "reportType": "week",
            "urlIsIslegal": False,
            "planId": self.planId,
            "startTime": self.startTime,
            "content": self.content,
            "endTime": self.endTime
        }
        for _ in range(3):
            try:
                _resp = requests.post(
                    url="https://api.moguding.net:9000/practice/paper/v2/save",
                    headers=_headers,
                    json=_weekJson,
                    timeout=10
                ).json()
            except Exception as e:
                print("提交周报失败！正在重试...")
                print(e, e.__traceback__.tb_lineno)
                time.sleep(1)
                continue
            if _resp["code"] != 200:
                print("提交周报失败！")
                print(_resp["msg"])
                self.push("提交周报失败", str(_resp))
                return None
            else:
                print("提交周报成功！")
                self.push("提交周报成功", str(_resp))
                return True
        return None

    def push(self, _title, _desp):
        send_url = "https://sctapi.ftqq.com/" + self.skey + ".send"
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

    def run(self):
        print("开始登录")
        login = self.login()
        if login is not None:
            print("开始获取planId")
            pid = self.getPlanId()
            if pid is not None:
                print("开始打卡")
                checkin = self.checkin()
                if checkin is not None:
                    print("开始提交周报")
                    needWeek = self.needWeek()
                    if needWeek is not None:
                        self.save()


def task(_startDate, _device, _ltype, _stype, _phone, _password, _city, _province, _longitude, _latitude, _address,
         _skey, _ua, _content):
    mogu = Mogu(_startDate, _device, _ltype, _stype, _phone, _password, _city, _province, _longitude, _latitude,
                _address,
                _skey, _ua, _content)
    mogu.run()


def main_handler(*args, **kwargs):
    with open("./user.json", "r", encoding="utf-8") as f:
        user = json.loads(f.read())
        info = user.get("info")
        content = user.get("content")
        for i in info:
            startDate = i.get("startDate")
            device = i.get("device")
            ltype = i.get("ltype")
            stype = i.get("stype")
            phone = i.get("phone")
            password = i.get("password")
            city = i.get("city")
            province = i.get("province")
            longitude = i.get("longitude")
            latitude = i.get("latitude")
            address = i.get("address")
            skey = i.get("skey")
            ua = i.get("ua")
            Task = threading.Thread(target=task, args=(
                startDate, device, ltype, stype, phone, password, city, province, longitude, latitude, address, skey,
                ua,content))
            Task.start()
            Task.join()
            print("Task Done")
