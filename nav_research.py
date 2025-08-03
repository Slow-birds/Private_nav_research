import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os
import copy
from WindPy import w

w.start()
from function import *
import pyecharts.options as opts
from pyecharts.charts import Line
from pyecharts.globals import ThemeType
import warnings

warnings.filterwarnings("ignore")

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False


class NavResearch:
    def __init__(
        self,
        nav_data_path,
        strategy,
        fund_name,
        benchmark_code,
        benchmark_name,
        threshold,
        end_date_dt = datetime.datetime.now(),
    ):
        self.nav_data_path = nav_data_path
        self.strategy = strategy
        self.fund_name = fund_name
        self.benchmark_code = benchmark_code
        self.benchmark_name = benchmark_name
        self.freq = None
        self.risk_free_rate = 0.02
        self.threshold = threshold
        self.end_date_dt = end_date_dt

    # df_nav, df_return, df_drawdown
    def get_data(self):
        # 净值数据读取、标准化、日期规范
        original_df = load_data(self.nav_data_path)
        original_df = nav_normalization(original_df)
        self.original_df = original_df
        freq = infer_frequency(original_df)
        nav_df = date_normalization(original_df, freq)
        nav_df = nav_df[(nav_df["date"] <= self.end_date_dt)]
        print(nav_df.head())
        start_day = nav_df["date"].min().strftime("%Y-%m-%d")
        end_day = nav_df["date"].max().strftime("%Y-%m-%d")
        self.freq = freq
        self.nav_df = nav_df
        self.start_day = start_day
        self.end_day = end_day
        return self.nav_df
    def get_analysis_table(self):
        df_nav, df_return, df_drawdown = intermediate_df(self.nav_df, self.benchmark_code)
        self.df_nav = df_nav
        self.df_return = df_return
        self.df_drawdown = df_drawdown
        overall_performance_table = calculate_overall_performance(df_nav, df_drawdown, df_return, self.freq)
        annual_performance_table = calculate_annual_performance(df_nav, self.benchmark_code)
        monthly_performance_table = calculate_monthly_performance(df_nav)
        drawdown_table = calculate_drawdown(df_nav, df_drawdown, self.threshold)
        basic_info_table = pd.DataFrame(
            {
                "基金产品": [self.fund_name],
                "基准指数": [self.benchmark_name],
                "净值起始日期": [self.start_day],
                "净值结束日期": [self.end_day],
                "单位净值": [
                    self.original_df.loc[self.original_df["date"] == self.end_day, "nav_unit"].values[0].round(4) 
                    if "nav_unit" in self.original_df.columns 
                    else np.nan
                ],
                "累计净值": [
                    self.original_df.loc[self.original_df["date"] == self.end_day, "nav_accumulated"].values[0].round(4)
                    if "nav_accumulated" in self.original_df.columns
                    else np.nan
                ],
                "复权净值": [
                    df_nav.loc[df_nav["date"] == self.end_day, "nav_adjusted"].values[0].round(4)
                    if "nav_adjusted" in df_nav.columns
                    else np.nan
                ],
            }
        )
        table_list = [
            basic_info_table,
            overall_performance_table,
            annual_performance_table,
            monthly_performance_table,
            drawdown_table,
        ]
        self.table_list = table_list
        return self.table_list

    def get_html(self):
        table_html_one = self.table_list[0].to_html(
            index=False, classes="uniform-width"
        )
        table_html_two = self.table_list[1].to_html(
            index=False, classes="uniform-width"
        )
        table_html_three = self.table_list[2].to_html(
            index=False, classes="uniform-width"
        )
        table_html_four = self.table_list[3].to_html(
            index=False, classes="uniform-width"
        )
        table_html_five = self.table_list[4].to_html(
            index=False, classes="uniform-width"
        )
        nav_line = get_nav_lines(self.df_nav, self.fund_name, self.benchmark_name)
        drawdown_line = get_drawdown_lines(
            self.df_drawdown, self.fund_name, self.benchmark_name
        )
        html = f"""
            <html>
                <head>
                    <meta charset="UTF-8">
                    <title>{self.fund_name}</title>
                    <style>
                        body {{
                                font-family: Arial, sans-serif;
                                margin: 0;
                                padding: 0;
                            }}
                        h1 {{  
                                text-align: center;  
                                margin-top: 20px;  
                                font-size: 24px;  
                                color: #333;  
                            }}.post-viewpoint {{  
                        margin: 20px auto;  
                        padding: 10px;  
                        width: 80%;  
                        border: 1px solid #ddd;  
                        background-color: #f9f9f9;  
                        text-align: left;  
                    }} 
                        table {{
                                margin: auto;
                                margin-bottom: 20px;
                                border-collapse: collapse;
                                width: 1500px;
                                text-align: center;
                            }}
                        table, th, td {{
                                border: 1px solid #ddd;
                                padding: 8px;
                                text-align: center; 
                            }}
                        th {{
                                background-color: #3299CC;
                                color: white;
                            }}
                    </style>
                </head>
                <body>
                    <h1>{self.strategy}_{self.fund_name}</h1>
                    {table_html_one}
                    {nav_line.render_embed()}
                    {table_html_two}
                    {table_html_three}
                    {table_html_four}
                    {drawdown_line.render_embed()}
                    {table_html_five}
                </body>
            </html>
        """
        html_name = (
            np.datetime_as_string(np.datetime64(self.start_day), unit="D").replace(
                "-", ""
            )
            + "_"
            + np.datetime_as_string(np.datetime64(self.end_day), unit="D").replace(
                "-", ""
            )
            + "_"
            + self.fund_name
            + "_nav_analysis"
        )
        # folder_path = rf"C:\Users\17820\Desktop\VScode\Private_nav_research\docs\{self.strategy}"
        folder_path = rf"docs\{self.strategy}"
        # 构建完整文件路径
        file_path = f"{folder_path}\\{html_name}.html"
        # 确保文件夹存在（如果不存在则创建）
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html)
        # print(f"Create:{html_name}.html")
        print(f"Create:{folder_path}/{html_name}.html")

    def get_plot(self):
        # plot
        fig, (ax1, ax2) = plt.subplots(nrows=2, figsize=(25, 14))
        # 画超额收益图
        ax1.plot(
            self.df_nav["date"],
            self.df_nav["nav_adjusted"] - 1,
            color="red",
            label="累计收益",
        )
        ax1.plot(
            self.df_nav["date"],
            self.df_nav[self.benchmark_code] - 1,
            color="blue",
            label=self.benchmark_name,
        )
        ax1.fill_between(
            self.df_nav["date"],
            self.df_nav["excess_nav"] - 1,
            color="gray",
            label="超额收益",
        )
        ax1.legend(loc="upper left", fontsize=15)
        ax1.tick_params(axis="x", rotation=45, labelsize=15)
        ax1.tick_params(axis="y", labelsize=15)
        ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        ax1.set_title("超额收益及动态回撤图", size=25)
        ax1.grid()
        # 画动态回撤图
        ax2.plot(
            self.df_drawdown["date"],
            self.df_drawdown["fund_drawdown"],
            color="red",
            label="基金回撤",
        )
        ax2.plot(
            self.df_drawdown["date"],
            self.df_drawdown["benchmark_drawdown"],
            color="blue",
            label="基准回撤",
        )
        ax2.fill_between(
            self.df_drawdown["date"],
            self.df_drawdown["excess_drawdown"],
            color="gray",
            label="超额回撤",
        )
        ax2.legend(loc="lower left", fontsize=15)
        ax2.tick_params(axis="x", rotation=45, labelsize=15)
        ax2.tick_params(axis="y", labelsize=15)
        ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
        ax2.grid()
        return plt.show()
