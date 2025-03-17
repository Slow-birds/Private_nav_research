from nav_research import NavResearch

data_path = r"temporary_data\SVW768_添禄量化股票策略1号私募证券投资基金净值数据_2022-06-30_2025-03-13.xlsx"
strategy = "市场中性"
fund_name = "添禄量化股票策略1号"
benchmark_code = "885007.WI"
benchmark_name = "万得混合债券型二级指数"
threshold = -0.05

demo = NavResearch(data_path,strategy,fund_name,benchmark_code,benchmark_name,threshold)
demo.get_data()
demo.get_analysis_table()
demo.get_html()

print(f"{fund_name}-网页已生成")