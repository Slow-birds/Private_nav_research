from NavResearch import NavResearch

data_path = r"E:\桌面文件\Vscode\Private_nav_research\data\STW548_细水居20号_2025-09-12.csv"
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