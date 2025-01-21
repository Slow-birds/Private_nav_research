from nav_research import NavResearch

data_path = "谊恒滴海一号净值20241231.xlsx"
strategy = "ETF套利"
fund_name = "谊恒滴海一号"
benchmark_code = "H11009.CSI"
benchmark_name = "中证综合债"
threshold = -0.05

demo = NavResearch(data_path,strategy,fund_name,benchmark_code,benchmark_name,threshold)
demo.get_data()
demo.get_analysis_table()
demo.get_html()

print(f"{fund_name}-网页已生成")