import numpy as np
import pandas as pd
from pathlib import Path
import datetime
from typing import Union, Tuple
from pandas import Series, Timestamp
import copy
from pyecharts.charts import Line
import pyecharts.options as opts
from typing import Literal
from WindPy import w

w.start()


# 时间格式转换
def format_date(
    date: Union[datetime.datetime, datetime.date, np.datetime64, int, str]
) -> Series | Timestamp:
    """
    输出格式为 pd.Timestamp, 等同于 np.datetime64
    如果想要str格式, 即调用format_date(***).strftime('%Y-%m-%d')
    """
    if isinstance(date, datetime.datetime):
        return pd.to_datetime(date.date())
    elif isinstance(date, datetime.date):
        return pd.to_datetime(date)
    elif isinstance(date, np.datetime64):
        return pd.to_datetime(date)
    elif isinstance(date, int):
        date = pd.to_datetime(date, format="%Y%m%d")
        return date
    elif isinstance(date, str):
        date = pd.to_datetime(date)
        return pd.to_datetime(date.date())
    else:
        raise TypeError("date should be str, int or timestamp!")


# 加载数据
def load_data(df_path):
    df_path = Path(df_path)
    file_suffix = df_path.suffix
    if file_suffix in [".csv"]:
        df = pd.read_csv(df_path, encoding="utf-8")
    elif file_suffix in [".xls", ".xlsx"]:
        df = pd.read_excel(df_path)
    else:
        print("非CSV或Excel格式的文件")
    return df


# 求复权净值(nav_adjusted)
def get_nav_adjusted(nav_df):
    nav_df = nav_df.copy()
    nav_df["nav_adjusted"] = np.nan
    nav_df.loc[0, "nav_adjusted"] = 1
    for i in range(1, len(nav_df)):
        nav_adjusted_new = (
            nav_df.loc[i, "nav_accumulated"] - nav_df.loc[i - 1, "nav_accumulated"]
        ) / nav_df.loc[i - 1, "nav_unit"] + 1
        nav_adjusted_new *= nav_df.loc[i - 1, "nav_adjusted"]
        nav_df.loc[i, "nav_adjusted"] = nav_adjusted_new
        nav_df = nav_df[["date", "nav_unit", "nav_accumulated", "nav_adjusted"]]
    return nav_df


# 净值数据标准化
def get_standardized_data(nav_df):
    # 规范净值数据列名
    if "净值日期" in nav_df.columns:
        nav_df = nav_df.rename(columns={"净值日期": "日期"})
    assert "日期" in nav_df.columns, "Error: 未找到日期列"
    if "累计单位净值" in nav_df.columns:
        nav_df = nav_df.rename(columns={"累计单位净值": "累计净值"})
    assert "累计净值" in nav_df.columns, "Error: 未找到累计净值列"
    if "复权单位净值" in nav_df.columns:
        nav_df = nav_df.rename(columns={"复权单位净值": "复权净值"})
    # 检查是否有日期/累计净值为空的数据
    assert nav_df["日期"].isnull().sum() == 0, "Error: 净值数据中存在日期为空的数据"
    assert (
        nav_df["累计净值"].isnull().sum() == 0
    ), "Error: 净值数据中存在累计净值为空的数据"
    # 检查是否有日期重复的数据
    assert (
        nav_df["日期"].duplicated(keep=False).sum() == 0
    ), "Error: 净值数据中存在日期重复的数据"
    # 标准化日期格式
    if nav_df["日期"].dtype == "int":
        nav_df["日期"] = pd.to_datetime(nav_df["日期"], format="%Y%m%d")
    else:
        nav_df["日期"] = pd.to_datetime(nav_df["日期"])
    # 排序
    nav_df = nav_df.sort_values(by="日期", ascending=True).reset_index(drop=True)
    
    nav_df.rename(
        columns={"日期": "date", "单位净值": "nav_unit", "累计净值": "nav_accumulated"},
        inplace=True,
    )
    if "复权净值" in nav_df.columns:
        nav_df.rename(columns={"复权净值": "nav_adjusted"}, inplace=True)
    else:
        nav_df = get_nav_adjusted(nav_df)
    nav_df = nav_df[["date", "nav_unit", "nav_accumulated","nav_adjusted"]]
    # 保留小数点后4位
    nav_df = nav_df.round(4)
    return nav_df


