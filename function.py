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

# 读取数据
def load_data(df_path: str) -> pd.DataFrame:
    df_path = Path(df_path)
    file_suffix = df_path.suffix
    if file_suffix in [".csv"]:
        df = pd.read_csv(df_path, encoding="utf-8")
    elif file_suffix in [".xls", ".xlsx"]:
        df = pd.read_excel(df_path)
    elif file_suffix in [".txt"]:
        df = pd.read_csv(df_path, delimiter=" ")
    else:
        raise ValueError(f"不支持的文件格式：{file_suffix}")
    return df

# 求复权净值
def nav_adjusted(nav_df: pd.DataFrame) -> pd.DataFrame:
    nav_df["nav_adjusted"] = np.nan
    nav_df.loc[0, "nav_adjusted"] = 1
    for i in range(1, len(nav_df)):
        nav_df.loc[i, "nav_adjusted"] = (
            (nav_df.loc[i, "nav_accumulated"] - nav_df.loc[i - 1, "nav_accumulated"])
            / nav_df.loc[i - 1, "nav_unit"]
            + 1
        ) * nav_df.loc[i - 1, "nav_adjusted"]
    nav_df = nav_df[["date", "nav_unit", "nav_accumulated", "nav_adjusted"]]
    return nav_df

def column_normalization(nav_df: pd.DataFrame):
    # 规范净值数据列名（日期、单位净值、累计净值、复权净值）
    column_mapping = {
    "date": ["日期", "净值日期"],
    "nav_unit": ["单位净值"],
    "nav_accumulated": ["累计净值", "累计单位净值"],
    "nav_adjusted": ["复权净值", "复权单位净值"],
    }
    for standard_name, alt_names in column_mapping.items():
        for alt_name in alt_names:
            if alt_name in nav_df.columns:
                nav_df = nav_df.rename(columns={alt_name: standard_name})
                break
    return nav_df
# 净值数据标准化
def nav_normalization(nav_df: pd.DataFrame) -> pd.DataFrame:
    # 规范净值数据列名（日期、单位净值、累计净值、复权净值）
    column_mapping = {
    "date": ["日期", "净值日期"],
    "nav_unit": ["单位净值"],
    "nav_accumulated": ["累计净值", "累计单位净值"],
    "nav_adjusted": ["复权净值", "复权单位净值"],
    }
    for standard_name, alt_names in column_mapping.items():
        for alt_name in alt_names:
            if alt_name in nav_df.columns:
                nav_df = nav_df.rename(columns={alt_name: standard_name})
                break
    # 检查是否有日期列、以及日期列是否有存在为空或者重复的数据
    assert "date" in nav_df.columns, "Error: 未找到日期列"
    assert nav_df["date"].isnull().sum() == 0, "Error: 净值数据中存在日期为空的数据"
    assert (nav_df["date"].duplicated(keep=False).sum() == 0), "Error: 净值数据中存在日期重复的数据"
    # 标准化日期格式、排序
    if nav_df["date"].dtype == "int":
        nav_df["date"] = pd.to_datetime(nav_df["date"], format="%Y%m%d")
    else:
        nav_df["date"] = pd.to_datetime(nav_df["date"])
    nav_df = nav_df.sort_values(by="date", ascending=True).reset_index(drop=True)
    # 判断是否有复权净值列
    if ("nav_adjusted" in nav_df.columns and "nav_unit" not in nav_df.columns and "nav_accumulated" not in nav_df.columns):
        nav_df = nav_df[["date", "nav_adjusted"]].round(4)
    else:
        # 检查是否有日期/单位净值/累计净值为空和日期重复的数据
        assert "nav_unit" in nav_df.columns, "Error: 未找到单位净值列"
        assert "nav_accumulated" in nav_df.columns, "Error: 未找到累计净值列"
        assert (nav_df["nav_unit"].isnull().sum() == 0), "Error: 净值数据中存在单位净值为空的数据"
        assert (nav_df["nav_accumulated"].isnull().sum() == 0), "Error: 净值数据中存在累计净值为空的数据"
        # 归一化
        nav_df["nav_unit"] = nav_df["nav_unit"] / nav_df["nav_unit"].iloc[0]
        nav_df["nav_accumulated"] = nav_df["nav_accumulated"] / nav_df["nav_accumulated"].iloc[0]
        # 复权净值
        nav_df = nav_adjusted(nav_df)
        nav_df = nav_df[["date", "nav_unit", "nav_accumulated", "nav_adjusted"]].round(4)
    return nav_df

