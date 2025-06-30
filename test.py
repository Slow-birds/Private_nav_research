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
    'Cookie': 'JSESSIONID=0FE1250068D56AFB169A00D94442C8C8; oem.userid=120493; client=2; themec=77008; JSESSIONID=8175BE6DE2391C670B27F8F44C50A60E; linkgtja=Dkd2%2FjxvtUIFG4%2BkT0HU6m8NP4sqFzpM4pTwCdXl464KjBgYHWj%2F6%2BPlaqKZreEHj20V7uMgxIBTIrNKFJf9FpmGdXHEdJjcLp9PbFsQvPVBtxwEhOB03SZxyQ1DMB8KfkKwg1w4xSKFDzzN4eCbauY1NwcZ4Ehd%2BVpw5ziH0sza3WoeTEnBbKpn6OFJz4MheIEQg8QmXyHDgs%2Fzl3AZIY6fq0PX3%2BKLgoU%2FiRt2yKZoYHIyh5oa1jCccXT4vpjQ5EUREsPVxJ2etC7Iuv89QbdXoGQIf9bPQ24po6x%2B7%2B8bQelWcd%2FA50k44hpJuzqBflt1KYWmiWuQX6a1T1ICQQ%3D%3D; link.sessionid=2506300190588493bf43e683b536eb2f23eaee026146; all.sessionid=2506300190588493bf43e683b536eb2f23eaee026146; LtpaToken=4bkxnyhMUNRR37TGVRMlBZ3aRywVFtn4GxV/mOTu0yohlndb9Pw9yVgP3pY2xrlBOkqIZMx0sPIzBXPsG6JaOpoqBFZQDBUS+QmzX5U0ztb6qyM6YycWOZxI++hBms8ynpt7TLakWzoeeH6moK6uoEFq2bjPfPeWBvMp0eipXJPAM0nAiX6yctpsvmwv6f1NA96Pxws1pZi8hga7RGSaRZBzuM4tYUA/WuMPStcxvb5w3ENm03T+11ViOT2nUSqBeU38S8OfQA9aV+Quyz0GuABushSK0LbZOxtoI5GIWUTRQx9xkKxKjJ609ZnYBlKh0p10KTJZ7wsPVvIVMEY3PvdzC+mSWv0Nz48vCxgdGUlkeol58QBEvzZN6jbJGd+/lV0ejP3lQQN4Hma+jIhrk9BccZBptcYcYSA6RX8v6TrBOI4C/zLNLKCVnJ3xN4MPB6ijDG1BDZzBJ61FTsnGeQ==; domain=https://www.gtht.com.cn; oem.sessionid=2506300190588493bf43e683b536eb2f23eaee026146; re_login_flag=1',
    'Origin': 'https://www.gtht.com.cn',
    'Referer': 'https://www.gtht.com.cn/bst/insideWeb/rank/no-referrer',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)  Chrome/109.0.0.0 GTJABrowser/2.1.0.5 Safari/537.36',
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
def data_format1(json_data):
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
def data_income1(dict,end_time):
    dict = {key: dict[key] for key in list(dict.keys())[0:4]}
    for key,value in dict.items():
            json_data = get_data(value,end_time)
            all_list = data_format1(json_data)
            data = pd.DataFrame(all_list, columns=["排名","分公司","分支编码","营业部","营业收入","交易类收入","借贷类收入","委托类收入","其他类收入"])
            if key == "营业收入_分公司月度" or key == "营业收入_分公司累计":
                data.drop(columns=["分支编码","营业部"], inplace=True)
            with pd.ExcelWriter("data_income.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                data.to_excel(writer, sheet_name=key, index=False)
            print(f"sheet-{key}-写入成功")

# 交易类收入
def data_format2(json_data):
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
def data_income2(dict,end_time):
    dict = {key: dict[key] for key in list(dict.keys())[4:8]}
    for key,value in dict.items():
            json_data = get_data(value,end_time)
            all_list = data_format2(json_data)
            data = pd.DataFrame(all_list, columns=["排名","分公司","分支编码","营业部","交易类收入","佣金类收入","其中_普通交易佣金收入","其中_信用交易佣金收入",
                                                   "其中_其他机构佣金协同收","其中_私募佣金协同收入","其中_港股通佣金收入","其中：衍生品佣金收入","其中_规费",
                                                   "其中_经纪人支出","保证金利差收入","期货IB分成收入","其中_其他业务分成收入","财税返还手续费收入","其他收入"])
            if key == "交易类收入_分公司月度" or key == "交易类收入_分公司累计":
                data.drop(columns=["分支编码","营业部"], inplace=True)
            with pd.ExcelWriter("data_income.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                data.to_excel(writer, sheet_name=key, index=False)
            print(f"sheet-{key}-写入成功")

# 借贷类收入
def data_format3(json_data):
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
def data_income3(dict,end_time):
    dict = {key: dict[key] for key in list(dict.keys())[8:12]}
    for key,value in dict.items():
            json_data = get_data(value,end_time)
            all_list = data_format3(json_data)
            data = pd.DataFrame(all_list, columns=["排名","分公司","分支编码","营业部","借贷类收入","其中_融资融券息差收入","其中_类贷款业务利息收入"])
            if key == "借贷类收入_分公司月度" or key == "借贷类收入_分公司累计":
                data.drop(columns=["分支编码","营业部"], inplace=True)
            with pd.ExcelWriter("data_income.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                data.to_excel(writer, sheet_name=key, index=False)
            print(f"sheet-{key}-写入成功")

# 委托类收入
def data_format4(json_data):
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
def data_income4(dict,end_time):
    dict = {key: dict[key] for key in list(dict.keys())[12:16]}
    for key,value in dict.items():
            json_data = get_data(value,end_time)
            all_list = data_format4(json_data)
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
def data_format5(json_data):
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
def data_income5(dict,end_time):
    dict = {key: dict[key] for key in list(dict.keys())[16:20]}
    for key,value in dict.items():
            json_data = get_data(value,end_time)
            all_list = data_format5(json_data)
            data = pd.DataFrame(all_list, columns=["排名","分公司","分支编码","营业部","其他类收入","其中_项目协作收入","其中_财务顾问收入"])
            if key == "其他类收入_分公司月度" or key == "其他类收入_分公司累计":
                data.drop(columns=["分支编码","营业部"], inplace=True)
            with pd.ExcelWriter("data_income.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                data.to_excel(writer, sheet_name=key, index=False)
            print(f"sheet-{key}-写入成功")

# 代买卖
def data_format6(json_data):
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
            i["V5"],
        ] 
        all_list.append(list)
    return all_list
def data_income6(dict,end_time):
    dict = {key: dict[key] for key in list(dict.keys())[20:24]}
    for key,value in dict.items():
            json_data = get_data(value,end_time)
            all_list = data_format6(json_data)
            data = pd.DataFrame(all_list, columns=["排名","分公司","分支编码","营业部","代理买卖证券业务净收入","其中_普通账户传统佣金净收入","其中_信用交易佣金净收入","代理买卖证券业务净收入（不含公募分仓）"])
            if key == "代买卖_分公司月度" or key == "代买卖_分公司累计":
                data.drop(columns=["分支编码","营业部"], inplace=True)
            with pd.ExcelWriter("data_income.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                data.to_excel(writer, sheet_name=key, index=False)
            print(f"sheet-{key}-写入成功")

# 客户日均资产
def data_format7(json_data):
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
def data_income7(dict,end_time):
    dict = {key: dict[key] for key in list(dict.keys())[24:26]}
    for key,value in dict.items():
            json_data = get_data(value,end_time)
            all_list = data_format7(json_data)
            data = pd.DataFrame(all_list, columns=["排名","分公司","分支编码","营业部","月日均资产","年度累计日均资产","当年新增客户月均资产","月末资产",
                                                   "月末个人客户资产","个人客户当月日均资产","个人客户当年日均资产","月末股票资产","当月日均股票资产",
                                                   "当年日均股票资产","个人客户月末股票资产","个人客户当月日均股票资产","个人客户当年日均股票资产","月末企业客户资产","交易资产规模"])
            if key == "客户日均资产_分公司":
                data.drop(columns=["分支编码","营业部"], inplace=True)
            with pd.ExcelWriter("data_income.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                data.to_excel(writer, sheet_name=key, index=False)
            print(f"sheet-{key}-写入成功")

# 零售客户资产
def data_format8(json_data):
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
        ]
        all_list.append(list)
    return all_list
def data_income8(dict,end_time):
    dict = {key: dict[key] for key in list(dict.keys())[26:28]}
    for key,value in dict.items():
            json_data = get_data(value,end_time)
            all_list = data_format8(json_data)
            data = pd.DataFrame(all_list, columns=["排名","分公司","分支编码","营业部","A_零售客户资产净增长","其中_当年新开个人客户合并资产","存量个人客户合并资产净转入","当年新开股权激励限售资产",
                                                   "存量客户股权激励限售资产净转入","B_零售客户资产净增长","其中_当年新开个人客户合并资产","存量个人客户合并资产净转入","当年新开股权激励限售资产",
                                                   "存量客户股权激励限售资产净转入","新增零售客户资产"])
            if key == "零售客户资产_分公司":
                data.drop(columns=["分支编码","营业部"], inplace=True)
            with pd.ExcelWriter("data_income.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                data.to_excel(writer, sheet_name=key, index=False)
            print(f"sheet-{key}-写入成功")

# 交易资产 list、dict、all_list、columns、key
def data_format9(json_data):
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
        ]
        all_list.append(list)
    return all_list
def data_income9(dict,end_time):
    dict = {key: dict[key] for key in list(dict.keys())[28:30]}
    for key,value in dict.items():
            json_data = get_data(value,end_time)
            all_list = data_format9(json_data)
            data = pd.DataFrame(all_list, columns=["排名","分公司","分支编码","营业部","月末资产","其中_个人月末资产","月均资产","其中_个人月均资产",
                                                   "月末资产","其中_个人月末资产","月均资产","其中_个人月均资产","月均资产（含股权激励）",
                                                   "其中_个人月均资产（含股权激励）"])
            if key == "交易资产_分公司":
                data.drop(columns=["分支编码","营业部"], inplace=True)
            with pd.ExcelWriter("data_income.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                data.to_excel(writer, sheet_name=key, index=False)
            print(f"sheet-{key}-写入成功")

# 非货公私募产品销量 list、dict、all_list、columns、key
def data_format10(json_data):
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
        ]
        all_list.append(list)
    return all_list
def data_income10(dict,end_time):
    dict = {key: dict[key] for key in list(dict.keys())[30:34]}
    for key,value in dict.items():
            json_data = get_data(value,end_time)
            all_list = data_format10(json_data)
            data = pd.DataFrame(all_list, columns=["排名","分公司","分支编码","营业部","非货公私募金融产品销量","其中_公募","其中_资管","其中_信托",
                                                   "其中_私募","其中_期货资管","群星荟萃池P1类产品销量"])
            if key == "非货公私募产品销量_分公司月度" or key == "非货公私募产品销量_分公司累计":
                data.drop(columns=["分支编码","营业部"], inplace=True)
            with pd.ExcelWriter("data_income.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                data.to_excel(writer, sheet_name=key, index=False)
            print(f"sheet-{key}-写入成功")

# 非货公私募产品保有量 list、dict、all_list、columns、key
def data_format11(json_data):
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
        ]
        all_list.append(list)
    return all_list
def data_income11(dict,end_time):
    dict = {key: dict[key] for key in list(dict.keys())[34:36]}
    for key,value in dict.items():
            json_data = get_data(value,end_time)
            print(json_data)
            all_list = data_format11(json_data)
            data = pd.DataFrame(all_list, columns=["排名","分公司","分支编码","营业部","非货公私募类金融产品月均保有量_当月日均","非货公私募类金融产品月均保有量_当年日均","非货公私募类金融产品月均保有量_年度月末均值","非货公私募类金融产品月均保有量_年度月均值（折算）",
                                                   "非货公募类金融产品月均保有量_当月日均","非货公募类金融产品月均保有量_当年日均","非货公募类金融产品月均保有量_年度月末均值",
                                                   "重点产品销售保有规模（不含君享投）_当月","重点产品销售保有规模（不含君享投）_年度累计"])
            if key == "非货公私募保有量_分公司月度":
                data.drop(columns=["分支编码","营业部"], inplace=True)
            with pd.ExcelWriter("data_income.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
                data.to_excel(writer, sheet_name=key, index=False)
            print(f"sheet-{key}-写入成功")



def main():
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
        "代买卖_分公司月度":"id_01_21_00_02_01_lf",
        "代买卖_营业部月度":"id_01_21_00_02_02_lf",
        "代买卖_分公司累计":"id_01_21_00_03_01_lf",
        "代买卖_营业部累计":"id_01_21_00_03_02_lf",
        "客户日均资产_分公司":"id_01_63_02_01_lf",
        "客户日均资产_营业部":"id_01_63_02_02_lf",
        "零售客户资产_分公司":"id_01_89_02_01_lf",
        "零售客户资产_营业部":"id_01_89_02_02_lf",
        "交易资产_分公司":"id_01_99_02_01_lf",
        "交易资产_营业部":"id_01_99_02_02_lf",
        "非货公私募产品销量_分公司月度":"id_01_93_02_01_lf",
        "非货公私募产品销量_营业部月度":"id_01_93_02_02_lf",
        "非货公私募产品销量_分公司累计":"id_01_93_03_01_lf",
        "非货公私募产品销量_营业部累计":"id_01_93_03_02_lf",
        "非货公私募保有量_分公司月度":"id_148_02_01",
        "非货公私募保有量_营业部月度":"id_148_02_02",
    }
    # data_income1(dict,end_time)
    # data_income2(dict,end_time)
    # data_income3(dict,end_time)
    # data_income4(dict,end_time)
    # data_income5(dict,end_time)
    # data_income6(dict,end_time)
    # data_income7(dict,end_time)
    # data_income8(dict,end_time)
    # data_income9(dict,end_time)
    # data_income10(dict,end_time)
    data_income11(dict,end_time)
    print("全部写入完成")

if __name__ == '__main__':
     main()