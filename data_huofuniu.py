import requests
import pandas as pd
from pathlib import Path
import time
import random

class NavData:
    def __init__(self, fund_code, fund_name, fund_coding):
        self.fund_code = fund_code
        self.fund_name = fund_name
        self.fund_coding = fund_coding
        self.token = "be154b690f1e1f943cfd04b13c8a0ddada4241d2b7c67b4f1e932e3294d655cea6692cc19a6d7738ee111bf447b2080f"
        #self.token = "b80e7f84dec465d910073c99aea0c4ffbc64c7587cb005b5dfe9cbd767028d74dcff01e9e093d23385a27848395b0551"
    def delete_csv_file(self):
        for csv_file in Path("./data").glob(f"{self.fund_code}_*.csv"):
            csv_file.unlink()
            print(f"清理旧文件：{csv_file.name}")
    def get_nav_data(self):
        headers = {
            "access-token": self.token,
        }
        url = f"https://pyapi.huofuniu.com/pyapi/fund/viewv2?fid={self.fund_coding}&pt=1&shareToken="
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
        path = Path(rf"data/{self.fund_code}_{self.fund_name}_{nav_data["日期"].max().strftime("%Y-%m-%d")}.csv")
        nav_data.to_csv(
            path,
            index=False,
            encoding="utf-8-sig",
        )
        print(f"正在爬取{self.fund_name}净值，并生成新文件：{path}")
        return nav_data

if __name__ == "__main__":
    fund_info = pd.read_csv(r'fund_list.txt', delimiter=' ')
    fund_info_hfn = fund_info[fund_info['数据来源'] == '火富牛']
    for row in fund_info_hfn.itertuples(index=False, name=None):
        demo = NavData(row[1], row[2], row[3])
        demo.delete_csv_file() 
        demo.get_nav_data()
        time.sleep(random.uniform(0.5, 1.5))
    print("所有产品净值爬取完成")