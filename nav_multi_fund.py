from function import load_data
from nav_research import NavResearch
import pandas as pd
from pathlib import Path


basic_info = load_data("产品目录.xlsx")
# strategy_info = basic_info[basic_info["大类策略"] == "量化CTA"]


def multi_fund_comparison(tables, fund_name):
    data1 = tables[0]
    data2 = tables[1].head(1)
    data3 = pd.DataFrame()
    data4 = tables[2]
    years = [2019, 2020, 2021, 2022, 2023, 2024, 2025]
    for year in years:
        data3[f"{year}收益"] = data4.loc[
            data4["分年度业绩"] == year, f"{fund_name}_收益"
        ].values
        '''
        data3[f"{year}最大回撤"] = data4.loc[
            data4["分年度业绩"] == year, f"{fund_name}_最大回撤"
        ].values
        '''
    # data3 = data3[["2025收益","2024收益","2023收益","2022收益","2021收益","2020收益","2019收益"]]
    data = pd.concat([data1, data2, data3], axis=1)
    data.drop(columns=["基准指数", "整体业绩"], inplace=True)
    return data


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
    demo = NavResearch(nav_df_path.item(), row[0], row[3], row[4], row[5], row[6])
    nav_df, _, _ = demo.get_data()
    nav_df.to_csv(f"temporary_data/{row[3]}.csv", index=False)
    tables = demo.get_analysis_table()
    nav_df = multi_fund_comparison(tables, row[3])
    data = pd.concat([data, nav_df], axis=0)

with pd.ExcelWriter(
    "data.xlsx", engine="openpyxl", mode="a", if_sheet_exists="replace"
) as writer:
    data.to_excel(writer, sheet_name="huofuniu", index=False)

print("数据已保存到data.xlsx")
