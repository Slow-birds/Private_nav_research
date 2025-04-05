import os
import numpy as np
import pandas as pd
from pathlib import Path
from function import load_data
from nav_research import NavResearch
from tqdm import tqdm


# 删除csv文件(辅助函数)
def delete_csv_files(directory):
    path = Path(directory)
    for csv_file in path.rglob("*.csv"):
        csv_file.unlink()
        print(f"Deleted: {csv_file.name}")


# 初次生成nav_dfs.csv(后续不需执行)
def get_nav_dfs(fund_info):
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


# 获取最新一期净值数据 nav_df
def get_new_nav(data_path, fund_info):
    fundcode_list = fund_info["基金代码"].tolist()
    df1 = pd.read_excel(data_path, sheet_name="私募产品")
    df2 = pd.read_excel(data_path, sheet_name="资管产品（私募）")
    # 处理表df1
    df3 = df1[
        ["产品代码", "产品名称", "最新日期", "最新单位净值（元）", "累计净值（元）"]
    ]
    df3.rename(
        columns={
            "产品代码": "基金代码",
            "产品名称": "基金名称",
            "最新日期": "日期",
            "最新单位净值（元）": "单位净值",
            "累计净值（元）": "累计净值",
        },
        inplace=True,
    )
    df3["日期"] = pd.to_datetime(df3["日期"], format="%Y-%m-%d").dt.strftime("%Y-%m-%d")
    # 处理表df2
    df4 = df2[["产品代码", "产品名称", "最新净值日", "单位净值", "累计净值"]]
    df4.rename(
        columns={"产品代码": "基金代码", "产品名称": "基金名称", "最新净值日": "日期"},
        inplace=True,
    )
    df4["日期"] = pd.to_datetime(df4["日期"], format="%Y%m%d").dt.strftime("%Y-%m-%d")
    df4["基金代码"] = df4["基金代码"].astype(str)
    # 合并处理完后的df3、df4
    df5 = pd.concat([df3, df4], ignore_index=True)
    nav_df = df5[df5["基金代码"].isin(fundcode_list)].reset_index(drop=True)
    # 使用map更新"基金名称"列
    fund_name_map = fund_info.set_index('基金代码')['基金名称'].to_dict()
    nav_df['基金名称'] = nav_df['基金代码'].map(fund_name_map)
    return nav_df


# 更新 nav_dfs.csv
def update_nav_dfs(nav_df):
    nav_dfs = pd.read_csv("nav_dfs.csv")
    nav_dfs = pd.concat([nav_dfs, nav_df], axis=0, ignore_index=True)
    nav_dfs.drop_duplicates(subset=["基金代码", "日期"], inplace=True)
    nav_dfs.sort_values(by=["基金代码", "日期"], inplace=True)
    nav_dfs.to_csv("nav_dfs.csv", index=False, encoding="utf-8-sig")
    return nav_dfs


# 生成单基金净值数据
def update_nav_df(nav_dfs, fund_info):
    fundcode_list = fund_info["基金代码"].unique().tolist()
    # 检查日期列的类型，如果不是 datetime 类型，则转换为 datetime 类型
    if nav_dfs["日期"].dtype != "datetime64[ns]":
        nav_dfs["日期"] = pd.to_datetime(nav_dfs["日期"], format="%Y-%m-%d")
    # 遍历 nav_dfs 中 "基金代码" 列的唯一值
    for fundcode in fundcode_list:
        nav_df = nav_dfs[nav_dfs["基金代码"] == fundcode]
        start_date = (
            fund_info[fund_info["基金代码"] == fundcode]["成立日期"]
            .iloc[0]
            .strftime("%Y-%m-%d")
        )
        filtered_df = nav_df[nav_df["日期"] >= start_date]
        end_date = nav_df["日期"].max().strftime("%Y-%m-%d")
        fund_name = nav_df["基金名称"].iloc[0]
        file_path = os.path.join(
            "nav_dfs", f"{fundcode}_{fund_name}_{start_date}_{end_date}.csv"
        )
        filtered_df.to_csv(file_path, index=False, encoding="utf-8-sig")
        print(f"Created:{fundcode}_{fund_name}_{start_date}_{end_date}.csv")


