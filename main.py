import os
import time
import hashlib
import hmac
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

app = FastAPI(title="蕨積宇宙影片產生器 API")

# 基本認證
security = HTTPBasic()

# 從環境變數讀取帳號密碼
VALID_USERNAME = os.getenv("PAGE_USERNAME", "admin")
VALID_PASSWORD = os.getenv("PAGE_PASSWORD", "zepower2025")

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """驗證使用者帳號密碼"""
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

# 生成影片 (使用 Replicate)
def generate_video_with_replicate(prompt: str, duration: int) -> str:
    import replicate
    
    num_frames = min(duration * 24, 200)
    
    output = replicate.run(
        "anotherjesse/zeroscope-v2-xl:9f747673945c62801b13b84701c783929c0ee784e4748ec062204894dda1b351",
        input={
            "prompt": prompt,
            "num_frames": num_frames,
            "width": 576,
            "height": 1024,
            "seed": -1,
        }
    )
    
    if isinstance(output, list) and len(output) > 0:
        return output[0]
    return output

# API 端點 (需要登入)
# 在 main.py 中加入這個新的 API 端點

@app.get("/api/test-replicate")
async def test_replicate_api():
    """測試 Replicate API 是否正常運作"""
    import replicate
    import os
    
    try:
        # 檢查 API Token
        token = os.getenv("REPLICATE_API_TOKEN")
        if not token:
            return {
                "success": False,
                "error": "REPLICATE_API_TOKEN 未設定",
                "hint": "請在 Render 的 Environment Variables 中加入 REPLICATE_API_TOKEN"
            }
        
        # 測試生成一張圖片
        output = replicate.run(
            "black-forest-labs/flux-schnell",
            input={"prompt": "a cute cartoon fern plant, white background"}
        )
        
        image_url = output[0] if isinstance(output, list) else output
        
        return {
            "success": True,
            "message": "Replicate API 運作正常",
            "image_url": image_url
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
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
    
    try:
        replicate_token = os.getenv("REPLICATE_API_TOKEN")
        if replicate_token:
            video_url = generate_video_with_replicate(prompt, req.duration)
        else:
            # 測試模式
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
    return {"status": "ok"}

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