# 日期频率推断
def infer_frequency(nav_df: pd.DataFrame):
    date = nav_df["date"].values
    if (np.diff(date) == np.timedelta64(1, "D")).mean() > 0.75:
        return "D"
    elif (np.diff(date) >= np.timedelta64(5, "D")).mean() > 0.75:
        return "W"
    else:
        # print(f"{fund_name}无法推断频率,自动转为周度")
        return "W"

# 生成交易日
def generate_trading_date(
    begin_date: np.datetime64 = np.datetime64("2015-01-01"),
    end_date: np.datetime64 = np.datetime64("today"),
) -> Tuple[np.ndarray[np.datetime64]]:
    assert begin_date >= np.datetime64("2015-01-04"), "系统预设起始日期仅支持2015年1月4日以后"
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

# 数据匹配
def match_data(
    nav_data: pd.DataFrame,
    trade_date: np.ndarray[np.datetime64],
) -> pd.DataFrame:
    """
    匹配交易日期到最近的净值日期，并保留原始交易日期和匹配到的净值日期。
    """
    # 确保 nav_data 的日期是 datetime64[ns] 类型，并重命名列以区分
    nav_clean = nav_data.copy()
    nav_clean["nav_date"] = pd.to_datetime(nav_clean["date"])  # 净值日期列
    nav_clean = nav_clean.drop(columns="date")
    # 过滤并转换 trade_date 为 datetime64[ns]
    min_nav_date = nav_clean["nav_date"].min()
    trade_filtered = trade_date[trade_date >= min_nav_date].astype("datetime64[ns]")

    if len(trade_filtered) == 0:
        return pd.DataFrame(columns=["trade_date", "nav_date"] + nav_clean.columns.tolist()[1:])
    # 创建交易日期 DataFrame（明确保留原始交易日期）
    trade_df = pd.DataFrame({
        "trade_date": trade_filtered,  # 原始交易日期
        "original_order": np.arange(len(trade_filtered))
    })
    # 按日期排序
    nav_sorted = nav_clean.sort_values("nav_date")
    trade_sorted = trade_df.sort_values("trade_date")
    # 使用 merge_asof 匹配最近的净值日期
    merged = pd.merge_asof(
        trade_sorted,          # 用 trade_date 的日期作为基准
        nav_sorted,           # 匹配 nav_date 的日期
        left_on="trade_date",  # 左表用交易日期
        right_on="nav_date",   # 右表用净值日期
        direction="nearest"   # 向后匹配最近的净值
    )
    # 恢复原始顺序并清理辅助列
    result = merged.sort_values("original_order").drop(columns=["original_order","trade_date"])
    result= result[["nav_date", "nav_adjusted"]]
    result.rename(columns={"nav_date": "date"}, inplace=True)
    result.reset_index(drop=True)
    return result

# 日期标准化
def date_normalization(nav_df, freq):
    start_day = nav_df["date"].min().strftime("%Y-%m-%d")
    end_day = nav_df["date"].max().strftime("%Y-%m-%d")
    trade_date, weekly_trade_date = generate_trading_date(
    begin_date=pd.to_datetime(start_day) - pd.Timedelta(days=10),
    end_date=pd.to_datetime(end_day) + pd.Timedelta(days=5),
    )
    if freq == "D":
        nav_df = match_data(nav_df, trade_date)
    else:  # freq is "W"
        nav_df = match_data(nav_df, weekly_trade_date)
    return nav_df

# 基准数据
def benchmark_data(code, start_day, end_day):
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

