from nav_research import NavResearch

data_path = "资产净值公告_SVZ009_铭跃行远均衡一号私募证券投资基金_2022-07-29_2024-12-30_mul.xlsx"
strategy = "量化CTA"
fund_name = "铭跃行远均衡一号"
benchmark_code = "NH0100.NHF"
benchmark_name = "南华商品指数"
threshold = -0.05

demo = NavResearch(data_path,strategy,fund_name,benchmark_code,benchmark_name,threshold)
demo.get_data()
demo.get_analysis_table()
demo.get_html()

print(f"{fund_name}-网页已生成")