from nav_research import NavResearch

data_path = "简雍斯量先锋私募证券投资基金_净值序列_20250218.xlsx"
strategy = "量化CTA"
fund_name = "简雍斯量先锋"
benchmark_code = "NH0100.NHF"
benchmark_name = "南华商品指数"
threshold = -0.05

demo = NavResearch(data_path,strategy,fund_name,benchmark_code,benchmark_name,threshold)
demo.get_data()
demo.get_analysis_table()
demo.get_html()

print(f"{fund_name}-网页已生成")