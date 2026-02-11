from NavResearch import NavResearch

data_path = r"E:\桌面文件\Vscode\Private_nav_research\data\SN3221_宏锡量化CTA7号_2025-12-31.csv"
strategy = "量化CTA"
fund_name = "宏锡量化CTA7号"
benchmark_code = "sz399852"
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