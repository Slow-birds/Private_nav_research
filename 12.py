import requests

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

data = 'data={"Param":"{\\"id\\":\\"id_148_02_01\\",\\"begindate\\":\\"202505\\"}","Type":"RPT_RANK_Q0051","Page":{"CurrentPage":1,"PageSize":9999}}'

response = requests.post(
    'https://www.gtht.com.cn/link/common/apiajax/ajaxMappingHandler',
    params=params,
    cookies=cookies,
    headers=headers,
    data=data,
)
json_data = response.json()["Data"]
print(json_data)