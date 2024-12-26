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

basic_info = load_data("产品目录.xlsx")

# 删除html文件
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

# 生成新的html文件
files_list_series = pd.Series([i.stem for i in Path("./data").glob("*.xlsx")])
for row in basic_info.itertuples(index=False, name=None):
    nav_df_path = Path("data").joinpath(f"{files_list_series[files_list_series.str.contains(row[3])].item()}.xlsx")
    demo = NavResearch(nav_df_path,row[0],row[3],row[4],row[5],row[6])
    demo.get_data()
    demo.get_analysis_table()
    demo.get_html()

# 生成新的index.html文件
def generate_index_html(folder_path: Path):
    # 获取目录及其子目录中的所有 HTML 文件
    html_files = folder_path.rglob("*.html")
    print(html_files)

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
        color: blue;
    }
    h2 {
        font-size: 25px;
        color: blue;

    }
    a {
        text-decoration: none;
    }
</style>
</head>
<body>"""
        )
        # 创建一个集合来存储已经处理过的文件夹，避免重复创建链接
        processed_folders = set()
        # 为每个 HTML 文件创建一个链接
        for html_file in html_files:
            if html_file.name == "index.html":
                continue
            relative_path = html_file.relative_to(folder_path)
            # 如果文件夹还没有被处理过，为文件夹创建一个链接
            if html_file.parent not in processed_folders:
                f.write(f"<h2><a>{html_file.parent.name}</a></h2>\n")
                processed_folders.add(html_file.parent)

            # 创建HTML文件的链接
            cleaned_name = relative_path.name.replace("_nav_analysis", "")
            f.write(f'<a href="{relative_path}" target="_blank">{cleaned_name}</a><br/>\n')

        f.write("</body>\n</html>")

# 使用函数
generate_index_html(Path("docs"))

print("生成完成")
