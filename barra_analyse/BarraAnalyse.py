import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import statsmodels.api as sm
from function import *
import warnings
warnings.filterwarnings('ignore')


class BarraAnalyse:
    def __init__(self, nav_data_path, factor_data_path):
        self.nav_data_path = nav_data_path
        self.factor_data_path = factor_data_path
    
    def get_data(self):
        # 获取净值数据，并求基金收益率（周度）
        nav_df = pd.read_excel(self.nav_data_path)
        nav_df.rename(columns={'日期': 'date'}, inplace=True)
        nav_df["date"] = pd.to_datetime(nav_df["date"])
        nav_df.sort_values(by=['date'], inplace=True)
        nav_df["nav_return"] = nav_df["复权净值"].pct_change()
        nav_return = nav_df[["date", "nav_return"]]
        
        # 读取并处理因子数据
        factor_return = pd.read_excel(self.factor_data_path)
        factor_return["date"] = pd.to_datetime(factor_return["date"])
        factor_return.set_index("date",inplace=True)
        ## 重采样为周度
        data = factor_return.add(1).resample('W').prod().sub(1)
        data.reset_index(inplace=True)
        data['week_number'] = data["date"].dt.isocalendar().week
        data['year'] = data["date"].dt.year
        ## 生成周度数据
        start_day = factor_return.index.min().strftime("%Y-%m-%d")
        end_day = factor_return.index.max().strftime("%Y-%m-%d")
        trade_date, weekly_trade_date = generate_trading_date(
            begin_date=pd.to_datetime(start_day) - pd.Timedelta(days=10),
            end_date=pd.to_datetime(end_day) + pd.Timedelta(days=10),
            )
        last_dates_df = pd.DataFrame({
            'week_number': pd.DatetimeIndex(weekly_trade_date).isocalendar().week,
            'year': pd.DatetimeIndex(weekly_trade_date).year
        }, index=weekly_trade_date)
        last_dates_df.reset_index(inplace=True, names=['date'])
        ## 重置日期列
        merged_df = pd.merge(data, last_dates_df, on=['year', 'week_number'], how='left')
        merged_df.drop(columns=["year","week_number","date_x"], inplace=True)
        merged_df.rename(columns={"date_y": "date"}, inplace=True)
        # 合并数据
        df = pd.merge(nav_return, merged_df, on='date', how='left')
        df.dropna(inplace=True)
        df.reset_index(drop=True, inplace=True)
        X = df.drop(columns=['date',"nav_return","country"])
        y = df['nav_return']
        self.df = df
        self.X = X
        self.y = y
        return df, X, y
   
    def get_style_exposure(self):
        model = sm.OLS(self.y, sm.add_constant(self.X)).fit()
        coefficients = model.params.reset_index()
        coefficients.rename(columns={"index":"factor", 0:"coefficient"}, inplace=True)
        coefficients_barra = coefficients[33:]
        coefficients_barra.sort_values(by='coefficient', ascending=False, inplace=True)
        coefficients_industry = coefficients[2:33]
        coefficients_industry.sort_values(by='coefficient', ascending=False, inplace=True)
        self.plot_coefficients(coefficients_barra, 'Barra Factors Regression Coefficients')
        self.plot_coefficients(coefficients_industry, 'Industry Factors Regression Coefficients')
        return coefficients_barra, coefficients_industry
    
    def get_barra(self):
        model = sm.OLS(self.y, sm.add_constant(self.X)).fit()
        industry_beta = model.params[2:33]
        barra_beta = model.params[33:]
        barra_return = []
        industry_return = []
        for i in self.X.index:
            barra_return.append((barra_beta * self.X.loc[i, barra_beta.index]).sum())
            industry_return.append((industry_beta * self.X.loc[i, industry_beta.index]).sum())
        data_return = self.df[["date","nav_return"]]
        data_return["barra_return"] = barra_return
        data_return["industry_return"] = industry_return
        data_return.loc[1, ["barra_return","industry_return"]] = 0
        data_return["nav_return_cumsum"] = (1 + data_return["nav_return"]).cumprod() - 1
        data_return["barra_return_cumsum"] = (1 + data_return["barra_return"]).cumprod() - 1
        data_return["industry_return_cumsum"] = (1 + data_return["industry_return"]).cumprod() - 1
        data_return["residual_return_cumsum"] = data_return["nav_return_cumsum"] - data_return["barra_return_cumsum"] - data_return["industry_return_cumsum"]
        data_return.set_index("date", inplace=True)
        # 画Wind商品指数20日滚动年化波动率图
        fig, (ax1) = plt.subplots(nrows=1, figsize=(12, 6))
        ax1.plot(data_return["nav_return_cumsum"], label="nav_return_cumsum")
        ax1.plot(data_return["barra_return_cumsum"], label='barra_return_cumsum')
        ax1.plot(data_return["industry_return_cumsum"], label='industry_return_cumsum')
        ax1.plot(data_return["residual_return_cumsum"], label='residual_return_cumsum')
        ax1.xaxis.set_major_locator(mdates.MonthLocator())
        ax1.tick_params(axis="x", rotation=45)
        ax1.tick_params(axis="y")
        ax1.set_title("Cumulative Returns Decomposition")
        ax1.legend(loc="upper left")
        plt.tight_layout()
        return data_return  

    def get_barra_rolling(self):
        # 假设数据已准备：y是因变量(基金收益)，X是自变量(包含因子和行业)
        window = 30
        factor_contributions = []
        industry_contributions = []
        # 创建结果DataFrame
        results = pd.DataFrame()
        for t in range(window, len(self.df)):
            # 滚动窗口数据
            y_rolling = self.y.iloc[t-window:t]
            X_rolling = self.X.iloc[t-window:t]
            # 拟合模型
            model = sm.OLS(y_rolling, sm.add_constant(X_rolling)).fit()
            # 获取当前期的因子暴露
            current_X = self.X.iloc[t-1]
            # 计算各类贡献
            barra_beta = model.params[32:]  # 假设33之后是barra因子
            barra_return = (barra_beta * current_X[barra_beta.index]).sum()
            beta_industry = model.params[1:32]  # 假设2-33是行业因子
            industry_return = (beta_industry * current_X[beta_industry.index]).sum()
            # 存储结果
            factor_contributions.append(barra_return)
            industry_contributions.append(industry_return)
        # 转换为Series
        results["barra_return"] = factor_contributions
        results["industry_return"] = industry_contributions
        results["nav_return"] = self.y[window:].reset_index(drop=True)
        results.loc[0, ["nav_return", "barra_return","industry_return"]] = 0
        # 累计收益计算
        results["nav_return_cumsum"] = (1 + results["nav_return"]).cumprod() - 1
        results["barra_return_cumsum"] = (1 + results["barra_return"]).cumprod() - 1
        results["industry_return_cumsum"] = (1 + results["industry_return"]).cumprod() - 1
        results["residual_return_cumsum"] = results["nav_return_cumsum"] - results["barra_return_cumsum"] - results["industry_return_cumsum"]
        results.index = self.df[30:]["date"]
        # 绘图
        plt.figure(figsize=(12, 6))
        plt.plot(results.index, results["nav_return_cumsum"], label="Fund Cumulative Return")
        plt.plot(results.index, results["barra_return_cumsum"], label="Barra Factors Cumulative Return")
        plt.plot(results.index, results["industry_return_cumsum"], label="Industry Factors Cumulative Return")
        plt.plot(results.index, results["residual_return_cumsum"], label="Residual Cumulative Return")
        plt.legend()
        plt.title("Cumulative Returns Decomposition")
        plt.tight_layout()
        plt.show()
        return results
    
if __name__ == "__main__":
    nav_data_path = r"千衍六和31号净值20250814.xlsx"
    factor_data_path = r"factor_return.xlsx"
    demo = BarraAnalyse(nav_data_path,factor_data_path)
    demo.get_data()
    demo.get_style_exposure()
    demo.get_barra()
    demo.get_barra_rolling()