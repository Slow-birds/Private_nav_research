import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random

dict = {
    "黑翼CTA8号":"HF000051UR",
    "宏锡量化CTA7号":"HF00002G7U",
    "千象15期":"HF00003HBI",
    "细水居20号":"HF00009G5B",
    "闻道稳健一号":"HF00005KKE",
    "金和和善对冲1号":"HF00007V41",
    "博普安兴私享一号B类份额":"HF0000BCQX"
    }

def get_nav_data(fund_id):
    url1 = f"https://dc.simuwang.com/product/{fund_id}.html?chat_off=1"
    headers = {
    "cookie":"collect=%7B%22count%22%3A2%2C%22time%22%3A1725694669429%7D; _ga=GA1.1.234740855.1738847378; tfstk=gzzrN_6I0aQP544PKj0e0kw2mM0-S4X6ayMItWVnNYDkPU930W2rV3T52kJE3JHSV44UDePT9z1-R_38w23hCO__87F-Jw0fEmzymEcLi3coEigmWEXL8O_157vpSTxhCzatGaDrt2cox2vcgbhHr2mnqZfqtX9kxU23iskxOpxHqDYcoXhkq203KSfq9xDnw_knCElZq6ofC7upWRirI7D27SUxZNkNWYYHfrlzNAVkjeY3ubouR2s3jko7x5nTPW7ek4NamqcUJ1xELcr3Pq4lnNmxxr2mi81BvjrUtP3-2BTQQ4yEjzm2tFPirxgqiPfBXxaqFJ4rm1TZAq4sj4qfDTiIzfy3y8Re-RVb1znY8OJmpuGtoXzdsHkExgJBpjv73yEyKHooMjk1gsSOT6RQG3MA8HKK2ohqC_CJvHnoMjk1gs-pv0FqgA1Rw; focus-certification-pop=-1; _c_WBKFRo=mbM2qgQUP7dIu5rp2qRkrzSNMv09pgJjy9NQbr9K; Hm_lvt_c3f6328a1a952e922e996c667234cdae=1743467790,1743516003,1743948583,1744204948; HMACCOUNT=7FEF1F4BA5D379B6; http_tK_cache=4ee199fb7a7d703d42ded10e8e970a142df637ea; rz_rem_u_p=%2FMko4euYG7M%3D%24tkXQWiOXTfXKGjTtLPHE6g%3D%3D; certification=1; qualified_investor=1; evaluation_result=5; _ga_ZCWR11HG01=GS1.1.1744204947.22.1.1744204961.0.0.0; Hm_lpvt_c3f6328a1a952e922e996c667234cdae=1744204961; Hm_lvt_9dd0363ce9ec438fb46a5e94be7d1e41=1743467800,1743516009,1743948598,1744204967; _ga_7SBBX4Y5RE=GS1.1.1744208769.18.1.1744208894.0.0.0; Hm_lpvt_9dd0363ce9ec438fb46a5e94be7d1e41=1744208895",
    "referer":"https://www.simuwang.com/",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
    }
    res1 = requests.get(url1, headers=headers)
    soup = BeautifulSoup(res1.text, "lxml")
    dict1 = {
        "管理人": soup.select("#screenshot-left > aside.bg-white.relative > div:nth-child(2) > ul > li:nth-child(10) > a")[0].get_text(),
        "管理规模": soup.select("#screenshot-left > aside.bg-white.relative > div:nth-child(2) > ul > li:nth-child(13) > div:nth-child(2)")[0].get_text(),
        "基金经理": soup.select("#screenshot-left > aside.bg-white.relative > div:nth-child(2) > ul > li:nth-child(11) > div.truncate > a")[0].get_text(),
        "基金名称": soup.select("#screenshot-left > aside.bg-white.relative > div.px-24.pt-16.pb-0.h-58 > div > div > h1")[0].get_text(),
        "基金代码": soup.select("#screenshot-left > aside.bg-white.relative > div:nth-child(2) > ul > li:nth-child(12) > div:nth-child(2)")[0].get_text(),
        "成立日期": soup.select("#screenshot-left > aside.bg-white.relative > div:nth-child(2) > ul > li:nth-child(9) > div:nth-child(2)")[0].get_text(),
        "夏普比": soup.select("#screenshot-left > aside.bg-white.relative > div:nth-child(2) > ul > li:nth-child(7) > div:nth-child(2)")[0].get_text()
        }
    url2 = f"https://sppwapi.simuwang.com/sun/fund/incomeIndex?id={fund_id}"
    headers = {
        "cookie":"collect=%7B%22count%22%3A2%2C%22time%22%3A1725694669429%7D; _ga=GA1.1.234740855.1738847378; tfstk=gzzrN_6I0aQP544PKj0e0kw2mM0-S4X6ayMItWVnNYDkPU930W2rV3T52kJE3JHSV44UDePT9z1-R_38w23hCO__87F-Jw0fEmzymEcLi3coEigmWEXL8O_157vpSTxhCzatGaDrt2cox2vcgbhHr2mnqZfqtX9kxU23iskxOpxHqDYcoXhkq203KSfq9xDnw_knCElZq6ofC7upWRirI7D27SUxZNkNWYYHfrlzNAVkjeY3ubouR2s3jko7x5nTPW7ek4NamqcUJ1xELcr3Pq4lnNmxxr2mi81BvjrUtP3-2BTQQ4yEjzm2tFPirxgqiPfBXxaqFJ4rm1TZAq4sj4qfDTiIzfy3y8Re-RVb1znY8OJmpuGtoXzdsHkExgJBpjv73yEyKHooMjk1gsSOT6RQG3MA8HKK2ohqC_CJvHnoMjk1gs-pv0FqgA1Rw; focus-certification-pop=-1; _c_WBKFRo=mbM2qgQUP7dIu5rp2qRkrzSNMv09pgJjy9NQbr9K; Hm_lvt_c3f6328a1a952e922e996c667234cdae=1743467790,1743516003,1743948583,1744204948; HMACCOUNT=7FEF1F4BA5D379B6; http_tK_cache=4ee199fb7a7d703d42ded10e8e970a142df637ea; rz_rem_u_p=%2FMko4euYG7M%3D%24tkXQWiOXTfXKGjTtLPHE6g%3D%3D; certification=1; qualified_investor=1; evaluation_result=5; _ga_ZCWR11HG01=GS1.1.1744204947.22.1.1744204961.0.0.0; Hm_lpvt_c3f6328a1a952e922e996c667234cdae=1744204961; _ga_7SBBX4Y5RE=GS1.1.1744204966.17.1.1744205293.0.0.0",
        "referer":"https://dc.simuwang.com/",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
        }
    res2 = requests.get(url2, headers = headers)
    dict2 = res2.json()["data"]
    dict1.update(dict2)
    nav_df = pd.DataFrame(dict1, index=[0])
    nav_df = nav_df[["管理人","管理规模","基金经理","基金名称","基金代码","成立日期","price_date","ret_incep","maxdrawdown_incep","夏普比","ret_ytd","maxdrawdown_ytd"]]
    nav_df.rename(columns={"price_date":"最新净值日期","ret_incep":"累计收益","maxdrawdown_incep":"最大回撤","ret_ytd":"2025收益","maxdrawdown_ytd":"2025最大回撤"},inplace=True)
    return nav_df

if __name__ == "__main__":
    nav_dfs = pd.DataFrame()
    for value in dict.values():
        nav_df = get_nav_data(value)
        nav_dfs = pd.concat([nav_dfs,nav_df],axis=0)
        time.sleep(random.uniform(0.1,0.3))
    with pd.ExcelWriter("data.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        nav_dfs.to_excel(writer, sheet_name="simupaipai", index=False)
    print("所有产品净值爬取完成")
