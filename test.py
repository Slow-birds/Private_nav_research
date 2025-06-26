import pandas as pd
import requests

def get_data(custom_id,end_time):
    url = 'https://www.gtht.com.cn/link/common/apiajax/ajaxMappingHandler'
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'JSESSIONID=449B49B626A958173E5BA6276238CC63; oem.userid=120493; client=2; themec=77008; JSESSIONID=BE190D4CE963AF87061C7607B9CCBA27; linkgtja=Dkd2%2FjxvtUIFG4%2BkT0HU6m8NP4sqFzpM4pTwCdXl464KjBgYHWj%2F6%2BPlaqKZreEH%2F9%2FGVSXbhiDw0ASvzNRP0806U%2FeGfgKHKiY9Z3yD9CKctpjEMBfNDrvYl220mx8dqxcvvNL5AK2f8xb304zZO4pbeYKPdNC07Feq9nYRXLr%2FX49yHOcKRyUcafi%2BVRk3BLt57Q8pTKsYAysTxxoOFyBcj9rFZG6Vl5xRwWo%2FRc%2FO7cL0JNgYcZ%2BFT0HwHXafMEoF5DZcpOY5hikSt4enFt2aAueWzatXQzi6IHtbeMRzMrhO9PO%2BdSVjPRw%2B9omG4uwS%2FiTy6hyyDfTNsAIHXg%3D%3D; link.sessionid=2506269b3a4ed75e6241d597c7e09eb7b6f953026146; all.sessionid=2506269b3a4ed75e6241d597c7e09eb7b6f953026146; LtpaToken=4bkxnyhMUNRR37TGVRMlBZ3aRywVFtn4GxV/mOTu0yohlndb9Pw9yVgP3pY2xrlBOkqIZMx0sPIzBXPsG6JaOpoqBFZQDBUS+QmzX5U0ztb6qyM6YycWOZxI++hBms8ynpt7TLakWzoeeH6moK6uoEFq2bjPfPeWBvMp0eipXJPAM0nAiX6yctpsvmwv6f1NA96Pxws1pZi8hga7RGSaRTntnPhC0NgYJrefXVw05utw3ENm03T+11ViOT2nUSqBeU38S8OfQA9aV+Quyz0GuABushSK0LbZOxtoI5GIWUTRQx9xkKxKjJ609ZnYBlKh0p10KTJZ7wsPVvIVMEY3PvdzC+mSWv0Nz48vCxgdGUlkeol58QBEvzZN6jbJGd+/lV0ejP3lQQN4Hma+jIhrk9BccZBptcYcYSA6RX8v6TrBOI4C/zLNLKCVnJ3xN4MPB6ijDG1BDZzBJ61FTsnGeQ==; domain=https://www.gtht.com.cn; oem.sessionid=2506269b3a4ed75e6241d597c7e09eb7b6f953026146; sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22026146%22%2C%22first_id%22%3A%22197aa9edaac937-024fc8efeaa62c-29726c34-2073600-197aa9edaad7d9%22%2C%22props%22%3A%7B%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTk3YWE5ZWRhYWM5MzctMDI0ZmM4ZWZlYWE2MmMtMjk3MjZjMzQtMjA3MzYwMC0xOTdhYTllZGFhZDdkOSIsIiRpZGVudGl0eV9sb2dpbl9pZCI6IjAyNjE0NiJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%22026146%22%7D%2C%22%24device_id%22%3A%22197aa9edaac937-024fc8efeaa62c-29726c34-2073600-197aa9edaad7d9%22%7D',
        'Origin': 'https://www.gtht.com.cn',
        'Referer': 'https://www.gtht.com.cn/bst/vpnWeb/rank/no-referrer',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)  Chrome/109.0.0.0 GTJABrowser/2.1.0.6 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="109"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    params = {
        'sysId': '100',
        'funId': 'RPT_RANK_Q0051',
    }
    data = f'data={{"Param":"{{\\"id\\":\\"{custom_id}\\",\\"begindate\\":\\"{end_time}\\"}}","Type":"RPT_RANK_Q0051","Page":{{"CurrentPage":1,"PageSize":9999}}}}'
    response = requests.post(url,params=params,headers=headers,data=data)
    json_data = response.json()["Data"]
    return json_data

