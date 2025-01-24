import requests
import pandas as pd
from pathlib import Path


class FOF99Data:
    def __init__(self, fid: str = "6788b59fd9a720b7"):
        self.fid = fid
        # self.token = ""
        self.token = "b80e7f84dec465d910073c99aea0c4ffbc64c7587cb005b5dfe9cbd767028d74dcff01e9e093d23385a27848395b0551"
        self.headers = {
            "access-token": self.token,
        }
        # url = "https://pyapi.huofuniu.com/pyapi/fund/viewv2?fid=60040aea103a3e1cf0c4fa42174d1aff&sd=2022-01-15&ed=&cycle=0&refer=a358b34bc9d0e2016591fb80c2b34061"

    def get_fund_info(self):
        nav_analyis_url = f"https://api.huofuniu.com/newgoapi/funds/analyze?token={self.token}&id={self.fid}&url="
        annlysis_data = requests.get(nav_analyis_url, headers=self.headers)
        annlysis_data = annlysis_data.json()["data"]
        advisor = annlysis_data["advisor"]
        self.register_number = annlysis_data["register_number"]
        fund_name = annlysis_data["fund_name"]
        self.fund_short_name = annlysis_data["fund_short_name"]
        scale = annlysis_data["scale"]
        strategy_name = annlysis_data["strategy"][0]["strategy_name"]
        if annlysis_data["strategy"][0]["child"]:

            strategy_name = (
                strategy_name
                + "_"
                + annlysis_data["strategy"][0]["child"][0]["strategy_name"]
            )
        self.price_date = annlysis_data["price_date"]
        fund_info = {
            "管理人名称": advisor,
            "产品代码": self.register_number,
            "产品名称": fund_name,
            "产品简称": self.fund_short_name,
            "管理人规模": scale,
            "策略类型": strategy_name,
        }
        return fund_info

    def get_nav_data(self):
        nav_data_url = f"https://pyapi.huofuniu.com/pyapi/fund/viewv2?fid={self.fid}&pt=1&shareToken="
        nav_data = requests.get(nav_data_url, headers=self.headers)
        nav_data = pd.DataFrame(nav_data.json()["data"]["fund"]["prices"])
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
        nav_data["日期"] = pd.to_datetime(nav_data["日期"])
        fund_info = self.get_fund_info()
        for i, v in fund_info.items():
            nav_data[i] = v
        return nav_data


if __name__ == "__main__":
    FOFData = FOF99Data("f71606d12628209b")
    data = FOFData.get_nav_data()
    data.to_csv(
        Path(
            rf"data/{FOFData.register_number}_{FOFData.fund_short_name}_{FOFData.price_date.replace("-","")}.csv"
        ),
        index=False,
        encoding="utf-8-sig",
    )