# 获取单基金指标
def single_fund_table(tables, fund_name):
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


# 获取多基金指标对比表 report_data.xlsx
def get_report_data(fund_info):
    data = pd.DataFrame()
    files_list_series = pd.Series(
        [
            i
            for i in Path("./nav_dfs").rglob("*")
            if i.suffix.lower() in {".csv", ".xlsx", ".xls"}
        ]
    )
    for row in tqdm(
        fund_info.itertuples(index=False, name=None),
        desc="生成多基金对比数据",
        total=len(fund_info),
    ):
        # 找到对应的文件路径，确保唯一
        nav_df_path = files_list_series[
            files_list_series.apply(lambda x: row[1] in x.stem)
        ]
        assert (
            len(nav_df_path) == 1
        ), f"找到{len(nav_df_path)}个文件匹配{row[2]},期望找到1个"
        nav_df_path = nav_df_path.iloc[0]
        # 假设 NavResearch 是一个类，初始化并获取数据
        demo = NavResearch(nav_df_path, row[0], row[2], row[3], row[4], row[5])
        df_nav, _, _ = demo.get_data()
        df_nav[["date", "nav_unit", "nav_accumulated", "nav_adjusted"]].to_csv(nav_df_path, index=False, encoding="utf-8-sig")
        tables = demo.get_analysis_table()
        nav_df = single_fund_table(tables, row[2])
        # 添加策略类型、近一周收益列（特定基金产品设置为 NaN）
        nav_df["策略类型"] = row[0]
        nav_df["基金代码"] = row[1]
        nav_df["近一周收益"] = (
            f"{(df_nav['nav_adjusted'].iloc[-1] / df_nav['nav_adjusted'].iloc[-2] - 1):.2%}"
        )
        specific_list = [
            "景林景泰优选GJ2期",
            "景林精选FOF子基金GJ2期",
            "景林景泰丰收GJ2期",
            "千宜乐享精选CTA2号",
        ]
        nav_df.loc[nav_df["基金产品"].isin(specific_list), "近一周收益"] = np.nan
        # 自定义排序列顺序
        cols = ["策略类型", "基金代码"] + [
            col for col in nav_df.columns if col not in ["策略类型", "基金代码"]
        ]
        nav_df = nav_df[cols]
        # 合并数据，使用 ignore_index=True 避免索引重复问题
        data = pd.concat([data, nav_df], axis=0, ignore_index=True)
    # 指定策略类型的自定义顺序
    custom_order = [
        "灵活配置",
        "主观成长",
        "主观价值",
        "主观逆向",
        "300指增",
        "500指增",
        "1000指增",
        "小市值指增",
        "量化选股",
        "市场中性",
        "套利",
        "CTA",
        "多策略",
        "其他",
    ]
    data["策略类型"] = pd.Categorical(
        data["策略类型"], categories=custom_order, ordered=True
    )
    data["2025收益数值"] = data["2025收益"].str.rstrip("%").astype(float) / 100
    data.sort_values(
        by=["策略类型", "2025收益数值"], ascending=[True, False], inplace=True
    )
    data.drop(columns=["2025收益数值"], inplace=True)
    # 重命名列
    data.rename(
        columns={"净值起始日期": "成立日期", "净值结束日期": "最新净值日期"},
        inplace=True,
    )
    # 保存到 Excel
    with pd.ExcelWriter(
        "report_data.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace"
    ) as writer:
        data.to_excel(writer, sheet_name="Sheet2", index=False)


# 主程序
if __name__ == "__main__":
    fund_info = load_data("产品代码.xlsx")
    fund_info["基金代码"] = fund_info["基金代码"].astype(str)
    data_path = Path("销售产品业绩表现监控表20250317-20250321.xlsx")
    nav_df = get_new_nav(data_path, fund_info)
    nav_dfs = update_nav_dfs(nav_df)
    delete_csv_files("./nav_dfs")
    update_nav_df(nav_dfs, fund_info)
    get_report_data(fund_info)
    print("数据更新完成")