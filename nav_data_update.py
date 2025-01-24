import requests
import pandas as pd
from pathlib import Path
import time
import os

fund_info = pd.read_csv('fund_list.txt', delimiter=' ')

def get_nav_data(fund_name,fund_nencoding):
    headers = {
        "access-token": "b80e7f84dec465d910073c99aea0c4ffbc64c7587cb005b5dfe9cbd767028d74dcff01e9e093d23385a27848395b0551",
    }
    url = f"https://pyapi.huofuniu.com/pyapi/fund/viewv2?fid={fund_nencoding}&pt=1&shareToken="
    res = requests.get(url, headers=headers)
    nav_data = pd.DataFrame(res.json()["data"]["fund"]["prices"])
    nav_data = nav_data.rename(
        columns={
            "pd": "日期",
            "nav": "单位净值",
            "cnw": "累计净值",
            "cn": "复权净值",
            "pc": "涨跌幅",
            "drawdown": "最大回撤",
        }
    ).drop(columns=["e_pc"])
    nav_data = nav_data[["日期", "单位净值", "累计净值", "复权净值"]]
    nav_data["日期"] = pd.to_datetime(nav_data["日期"])
    nav_data.to_csv(
        Path(
            rf"data/{fund_name}_{nav_data["日期"].max().strftime("%Y-%m-%d")}.csv"
        ),
        index=False,
        encoding="utf-8-sig",
    )
    return nav_data

for row in fund_info.itertuples(index=False, name=None):
    files_list_series = pd.Series([i for i in Path("./data").rglob("*.csv")])
    contains_specific_string = files_list_series.apply(lambda x: row[0] in str(x.name)).any()
    if contains_specific_string:
        files_to_delete = files_list_series[files_list_series.apply(lambda x: row[0] in str(x.name))]
        for file_path in files_to_delete:
                os.remove(file_path)
                print(f"Deleted file: {file_path}")
    get_nav_data(row[0],row[1])
    print(f"正在爬取{row[0]}净值")
    time.sleep(2)

print("爬取完成")