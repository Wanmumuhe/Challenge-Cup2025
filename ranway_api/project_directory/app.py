import os
import base64
from flask import Flask, request, render_template, redirect, url_for
from zhipuai import ZhipuAI
import requests
import time

# 获取当前脚本的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 初始化 Flask 应用程序，并显式指定模板文件夹路径
app = Flask(__name__, template_folder=os.path.join(current_dir, "templates"))

# 初始化智谱清言客户端
client = ZhipuAI(api_key="406b4e5efb7a4223bbe605cf6b7618f0.XpCZcl7J7tvz77Ml")

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        # 获取用户上传的图片
        image_file = request.files["image"]
        if image_file:
            # 保存上传的图片到临时文件
            image_path = os.path.join(current_dir, "temp_image.jpg")
            image_file.save(image_path)
            
            # 将图片转换为 Base64 编码
            with open(image_path, "rb") as f:
                image_data = f.read()

            # 使用 base64 编码
            image_base64 = base64.b64encode(image_data).decode('utf-8')

            # 构建 image_url
            image_url = f"data:image/jpeg;base64,{image_base64}"
            
            # 获取用户输入的提示词
            prompt = request.form["prompt"]
            
            # 调用视频生成接口
            response = client.videos.generations(
                model="cogvideox-2",
                image_url=image_url,
                prompt=prompt,
                quality="quality",
                with_audio=True,
                size="1920x1080",
                fps=30
            )
            
            # 检查任务状态
            task_id = response.id
            while True:
                result = client.videos.retrieve_videos_result(id=task_id)
                if result.task_status == "SUCCESS":
                    video_url = result.video_result[0].url
                    break
                elif result.task_status == "FAILED":
                    return "视频生成失败，请检查任务参数或重新尝试。"
                time.sleep(10)
            
            # 下载并保存视频
            save_path = os.path.join(current_dir, "static", "generated_video.mp4")
            response = requests.get(video_url)
            if response.status_code == 200:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                with open(save_path, "wb") as f:
                    f.write(response.content)
                return redirect(url_for("download"))
            else:
                return "视频下载失败，请检查网络或视频链接。"
    
    return render_template("index.html")

@app.route("/download")
def download():
    return render_template("download.html")

if __name__ == "__main__":
    app.run(debug=True)
