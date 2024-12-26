import numpy as np
import pandas as pd
from pathlib import Path
import datetime
from typing import Union, Tuple
from pandas import Series, Timestamp
import copy
from pyecharts.charts import Line
import pyecharts.options as opts
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
    nav_df_copy = nav_df.copy()
    nav_df_copy["nav_adjusted"] = np.nan
    nav_df_copy.loc[0, "nav_adjusted"] = 1
    for i in range(1, len(nav_df_copy)):
        nav_adjusted_new = (
            nav_df_copy.loc[i, "nav_accumulated"] - nav_df_copy.loc[i - 1, "nav_accumulated"]
        ) / nav_df_copy.loc[i - 1, "nav_unit"] + 1
        nav_adjusted_new *= nav_df_copy.loc[i - 1, "nav_adjusted"]
        nav_df_copy.loc[i, "nav_adjusted"] = nav_adjusted_new
    return nav_df_copy

# 净值数据标准化
def get_standardized_data(nav_df):
    # 规范净值数据列名
    if "净值日期" in nav_df.columns:
        nav_df = nav_df.rename(columns={"净值日期": "日期"})
    assert "日期" in nav_df.columns, "Error: 未找到日期列"
    if "累计单位净值" in nav_df.columns:
        nav_df = nav_df.rename(columns={"累计单位净值": "累计净值"})
    assert "累计净值" in nav_df.columns, "Error: 未找到累计净值列"
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
    nav_df = nav_df[["日期", "单位净值", "累计净值"]]
    nav_df.rename(columns={"日期": "date","单位净值": "nav_unit","累计净值": "nav_accumulated"}, inplace=True)
    nav_df = get_nav_adjusted(nav_df)
    # 保留小数点后4位
    nav_df = nav_df.round(4)
    return nav_df

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
def get_benchmark_data(self):
    error_code, benchmark_df = w.wsd(
        self.benchmark_code,
        "close",
        self.start_day_t,
        self.end_day_t,
        "Fill=Previous",
        usedf=True,
    )
    benchmark_df.reset_index(inplace=True)
    benchmark_df.columns = ["date", self.benchmark_code]
    benchmark_df["date"] = pd.to_datetime(benchmark_df["date"])
    benchmark_df[self.benchmark_code] = benchmark_df[self.benchmark_code]/benchmark_df[self.benchmark_code].iloc[0]
    return benchmark_df

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
