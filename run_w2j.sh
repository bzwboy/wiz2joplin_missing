#!/bin/bash

# 设置必要的参数
WIZNOTE_DIR="$HOME/.wiznote"  # WizNote 数据目录
WIZNOTE_USER="mousecat4444@126.com"  # WizNote 用户邮箱
JOPLIN_TOKEN="18dd9c058556c74ad5d26fc995e4705bc6b18769ca64129ddc7da61506727e6c0c579bc668adad1e914da26a7ec6621cb1b641cfb169fab6da419b16be057a03"  # Joplin Web Clipper 服务的授权令牌
OUTPUT_DIR="$HOME/git/wiz2joplin_missing/data"  # 输出目录

# 运行迁移程序
python3 -m w2j \
    --wiz-dir "$WIZNOTE_DIR" \
    --wiz-user "$WIZNOTE_USER" \
    --joplin-token "$JOPLIN_TOKEN" \
    --output "$OUTPUT_DIR" \
    --all \
    --skip-missing-attachments \
    --log-level DEBUG

