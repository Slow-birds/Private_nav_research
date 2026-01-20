from NavResearch import NavResearch

data_path = r"C:\Users\yueku\Desktop\VScode\Private_nav_research\data\AHS76B_博普安兴私享一号B类_2026-01-05.csv"
strategy = "主观多头"
fund_name = "SP2"
benchmark_code = "399852.SZ"
benchmark_name = "中证1000"
threshold = -0.05

demo = NavResearch(data_path,strategy,fund_name,benchmark_code,benchmark_name,threshold)
demo.get_data()
tables = demo.get_analysis_table()
print(tables)
demo.get_html()

print(f"{fund_name}-网页已生成")



'''
885007.WI 万得混合债券型二级指数
399852.SZ 中证1000
932000.CSI 中证2000
'''