def get_date_range(nav_df):
    start_day = nav_df["date"].min().strftime("%Y-%m-%d")
    end_day = nav_df["date"].max().strftime("%Y-%m-%d")
    return start_day, end_day


def infer_frequency(fund_name, nav_df):
    date = nav_df["date"].values
    # 如果大部分日期间隔为 1 天，那么数据可能是日度的
    if (np.diff(date) == np.timedelta64(1, "D")).mean() > 0.75:
        return "D"
    elif (np.diff(date) >= np.timedelta64(5, "D")).mean() > 0.75:
        return "W"
    else:
        print(f"{fund_name}无法推断频率,自动转为周度")
        return "W"


def generate_trading_date(
    begin_date: np.datetime64 = np.datetime64("2015-01-01"),
    end_date: np.datetime64 = np.datetime64("today"),
) -> Tuple[np.ndarray[np.datetime64]]:
    assert begin_date >= np.datetime64(
        "2015-01-04"
    ), "系统预设起始日期仅支持2015年1月4日以后"
    with open(
        Path(__file__).resolve().parent.joinpath("Chinese_special_holiday.txt"), "r"
    ) as f:
        chinese_special_holiday = pd.Series(
            [date.strip() for date in f.readlines()]
        ).values.astype("datetime64[D]")
    working_date = pd.date_range(begin_date, end_date, freq="B").values.astype(
        "datetime64[D]"
    )
    trading_date = np.setdiff1d(working_date, chinese_special_holiday)
    trading_date_df = pd.DataFrame(working_date, columns=["working_date"])
    trading_date_df["is_friday"] = trading_date_df["working_date"].apply(
        lambda x: x.weekday() == 4
    )
    trading_date_df["trading_date"] = (
        trading_date_df["working_date"]
        .apply(lambda x: x if x in trading_date else np.nan)
        .ffill()
    )
    return (
        trading_date,
        np.unique(
            trading_date_df[trading_date_df["is_friday"]]["trading_date"].values[1:]
        ).astype("datetime64[D]"),
    )


def match_data(
    nav_data: pd.DataFrame,
    trade_date: np.ndarray[np.datetime64],
) -> pd.DataFrame:
    """
    如果trade_date 的日期不在nav_data中, 则用前一个交易日的数据填充
    特殊的, 如果trade_date的开始日期早于nav_data的开始日期, 则需要对trade_date进行截取
    """
    first_row = nav_data.iloc[[0]].copy()
    trade_date = trade_date[trade_date >= nav_data["date"].min()]
    nav_data = nav_data.set_index("date")
    nav_data = nav_data.reindex(trade_date, method="ffill")
    nav_data = nav_data.reset_index(drop=False)
    combined = pd.concat([nav_data, first_row], ignore_index=True)
    combined = combined.sort_values(by="date")
    combined_unique = combined.drop_duplicates()
    combined_unique = combined_unique.reset_index(drop=True)
    return combined_unique


# benchmark data
def get_benchmark_data(code, start_day, end_day):
    error_code, benchmark_df = w.wsd(
        code,
        "close",
        start_day,
        end_day,
        "Fill=Previous",
        usedf=True,
    )
    benchmark_df.reset_index(inplace=True)
    benchmark_df.columns = ["date", code]
    benchmark_df["date"] = pd.to_datetime(benchmark_df["date"])
    benchmark_df[code] = benchmark_df[code] / benchmark_df[code].iloc[0]
    return benchmark_df

