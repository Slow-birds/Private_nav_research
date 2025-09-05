import pandas as pd
import os
import base64
import json
from pathlib import Path
from openai import OpenAI

system_promtp = """
你是一位专注于图片内容提取的专业人士, 你需要帮助人类把图片内容提取出来保存为字典格式数据。
你只能输出以下DataFrame格式, 禁止输出其他内容, 禁止输出字典以外的文字信息: 
选项1: 
{  
    "序号": list,  
    "证券代码": list,  
    "证券名称": list,
    "总持仓" :list,
    "可变持仓":list,
    "参考市值":list,
    "现价":list,
    "涨幅":list,
    "当日盈亏":list,
}  
"""
user = """
将图片整理为dataframe格式数据。
"""

def kimi_model(image_path, system_promtp, user):
    with open(image_path, "rb") as f:
        image_data = f.read()
    image_url = f"data:image/{os.path.splitext(image_path)[1]};base64,{base64.b64encode(image_data).decode('utf-8')}"
    client = OpenAI(
        api_key="sk-8rz6aB58IUEYFyN8kLwyNk1FD0zl9HCjMTzJOxxWJ2RY9h0q",
        base_url="https://api.moonshot.cn/v1",
    )
    completion = client.chat.completions.create(
        model="moonshot-v1-8k-vision-preview",
        messages=[
            {"role": "system", "content": system_promtp},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                        },
                    },
                    {
                        "type": "text",
                        "text": user,
                    },
                ],
            },
        ],
    )
    response = completion.choices[0].message.content
    return response


if __name__ == "__main__":
    data_all = pd.DataFrame()
    files_list_series = pd.Series(
            [
                i
                for i in Path("./股票持仓").rglob("*")
                if i.suffix.lower() in {".png"}
            ]
        )
    for image_path in files_list_series:
        response = kimi_model(image_path, system_promtp, user)
        res = json.loads(response)
        data = pd.DataFrame(res)
        data["日期"] = image_path.name.split('.')[0]
        data_all = pd.concat([data_all, data], axis=0)
        print(f"{image_path.name} 处理完成")
    data_all.to_csv("./股票持仓/data.csv", index=False)