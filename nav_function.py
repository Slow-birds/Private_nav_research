import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import copy
from pyecharts.charts import Line
import pyecharts.options as opts
from WindPy import w

w.start()


# nav_adjusted
def get_nav_adjusted(nav_df):
    nav_df_copy = nav_df.copy()
    nav_df_copy["nav_adjusted"] = np.nan
    nav_df_copy.loc[0, "nav_adjusted"] = 1
    for i in range(1, len(nav_df_copy)):
        nav_adjusted_new = (
            nav_df_copy.loc[i, "nav_accumulated"]
            - nav_df_copy.loc[i - 1, "nav_accumulated"]
        ) / nav_df_copy.loc[i - 1, "nav_unit"] + 1
        nav_adjusted_new *= nav_df_copy.loc[i - 1, "nav_adjusted"]
        nav_df_copy.loc[i, "nav_adjusted"] = nav_adjusted_new
    return nav_df_copy


# df_nav, df_return, df_drawdown
def get_data(nav_df_path, fund_name, benchmark):
    # nav data
    nav_df = pd.read_excel(nav_df_path, sheet_name=fund_name)
    nav_df = nav_df[["日期", "单位净值", "累计净值"]].rename(
        columns={"日期": "date", "单位净值": "nav_unit", "累计净值": "nav_accumulated"}
    )
    nav_df["date"] = pd.to_datetime(nav_df["date"])
    nav_df = nav_df.sort_values(by="date")
    nav_df["nav_unit"] = nav_df["nav_unit"] / nav_df["nav_unit"][0]
    nav_df["nav_accumulated"] = nav_df["nav_accumulated"] / nav_df["nav_accumulated"][0]
    nav_df = get_nav_adjusted(nav_df)
    # start_date, end_date
    start_date = pd.Timestamp(nav_df["date"].min()).strftime("%Y-%m-%d")
    end_date = pd.Timestamp(nav_df["date"].max()).strftime("%Y-%m-%d")
    # benchmark data
    error_code, benchmark_df = w.wsd(
        benchmark, "close", start_date, end_date, "Fill=Previous", usedf=True
    )
    benchmark_df.reset_index(inplace=True)
    benchmark_df.columns = ["date", benchmark]
    benchmark_df["date"] = pd.to_datetime(benchmark_df["date"])
    benchmark_df[benchmark] = benchmark_df[benchmark] / benchmark_df[benchmark][0]
    # df_nav
    df = pd.merge(nav_df, benchmark_df, on="date", how="left")
    df["excess_nav"] = df["nav_adjusted"] - df[benchmark] + 1
    df_nav = df[
        ["date", "nav_unit", "nav_accumulated", "nav_adjusted", benchmark, "excess_nav"]
    ].round(4)
    # df_return
    df["nav_return"] = df["nav_adjusted"].pct_change()
    df["benchmark_return"] = df[benchmark].pct_change()
    df[["nav_return", "benchmark_return"]] = df[
        ["nav_return", "benchmark_return"]
    ].fillna(0)
    df["excess_return"] = df["nav_return"] - df["benchmark_return"]
    df_return = df[["date", "nav_return", "benchmark_return", "excess_return"]].round(4)
    df_nav_copy = df_nav.copy()
    # df_drawdown
    df_nav_copy = df_nav.copy()
    # fund_drawdown
    df_nav_copy["fun_max_so_far"] = df_nav_copy["nav_adjusted"].cummax()
    df_nav_copy["fund_drawdown"] = (
        df_nav_copy["nav_adjusted"] - df_nav_copy["fun_max_so_far"]
    ) / df_nav_copy["fun_max_so_far"]
    # benchmark_drawdown
    df_nav_copy["benchmark_max_so_far"] = df_nav_copy[benchmark].cummax()
    df_nav_copy["benchmark_drawdown"] = (
        df_nav_copy[benchmark] - df_nav_copy["benchmark_max_so_far"]
    ) / df_nav_copy["benchmark_max_so_far"]
    # excess_drawdown
    df_nav_copy["excess_max_so_far"] = df_nav_copy["excess_nav"].cummax()
    df_nav_copy["excess_drawdown"] = (
        df_nav_copy["excess_nav"] - df_nav_copy["excess_max_so_far"]
    ) / df_nav_copy["excess_max_so_far"]
    df_drawdown = df_nav_copy[
        ["date", "fund_drawdown", "benchmark_drawdown", "excess_drawdown"]
    ].round(4)
    return df_nav, df_return, df_drawdown


def infer_frequency(df_nav):
    date = df_nav["date"].values
    # 如果大部分日期间隔为 1 天，那么数据可能是日度的
    if (np.diff(date) == np.timedelta64(1, "D")).mean() > 0.75:
        return "D"
    elif (np.diff(date) >= np.timedelta64(5, "D")).mean() > 0.75:
        return "W"
    else:
        raise ValueError("无法推断频率")


