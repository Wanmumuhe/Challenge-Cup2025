import time
import os
import requests
from zhipuai import ZhipuAI

# 初始化客户端，请填写您自己的APIKey
client = ZhipuAI(api_key="406b4e5efb7a4223bbe605cf6b7618f0.XpCZcl7J7tvz77Ml")

# 定义图片的URL地址（需要是可访问的HTTPS URL或Base64编码）
image_url = "https://tse3-mm.cn.bing.net/th/id/OIP-C.WOPVh3E2xswNnm5qIGLvWgHaFj?rs=1&pid=ImgDetMain "  # 替换为有效的图片URL或Base64编码[^23^]

# 调用视频生成接口
response = client.videos.generations(
    model="cogvideox-2",  # 使用的视频生成模型
    image_url=image_url,  # 提供的图片URL地址或者Base64编码
    prompt="让画面动起来，人物嘴微微笑",  # 提示文本
    quality="quality",  # 输出模式，"quality"为质量优先，"speed"为速度优先
    with_audio=True,
    size="1920x1080",  # 视频分辨率
    fps=30,  # 帧率
)

# 打印返回结果
print(response)

# 检查任务状态
task_id = response.id
print(f"Task ID: {task_id}")

# 轮询任务状态，直到任务完成
while True:
    result = client.videos.retrieve_videos_result(id=task_id)
    print("Current result from the status check API:")
    print(result)  # 打印当前轮询的结果，用于调试

    print(f"Task Status: {result.task_status}")

    if result.task_status == "SUCCESS":
        print("视频生成完成！")
         # 获取视频URL
        video_url = result.video_result[0].url
        break
    elif result.task_status == "FAILED":
        print("视频生成失败，请检查任务参数或重新尝试。")
        break

    print("视频尚未生成，10秒后重新检查...")
    time.sleep(10)

# 如果任务成功，下载并保存视频
if result.task_status == "SUCCESS":
    save_path = r"D:\Study\cup\ranway_api\try.py\generate_picture"
    os.makedirs(save_path, exist_ok=True)  # 确保保存路径存在

    video_file_path = os.path.join(save_path, "generated_video.mp4")
    response = requests.get(video_url)
    if response.status_code == 200:
        with open(video_file_path, "wb") as f:
            f.write(response.content)
        print(f"视频已保存到 {video_file_path}")
    else:
        print("视频下载失败，请检查网络或视频链接。")