import os
import numpy as np
import pandas as pd
import datetime
from pathlib import Path
from function import load_data
from nav_research import NavResearch
from tqdm import tqdm
from WindPy import w
w.start()

def delete_csv_files(directory: str)-> None:
    '''删除指定目录下所有CSV文件'''
    path = Path(directory)
    for csv_file in path.rglob("*.csv"):
        csv_file.unlink()
        print(f"Deleted: {csv_file.name}")

def get_nav_dfs(fund_info: pd.DataFrame)-> None:
    '''初次生成nav_dfs.csv(后续不需执行)'''
    files_list_series = pd.Series(
        [
            i
            for i in Path("./nav_data").rglob("*")
            if i.suffix.lower() in {".csv", ".xlsx", ".xls"}
        ]
    )
    nav_dfs = pd.DataFrame()
    for row in fund_info.itertuples(index=False, name=None):
        nav_df_path = files_list_series[
            files_list_series.apply(lambda x: row[1] in x.stem)
        ]
        assert (
            len(nav_df_path) == 1
        ), f"找到{len(nav_df_path)}个文件匹配{row[2]},期望找到1个"
        nav_df = load_data(nav_df_path.iloc[0])
        nav_df["基金代码"] = row[1]
        nav_df["基金名称"] = row[2]
        nav_df = nav_df[["基金代码", "基金名称", "日期", "单位净值", "累计净值"]]
        nav_dfs = pd.concat([nav_dfs, nav_df], ignore_index=True)
    nav_dfs.to_csv("nav_dfs.csv", index=False, encoding="utf-8-sig")

def get_new_nav_df(data_path:str, fund_info: pd.DataFrame)-> pd.DataFrame:
    '''获取最新一期净值数据nav_df'''
    fundcode_list = fund_info["基金代码"].tolist()
    df1 = pd.read_excel(data_path, sheet_name="私募产品")
    df2 = pd.read_excel(data_path, sheet_name="资管产品（私募）")
    # 处理表df1
    df3 = df1[
        ["产品代码", "产品名称", "最新日期", "最新单位净值（元）", "累计净值（元）"]
    ]
    df3.columns = ["基金代码", "基金名称", "日期", "单位净值", "累计净值"]
    # 处理表df2
    df4 = df2[["产品代码", "产品名称", "最新净值日", "单位净值", "累计净值"]]
    df4.columns = ["基金代码", "基金名称", "日期", "单位净值", "累计净值"]
    df4["基金代码"] = df4["基金代码"].astype(str)
    # 合并处理完后的df3、df4
    df5 = pd.concat([df3, df4], ignore_index=True)
    df5["日期"] = pd.to_datetime(df5["日期"]).dt.strftime("%Y-%m-%d")
    nav_df = df5[df5["基金代码"].isin(fundcode_list)].reset_index(drop=True)
    # 使用map更新"基金名称"列
    fund_name_map = fund_info.set_index('基金代码')['基金名称'].to_dict()
    nav_df['基金名称'] = nav_df['基金代码'].map(fund_name_map)
    return nav_df

def update_nav_dfs(nav_df: pd.DataFrame)->pd.DataFrame:
    ''' 将最新一期净值数据nav_df更新到nav_dfs'''
    nav_dfs = pd.read_csv("nav_dfs.csv")
    update_nav_dfs = pd.concat([nav_dfs, nav_df], axis=0, ignore_index=True)
    update_nav_dfs.drop_duplicates(subset=["基金代码", "日期"], inplace=True)
    update_nav_dfs.sort_values(by=["基金代码", "日期"], inplace=True)
    update_nav_dfs.to_csv("nav_dfs.csv", index=False, encoding="utf-8-sig")
    return update_nav_dfs

def generate_sigle_nav_df(nav_dfs:pd.DataFrame, fund_info: pd.DataFrame)-> None:
    '''生成单基金净值数据'''
    nav_dfs["日期"] = pd.to_datetime(nav_dfs["日期"], format="%Y-%m-%d")
    fund_info["成立日期"] = pd.to_datetime(fund_info["成立日期"], format="%Y-%m-%d")
    # 遍历 nav_dfs 中 "基金代码" 列的唯一值
    fundcode_list = fund_info["基金代码"].unique().tolist()
    for fundcode in fundcode_list:
        nav_df = nav_dfs[nav_dfs["基金代码"] == fundcode]
        start_date = (fund_info[fund_info["基金代码"] == fundcode]["成立日期"].iloc[0].strftime("%Y-%m-%d"))
        end_date = nav_df["日期"].max().strftime("%Y-%m-%d")
        fund_name = nav_df["基金名称"].iloc[0]
        file_path = os.path.join("nav_dfs", f"{fundcode}_{fund_name}_{start_date}_{end_date}.csv")
        filtered_df = nav_df[nav_df["日期"] >= start_date]
        filtered_df.to_csv(file_path, index=False, encoding="utf-8-sig")
        print(f"Created:{file_path}")

def single_fund_table(tables:list, fund_name:str):
    '''获取单基金业绩表现指标数据'''
    data1 = tables[0]
    data2 = tables[1].head(1)
    data3 = pd.DataFrame()
    data4 = tables[2]
    years = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
    for year in years:
        data3[f"{year}收益"] = data4.loc[
            data4["分年度业绩"] == year, f"{fund_name}_收益"
        ].values
    data = pd.concat([data1, data2, data3], axis=1)
    data.drop(columns=["基准指数", "整体业绩"], inplace=True)
    return data

