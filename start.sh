#!/bin/bash
# 坚果云同步数据库路径
NUTSTORE_DB="$HOME/Nutstore Files/kb/kb.db"

if [ ! -f "$NUTSTORE_DB" ]; then
    echo "未找到同步数据库，使用本地数据库"
    export KB_DB_PATH="$(dirname "$0")/kb.db"
else
    echo "使用坚果云同步数据库: $NUTSTORE_DB"
    export KB_DB_PATH="$NUTSTORE_DB"
fi

pip install -r requirements.txt -q 2>/dev/null
echo "启动服务: http://localhost:8000"
uvicorn main:app --host 0.0.0.0 --port 8000
