# encoding: utf-8
"""
@author: suchao
@file: report_process.py
@time: 2018/11/8 13:28
@desc:解析Report结果文件JSON类
"""

import json
import os
import sys
import requests

if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

global list_testLink
list_testLink = []


class CukeTest:
    def __init__(self):
        self.reports_path = os.path.join(os.path.dirname(os.getcwd()), "reports\\")

    # 获取JSON文件路径
    def getJsonFile(self):
        f_list = os.listdir(self.reports_path)
        for i in f_list:
            if os.path.splitext(i)[1] == '.json':
                abs_path = os.path.join(os.path.dirname(os.getcwd()), "reports\\%s" % (i))
                print abs_path
                return abs_path

    # 读取JSON文件
    def readJsonFile(self, file_path):
        with open(file_path) as load_f:
            list_load = json.load(load_f)
            return list_load

    # 解析读到的JSON文件内容里的一个场景
    def parseJson(self, rs_dict):
        dict_scenario = {}  # 发给TestLink数据里最外层的字典
        case_dict = {"data": []}  # 每个用例的数据

        # 给dict_scenario添加测试计划名称
        dict_scenario['planname'] = rs_dict['description']
        print "测试计划名称：", rs_dict['description']
        # 获取测试用例个数
        cases_count = len(rs_dict['elements'])
        print "获取用例个数:", cases_count

        # 遍历测试用例并解析
        for case in range(cases_count):
            # 每个测试用例的最终结果
            case_result = ""

            # 获取每个测试用例的id
            case_id = rs_dict['elements'][case]['name'].split(':', 1)[0];
            print "第%d个测试用例ID为%s:" % (case, case_id)

            # 获取每个测试用例的步数
            steps = len(rs_dict['elements'][0]['steps'])
            print "第%d个测试用例共有%d步" % (case, steps - 2)

            # 遍历每个测试用例每一步的结果
            for i in range(1, steps - 1):
                # 遍历每一步的结果，如果为failed，那么将case_result写为f
                if rs_dict['elements'][case]['steps'][i]['result']['status'] == "failed":
                    case_result = "f"
                    break

            # 遍历结束后，判断case_result的状态，如果不为f，那么就将case_result写为p
            if case_result != "f":
                case_result = "p"

            print "测试用例的结果为：", case_result

            # 组装每个测试用例的数据
            case_dict["data"].append({"caseid": case_id, "result": case_result, "message": ""})

            dict_scenario["data"] = case_dict["data"]
        return dict_scenario


if __name__ == '__main__':
    ct = CukeTest()
    # 得到JSON文件路径
    json_path = ct.getJsonFile()
    # 读取JSON内容
    list_json = ct.readJsonFile(json_path)

    # 遍历JSON内容里面一共有多少个场景
    print '一共有%d个场景' % (len(list_json))
    for scenario in list_json:
        rs_case = ct.parseJson(scenario)
        # 解析一个场景的JSON内容
        list_testLink.append(rs_case)

    print "发送给testLink的最终数据结果为:", list_testLink

    # 向TestLink接口发送Post请求
    url = "http://192.168.4.173:8085/api/v1/testlinkservice/fillAllResult"
    headers = {
        "Content-Type": "application/json;charset=UTF-8"
    }

    response = requests.post(url, data=json.dumps(list_testLink), headers=headers)
    print response.text
    print response.status_code
