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
    ):
        self.nav_data_path = nav_data_path
        self.strategy = strategy
        self.fund_name = fund_name
        self.benchmark_code = benchmark_code
        self.benchmark_name = benchmark_name
        self.freq = None
        self.risk_free_rate = 0.02
        self.threshold = threshold

    # df_nav, df_return, df_drawdown
    def get_data(self):
        # 净值数据读取、标准化、日期规范
        nav_df = load_data(self.nav_data_path)
        nav_df = nav_normalization(nav_df)
        freq = infer_frequency(self.fund_name, nav_df)
        nav_df = date_normalization(nav_df, freq)
        # 获取基准数据
        start_day = nav_df["date"].min().strftime("%Y-%m-%d")
        end_day = nav_df["date"].max().strftime("%Y-%m-%d")
        benchmark_df = benchmark_data(self.benchmark_code, start_day, end_day)
        # 合并数据
        nav_merge = pd.merge(nav_df, benchmark_df, on="date", how="left")
        # 剔除空值行、重置索引
        nav_merge = nav_merge.dropna()
        nav_merge = nav_merge.reset_index(drop=True)
        self.freq = freq
        self.start_day = start_day
        self.end_day = end_day
        self.nav_merge = nav_merge
        return self.nav_merge

    def get_data1(self):
        df = self.nav_merge
        # df_nav
        df["excess_nav"] = df["nav_adjusted"] - df[self.benchmark_code] + 1
        df_nav = df[
            [
                "date",
                "nav_unit",
                "nav_accumulated",
                "nav_adjusted",
                self.benchmark_code,
                "excess_nav",
            ]
        ].round(4)
        df_nav.drop_duplicates(subset=["date"], inplace=True)
        # df_return
        df["nav_return"] = df["nav_adjusted"].pct_change()
        df["benchmark_return"] = df[self.benchmark_code].pct_change()
        df[["nav_return", "benchmark_return"]] = df[
            ["nav_return", "benchmark_return"]
        ].fillna(0)
        df["excess_return"] = df["nav_return"] - df["benchmark_return"]
        df_return = df[
            ["date", "nav_return", "benchmark_return", "excess_return"]
        ].round(4)
        # df_drawdown
        df_nav_copy = df_nav.copy()
        ## fund_drawdown
        df_nav_copy["fun_max_so_far"] = df_nav_copy["nav_adjusted"].cummax()
        df_nav_copy["fund_drawdown"] = (
            df_nav_copy["nav_adjusted"] - df_nav_copy["fun_max_so_far"]
        ) / df_nav_copy["fun_max_so_far"]
        ## benchmark_drawdown
        df_nav_copy["benchmark_max_so_far"] = df_nav_copy[self.benchmark_code].cummax()
        df_nav_copy["benchmark_drawdown"] = (
            df_nav_copy[self.benchmark_code] - df_nav_copy["benchmark_max_so_far"]
        ) / df_nav_copy["benchmark_max_so_far"]
        ## excess_drawdown
        df_nav_copy["excess_max_so_far"] = df_nav_copy["excess_nav"].cummax()
        df_nav_copy["excess_drawdown"] = (
            df_nav_copy["excess_nav"] - df_nav_copy["excess_max_so_far"]
        ) / df_nav_copy["excess_max_so_far"]
        df_drawdown = df_nav_copy[
            ["date", "fund_drawdown", "benchmark_drawdown", "excess_drawdown"]
        ].round(4)
        # df_nav,f_return,df_drawdown
        self.df_nav = df_nav
        self.df_return = df_return
        self.df_drawdown = df_drawdown
        return self.df_nav, self.df_return, self.df_drawdown

    def get_analysis_table(self):
        # basic info table
        basic_info_table = pd.DataFrame(
            {
                "基金产品": [self.fund_name],
                "基准指数": [self.benchmark_name],
                "净值起始日期": [self.start_day],
                "净值结束日期": [self.end_day],
                "单位净值": [
                    self.df_nav.loc[self.df_nav["date"] == self.end_day, "nav_unit"]
                    .values[0]
                    .round(4)
                ],
                "累计净值": [
                    self.df_nav.loc[
                        self.df_nav["date"] == self.end_day, "nav_accumulated"
                    ]
                    .values[0]
                    .round(4)
                ],
                "复权净值": [
                    self.df_nav.loc[
                        self.df_nav["date"] == self.end_day, "nav_adjusted"
                    ]
                    .values[0]
                    .round(4)
                ],
            }
        )
        # nav ratio table
        days_diff = (
            (np.datetime64(self.end_day) - np.datetime64(self.start_day))
            .astype("timedelta64[D]")
            .astype(int)
        )
        ## total_return
        total_return = (
            list(self.df_nav["nav_adjusted"])[-1] / list(self.df_nav["nav_adjusted"])[0]
            - 1
        )
        excess_total_return = (
            list(self.df_nav["excess_nav"])[-1] / list(self.df_nav["excess_nav"])[0] - 1
        )
        ## annual_return
        annual_return = pow(1 + total_return, 365 / days_diff) - 1
        excess_annual_return = pow(1 + excess_total_return, 365 / days_diff) - 1
        ## max_drawdown
        max_drawdown = self.df_drawdown["fund_drawdown"].min()
        excess_max_drawdown = self.df_drawdown["excess_drawdown"].min()
        ## annual_volatility
        annual_volatility = self.df_return["nav_return"].std() * np.sqrt(
            250 if self.freq == "D" else 52
        )
        excess_annual_volatility = self.df_return["excess_return"].std() * np.sqrt(
            250 if self.freq == "D" else 52
        )
        ## sharpe_ratio
        sharpe_ratio = (annual_return - self.risk_free_rate) / annual_volatility
        excess_sharpe_ratio = (
            excess_annual_return - self.risk_free_rate
        ) / excess_annual_volatility
        nav_ratio_table = pd.DataFrame(
            {
                "整体业绩": ["产品收益", "超额收益"],
                "总收益率": [
                    format(total_return, ".2%"),
                    format(excess_total_return, ".2%"),
                ],
                "年化收益率": [
                    format(annual_return, ".2%"),
                    format(excess_annual_return, ".2%"),
                ],
                "最大回撤": [
                    format(max_drawdown, ".2%"),
                    format(excess_max_drawdown, ".2%"),
                ],
                "年化波动率": [
                    format(annual_volatility, ".2%"),
                    format(excess_annual_volatility, ".2%"),
                ],
                "夏普比率": [
                    format(sharpe_ratio, ".2f"),
                    format(excess_sharpe_ratio, ".2f"),
                ],
            }
        )
        # year return table
        # 计算年度指标
        year_return_table = calculate_annual_metrics(
            self.df_nav, self.fund_name, self.benchmark_code, self.benchmark_name
        )
        # 转换百分比为字符串
        year_return_table[f"{self.fund_name}_收益"] = year_return_table[
            f"{self.fund_name}_收益"
        ].map("{:.2%}".format)
        year_return_table[f"{self.benchmark_name}_收益"] = year_return_table[
            f"{self.benchmark_name}_收益"
        ].map("{:.2%}".format)
        year_return_table[f"{self.fund_name}_最大回撤"] = year_return_table[
            f"{self.fund_name}_最大回撤"
        ].map("{:.2%}".format)
        year_return_table[f"{self.benchmark_name}_最大回撤"] = year_return_table[
            f"{self.benchmark_name}_最大回撤"
        ].map("{:.2%}".format)
        year_return_table["超额收益"] = year_return_table["超额收益"].map("{:.2%}".format)
        # 不转换百分比为字符串，而是使用style来格式化输出
        """
        def format_percentages(val):
            return f"{val * 100:.2f}%" if val is not None else "-"
        year_return_table =year_return_df.style.format({
            f"{self.fund_name}_收益": format_percentages,
            f"{self.fund_name}_最大回撤": format_percentages,  # 假设最大回撤也是一个小数形式的比例
            f"{self.benchmark_name}_收益": format_percentages,
            f"{self.benchmark_name}_最大回撤": format_percentages,
            "超额收益": format_percentages,
        })
        """
        # month_return
        data = self.df_nav[["date", "nav_adjusted"]]
        month_return = win_ratio_stastics(nav=data["nav_adjusted"],date=data["date"])
        month_return.index.name = "分月度业绩"
        month_return_table = month_return.reset_index(drop=False)
        # drawdown table
        # 初始化
        drawdowns = []
        start_idx = None
        end_idx = None
        peak_value = None
        for i in range(1, len(self.df_nav)):
            if start_idx is None and self.df_drawdown["fund_drawdown"].iloc[i] < 0:
                # 回撤开始
                start_idx = i - 1
                peak_value = self.df_nav["nav_adjusted"].iloc[i - 1]
            elif start_idx is not None:
                # 检查是否回升到回撤前的水平
                if self.df_nav["nav_adjusted"].iloc[i] >= peak_value:
                    # 回补结束
                    end_idx = i
                    # 记录回撤信息
                    drawdown_start_date = self.df_drawdown["date"].iloc[start_idx]
                    drawdown_end_date = self.df_drawdown["date"].iloc[
                        np.argmin(self.df_drawdown["fund_drawdown"][start_idx:end_idx])
                        + start_idx
                    ]
                    reset_end_date = self.df_drawdown["date"].iloc[end_idx]
                    fund_drawdown_percentage = self.df_drawdown["fund_drawdown"].iloc[
                        np.argmin(self.df_drawdown["fund_drawdown"][start_idx:end_idx])
                        + start_idx
                    ]
                    drawdowns.append(
                        (
                            drawdown_start_date,
                            drawdown_end_date,
                            reset_end_date,
                            fund_drawdown_percentage,
                        )
                    )
                    # 重置变量以寻找下一个回撤
                    start_idx = None
                    peak_value = None
        # 检查遍历结束后是否还有未完成的回撤
        if start_idx is not None:
            # 假设回撤结束于数据的最后一天
            end_idx = len(self.df_drawdown) - 1
            drawdown_start_date = self.df_drawdown["date"].iloc[start_idx]
            drawdown_end_date = self.df_drawdown["date"].iloc[
                np.argmin(self.df_drawdown["fund_drawdown"][start_idx:end_idx])
                + start_idx
            ]
            # 注意：这里我们假设没有回补，所以reset_end_date就是数据的最后一天
            reset_end_date = self.df_drawdown["date"].iloc[end_idx]
            fund_drawdown_percentage = self.df_drawdown["fund_drawdown"].iloc[
                np.argmin(self.df_drawdown["fund_drawdown"][start_idx:end_idx])
                + start_idx
            ]
            drawdowns.append(
                (
                    drawdown_start_date,
                    drawdown_end_date,
                    reset_end_date,
                    fund_drawdown_percentage,
                )
            )
        data_drawdown = pd.DataFrame(
            drawdowns, columns=["回撤开始时间", "回撤结束时间", "回补结束时间", "回撤"]
        )
        data_drawdown["回撤天数"] = (
            data_drawdown["回撤结束时间"] - data_drawdown["回撤开始时间"]
        )
        data_drawdown["回补天数"] = (
            data_drawdown["回补结束时间"] - data_drawdown["回撤结束时间"]
        )
        filtered_data = data_drawdown[data_drawdown["回撤"] < self.threshold]
        filtered_data.loc[
            filtered_data["回补结束时间"] == self.df_drawdown["date"].max(),
            ["回补结束时间", "回补天数"],
        ] = ""
        filtered_data["回撤"] = filtered_data["回撤"].map(lambda x: f"{x*100:.2f}%")
        drawdown_table = filtered_data
        table_list = [
            basic_info_table,
            nav_ratio_table,
            year_return_table,
            drawdown_table,
            month_return_table,
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
                    {table_html_five}
                    {drawdown_line.render_embed()}
                    {table_html_four}
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
