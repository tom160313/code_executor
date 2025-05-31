
from fastapi import FastAPI, Request, UploadFile, File
from pydantic import BaseModel
import uuid
import os
import traceback
import matplotlib.pyplot as plt
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.cors import CORSMiddleware
import codecs

app = FastAPI()

# CORS対応
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# static ディレクトリ作成
STATIC_DIR = "static"
os.makedirs(STATIC_DIR, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class CodeInput(BaseModel):
    code: str

@app.post("/execute")
async def execute_code(payload: CodeInput):
    code = codecs.decode(payload.code, "unicode_escape")
    local_vars = {}

    try:
        exec(code, local_vars, local_vars)

        for val in local_vars.values():
            if hasattr(val, "savefig"):
                filename = f"{uuid.uuid4().hex}.png"
                filepath = os.path.join(STATIC_DIR, filename)
                val.savefig(filepath)
                plt.close("all")

                # ファイルをそのままレスポンスとして返す（ダウンロード対応）
                return FileResponse(
                    path=filepath,
                    filename="graph.png",
                    media_type="image/png",
                    headers={
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Expose-Headers": "Content-Disposition"
                    }
                )

        return {
            "status_code": 200,
            "body": "コードは実行されましたが、画像は生成されませんでした。",
            "files": []
        }

    except Exception as e:
        return {
            "status_code": 500,
            "body": f"エラーが発生しました: {str(e)}",
            "traceback": traceback.format_exc(),
            "files": []
        }