# 营业收入
def operating_data_format(json_data):
    all_list = []
    for i in json_data:
        list = [
            i["RANKNAME"],
            i["COMPNAME"],
            i["BRANCH_NAME"],
            i["ORGCODE"],
            i["V1"],
            i["V2"],
            i["V3"],
            i["V4"],
            i["V5"]
        ]
        all_list.append(list)
    return all_list
def operating_income(dict,end_time):
    dict = {key: dict[key] for key in list(dict.keys())[0:4]}
    for key,value in dict.items():
            json_data = get_data(value,end_time)
            all_list = operating_data_format(json_data)
            data = pd.DataFrame(all_list, columns=["排名","分公司","分支编码","营业部","营业收入","交易类收入","借贷类收入","委托类收入","其他类收入"])
            if key == "营业收入_分公司月度" or key == "营业收入_分公司累计":
                data.drop(columns=["分支编码","营业部"], inplace=True)
            with pd.ExcelWriter("data_income.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                data.to_excel(writer, sheet_name=key, index=False)
            print(f"sheet-{key}-写入成功")

# 交易类收入
def trading_data_format(json_data):
    all_list = []
    for i in json_data:
        list = [
            i["RANKNAME"],
            i["COMPNAME"],
            i["ORGCODE"],
            i["BRANCH_NAME"],
            i["V1"],
            i["V2"],
            i["V3"],
            i["V4"],
            i["V5"],
            i["V6"],
            i["V7"],
            i["V8"],
            i["V9"],
            i["V10"],
            i["V11"],
            i["V12"],
            i["V13"],
            i["V14"],
            i["V15"],
        ]
        all_list.append(list)
    return all_list
def trading_income(dict,end_time):
    dict = {key: dict[key] for key in list(dict.keys())[4:8]}
    for key,value in dict.items():
            json_data = get_data(value,end_time)
            all_list = trading_data_format(json_data)
            data = pd.DataFrame(all_list, columns=["排名","分公司","分支编码","营业部","交易类收入","佣金类收入","其中_普通交易佣金收入","其中_信用交易佣金收入",
                                                   "其中_其他机构佣金协同收","其中_私募佣金协同收入","其中_港股通佣金收入","其中：衍生品佣金收入","其中_规费",
                                                   "其中_经纪人支出","保证金利差收入","期货IB分成收入","其中_其他业务分成收入","财税返还手续费收入","其他收入"])
            if key == "交易类收入_分公司月度" or key == "交易类收入_分公司累计":
                data.drop(columns=["分支编码","营业部"], inplace=True)
            with pd.ExcelWriter("data_income.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                data.to_excel(writer, sheet_name=key, index=False)
            print(f"sheet-{key}-写入成功")

# 借贷类收入
def borrowing_data_format(json_data):
    all_list = []
    for i in json_data:
        list = [
            i["RANKNAME"],
            i["COMPNAME"],
            i["ORGCODE"],
            i["BRANCH_NAME"],
            i["V1"],
            i["V2"],
            i["V3"]
        ]
        all_list.append(list)
    return all_list
def borrowing_income(dict,end_time):
    dict = {key: dict[key] for key in list(dict.keys())[8:12]}
    for key,value in dict.items():
            json_data = get_data(value,end_time)
            all_list = borrowing_data_format(json_data)
            data = pd.DataFrame(all_list, columns=["排名","分公司","分支编码","营业部","借贷类收入","其中_融资融券息差收入","其中_类贷款业务利息收入"])
            if key == "借贷类收入_分公司月度" or key == "借贷类收入_分公司累计":
                data.drop(columns=["分支编码","营业部"], inplace=True)
            with pd.ExcelWriter("data_income.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                data.to_excel(writer, sheet_name=key, index=False)
            print(f"sheet-{key}写入成功")

# 委托类收入
def entrusting_data_format(json_data):
    all_list = []
    for i in json_data:
        list = [
            i["RANKNAME"],
            i["COMPNAME"],
            i["ORGCODE"],
            i["BRANCH_NAME"],
            i["V1"],
            i["V2"],
            i["V3"],
            i["V4"],
            i["V5"],
            i["V6"],
            i["V7"],
            i["V8"],
            i["V9"],
            i["V10"],
            i["V11"],
            i["V12"],
            i["V13"],
            i["V14"],
            i["V15"],
            i["V16"],
            i["V17"],
        ]
        all_list.append(list)
    return all_list
def entrusting_income(dict,end_time):
    dict = {key: dict[key] for key in list(dict.keys())[12:16]}
    for key,value in dict.items():
            json_data = get_data(value,end_time)
            all_list = entrusting_data_format(json_data)
            data = pd.DataFrame(all_list, columns=["排名","分公司","分支编码","营业部","委托类收入","其中_产品代销手续费","其中_公募尾随收入","其中_私募及其他产品存续收入",
                                                   "其中_投顾签约业务收入","包含_公募基金投顾收入","其中_私客专户收入","其中_网上商城业务收入","其中_其他投资咨询收入",
                                                   "其中_资管业务分成收入(不含定向)","其中_资管业务分成收入","其中_固收业务分成收入","其中_柜台市场业务分成收入",
                                                   "其中_场外期权分成收入","其中_产品利息支出","其中_资产托管业务分成收入","其中_其他协同收入"])
            if key == "委托类收入_分公司月度" or key == "委托类收入_分公司累计":
                data.drop(columns=["分支编码","营业部"], inplace=True)
            with pd.ExcelWriter("data_income.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                data.to_excel(writer, sheet_name=key, index=False)
            print(f"sheet-{key}-写入成功")

# 其他类收入
def other_data_format(json_data):
    all_list = []
    for i in json_data:
        list = [
            i["RANKNAME"],
            i["COMPNAME"],
            i["ORGCODE"],
            i["BRANCH_NAME"],
            i["V1"],
            i["V2"],
            i["V3"]
        ]
        all_list.append(list)
    return all_list
def other_income(dict,end_time):
    dict = {key: dict[key] for key in list(dict.keys())[16:20]}
    for key,value in dict.items():
            json_data = get_data(value,end_time)
            all_list = other_data_format(json_data)
            data = pd.DataFrame(all_list, columns=["排名","分公司","分支编码","营业部","其他类收入","其中_项目协作收入","其中_财务顾问收入"])
            if key == "其他类收入_分公司月度" or key == "其他类收入_分公司累计":
                data.drop(columns=["分支编码","营业部"], inplace=True)
            with pd.ExcelWriter("data_income.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                data.to_excel(writer, sheet_name=key, index=False)
            print(f"sheet-{key}-写入成功")


if __name__ == '__main__':
    end_time = "202505"
    dict = {
        "营业收入_分公司月度":"id_01_72_01_01_lf",
        "营业收入_营业部月度":"id_01_72_01_02_lf",
        "营业收入_分公司累计":"id_01_72_02_01_lf",
        "营业收入_营业部累计":"id_01_72_02_02_lf",
        "交易类收入_分公司月度":"id_01_73_01_01_lf",
        "交易类收入_营业部月度":"id_01_73_01_02_lf",
        "交易类收入_分公司累计":"id_01_73_02_01_lf",
        "交易类收入_营业部累计":"id_01_73_02_02_lf",
        "借贷类收入_分公司月度":"id_01_74_01_01_lf",
        "借贷类收入_营业部月度":"id_01_74_01_02_lf",
        "借贷类收入_分公司累计":"id_01_74_02_01_lf",
        "借贷类收入_营业部累计":"id_01_74_02_02_lf",
        "委托类收入_分公司月度":"id_01_75_01_01_lf",
        "委托类收入_营业部月度":"id_01_75_01_02_lf",
        "委托类收入_分公司累计":"id_01_75_02_01_lf",
        "委托类收入_营业部累计":"id_01_75_02_02_lf",
        "其他类收入_分公司月度":"id_01_76_01_01_lf",
        "其他类收入_营业部月度":"id_01_76_01_02_lf",
        "其他类收入_分公司累计":"id_01_76_02_01_lf",
        "其他类收入_营业部累计":"id_01_76_02_02_lf",
    }
    operating_income(dict,end_time)
    trading_income(dict,end_time)
    borrowing_income(dict,end_time)
    entrusting_income(dict,end_time)
    other_income(dict,end_time)
