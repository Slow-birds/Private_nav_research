import pandas as pd
import time
import random
from DrissionPage import ChromiumPage


def get_nav_data(fund_id):
    page = ChromiumPage()
    page.get(f"https://dc.simuwang.com/product/{fund_id}.html")
    """
    page.ele('xpath:/html/body/aside[4]/div/div/div[2]/div[2]/div[2]/div[1]/div/aside[1]/div/div[1]/button[2]').click()
    page.ele('xpath:/html/body/aside[4]/div/div/div[2]/div[2]/div[2]/div[1]/div/aside[1]/div/div[3]/div[1]/input').input('18380173229')
    page.ele('xpath:/html/body/aside[4]/div/div/div[2]/div[2]/div[2]/div[1]/div/aside[1]/div/div[3]/div[2]/input').input('ykz199582')
    page.ele('xpath:/html/body/aside[4]/div/div/div[2]/div[2]/div[2]/div[1]/div/aside[1]/div/div[4]/label/span/span').click()
    page.ele('xpath:/html/body/aside[4]/div/div/div[2]/div[2]/div[2]/div[1]/div/aside[1]/div/div[5]/button/span').click()
    """
    time.sleep(random.uniform(0.5, 1.5))
    page.ele('xpath://*[@id="nav-el-m2QCkZj"]/div[3]').click()
    time.sleep(random.uniform(0.5, 1.5))
    page.ele('xpath://*[@id="screenshot-range-gain"]/div/div[1]/aside/div[3]').click()
       
    data1 = page.ele('xpath://*[@id="screenshot-left"]/aside[1]/div[2]/ul').text
    blocks1 = [b.strip() for b in data1.split("\n") if b.strip()]
    dict1 = {
        "管理人": blocks1[-11],
        "管理规模": blocks1[-5],
        "基金经理": blocks1[-9],
        "基金代码": blocks1[-7],
        "成立日期": blocks1[-13],
        "最新净值日期": page.ele('xpath://*[@id="screenshot-left"]/section[1]/aside[1]/div[1]/div/div[2]/div[1]/div/span[2]').text,
        "年化收益": blocks1[-21],
        "最大回撤": blocks1[-19],
        "夏普比": blocks1[-17],
    }

    data2 = page.ele('xpath://*[@id="screenshot-range-gain"]/aside[2]/div[1]/div[1]/div[1]/div[3]/div/div[1]/div/table/tbody').text
    blocks2 = [b.strip() for b in data2.split("\n\t\n") if b.strip()]
    dict2 = {}
    for block in blocks2:
        year_data = [b.strip() for b in block.split("\n\t") if b.strip()]
        dict2[f"{year_data[0]}收益"] = year_data[1]

    dict1.update(dict2)
    nav_df = pd.DataFrame(dict1, index=[0])
    return nav_df


if __name__ == "__main__":
    dict = {
        "黑翼CTA8号": "HF000051UR",
        "宏锡量化CTA7号": "HF00002G7U",
        "千象15期": "HF00003HBI",
        "细水居20号": "HF00009G5B",
        "闻道稳健一号": "HF00005KKE",
        "金和和善对冲1号": "HF00007V41",
        "博普安兴私享一号B类份额": "HF0000BCQX",
    }
    nav_dfs = pd.DataFrame()
    for fund_name, fund_code in dict.items():
        print(f"正在获取 {fund_name} 的净值...")
        nav_df = get_nav_data(fund_code)
        nav_df.insert(loc=4, column="基金名称", value=fund_name)
        nav_dfs = pd.concat([nav_dfs, nav_df], axis=0)
        time.sleep(random.uniform(0.1, 0.3))
    with pd.ExcelWriter("data.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        nav_dfs.to_excel(writer, sheet_name="simupaipai", index=False)
    print("所有产品净值爬取完成")
