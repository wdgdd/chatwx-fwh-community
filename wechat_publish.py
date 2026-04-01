#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号文章发布脚本 v8（双模式版）
- 新增发布方式选择：A自动发布 / B导出Markdown手动WeMark
- python wechat_publish.py --setup 引导式配置
- 必填项仅4项，其余全部智能默认值
"""

import requests, json, re, os, sys, io, yaml, getpass
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.yaml")

def resolve_path(path):
    if os.path.isabs(path):
        return path
    return os.path.normpath(os.path.join(SCRIPT_DIR, path))

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
    else:
        raw = {}

    brand = raw.get("brand", {})
    return {
        "brand": {
            "name": brand.get("name", ""),
            "product": brand.get("product", ""),
            "miniprogram_link": brand.get("miniprogram_link", ""),
            "signature_line": brand.get("signature_line", ""),
            "promise_line": brand.get("promise_line", ""),
            "footer_image": resolve_path(brand.get("footer_image", "")),
        },
        "article": {
            "file": resolve_path(raw.get("article", {}).get("file", "")),
            "title": raw.get("article", {}).get("title", "untitled"),
            "archive_path": resolve_path(raw.get("article", {}).get("archive_path", "./articles")),
        },
        "image_dirs": [resolve_path(d) for d in raw.get("image_dirs", ["./"])],
        "theme": {
            "name": raw.get("theme", {}).get("name", "simple"),
            "primary_color": raw.get("theme", {}).get("primary_color", "#009874"),
        },
        "wechat": {
            "appid": raw.get("wechat", {}).get("appid", ""),
            "secret": raw.get("wechat", {}).get("secret", ""),
        },
        "image_search": raw.get("image_search", {}),
        "seo": raw.get("seo", {"enabled": True, "description_max_length": 200, "keywords_max": 10}),
        "advanced": raw.get("advanced", {"append_footer": True, "use_media_cache": True}),
    }

config = load_config()

def interactive_setup():
    print(f"\n{'='*50}")
    print(f"  公众号发布工具 · 首次配置向导")
    print(f"{'='*50}")
    print("\n只需回答4个问题，我来帮你填好配置。\n")

    answers = {}

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("❓ 第一个问题：你的品牌叫什么名字？")
    print("   （显示在文章末尾签名，如：瑞幸咖啡）")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    answers["brand_name"] = input("请输入品牌名称：").strip()
    if not answers["brand_name"]:
        print("⚠️  品牌名称不能为空")
        return

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("❓ 第二个问题：你的产品是什么？")
    print("   （如：生椰拿铁、旺旺大礼包）")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    answers["product_name"] = input("请输入产品名称：").strip()
    if not answers["product_name"]:
        print("⚠️  产品名称不能为空")
        return

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("❓ 第三个问题：你的公众号 AppID 是什么？")
    print("   获取：https://mp.weixin.qq.com → 设置与开发 → 基本配置")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    answers["appid"] = input("请输入 AppID：").strip()
    if not answers["appid"]:
        print("⚠️  AppID 不能为空")
        return

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("❓ 第四个问题：你的公众号 AppSecret 是什么？")
    print("   同上页面，点「重置」→ 管理员微信扫码 → 复制")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    answers["appsecret"] = getpass.getpass("请输入 AppSecret：").strip()
    if not answers["appsecret"]:
        print("⚠️  AppSecret 不能为空")
        return

    config_content = f'''# ============================================================
# 公众号写作发布工具 · 配置文件
# 由引导式配置自动生成
# ============================================================

brand:
  name: "{answers["brand_name"]}"
  product: "{answers["product_name"]}"

wechat:
  appid: "{answers["appid"]}"
  secret: "{answers["appsecret"]}"

brand:
  signature_line: ""
  promise_line: ""
  miniprogram_link: ""
  footer_image: ""

article:
  file: "./articles/01-example.md"
  title: "01"
  archive_path: "./articles"

theme:
  name: "simple"

image_search:
  pixabay_api_key: ""

seo:
  enabled: false

advanced:
  append_footer: false
  use_media_cache: true
'''

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        f.write(config_content)

    print(f"\n{'='*50}")
    print(f"  ✅ 配置完成！")
    print(f"{'='*50}")
    print(f"\n📝 已生成 config.yaml：")
    print(f"   品牌：{answers['brand_name']}")
    print(f"   产品：{answers['product_name']}")
    print(f"\n📁 接下来把文章 .md 文件放到 articles/ 目录")
    print(f"   然后运行 python wechat_publish.py 即可发布")
    print(f"{'='*50}\n")

if len(sys.argv) > 1 and sys.argv[1] in ["--setup", "-s", "setup"]:
    interactive_setup()
    sys.exit(0)

# 验证必填项
missing = []
if not config["wechat"]["appid"] or "{{" in config["wechat"]["appid"]:
    missing.append("wechat.appid")
if not config["wechat"]["secret"] or "{{" in config["wechat"]["secret"]:
    missing.append("wechat.secret")
if not config["brand"]["name"] or "{{" in config["brand"]["name"]:
    missing.append("brand.name")
if not config["brand"]["product"] or "{{" in config["brand"]["product"]:
    missing.append("brand.product")
if missing:
    print(f"\n⚠️  config.yaml 缺少必填项：")
    for m in missing:
        print(f"   ❌ {m}")
    print(f"\n💡 运行 python wechat_publish.py --setup 引导式配置")
    sys.exit(1)

# 后续完整脚本（完整版见仓库）
print("\n配置验证通过！请参考仓库完整版 wechat_publish.py")
print(f"仓库地址：https://github.com/wdgdd/chatwx-fwh-community")