def calc_nav_rtn(nav: np.ndarray, types: Literal["log", "simple"] = "log"):
    if types == "simple":
        rtn = nav[1:] / nav[:-1] - 1
    elif types == "log":
        rtn = np.log(nav[1:] / nav[:-1])
    else:
        raise ValueError("types参数错误")
    return np.insert(rtn, 0, np.nan)

def win_ratio_stastics(nav: np.ndarray, date: np.ndarray[np.datetime64]):
    """
    目前只支持月度胜率统计
    """
    assert len(nav) == len(date), "nav和date长度不一致"
    
    nav_data = pd.DataFrame({"日期": date, "累计净值": nav})
    # 找到日期序列中每个月的最后一天
    nav_data["year_month"] = nav_data["日期"].dt.to_period("M")
    monthly_rtn = nav_data.drop_duplicates(
        subset="year_month", keep="last"
    ).reset_index(drop=True)

    monthly_rtn["rtn"] = calc_nav_rtn(monthly_rtn["累计净值"].values, types="simple")
    monthly_rtn = monthly_rtn.copy()
    monthly_rtn.iloc[0, monthly_rtn.columns.get_loc("rtn")] = (
        monthly_rtn.iloc[0]["累计净值"] - 1
    )
    monthly_rtn["year"] = monthly_rtn["日期"].dt.year
    monthly_rtn["month"] = monthly_rtn["日期"].dt.month
    monthly_rtn = monthly_rtn.pivot_table(
        index="year", columns="month", values="rtn", aggfunc="sum"
    )

    monthly_rtn.columns = [f"{x}月" for x in monthly_rtn.columns]
    monthly_rtn.index.name = None
    # monthly_rtn["年度总收益"] = monthly_rtn.apply(lambda x: np.prod(x + 1) - 1, axis=1)
    monthly_rtn["月度胜率"] = monthly_rtn.apply(
        lambda x: (x >= 0).sum() / (~np.isnan(x)).sum(), axis=1
    )
    # 保留四位小数
    monthly_rtn = monthly_rtn.map(lambda x: round(x, 4))
    for col in monthly_rtn.columns:
        monthly_rtn[col] = monthly_rtn[col].map(lambda x: f"{x:.2%}")

    # 将NAN变成NULL
    if (monthly_rtn.iloc[0, :] == "nan%").sum() + 3 == monthly_rtn.shape[1] and monthly_rtn.iloc[0, monthly_rtn.shape[1] - 3] == "0.000%":
        monthly_rtn = monthly_rtn.iloc[1:]
    return monthly_rtn.replace("nan%", "")

def get_nav_lines(df, fund_name, benchmark_name):

    x_data = df["date"].dt.strftime("%Y-%m-%d").tolist()
    ys_data = (
        (df.drop(columns=["date", "nav_unit", "nav_accumulated"], axis=1) - 1) * 100
    ).round(2)
    min_data = (ys_data.values.min() - 0.1 * abs(ys_data.values.min())).round()
    max_data = (ys_data.values.max() + 0.1 * abs(ys_data.values.max())).round()
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

    min_data = (ys_data.values.min() - 0.1 * abs(ys_data.values.min())).round(0)
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


def format_index(df: pd.DataFrame):
    x = df.index.values
    if x.dtype == "datetime64[ns]":
        x = np.datetime_as_string(x, unit="D")
    df.index = x
    return df


