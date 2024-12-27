from nav_research import NavResearch

data_path = r"data\旭诺CTA一号净值.xlsx"
strategy = "量化CTA"
fund_name = "旭诺CTA一号"
benchmark_code = "NH0100.NHF"
benchmark_name = "南华商品指数"
threshold = -0.05

demo = NavResearch(data_path,strategy,fund_name,benchmark_code,benchmark_name,threshold)
demo.get_data()
demo.get_analysis_table()
demo.get_html()

print(f"{fund_name}-网页已生成")