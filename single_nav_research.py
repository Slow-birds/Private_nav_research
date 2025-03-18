from nav_research import NavResearch

data_path = r"temporary_data\净值序列_通怡股票低波择时1号私募证券投资基金.xlsx"
strategy = "低波择时"
fund_name = "通怡股票低波择时1号"
benchmark_code = "885007.WI"
benchmark_name = "万得混合债券型二级指数"
threshold = -0.05

demo = NavResearch(data_path,strategy,fund_name,benchmark_code,benchmark_name,threshold)
demo.get_data()
demo.get_analysis_table()
demo.get_html()

print(f"{fund_name}-网页已生成")



'''
885007.WI 万得混合债券型二级指数
932000.CSI 中证2000
'''