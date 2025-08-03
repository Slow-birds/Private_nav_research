from function import load_data
from nav_research import NavResearch
import pandas as pd
from pathlib import Path
import datetime

def single_fund_ratio(tables):
    data1 = tables[0]
    data2 = tables[1].head(1)
    data3 = pd.DataFrame()
    data4 = tables[2]
    years = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
    for year in years:
        data3[f"{year}收益"] = data4.loc[
            data4["分年度业绩"] == year, "基金收益"
        ].values
        '''
        data3[f"{year}最大回撤"] = data4.loc[
            data4["分年度业绩"] == year, "基金最大回撤"
        ].values
        '''
    # data3 = data3[["2025收益","2024收益","2023收益","2022收益","2021收益","2020收益","2019收益"]]
    data = pd.concat([data1, data2, data3], axis=1)
    data.drop(columns=["基准指数","整体收益"], inplace=True)
    return data

def multi_fund_comparison(basic_info, end_day = "2025-07-25"):
    data = pd.DataFrame()
    files_list_series = pd.Series(
        [
            i
            for i in Path("./data").rglob("*")
            if i.suffix.lower() in {".csv", ".xlsx", ".xls"}
        ]
    )
    for row in basic_info.itertuples(index=False, name=None):
        nav_df_path = files_list_series[files_list_series.apply(lambda x: row[3] in x.stem)]
        assert len(nav_df_path) == 1, "找到多个文件或者没有文件"
        demo = NavResearch(nav_df_path.item(), row[0], row[3], row[4], row[5], row[6], end_day)
        nav_df = demo.get_data()
        tables = demo.get_analysis_table()
        nav_ratio = single_fund_ratio(tables)
        # 增加近一月、近一周收益列
        enddate = datetime.datetime.strptime(end_day, "%Y-%m-%d")
        nav_ratio[f"{enddate.month}月收益"] = tables[3].loc[tables[3]["分月度业绩"] == enddate.year,f"{enddate.month}月"].item()
        nav_ratio["近一周收益"] = (f"{(nav_df['nav_adjusted'].iloc[-1] / nav_df['nav_adjusted'].iloc[-2] - 1):.2%}")
        data = pd.concat([data, nav_ratio], axis=0)
    return data

if __name__ == "__main__":
    basic_info = load_data("产品目录.xlsx")
    data = multi_fund_comparison(basic_info, end_day = "2025-07-25")
    with pd.ExcelWriter(
        "report_data.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace"
    ) as writer:
        data.to_excel(writer, sheet_name="sheet1", index=False)

    print("数据已保存到report_data.xlsx")
