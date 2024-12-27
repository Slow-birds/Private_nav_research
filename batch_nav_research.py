import pandas as pd
import matplotlib.pyplot as plt
from WindPy import w
w.start()
from function import *
from nav_research import NavResearch
from pathlib import Path
import os
import warnings
warnings.filterwarnings("ignore")
warnings.simplefilter('ignore')

plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

print("项目开始------------------------")
basic_info = load_data("产品目录.xlsx")

print("删除html文件")
def delete_html_files(directory):
    # 遍历目录及其子目录
    for root, dirs, files in os.walk(directory):
        for file in files:
            # 检查文件是否以.html 结尾
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                try:
                    # 删除文件
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")

directory_to_clean = "docs"
delete_html_files(directory_to_clean)

print("生成新的html文件")
files_list_series = pd.Series([i.stem for i in Path("./data").glob("*.xlsx")])
for row in basic_info.itertuples(index=False, name=None):
    nav_df_path = Path("data").joinpath(f"{files_list_series[files_list_series.str.contains(row[3])].item()}.xlsx")
    demo = NavResearch(nav_df_path,row[0],row[3],row[4],row[5],row[6])
    demo.get_data()
    demo.get_analysis_table()
    demo.get_html()

print("生成index.html")
def generate_index_html(folder_path: Path):
    # 获取目录及其子目录中的所有 HTML 文件
    html_files = list(folder_path.rglob("*.html"))
    # 创建一个集合来存储所有唯一的文件夹路径（不包括 index.html 所在的文件夹）
    unique_folders = {html_file.parent for html_file in html_files if html_file.name != "index.html"}
    # 定义排序顺序
    sorted_folder_names = ["主观CTA", "量化CTA", "套利"]
    # 创建一个新的 index.html 文件
    with open(folder_path.joinpath("index.html"), "w", encoding="utf-8") as f:
        f.write(
            """<html>
<head>
<meta charset="UTF-8">
<title>Value over Time</title>
<style>
    body {
        font-family: Arial, sans-serif;
        font-size: 20px;
        color: black;
    }
    h2 {
        font-size: 25px;
        color: black;
    }
    a {
        text-decoration: none;
    }
</style>
</head>
<body>"""
        )
        # 按照指定的顺序写入 <h2> 标题
        for folder_name in sorted_folder_names:
            # 检查文件夹是否存在
            folder_path_obj = folder_path / folder_name
            if folder_path_obj in unique_folders:
                # 写入 <h2> 标题和文件夹链接（这里链接到文件夹本身，但可以根据需要调整）
                f.write(f"<h2><a>{folder_name}</a></h2>\n")
                # 列出该文件夹下的所有HTML文件
                f.write("<ul>\n")
                for html_file in html_files:
                    if html_file.parent == folder_path_obj:
                        cleaned_name = html_file.name.replace("_nav_analysis", "")
                        relative_path = html_file.relative_to(folder_path)
                        f.write(f'<li><a href="{relative_path}" target="_blank">{cleaned_name}</a></li>\n')
                f.write("</ul>\n")
        f.write("</body>\n</html>")

print("Cerate:index.html")

print("项目完成------------------------")