# 中间变量
def intermediate_df(nav_df, benchmark_code):
    # 获取基准数据、合并数据
    start_day = nav_df["date"].min().strftime("%Y-%m-%d")
    end_day = nav_df["date"].max().strftime("%Y-%m-%d")
    benchmark_df = benchmark_data(benchmark_code, start_day, end_day)
    df = pd.merge(nav_df, benchmark_df, on="date", how="left")
    # 辅助数据
    ## df_nav
    df["excess_nav"] = df["nav_adjusted"] - df[benchmark_code] + 1
    df_nav = df[["date","nav_adjusted",benchmark_code,"excess_nav"]].round(4)
    df_nav.drop_duplicates(subset=["date"], inplace=True)
    ## df_return
    df["nav_return"] = df["nav_adjusted"].pct_change()
    df["benchmark_return"] = df[benchmark_code].pct_change()
    df[["nav_return", "benchmark_return"]] = df[["nav_return", "benchmark_return"]].fillna(0)
    df["excess_return"] = df["nav_return"] - df["benchmark_return"]
    df_return = df[["date", "nav_return", "benchmark_return", "excess_return"]].round(4)
    ## df_drawdown
    df_nav_copy = df_nav.copy()
    df_nav_copy["fun_max_so_far"] = df_nav_copy["nav_adjusted"].cummax()
    df_nav_copy["fund_drawdown"] = (df_nav_copy["nav_adjusted"] - df_nav_copy["fun_max_so_far"]) / df_nav_copy["fun_max_so_far"]
    df_nav_copy["benchmark_max_so_far"] = df_nav_copy[benchmark_code].cummax()
    df_nav_copy["benchmark_drawdown"] = (df_nav_copy[benchmark_code] - df_nav_copy["benchmark_max_so_far"]) / df_nav_copy["benchmark_max_so_far"]
    df_nav_copy["excess_max_so_far"] = df_nav_copy["excess_nav"].cummax()
    df_nav_copy["excess_drawdown"] = (df_nav_copy["excess_nav"] - df_nav_copy["excess_max_so_far"]) / df_nav_copy["excess_max_so_far"]
    df_drawdown = df_nav_copy[["date", "fund_drawdown", "benchmark_drawdown", "excess_drawdown"]].round(4)
    return df_nav, df_return, df_drawdown

# 整体业绩指标
def calculate_overall_performance(df_nav, df_drawdown, df_return, freq):
    df_nav = df_nav.copy()
    df_drawdown = df_drawdown.copy()
    df_return = df_return.copy()
    days_diff = (df_nav["date"].max() - df_nav["date"].min()).days
    ## total_return
    total_return = df_nav["nav_adjusted"].iloc[-1] /df_nav["nav_adjusted"].iloc[0]- 1
    excess_total_return = df_nav["excess_nav"].iloc[-1] / df_nav["excess_nav"].iloc[0] - 1
    ## annual_return
    annual_return = pow(1 + total_return, 365 / days_diff) - 1
    excess_annual_return = pow(1 + excess_total_return, 365 / days_diff) - 1
    ## max_drawdown
    max_drawdown = df_drawdown["fund_drawdown"].min()
    excess_max_drawdown = df_drawdown["excess_drawdown"].min()
    ## annual_volatility
    annual_volatility = df_return["nav_return"].std() * np.sqrt(250 if freq == "D" else 52)
    excess_annual_volatility = df_return["excess_return"].std() * np.sqrt(250 if freq == "D" else 52)
    ## sharpe_ratio
    sharpe_ratio = (annual_return - 0.02) / annual_volatility
    excess_sharpe_ratio = (excess_annual_return - 0.02) / excess_annual_volatility
    list = [["产品收益",total_return,annual_return,max_drawdown,annual_volatility,sharpe_ratio],["超额收益",excess_total_return,excess_annual_return,excess_max_drawdown,excess_annual_volatility,excess_sharpe_ratio]]
    overall_performance = pd.DataFrame(list,columns=['整体收益','总收益','年化收益','最大回撤','年化波动率','夏普比'])
    # 格式化
    for col in overall_performance.columns:
        overall_performance['夏普比'] = overall_performance['夏普比'].round(2)
        if col != '夏普比' and col != '整体收益': 
            overall_performance[col] = overall_performance[col].map(lambda x: f"{x:.2%}")
    return overall_performance

# max_drawdown
def get_max_drawdown(df_nav, column_name):
    df_nav[f"{column_name}_max_so_far"] = df_nav[column_name].cummax()
    df_nav[f"{column_name}_drawdown"] = (
        df_nav[column_name] - df_nav[f"{column_name}_max_so_far"]
    ) / df_nav[f"{column_name}_max_so_far"]
    max_drawdown = df_nav[f"{column_name}_drawdown"].min()
    return max_drawdown

