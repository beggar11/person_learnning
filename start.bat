@echo off
set "NUTSTORE_DB=%USERPROFILE%\Nutstore Files\kb\kb.db"

if exist "%NUTSTORE_DB%" (
    echo 使用坚果云同步数据库: %NUTSTORE_DB%
    set KB_DB_PATH=%NUTSTORE_DB%
) else (
    echo 未找到同步数据库，使用本地数据库
    set KB_DB_PATH=%~dp0kb.db
)

pip install -r requirements.txt -q
echo 启动服务: http://localhost:8000
python -m uvicorn main:app --host 0.0.0.0 --port 8000
