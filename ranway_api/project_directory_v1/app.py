import os
import base64
import random
from flask import Flask, request, render_template, jsonify, send_file, url_for
from zhipuai import ZhipuAI
import requests
import time

# 获取当前脚本的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 初始化 Flask 应用程序，并显式指定模板文件夹路径
app = Flask(__name__, template_folder=os.path.join(current_dir, "templates"))

# 初始化智谱清言客户端
client = ZhipuAI(api_key="406b4e5efb7a4223bbe605cf6b7618f0.XpCZcl7J7tvz77Ml")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/send_message", methods=["POST"])
def send_message():
    try:
        data = request.json
        user_message = data.get("message")
        image_data = data.get("image")
        
        if not image_data or not user_message:
            return jsonify({"error": "缺少必要的参数"}), 400

        # 保存图片
        image_path = os.path.join(current_dir, "temp_image.jpg")
        image_base64 = image_data.split(',')[1]
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(image_base64))

        # 生成data URI格式的图片URL
        image_url = f"data:image/jpeg;base64,{image_base64}"

        # 调用视频生成API
        response = client.videos.generations(
            model="cogvideox-2",
            image_url=image_url,
            prompt=user_message,
            quality="quality",
            with_audio=True,
            size="1920x1080",
            fps=30
        )

        return jsonify({"task_id": response.id})

    except Exception as e:
        print(f"Error in send_message: {str(e)}")  # 打印错误信息到控制台
        return jsonify({"error": str(e)}), 500

@app.route("/check_status/<task_id>", methods=["GET"])
def check_status(task_id):
    try:
        result = client.videos.retrieve_videos_result(id=task_id)
        
        if result.task_status == "SUCCESS":
            video_url = result.video_result[0].url
            
            # 确保static目录存在
            static_dir = os.path.join(current_dir, "static")
            os.makedirs(static_dir, exist_ok=True)
            
            # 下载视频
            save_path = os.path.join(static_dir, "generated_video.mp4")
            response = requests.get(video_url)
            
            if response.status_code == 200:
                with open(save_path, "wb") as f:
                    f.write(response.content)
                
                # 随机选择一个回复
                responses = [
                    "游客您的创意太棒了！",
                    "真是有趣的动图。",
                    "看起来不错呢！"
                ]
                bot_response = random.choice(responses)
                
                return jsonify({
                    "status": "SUCCESS",
                    "video_url": url_for("static", filename="generated_video.mp4"),
                    "message": bot_response
                })
            else:
                return jsonify({"status": "FAILED", "message": "视频下载失败"})
                
        elif result.task_status == "FAILED":
            return jsonify({"status": "FAILED", "message": "视频生成失败"})
        else:
            return jsonify({"status": "PROCESSING", "message": "正在生成中，请稍候..."})
            
    except Exception as e:
        print(f"Error in check_status: {str(e)}")  # 打印错误信息到控制台
        return jsonify({"status": "ERROR", "message": str(e)})

if __name__ == "__main__":
    app.run(debug=True)