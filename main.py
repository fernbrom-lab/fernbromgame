import os
import time
import hashlib
import hmac
import requests
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

app = FastAPI(title="蕨積宇宙影片產生器 API")

# 基本認證
security = HTTPBasic()

VALID_USERNAME = os.getenv("PAGE_USERNAME", "admin")
VALID_PASSWORD = os.getenv("PAGE_PASSWORD", "zepower2025")

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    is_username_correct = hmac.compare_digest(credentials.username, VALID_USERNAME)
    is_password_correct = hmac.compare_digest(credentials.password, VALID_PASSWORD)
    if not (is_username_correct and is_password_correct):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="帳號或密碼錯誤",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 請求格式
class RoleLine(BaseModel):
    id: str
    name: str
    line: str

class GenerateRequest(BaseModel):
    roles: List[RoleLine]
    scene: str
    outline: str
    duration: int

# 建立 prompt
def build_prompt(req: GenerateRequest) -> str:
    role_text = "\n".join([f"{r.name}：{r.line}" for r in req.roles])
    
    if req.duration <= 15:
        detail_level = "簡短精簡"
    elif req.duration <= 30:
        detail_level = "適中"
    else:
        detail_level = "詳細完整"
    
    prompt = f"""【影片風格】
2D動畫風格，可愛、輕鬆戲謔，角色為植物擬人，背景明亮乾淨。

【場景】
{req.scene}

【劇情大綱】
{req.outline}

【角色對話】
{role_text}

【影片長度】
{req.duration}秒，{detail_level}節奏。

請生成一段符合以上描述的短動畫影片。"""
    
    return prompt

# 生成影片 (使用 WaveSpeedAI Cosmos Predict 2.5)
def generate_video_with_cosmos(prompt: str, duration: int) -> str:
    """
    呼叫 WaveSpeedAI Cosmos Predict 2.5 模型生成影片
    使用异步任务模式：提交 → 轮询 → 返回影片URL
    """
    API_KEY = os.getenv("WAVESPEED_API_KEY")
    if not API_KEY:
        raise Exception("WAVESPEED_API_KEY 未設定")
    
    # 模型路径（文字生成影片）
    MODEL = "wavespeed-ai/cosmos-predict-2.5/text-to-video"
    API_BASE = "https://api.wavespeed.ai/api/v3"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    # 步骤 1: 提交任务
    submit_url = f"{API_BASE}/{MODEL}"
    payload = {"prompt": prompt}
    
    print(f"📡 提交任务到 WaveSpeedAI: {MODEL}")
    submit_response = requests.post(submit_url, headers=headers, json=payload)
    submit_response.raise_for_status()
    
    submit_result = submit_response.json()
    task_id = submit_result.get("data", {}).get("id")
    
    if not task_id:
        raise Exception(f"提交任务失败: {submit_result}")
    
    print(f"✅ 任务已提交，ID: {task_id}")
    
    # 步骤 2: 轮询结果
    result_url = f"{API_BASE}/predictions/{task_id}/result"
    
    max_attempts = 60  # 最多等 2 分钟
    for attempt in range(max_attempts):
        time.sleep(2)  # 每 2 秒检查一次
        
        result_response = requests.get(result_url, headers=headers)
        result_response.raise_for_status()
        
        result_data = result_response.json()
        status = result_data.get("data", {}).get("status")
        
        if status == "completed":
            outputs = result_data.get("data", {}).get("outputs", [])
            if outputs and len(outputs) > 0:
                video_url = outputs[0]
                print(f"✅ 影片生成成功: {video_url}")
                return video_url
            else:
                raise Exception("任务完成但没有输出影片")
        
        elif status == "failed":
            error_msg = result_data.get("data", {}).get("error", "未知错误")
            raise Exception(f"影片生成失败: {error_msg}")
        
        else:
            print(f"⏳ 处理中... ({status}) 尝试 {attempt + 1}/{max_attempts}")
    
    raise Exception("生成超时，请稍后重试")

# 测试端点
@app.get("/api/test-replicate")
async def test_api():
    """测试 WaveSpeedAI API 是否正常"""
    try:
        token = os.getenv("WAVESPEED_API_KEY")
        if not token:
            return {
                "success": False,
                "error": "WAVESPEED_API_KEY 未设定",
                "hint": "请在 Render 环境变量中添加 WAVESPEED_API_KEY"
            }
        
        return {
            "success": True,
            "message": "WAVESPEED_API_KEY 已设定",
            "api_key_preview": token[:8] + "..."
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

# 主要影片生成 API 端點
@app.post("/api/generate-video")
async def generate_video(
    req: GenerateRequest,
    username: str = Depends(verify_credentials)
):
    if not req.roles:
        raise HTTPException(status_code=400, detail="請至少選擇一個角色")
    
    if not req.outline.strip():
        raise HTTPException(status_code=400, detail="請填寫內容大綱")
    
    prompt = build_prompt(req)
    print(f"👤 使用者: {username}")
    print(f"📝 Prompt:\n{prompt}\n")
    print(f"⏱️ 影片長度: {req.duration} 秒")
    
    try:
        # 使用 WaveSpeedAI 的 Cosmos 模型
        wavespeed_token = os.getenv("WAVESPEED_API_KEY")
        if wavespeed_token:
            video_url = generate_video_with_cosmos(prompt, req.duration)
        else:
            # 如果沒有 WaveSpeedAI API Key，回傳測試影片
            print("⚠️ WAVESPEED_API_KEY 未設定，使用測試影片")
            video_url = "https://replicate.delivery/pbxt/example-test-video.mp4"
        
        return {
            "success": True,
            "videoUrl": video_url,
            "prompt": prompt
        }
        
    except Exception as e:
        print(f"❌ 錯誤: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成失敗: {str(e)}")

# 健康檢查 (不需要登入)
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "蕨積宇宙影片產生器"}

# 提供前端頁面 (需要登入)
@app.get("/", response_class=HTMLResponse)
async def get_index(credentials: HTTPBasicCredentials = Depends(security)):
    """保護首頁，需要登入"""
    verify_credentials(credentials)
    
    # 讀取 index.html 內容
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            html_content = f.read()
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        return HTMLResponse(content="<h1>index.html 不存在</h1><p>請確認檔案已上傳</p>", status_code=404)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