# 年度业绩指标
def calculate_annual_performance(df_nav: pd.DataFrame, benchmark_code: str) -> pd.DataFrame:
    # 确保日期是datetime类型并按日期排序（避免inplace修改）
    df_nav = df_nav.sort_values('date').copy()  # 只在需要时复制一次
    # 获取每年最后一天的记录
    year_end_nav = df_nav.groupby(df_nav['date'].dt.year).last()
    # 初始化结果DataFrame
    results = []
    years = sorted(df_nav['date'].dt.year.unique())
    for i, year in enumerate(years):
        year_data = df_nav[df_nav['date'].dt.year == year]
        # 计算年初价值
        if i == 0:
            fund_start = year_data['nav_adjusted'].iloc[0]
            bench_start = year_data[benchmark_code].iloc[0]
        else:
            fund_start = year_end_nav.loc[years[i-1]]['nav_adjusted']
            bench_start = year_end_nav.loc[years[i-1]][benchmark_code]
        # 计算年末价值和收益率
        fund_end = year_data['nav_adjusted'].iloc[-1]
        bench_end = year_data[benchmark_code].iloc[-1]
        fund_return = fund_end / fund_start - 1
        bench_return = bench_end / bench_start - 1
        excess_return = fund_return - bench_return
        # 计算最大回撤
        fund_mdd = get_max_drawdown(year_data, 'nav_adjusted')
        bench_mdd = get_max_drawdown(year_data, benchmark_code)
        results.append({
            '分年度业绩': year,
            '基金收益': fund_return,
            '基金最大回撤': fund_mdd,
            '基准收益': bench_return,
            '基准最大回撤': bench_mdd,
            '超额收益': excess_return
        })
    # 创建结果DataFrame并格式化
    yearly_rtn = pd.DataFrame(results)
    yearly_rtn.set_index('分年度业绩', inplace=True)
    yearly_rtn.index.name = "分年度业绩"
    # 更高效的小数处理方式（避免重复round）
    yearly_rtn = yearly_rtn.applymap(lambda x: f"{round(x, 4):.2%}")
    yearly_rtn.reset_index(inplace=True)
    return yearly_rtn

# 月度业绩指标
def calculate_monthly_performance(df_nav):
    df_nav = df_nav.copy()
    """
    目前只支持月度胜率统计
    """
    # 找到日期序列中每个月的最后一天,并求月度收益
    monthly_rtn = df_nav.sort_values("date").groupby(df_nav["date"].dt.to_period("M")).tail(1).reset_index(drop=True)
    monthly_rtn["rtn"] = monthly_rtn["nav_adjusted"] / monthly_rtn["nav_adjusted"].shift(1)-1
    monthly_rtn.iloc[0, monthly_rtn.columns.get_loc("rtn")] = (monthly_rtn.iloc[0]["nav_adjusted"] - 1)
    # 生成月度收益表
    monthly_rtn["year"] = monthly_rtn["date"].dt.year
    monthly_rtn["month"] = monthly_rtn["date"].dt.month
    monthly_rtn = monthly_rtn.pivot_table(index="year", columns="month", values="rtn", aggfunc="sum")
    monthly_rtn.columns = [f"{x}月" for x in monthly_rtn.columns]
    monthly_rtn.index.name = None
    # 计算年度总收益和月度胜率
    monthly_rtn["年度总收益"] = monthly_rtn.apply(lambda x: np.prod(x + 1) - 1, axis=1)
    monthly_rtn["月度胜率"] = monthly_rtn.apply(lambda x: (x >= 0).sum() / (~np.isnan(x)).sum(), axis=1)
    # 保留四位小数
    monthly_rtn = monthly_rtn.map(lambda x: round(x, 4))
    for col in monthly_rtn.columns:
        monthly_rtn[col] = monthly_rtn[col].map(lambda x: f"{x:.2%}")
    # 将NAN变成NULL
    if (monthly_rtn.iloc[0, :] == "nan%").sum() + 3 == monthly_rtn.shape[1] and monthly_rtn.iloc[0, monthly_rtn.shape[1] - 3] == "0.000%":
        monthly_rtn = monthly_rtn.iloc[1:]
    monthly_rtn.reset_index(inplace=True)
    monthly_rtn = monthly_rtn.rename(columns={monthly_rtn.columns[0]: '分月度业绩'})
    return monthly_rtn.replace("nan%", "")

# 回撤情况
def calculate_drawdown(df_nav, df_drawdown, threshold):
    df_nav = df_nav.copy()
    df_drawdown = df_drawdown.copy()
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
            np.argmin(df_drawdown["fund_drawdown"][start_idx:end_idx])
            + start_idx
        ]
        # 注意：这里我们假设没有回补，所以reset_end_date就是数据的最后一天
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
    drawdown_table = filtered_data
    return drawdown_table

def get_nav_lines(df, fund_name, benchmark_name):
    x_data = df["date"].dt.strftime("%Y-%m-%d").tolist()
    ys_data = (
        (df.drop(columns=["date"], axis=1) - 1) * 100
    ).round(2)
    min_data = round((ys_data.values.min() - 0.1 * abs(ys_data.values.min())))
    max_data = round((ys_data.values.max() + 0.1 * abs(ys_data.values.max())))
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

# 时间格式转换
def format_date(
    date: Union[datetime.datetime, datetime.date, np.datetime64, int, str]
) -> pd.Timestamp:
    """
    输出格式为pd.Timestamp, 等同于 np.datetime64
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