# basic info table
def get_basic_info(df_nav, fund_name, benchmark_name):
    # start_date->end_date
    start_date = pd.Timestamp(df_nav["date"].min()).strftime("%Y-%m-%d")
    end_date = pd.Timestamp(df_nav["date"].max()).strftime("%Y-%m-%d")
    basic_info_table = pd.DataFrame(
        {
            "基金产品": [fund_name],
            "基准指数": [benchmark_name],
            "净值起始日期": [start_date],
            "净值结束日期": [end_date],
            "单位净值": [
                df_nav.loc[df_nav["date"] == end_date, "nav_unit"].values[0].round(4)
            ],
            "累计净值": [
                df_nav.loc[df_nav["date"] == end_date, "nav_accumulated"]
                .values[0]
                .round(4)
            ],
            "复权净值": [
                df_nav.loc[df_nav["date"] == end_date, "nav_adjusted"]
                .values[0]
                .round(4)
            ],
        }
    )
    return basic_info_table


# nav ratio table
def get_nav_ratio(df_nav, df_return, df_drawdown, freq):
    # start_date->end_date
    start_date = np.datetime64(pd.Timestamp(df_nav["date"].min()).strftime("%Y-%m-%d"))
    end_date = np.datetime64(pd.Timestamp(df_nav["date"].max()).strftime("%Y-%m-%d"))
    days_diff = (end_date - start_date).astype("timedelta64[D]").astype(int)
    risk_free_rate = 0.02
    # total_return
    total_return = (
        list(df_nav["nav_adjusted"])[-1] / list(df_nav["nav_adjusted"])[0] - 1
    )
    excess_total_return = (
        list(df_nav["excess_nav"])[-1] / list(df_nav["excess_nav"])[0] - 1
    )
    # annual_return
    annual_return = pow(1 + total_return, 365 / days_diff) - 1
    excess_annual_return = pow(1 + excess_total_return, 365 / days_diff) - 1
    # max_drawdown
    max_drawdown = df_drawdown["fund_drawdown"].min()
    excess_max_drawdown = df_drawdown["excess_drawdown"].min()
    # annual_volatility
    annual_volatility = df_return["nav_return"].std() * np.sqrt(
        250 if freq == "D" else 52
    )
    excess_annual_volatility = df_return["excess_return"].std() * np.sqrt(
        250 if freq == "D" else 52
    )
    # sharpe_ratio
    sharpe_ratio = (annual_return - risk_free_rate) / annual_volatility
    excess_sharpe_ratio = (
        excess_annual_return - risk_free_rate
    ) / excess_annual_volatility
    nav_ratio_table = pd.DataFrame(
        {
            "整体业绩": ["绝对收益", "超额收益"],
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
    return nav_ratio_table


# year return table
def get_year_return(df_nav, fund_name, benchmark, benchmark_name):
    df_year = (
        df_nav.sort_values("date").groupby(df_nav["date"].dt.to_period("Y")).tail(1)
    )
    first_row_df_nav = df_nav.iloc[0:1]
    df_year = pd.concat([first_row_df_nav, df_year], ignore_index=True)
    df_year[f"{fund_name}_收益"] = (
        df_year["nav_adjusted"] / df_year["nav_adjusted"].shift(1) - 1
    )
    df_year[f"{benchmark_name}_收益"] = (
        df_year[benchmark] / df_year[benchmark].shift(1) - 1
    )
    df_year["超额收益"] = (
        df_year[f"{fund_name}_收益"] - df_year[f"{benchmark_name}_收益"]
    )
    df_year["分年度业绩"] = df_year["date"].dt.year
    df_year[f"{fund_name}_收益"] = df_year[f"{fund_name}_收益"].apply(
        lambda x: f"{x:.2%}"
    )
    df_year[f"{benchmark_name}_收益"] = df_year[f"{benchmark_name}_收益"].apply(
        lambda x: f"{x:.2%}"
    )
    df_year["超额收益"] = df_year["超额收益"].apply(lambda x: f"{x:.2%}")
    year_return_table = df_year[
        ["分年度业绩", f"{fund_name}_收益", f"{benchmark_name}_收益", "超额收益"]
    ].drop(index=0)
    return year_return_table


# drawdown table
def get_drawdown_info(df_nav, df_drawdown, threshold):
    # 初始化
    drawdowns = []
    start_idx = None
    end_idx = None
    peak_value = None
    for i in range(1, len(df_nav)):
        if start_idx is None and df_drawdown["fund_drawdown"].iloc[i] < 0:
            # 回撤开始
            start_idx = i - 1
            peak_value = df_nav["nav_adjusted"].iloc[i - 1]
        elif start_idx is not None:
            # 检查是否回升到回撤前的水平
            if df_nav["nav_adjusted"].iloc[i] >= peak_value:
                # 回补结束
                end_idx = i
                # 记录回撤信息
                drawdown_start_date = df_drawdown["date"].iloc[start_idx]
                drawdown_end_date = df_drawdown["date"].iloc[
                    np.argmin(df_drawdown["fund_drawdown"][start_idx:end_idx])
                    + start_idx
                ]
                reset_end_date = df_drawdown["date"].iloc[end_idx]
                fund_drawdown_percentage = df_drawdown["fund_drawdown"].iloc[
                    np.argmin(df_drawdown["fund_drawdown"][start_idx:end_idx])
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
        end_idx = len(df_drawdown) - 1
        drawdown_start_date = df_drawdown["date"].iloc[start_idx]
        drawdown_end_date = df_drawdown["date"].iloc[
            np.argmin(df_drawdown["fund_drawdown"][start_idx:end_idx]) + start_idx
        ]
        # 注意：这里我们假设没有回补，所以reset_end_date就是数据的最后一天
        reset_end_date = df_drawdown["date"].iloc[end_idx]
        fund_drawdown_percentage = df_drawdown["fund_drawdown"].iloc[
            np.argmin(df_drawdown["fund_drawdown"][start_idx:end_idx]) + start_idx
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
    filtered_data = data_drawdown[data_drawdown["回撤"] < threshold]
    filtered_data.loc[
        filtered_data["回补结束时间"] == df_drawdown["date"].max(),
        ["回补结束时间", "回补天数"],
    ] = ""
    filtered_data["回撤"] = filtered_data["回撤"].map(lambda x: f"{x*100:.2f}%")
    return filtered_data


def get_nav_lines(df, fund_name, benchmark_name):

    x_data = df["date"].dt.strftime("%Y-%m-%d").tolist()
    ys_data = (
        (df.drop(columns=["date", "nav_unit", "nav_accumulated"], axis=1) - 1) * 100
    ).round(2)
    min_data = (ys_data.values.min() - 10).round()
    max_data = (ys_data.values.max() + 10).round()
    names = [
        f"{fund_name}_累计收益(%)",
        f"{benchmark_name}_累计收益(%)",
        f"{fund_name}_超额收益(%)",
    ]
    init_opts = {
        "width": "1500px",
        "height": "500px",
        "is_horizontal_center": True,
    }
    line = Line(init_opts)
    line.add_xaxis(x_data)
    for i, name in enumerate(names):
        y_values = ys_data.iloc[:, i].tolist()
        line.add_yaxis(name, y_values, symbol="none")

    line.set_global_opts(
        legend_opts=opts.LegendOpts(
            textstyle_opts=opts.TextStyleOpts(font_weight="bold", font_size=20)
        ),
        datazoom_opts=[
            opts.DataZoomOpts(range_start=0, range_end=100, orient="horizontal")
        ],
        title_opts=opts.TitleOpts("Value over Time"),
        yaxis_opts=opts.AxisOpts(min_=min_data, max_=max_data),
        tooltip_opts=opts.TooltipOpts(trigger="axis"),
    ).set_series_opts(
        linestyle_opts=opts.LineStyleOpts(width=2),
    )
    # line.render_notebook()
    return line


def get_drawdown_lines(df, fund_name, benchmark_name):
    x_data = df["date"].dt.strftime("%Y-%m-%d").tolist()
    ys_data = ((df.drop("date", axis=1)) * 100).round(2)

    min_data = (ys_data.values.min() - 10).round(0)
    max_data = ys_data.values.max().round(0)
    names = [
        f"{fund_name}_回撤(%)",
        f"{benchmark_name}_回撤(%)",
        f"{fund_name}_超额回撤(%)",
    ]
    init_opts = {
        "width": "1500px",
        "height": "500px",
        "is_horizontal_center": True,
    }
    line = Line(init_opts)
    line.add_xaxis(x_data)
    for i, name in enumerate(names):
        y_values = ys_data.iloc[:, i].tolist()
        line.add_yaxis(name, y_values, symbol="none")

    line.set_global_opts(
        legend_opts=opts.LegendOpts(
            textstyle_opts=opts.TextStyleOpts(font_weight="bold", font_size=20)
        ),
        datazoom_opts=[
            opts.DataZoomOpts(range_start=0, range_end=100, orient="horizontal")
        ],
        title_opts=opts.TitleOpts("Value over Time"),
        yaxis_opts=opts.AxisOpts(min_=min_data, max_=max_data),
        tooltip_opts=opts.TooltipOpts(trigger="axis"),
    ).set_series_opts(
        linestyle_opts=opts.LineStyleOpts(width=2),
    )
    # line.render_notebook()
    return line


def get_html(
    df_nav,
    fund_name,
    post_viewpoint_content,
    table_one,
    table_two,
    table_three,
    table_four,
    line_one,
    line_two,
):
    # start_date->end_date
    start_date = np.datetime64(pd.Timestamp(df_nav["date"].min()).strftime("%Y-%m-%d"))
    end_date = np.datetime64(pd.Timestamp(df_nav["date"].max()).strftime("%Y-%m-%d"))
    table_html_one = table_one.to_html(index=False, classes="uniform-width")
    table_html_two = table_two.to_html(index=False, classes="uniform-width")
    table_html_three = table_three.to_html(index=False, classes="uniform-width")
    table_html_four = table_four.to_html(index=False, classes="uniform-width")
    html = f"""
        <html>
            <head>
                <meta charset="UTF-8">
                <title>Value over Time</title>
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
                            width: 80%;
                        }}
                    table, th, td {{
                            border: 1px solid #ddd;
                            padding: 8px;
                            text-align: center; 
                        }}
                    th {{
                            background-color: #f59e00;
                            color: white;
                        }}
                </style>
            </head>
            <body>
                <h1>后维单页_{fund_name}</h1>
                {post_viewpoint_content}
                {table_html_one}
                {line_one.render_embed()}
                {table_html_two}
                {table_html_three}
                {line_two.render_embed()}
                {table_html_four}
            </body>
        </html>
    """
    html_name = (
        np.datetime_as_string(start_date, unit="D").replace("-", "")
        + "_"
        + np.datetime_as_string(end_date, unit="D").replace("-", "")
        + "_"
        + fund_name
        + "_nav_analysis"
    )
    with open(html_name + ".html", "w", encoding="utf-8") as f:
        f.write(html)


def get_plot(df_nav, benchmark, benchmark_name):
    # data
    df_nav_ = df_nav.copy()
    # fund_drawdown
    df_nav_["fun_max_so_far"] = df_nav_["nav_adjusted"].cummax()
    df_nav_["fund_drawdown"] = (
        df_nav_["fun_max_so_far"] - df_nav_["nav_adjusted"]
    ) / df_nav_["fun_max_so_far"]
    # benchmark_drawdown
    df_nav_["benchmark_max_so_far"] = df_nav_[benchmark].cummax()
    df_nav_["benchmark_drawdown"] = (
        df_nav_["benchmark_max_so_far"] - df_nav_[benchmark]
    ) / df_nav_["benchmark_max_so_far"]
    # excess_drawdown
    df_nav_["excess_max_so_far"] = df_nav_["excess_nav"].cummax()
    df_nav_["excess_drawdown"] = (
        df_nav_["excess_max_so_far"] - df_nav_["excess_nav"]
    ) / df_nav_["excess_max_so_far"]
    # plot
    fig, (ax1, ax2) = plt.subplots(nrows=2, figsize=(25, 14))
    # 画超额收益图
    ax1.plot(
        df_nav_["date"], df_nav_["nav_adjusted"] - 1, color="red", label="累计收益"
    )
    ax1.plot(
        df_nav_["date"], df_nav_[benchmark] - 1, color="blue", label=benchmark_name
    )
    ax1.fill_between(
        df_nav_["date"], df_nav_["excess_nav"] - 1, color="gray", label="超额收益"
    )
    ax1.legend(loc="upper left", fontsize=15)
    ax1.tick_params(axis="x", rotation=45, labelsize=15)
    ax1.tick_params(axis="y", labelsize=15)
    ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax1.set_title("超额收益及动态回撤图", size=25)
    ax1.grid()
    # 画动态回撤图
    ax2.plot(df_nav_["date"], -df_nav_["fund_drawdown"], color="red", label="基金回撤")
    ax2.plot(
        df_nav_["date"], -df_nav_["benchmark_drawdown"], color="blue", label="基准回撤"
    )
    ax2.fill_between(
        df_nav_["date"], -df_nav_["excess_drawdown"], color="gray", label="超额回撤"
    )
    ax2.legend(loc="lower left", fontsize=15)
    ax2.tick_params(axis="x", rotation=45, labelsize=15)
    ax2.tick_params(axis="y", labelsize=15)
    ax2.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
    ax2.grid()
    return plt.show()


# 暂时弃用
# max_drawdown
def get_max_drawdown(df_nav, column_name):
    df_nav[f"{column_name}_max_so_far"] = df_nav[column_name].cummax()
    df_nav[f"{column_name}_drawdown"] = (
        df_nav[column_name] - df_nav[f"{column_name}_max_so_far"]
    ) / df_nav[f"{column_name}_max_so_far"]
    max_drawdown = df_nav[f"{column_name}_drawdown"].min()
    return max_drawdown