def get_line(df, title):
    df = format_index(df)
    x = df.index
    y = df.reset_index(drop=True).round(2)
    y_min = y.min().min()
    y_max = y.max().max()
    line = Line()
    line.add_xaxis(list(x))
    for i in df.columns:
        line.add_yaxis(i, list(y[i]), is_symbol_show=False)
    yaxis_opts = opts.AxisOpts(
        min_=y_min,
        max_=y_max,
        # type_="value",
        # name_="Y轴名称",
        # axislabel_opts=opts.LabelOpts(formatter="{value} 单位"),
    )
    line.set_global_opts(
        title_opts=opts.TitleOpts(title=title, pos_left="center", pos_top="0"),  # 标题
        legend_opts=opts.LegendOpts(pos_left="center", pos_bottom="0%"),  # 图例
        tooltip_opts=opts.TooltipOpts(trigger="axis"),  # 提示框
        yaxis_opts=yaxis_opts,
        # toolbox_opts=opts.ToolboxOpts(is_show=True, pos_left = '65%', pos_top='5%'), # 工具箱
        # datazoom_opts=[opts.DataZoomOpts(range_start=0, range_end=100, orient="horizontal")] # 区域缩放条
    )
    line.set_series_opts(linestyle_opts=opts.LineStyleOpts(width=2))
    return line


# 暂时弃用
# max_drawdown
def get_max_drawdown(df_nav, column_name):
    df_nav[f"{column_name}_max_so_far"] = df_nav[column_name].cummax()
    df_nav[f"{column_name}_drawdown"] = (
        df_nav[column_name] - df_nav[f"{column_name}_max_so_far"]
    ) / df_nav[f"{column_name}_max_so_far"]
    max_drawdown = df_nav[f"{column_name}_drawdown"].min()
    return max_drawdown


def calculate_annual_metrics(df, fund_name, benchmark_code, benchmark_name):
    nav_year_end = df.sort_values("date").groupby(df["date"].dt.to_period("Y")).tail(1)
    year_return = pd.DataFrame(
        columns=[
            "分年度业绩",
            f"{fund_name}_收益",
            f"{fund_name}_最大回撤",
            f"{benchmark_name}_收益",
            f"{benchmark_name}_最大回撤",
            "超额收益",
        ]
    )
    years = df["date"].dt.year.unique()
    for year in years:
        year_df = df[df["date"].dt.year == year]
        fund_start_value = (
            nav_year_end[nav_year_end["date"].dt.year == (year - 1)][
                "nav_adjusted"
            ].iloc[0]
            if year > years.min()
            else year_df["nav_adjusted"].iloc[0]
        )
        fund_end_value = year_df["nav_adjusted"].iloc[-1]
        fund_return = fund_end_value / fund_start_value - 1
        fund_max_drawdown = get_max_drawdown(year_df, "nav_adjusted")

        benchmark_start_value = (
            nav_year_end[nav_year_end["date"].dt.year == (year - 1)][
                benchmark_code
            ].iloc[0]
            if year > years.min()
            else year_df[benchmark_code].iloc[0]
        )
        benchmark_end_value = year_df[benchmark_code].iloc[-1]
        benchmark_return = benchmark_end_value / benchmark_start_value - 1
        benchmark_max_drawdown = get_max_drawdown(year_df, benchmark_code)

        excess_return = fund_return - benchmark_return
        new_row = pd.DataFrame(
            [
                [
                    year,
                    fund_return,
                    fund_max_drawdown,
                    benchmark_return,
                    benchmark_max_drawdown,
                    excess_return,
                ]
            ],
            columns=year_return.columns,
        )
        year_return = pd.concat([year_return, new_row], ignore_index=True)
    return year_return

# import os
# data = pd.read_excel(r"C:\Users\17820\Desktop\Private_nav_research\nav_data\私募产品净值数据.xlsx")
# code = list(data["产品代码"].unique())
# folder_name = 'data'
# if not os.path.exists(folder_name):
#     os.makedirs(folder_name)
# for i in code:
#     data_i = data[data["产品代码"]==i]
#     file_name = os.path.join(folder_name, f'{i}.csv')
#     data_i.to_csv(file_name, index=False)
# basic_info = pd.read_excel(r"C:\Users\17820\Desktop\Private_nav_research\nav_data\产品目录.xlsx")
# basic_info['产品代码'] = basic_info['产品代码'].astype(str)
