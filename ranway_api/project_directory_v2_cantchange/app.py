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

        if image_data and user_message:
            # 保存图片
            image_path = os.path.join(current_dir, "temp_image.jpg")
            image_base64 = image_data.split(',')[1]
            with open(image_path, "wb") as f:
                f.write(base64.b64decode(image_base64))

            # 调用视频生成 API
            response = client.videos.generations(
                model="cogvideox-2",
                image_url=f"data:image/jpeg;base64,{image_base64}",
                prompt=user_message,
                quality="quality",
                with_audio=True,
                size="1920x1080",
                fps=30
            )

            return jsonify({"task_id": response.id})
        else:
            return jsonify({"error": "缺少必要的参数"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/check_status/<task_id>", methods=["GET"])
def check_status(task_id):
    try:
        result = client.videos.retrieve_videos_result(id=task_id)
        if result.task_status == "SUCCESS":
            video_url = result.video_result[0].url

            # 下载视频
            save_path = os.path.join(current_dir, "static", "generated_video.mp4")
            response = requests.get(video_url)
            if response.status_code == 200:
                os.makedirs(os.path.dirname(save_path), exist_ok=True)
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
        return jsonify({"status": "ERROR", "message": str(e)})

@app.route("/upload_image", methods=["POST"])
def upload_image():
    try:
        data = request.json
        image_data = data.get("image")
        if not image_data:
            return jsonify({"error": "未上传图片"}), 400

        # 保存图片
        image_path = os.path.join(current_dir, "temp_image.jpg")
        image_base64 = image_data.split(',')[1]
        with open(image_path, "wb") as f:
            f.write(base64.b64decode(image_base64))

        return jsonify({"message": "图片上传成功"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)