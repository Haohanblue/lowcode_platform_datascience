import asyncio
from zhipuai import ZhipuAI
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv(verbose=True)

# 获取单个环境变量的值
api_key = os.environ.get('ZHIPUAI_API_KEY')
client = ZhipuAI(api_key=api_key)  # 填写您自己的APIKey

# 异步获取ZhipuAI的响应
async def get_zhipu_response(message, model):
    response = client.chat.completions.create(
        model=model,  # 填写需要调用的模型名称
        messages=[{"role": "user", "content": message}],
        # 拓展参数
        extra_body={"temperature": 0.1},
    )
    return response.choices[0].message.content

# 主函数
async def main():
    message = "你好"
    model = "glm-4-air-0111"
    print(await get_zhipu_response(message, model))

if __name__ == '__main__':
    asyncio.run(main())
