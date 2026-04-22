# test_replicate.py
# 這個檔案用來測試 Replicate API 是否正常運作

import os
import replicate
from dotenv import load_dotenv

# 載入環境變數（Render 會自動注入，本地測試用 .env）
load_dotenv()

def test_replicate():
    print("🔍 開始測試 Replicate API...")
    
    # 檢查 API Token 是否存在
    api_token = os.getenv("REPLICATE_API_TOKEN")
    if not api_token:
        print("❌ 錯誤：找不到 REPLICATE_API_TOKEN 環境變數")
        print("   請確認 Render 的 Environment Variables 有設定")
        return False
    
    print(f"✅ API Token 已設定 (前8碼: {api_token[:8]}...)")
    
    try:
        # 使用 Flux Schnell 模型測試（最快、最穩定）
        print("📡 呼叫 Flux Schnell 模型生成圖片...")
        
        output = replicate.run(
            "black-forest-labs/flux-schnell",
            input={
                "prompt": "a cute cartoon fern plant wearing glasses, professional style, white background, 2D animation"
            }
        )
        
        # output 可能是字串或列表
        if isinstance(output, list):
            image_url = output[0]
        else:
            image_url = output
        
        print(f"✅ 測試成功！")
        print(f"🖼️ 圖片網址: {image_url}")
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_replicate()
    exit(0 if success else 1)
