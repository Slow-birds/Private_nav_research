import os
import pandas as pd
from pathlib import Path
from function import load_data
from nav_research import NavResearch

# 删除csv文件(辅助函数)
def delete_csv_files(directory):
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".csv"):
                os.remove(os.path.join(root, file))
                print(f"Deleted: {file}")

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
        nav_df = load_data(nav_df_path.iloc[0])
        nav_df["基金代码"] = row[1]
        nav_df["基金名称"] = row[2]
        nav_df = nav_df[["基金代码", "基金名称", "日期", "单位净值", "累计净值"]]
        nav_dfs = pd.concat([nav_dfs, nav_df], ignore_index=True)
    nav_dfs.to_csv("nav_dfs.csv", index=False, encoding="utf-8-sig")

# 获取需要更新的数据nav_df
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
    # 合并处理完后的df3、df4
    df5 = pd.concat([df3, df4], ignore_index=True)
    nav_df = df5[df5["基金代码"].isin(fundcode_list)].reset_index(drop=True)
    # 使用map更新"基金名称"列
    fund_name_map = fund_info.set_index("基金代码")["基金名称"].to_dict()
    nav_df["基金名称"] = nav_df["基金代码"].map(fund_name_map)
    return nav_df

# 更新nav_dfs.csv
def update_nav_dfs(nav_df):
    nav_dfs = pd.read_csv("nav_dfs.csv")
    nav_dfs = pd.concat([nav_dfs, nav_df], axis=0, ignore_index=True)
    nav_dfs.drop_duplicates(subset=["基金代码", "日期"], inplace=True)
    nav_dfs.sort_values(by=["基金代码", "日期"], inplace=True)
    nav_dfs.to_csv("nav_dfs.csv", index=False, encoding="utf-8-sig")
    return nav_dfs

# 生成单一净值数据
def update_nav_df(nav_dfs, fund_info):
    fundcode_list = fund_info["基金代码"].unique().tolist()
    # 确保输出目录存在
    os.makedirs("nav_data", exist_ok=True)
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
        print(f"Creat:{fundcode}_{fund_name}_{start_date}_{end_date}.csv")

# 获取多基金对比数据
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

# 生成可视化表格report_data.xlsx
def get_report_data(fund_info):
    data = pd.DataFrame()
    files_list_series = pd.Series(
        [
            i
            for i in Path("./nav_dfs").rglob("*")
            if i.suffix.lower() in {".csv", ".xlsx", ".xls"}
        ]
    )
    for row in fund_info.itertuples(index=False, name=None):
        nav_df_path = files_list_series[
            files_list_series.apply(lambda x: row[1] in x.stem)
        ]
        assert len(nav_df_path) == 1, "找到多个文件或者没有文件"
        demo = NavResearch(nav_df_path.item(), row[0], row[2], row[3], row[4], row[5])
        demo.get_data()
        tables = demo.get_analysis_table()
        nav_df = single_fund_table(tables, row[2])
        nav_df["策略类型"] = row[0]
        cols = ["策略类型"] + [col for col in nav_df.columns if col != "策略类型"]
        nav_df = nav_df[cols]
        data = pd.concat([data, nav_df], axis=0)
        data["2025收益数值"] = data["2025收益"].str.rstrip('%').astype(float) / 100
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
        data["策略类型"] = pd.Categorical(data["策略类型"], categories=custom_order, ordered=True)
        data.sort_values(by=["策略类型", "2025收益数值"], ascending=[True, False], inplace=True)
        data.drop(columns=["2025收益数值"], inplace=True)
    data.to_excel("report_data.xlsx", index=False)

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