def multiple_fund_table(fund_info, end_date):
    '''获取多基金业绩表现指标数据'''
    data = pd.DataFrame()
    file_map = {path.stem.split("_")[0]: path for path in Path("./nav_dfs").glob("*.csv")}
    results = []
    for row in tqdm(fund_info.itertuples(index=False, name=None),desc="生成多基金对比数据",total=len(fund_info)):
        # 找到对应的文件路径，确保唯一
        nav_df_path = file_map.get(row[1])
        # 初始化并获取数据
        demo = NavResearch(nav_df_path, row[0], row[2], row[3], row[4], row[5])
        df_nav, _, _ = demo.get_data()
        # 保存数据
        df_nav[["date", "nav_unit", "nav_accumulated", "nav_adjusted"]].to_csv(nav_df_path, index=False, encoding="utf-8-sig")
        tables = demo.get_analysis_table()
        nav_df = single_fund_table(tables, row[2])
        # 添加策略类型、近一月收益率、近一周收益列（特定基金产品设置为 NaN）
        nav_df["策略类型"] = row[0]
        nav_df["基金代码"] = row[1]
        enddate = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        nav_df[f"{enddate.month}月收益"] = tables[4].loc[tables[4]["分月度业绩"] == enddate.year,f"{enddate.month}月"].item()
        nav_df["近一周收益"] = (f"{(df_nav['nav_adjusted'].iloc[-1] / df_nav['nav_adjusted'].iloc[-2] - 1):.2%}")
        specific_list = ["景林景泰优选GJ2期", "景林精选FOF子基金GJ2期","景林景泰丰收GJ2期","千宜乐享精选CTA2号"]
        nav_df.loc[nav_df["基金产品"].isin(specific_list), "近一周收益"] = np.nan
        results.append(nav_df)
        data = pd.concat(results, ignore_index=True)
        # 自定义排序列顺序
        cols = ["策略类型", "基金代码"] + [col for col in nav_df.columns if col not in ["策略类型", "基金代码"]]
        data = data[cols]
    # 指定策略类型的自定义顺序
    custom_order = [
        "灵活配置","主观成长","主观价值","主观逆向",
        "300指增","500指增","1000指增","小市值指增","量化选股","市场中性",
        "套利","CTA","多策略","其他",
    ]
    data["策略类型"] = pd.Categorical(data["策略类型"], categories=custom_order, ordered=True)
    data["2025收益数值"] = data["2025收益"].str.rstrip("%").astype(float) / 100
    data.sort_values(by=["策略类型", "2025收益数值"], ascending=[True, False], inplace=True)
    data.drop(columns=["2025收益数值"], inplace=True)
    # 重命名列
    data.rename(columns={"净值起始日期": "成立日期", "净值结束日期": "最新净值日期"},inplace=True,)
    # 保存到 Excel
    with pd.ExcelWriter(
        "report_data.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace"
    ) as writer:
        data.to_excel(writer, sheet_name="Sheet2", index=False)

def get_index_rtn(end_date: str) -> pd.DataFrame:
    '''获取基准指数收益率'''
    index_code = ["881001.WI", "000300.SH", "000905.SH", "000852.SH", "8841425.WI", "HSTECH.HI", "IXIC.GI"]
    index_name = ["万得全A", "沪深300", "中证500", "中证1000", "万得小市值指数", "恒生科技", "纳斯达克"]
    end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    # 自动计算各时间段起始日期
    periods = [
        {
            'type': 'year',
            'start_date': f"{end_dt.year}-01-01",
            'col_name': f"{end_dt.year}收益"
        },
        {
            'type': 'month',
            'start_date': end_dt.replace(day=1).strftime("%Y-%m-%d"),
            'col_name': f"{end_dt.month}月收益"
        },
        {
            'type': 'week',
            'start_date': (end_dt - datetime.timedelta(days=4)).strftime("%Y-%m-%d"),
            'col_name': "近一周收益"
        }
    ]
    dfs = []
    for period in periods:
        error_code, df = w.wss(index_code,"pct_chg_per",startDate=period['start_date'],endDate=end_date,usedf=True)
        df.rename(columns={'PCT_CHG_PER': period['col_name']}, inplace=True)
        df.index = index_name
        dfs.append(df)
    rtn = pd.concat(dfs, axis=1).reset_index()
    rtn.rename(columns={'index': '指数名称'}, inplace=True)
    with pd.ExcelWriter("report_data.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        rtn.to_excel(writer, sheet_name="Sheet3", index=False)
    return rtn

# 主程序
def main():
    fund_info = load_data("产品代码.xlsx")
    fund_info["基金代码"] = fund_info["基金代码"].astype(str)
    data_path = Path("销售产品业绩表现监控表20250324-20250328.xlsx")
    # 辅助日期格式
    enddate = datetime.datetime.strptime(data_path.stem.split("-")[-1], "%Y%m%d").strftime("%Y-%m-%d")
    # 获取新一期净值nav_df
    nav_df = get_new_nav_df(data_path, fund_info)
    # 更新nav_dfs
    nav_dfs = update_nav_dfs(nav_df)
    # 生成单个净值数据
    delete_csv_files("./nav_dfs")
    generate_sigle_nav_df(nav_dfs, fund_info)
    # 获取多基金指标对比表
    multiple_fund_table(fund_info, enddate)
    # 获取基准指数收益
    get_index_rtn(enddate)
    print("数据更新完成")
    
if __name__ == "__main__":
    main()