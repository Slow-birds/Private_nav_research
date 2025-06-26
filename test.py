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
        'Cookie': 'JSESSIONID=A16FF86879ACBFBACDBAE2F36DE735DD; oem.userid=120493; client=2; themec=77008; JSESSIONID=DA639C7159991983EF9021F3BF62FEB8; linkgtja=Dkd2%2FjxvtUIFG4%2BkT0HU6m8NP4sqFzpM4pTwCdXl464KjBgYHWj%2F6%2BPlaqKZreEH%2F9%2FGVSXbhiAqDV0NzaYU5%2B32BcYcyEHJ00gFHejjwxiZzsHhn9iVw5esFuioFCUjNi0myp1z%2FCS9jFgAGfo%2Bter4rkH4sqBRIH7ktKqFgjliq7CAEJs%2Bbx9u5wTpvcvbdj4pKY3LElnM60HTTfc40Lc%2BhYg%2Bnz%2F6DYBPUlCRMiypY6wSEW%2BH5fmXpF0NE1OgxEKqbv%2Fi8MSa3pZ%2Bf2g9o1XNUwkqlnqx9KGatWT%2FzhvpuJ000TskkI8UjY2U%2B5zwFPPFt6SSU8WZ9nQvSMZjsg%3D%3D; link.sessionid=2506257fffe0f13a9c40538df64ff3f1bbbcd9026146; all.sessionid=2506257fffe0f13a9c40538df64ff3f1bbbcd9026146; LtpaToken=4bkxnyhMUNRR37TGVRMlBZ3aRywVFtn4GxV/mOTu0yohlndb9Pw9yVgP3pY2xrlBOkqIZMx0sPIzBXPsG6JaOpoqBFZQDBUS+QmzX5U0ztb6qyM6YycWOZxI++hBms8ynpt7TLakWzoeeH6moK6uoEFq2bjPfPeWBvMp0eipXJPAM0nAiX6yctpsvmwv6f1NA96Pxws1pZi8hga7RGSaRSCWqoR5jCoBHoJUeFoAJD1w3ENm03T+11ViOT2nUSqBeU38S8OfQA9aV+Quyz0GuABushSK0LbZOxtoI5GIWUTRQx9xkKxKjJ609ZnYBlKh0p10KTJZ7wsPVvIVMEY3PvdzC+mSWv0Nz48vCxgdGUlkeol58QBEvzZN6jbJGd+/lV0ejP3lQQN4Hma+jIhrk9BccZBptcYcYSA6RX8v6TrBOI4C/zLNLKCVnJ3xN4MPB6ijDG1BDZzBJ61FTsnGeQ==; domain=https://www.gtht.com.cn; oem.sessionid=2506257fffe0f13a9c40538df64ff3f1bbbcd9026146; sajssdk_2015_cross_new_user=1; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22026146%22%2C%22first_id%22%3A%22197a739f5666c0-0ec8062e36a434-2a726c34-1474560-197a739f567876%22%2C%22props%22%3A%7B%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMTk3YTczOWY1NjY2YzAtMGVjODA2MmUzNmE0MzQtMmE3MjZjMzQtMTQ3NDU2MC0xOTdhNzM5ZjU2Nzg3NiIsIiRpZGVudGl0eV9sb2dpbl9pZCI6IjAyNjE0NiJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%24identity_login_id%22%2C%22value%22%3A%22026146%22%7D%2C%22%24device_id%22%3A%22197a739f5666c0-0ec8062e36a434-2a726c34-1474560-197a739f567876%22%7D',
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
        'funId': 'RPT_RANK_Q0056',
    }
    data = f'data={{"Param":"{{\\"id\\":\\"{custom_id}\\",\\"begindate\\":\\"{end_time}\\"}}","Type":"RPT_RANK_Q0056","Page":{{"CurrentPage":1,"PageSize":9999}}}}'
    response = requests.post(url,params=params,headers=headers,data=data)
    json_data = response.json()["Data"]
    return json_data

if __name__ == '__main__':
    custom_id = "id_01_73_01_02_lf"
    end_time = "202505"
    json_data = get_data(custom_id,end_time)
    all_list = []
    for i in json_data:
        list = [
            i["RANKNAME"],
            i["COMPNAME"],
            i["BRANCH_NAME"],
            i["BRANCH_CODE"],
            i["V1"],
            i["V2"],
            i["V3"],
            i["V4"],
            i["V5"]
        ]
        all_list.append(list)
    nav_df = pd.DataFrame(all_list,columns=["排名","分公司","分支编码","营业部","营业收入","交易类收入","借贷类收入","委托类收入","其他类收入"])
    print(nav_df)