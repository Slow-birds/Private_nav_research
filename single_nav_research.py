from nav_research import NavResearch

data_path = r"temporary_data\SJV784_文谛量化多策略十号私募证券投资基金A净值数据_2021-08-04_2025-03-04.xlsx"
strategy = "量化CTA"
fund_name = "文谛量化多策略十号A"
benchmark_code = "NH0100.NHF"
benchmark_name = "南华商品指数"
threshold = -0.05

demo = NavResearch(data_path,strategy,fund_name,benchmark_code,benchmark_name,threshold)
demo.get_data()
demo.get_analysis_table()
demo.get_html()

print(f"{fund_name}-网页已生成")