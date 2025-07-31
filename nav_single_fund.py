from nav_research import NavResearch

data_path = r"C:\Users\yueku\Desktop\VScode\Private_nav_research\data\SAPG52_简雍斯量先锋_2025-07-25.csv"
strategy = "量化CTA"
fund_name = "简雍斯量先锋"
benchmark_code = "885007.WI"
benchmark_name = "万得混合债券型二级指数"
threshold = -0.05

demo = NavResearch(data_path,strategy,fund_name,benchmark_code,benchmark_name,threshold)
demo.get_data()
nav_df,_,_= demo.get_data1()
nav_df.to_csv(f"{fund_name}-净值序列.csv",encoding="utf-8-sig",index=False)
demo.get_analysis_table()
demo.get_html()

print(f"{fund_name}-网页已生成")



'''
885007.WI 万得混合债券型二级指数
399852.SZ 中证1000
932000.CSI 中证2000
'''