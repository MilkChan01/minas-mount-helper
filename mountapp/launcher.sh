#!/bin/bash
# 小米智能存储 Finder 挂载助手 - 启动器
# 优先使用支持 Ed25519 客户端证书的解释器（可显示存储统计），否则退回系统 Python
DIR="$(cd "$(dirname "$0")/../Resources" && pwd)"
cd "$DIR" || exit 1

# 已有实例在跑则不再重复启动（无论是否 --hidden）
if pgrep -f "Resources/main.py" >/dev/null 2>&1; then
    exit 0
fi

PY=""
for base in "$HOME/Library/Application Support/Doubao/sandbox_runtime/bases/"*/bin/python3; do
    [ -x "$base" ] || continue
    if "$base" -c "import ssl,tkinter" >/dev/null 2>&1; then
        PY="$base"
        break
    fi
done
[ -z "$PY" ] && PY="/usr/bin/python3"

exec "$PY" "$DIR/main.py" "$@"
