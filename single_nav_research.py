from nav_research import NavResearch

data_path = r"data\主观价值_睿郡财富11号1期.xlsx"
strategy = "主观多头"
fund_name = "睿郡财富11号1期"
benchmark_code = "000300.SH"
benchmark_name = "沪深300"
threshold = -0.1

demo = NavResearch(data_path,strategy,fund_name,benchmark_code,benchmark_name,threshold)
demo.get_data()
demo.get_analysis_table()
demo.get_html()

print(f"{fund_name}-网页已生成")