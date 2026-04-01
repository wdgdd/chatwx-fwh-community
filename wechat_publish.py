#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号文章发布脚本 v8（双模式版）
- 新增发布方式选择：A自动发布 / B导出Markdown手动复制到编辑器
- python wechat_publish.py --setup 引导式配置
- 必填项仅4项，其余全部智能默认值
- 所有路径支持相对路径
- 6套排版主题
- SEO可选（默认关闭）
- 图片缓存机制
"""

import requests
import json
import re
import os
import sys
import io
import yaml
import getpass
from pathlib import Path

# 确保输出编码正确
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 脚本所在目录作为基准路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def resolve_path(path):
    """将相对路径转换为绝对路径，以脚本目录为基准"""
    if os.path.isabs(path):
        return path
    return os.path.normpath(os.path.join(SCRIPT_DIR, path))

# 加载配置文件
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.yaml")

def load_config():
    """加载配置文件，处理缺失值和相对路径"""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
    else:
        print(f"[WARN] config.yaml not found at {CONFIG_FILE}")
        raw = {}

    brand = raw.get("brand", {})
    config = {
        "brand": {
            "name": brand.get("name", ""),
            "product": brand.get("product", ""),
            "miniprogram_link": brand.get("miniprogram_link", ""),
            "signature_line": brand.get("signature_line", ""),
            "promise_line": brand.get("promise_line", ""),
            "footer_image": resolve_path(brand.get("footer_image", "")),
            "logo": resolve_path(brand.get("logo", "")) if brand.get("logo") else "",
        },
        "article": {
            "file": resolve_path(raw.get("article", {}).get("file", "")),
            "title": raw.get("article", {}).get("title", "untitled"),
            "archive_path": resolve_path(raw.get("article", {}).get("archive_path", "./articles")),
        },
        "image_dirs": [resolve_path(d) for d in raw.get("image_dirs", ["./"])],
        "theme": {
            "name": raw.get("theme", {}).get("name", "green"),
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
    return config

config = load_config()

# ============================================================
# 引导式配置模式
# ============================================================
def interactive_setup():
    """引导式配置，回答4个问题即可开始使用"""
    print(f"\n{'='*50}")
    print(f"  公众号发布工具 · 首次配置向导")
    print(f"{'='*50}")
    print("\n只需回答4个问题，我来帮你填好配置。\n")

    answers = {}

    # Q1: 品牌名称
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("❓ 第一个问题：你的品牌叫什么名字？")
    print("   （显示在文章末尾签名，如：瑞幸咖啡）")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    answers["brand_name"] = input("请输入品牌名称：").strip()
    if not answers["brand_name"]:
        print("⚠️  品牌名称不能为空")
        return

    # Q2: 产品名称
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("❓ 第二个问题：你的产品是什么？")
    print("   （如：生椰拿铁、旺旺大礼包、空气蜜粉）")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    answers["product_name"] = input("请输入产品名称：").strip()
    if not answers["product_name"]:
        print("⚠️  产品名称不能为空")
        return

    # Q3: AppID
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("❓ 第三个问题：你的公众号 AppID 是什么？")
    print("   ┌────────────────────────────────────────────────┐")
    print("   │ 📍 获取步骤：                                   │")
    print("   │ 1. 打开 https://mp.weixin.qq.com               │")
    print("   │ 2. 登录你的公众号                              │")
    print("   │ 3. 点「设置与开发」→「基本配置」                │")
    print("   │ 4. 找到「AppID」复制即可                       │")
    print("   └────────────────────────────────────────────────┘")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    answers["appid"] = input("请输入 AppID：").strip()
    if not answers["appid"]:
        print("⚠️  AppID 不能为空")
        return

    # Q4: AppSecret
    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("❓ 第四个问题：你的公众号 AppSecret 是什么？")
    print("   ┌────────────────────────────────────────────────┐")
    print("   │ 📍 获取步骤：                                   │")
    print("   │ 1. 同上页面，点击「AppSecret」旁边的「重置」      │")
    print("   │ 2. 用管理员微信扫码确认                         │")
    print("   │ 3. 获取后复制即可（只显示一次！）               │")
    print("   └────────────────────────────────────────────────┘")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    answers["appsecret"] = getpass.getpass("请输入 AppSecret：").strip()
    if not answers["appsecret"]:
        print("⚠️  AppSecret 不能为空")
        return

    # 生成 config.yaml
    config_content = f'''# ============================================================
# 公众号写作发布工具 · 配置文件
# ============================================================
# 由引导式配置自动生成
# 如需修改，直接编辑本文件即可
# ============================================================


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔴 必填项（4项）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

brand:
  name: "{answers["brand_name"]}"
  product: "{answers["product_name"]}"

wechat:
  appid: "{answers["appid"]}"
  secret: "{answers["appsecret"]}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🟡 可选项（不填则使用默认值，可稍后修改）
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

brand:
  signature_line: ""
  promise_line: ""
  miniprogram_link: ""
  footer_image: ""

article:
  file: "./articles/01-example.md"
  title: "01"
  archive_path: "./articles"

image_dirs:
  - "./articles/assets/"
  - "./assets/"
  - "./"

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
    print(f"   AppID：{answers['appid'][:8]}...（已隐藏）")
    print(f"\n📁 接下来把文章 .md 文件放到 articles/ 目录")
    print(f"   然后运行 python wechat_publish.py 即可发布")
    print(f"\n💡 高级功能（主题/SEO/结尾图）可稍后修改 config.yaml 开启")
    print(f"{'='*50}\n")


def run_setup_mode():
    """执行引导式配置"""
    interactive_setup()
    sys.exit(0)

# 检查是否运行引导式配置
if len(sys.argv) > 1 and sys.argv[1] in ["--setup", "-s", "setup"]:
    run_setup_mode()

# 验证必填项（仅4项）
missing = []
if not config["wechat"]["appid"] or "{{" in config["wechat"]["appid"]:
    missing.append("wechat.appid（必填）")
if not config["wechat"]["secret"] or "{{" in config["wechat"]["secret"]:
    missing.append("wechat.secret（必填）")
if not config["brand"]["name"] or "{{" in config["brand"]["name"]:
    missing.append("brand.name（必填）")
if not config["brand"]["product"] or "{{" in config["brand"]["product"]:
    missing.append("brand.product（必填）")
if missing:
    print(f"\n⚠️  config.yaml 缺少必填项：")
    for m in missing:
        print(f"   ❌ {m}")
    print(f"\n💡 运行 python wechat_publish.py --setup 引导式配置，只需回答4个问题")
    print(f"   或直接打开 config.yaml 填写缺失项")
    sys.exit(1)

# 智能默认值处理
if not BRAND_SIGNATURE:
    BRAND_SIGNATURE = f"{BRAND_NAME} · {BRAND_PRODUCT}"

if not BRAND_FOOTER_IMAGE or not os.path.exists(BRAND_FOOTER_IMAGE):
    if config["advanced"].get("append_footer") and BRAND_FOOTER_IMAGE:
        print(f"[WARN] 结尾图不存在，已跳过：{BRAND_FOOTER_IMAGE}")
    BRAND_FOOTER_IMAGE = ""

# SEO降级：jieba未安装时静默跳过
seo_enabled = config["seo"].get("enabled", False)
try:
    if seo_enabled:
        import jieba
except ImportError:
    if seo_enabled:
        print("[INFO] jieba 未安装，SEO关键词生成已跳过（不影响发布）")
    seo_enabled = False

# 加载主题
THEMES_FILE = os.path.join(SCRIPT_DIR, "themes.yaml")

def load_themes():
    if os.path.exists(THEMES_FILE):
        with open(THEMES_FILE, "r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    return {}

def load_theme_by_name(theme_name):
    themes_data = load_themes()
    themes = themes_data.get("themes", {})
    default_name = themes_data.get("default_theme", "green")
    theme_name = theme_name if theme_name in themes else default_name
    theme = themes.get(theme_name, {})
    return {
        "name": theme.get("name", "默认主题"),
        "primary_color": theme.get("primary_color", "#009874"),
        "secondary_color": theme.get("secondary_color", "#006B5C"),
        "text_color": theme.get("text_color", "#333333"),
        "heading_style": theme.get("heading_style", "colored"),
        "table_style": theme.get("table_style", "colored_header"),
        "button_style": theme.get("button_style", "filled"),
        "separator_style": theme.get("separator_style", "line"),
        "list_style": theme.get("list_style", "simple"),
        "alignment": theme.get("alignment", "left"),
    }

theme_name = config["theme"]["name"]
if theme_name.startswith("#"):
    THEME = load_theme_by_name("green")
    THEME["primary_color"] = theme_name
else:
    THEME = load_theme_by_name(theme_name)

GREEN = THEME["primary_color"]

# 品牌配置
BRAND_NAME = config["brand"]["name"]
BRAND_PRODUCT = config["brand"]["product"]
BRAND_SIGNATURE = config["brand"]["signature_line"]
BRAND_PROMISE = config["brand"]["promise_line"]
BRAND_MINIPROGRAM = config["brand"]["miniprogram_link"]
BRAND_FOOTER_IMAGE = config["brand"]["footer_image"]

# 图片缓存
MEDIA_CACHE_FILE = os.path.join(SCRIPT_DIR, "media_cache.json")

def load_media_cache():
    if os.path.exists(MEDIA_CACHE_FILE):
        try:
            with open(MEDIA_CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {}

def save_media_cache(cache):
    with open(MEDIA_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def search_and_download_image(keyword, save_dir, filename=None, min_width=1920):
    """从Pixabay搜索并下载图片（需要API Key）"""
    api_key = config["image_search"].get("pixabay_api_key", "")
    if not api_key:
        return None
    try:
        params = {
            "key": api_key, "q": keyword, "image_type": "photo",
            "orientation": "horizontal", "safesearch": "true", "per_page": 5
        }
        resp = requests.get("https://pixabay.com/api/", params=params, timeout=10)
        data = resp.json()
        if int(data.get("totalHits", 0)) == 0:
            return None
        for hit in data.get("hits", []):
            if hit.get("imageWidth", 0) >= min_width:
                img_url = hit.get("webformatURL")
                if not img_url:
                    continue
                img_resp = requests.get(img_url, timeout=10)
                if img_resp.status_code != 200:
                    continue
                if not filename:
                    filename = keyword.replace(" ", "_")
                save_path = os.path.join(save_dir, f"{filename}.jpg")
                with open(save_path, "wb") as f:
                    f.write(img_resp.content)
                print(f"  [IMG-SEARCH] '{keyword}' -> {os.path.basename(save_path)}")
                return save_path
        return None
    except Exception as e:
        print(f"  [IMG-SEARCH] Error: {e}")
        return None


def extract_keywords_from_content(md_content):
    """从文章内容提取关键词（用于SEO）"""
    keywords = []
    if BRAND_NAME:
        keywords.append(BRAND_NAME)
    if BRAND_PRODUCT:
        keywords.append(BRAND_PRODUCT)
    lines = md_content.split('\n')
    for line in lines[:10]:
        if line.strip().startswith('# '):
            for word in line.strip()[2:].split():
                if len(word) >= 2 and word not in keywords:
                    keywords.append(word)
            break
    try:
        import jieba
        from collections import Counter
        text = '\n'.join([l for l in text.split('\n')
                          if not l.startswith('#') and not l.startswith('[📎') and not l.startswith('```')])
        words = jieba.cut(text)
        stopwords = {'的', '了', '是', '在', '和', '有', '我', '你', '他', '她', '它', '这', '那',
                     '个', '就', '也', '都', '很', '但', '吗', '啊', '呀', '呢', '吧', '与', '和', '为'}
        filtered = [w for w in words if len(w) >= 2 and w not in stopwords and w not in keywords]
        for word, _ in Counter(filtered).most_common(5):
            if word not in keywords:
                keywords.append(word)
    except ImportError:
        pass
    return keywords[:config["seo"].get("keywords_max", 10)]


def generate_seo_meta(md_content):
    """生成SEO元数据"""
    lines = md_content.split('\n')
    parts = []
    for line in lines:
        line = line.strip()
        if line and not line.startswith('#') and not line.startswith('[📎'):
            parts.append(line)
            if sum(len(p) for p in parts) >= config["seo"].get("description_max_length", 200):
                break
    description = ' '.join(parts)[:200] + "..."
    keywords = extract_keywords_from_content(md_content)
    return {"description": description, "keywords": keywords}


def get_article_stats(publisher, days=7):
    """获取文章统计数据"""
    try:
        url = f"https://api.weixin.qq.com/cgi-bin/material/get_materiallist?access_token={publisher.access_token}&type=news&offset=0&count=20"
        data = requests.get(url).json()
        if data.get("errcode") != 0:
            print(f"[ERR] Get stats failed: {data}")
            return []
        return [{
            "title": item.get("content", {}).get("news_item", [{}])[0].get("title", ""),
            "read_num": item.get("content", {}).get("news_item", [{}])[0].get("read_num", 0),
            "like_num": item.get("content", {}).get("news_item", [{}])[0].get("like_num", 0),
        } for item in data.get("item", [])]
    except Exception as e:
        print(f"[ERR] Get stats error: {e}")
        return []


def analyze_article_stats(stats):
    if not stats:
        print("\n[ANALYSIS] No stats available")
        return
    print("\n=== 文章数据分析 ===")
    for i, s in enumerate(stats, 1):
        print(f"\n{i}. {s['title']}")
        print(f"   阅读: {s['read_num']} | 点赞: {s['like_num']}")
    best = max(stats, key=lambda x: x["read_num"])
    print(f"\n🏆 表现最佳: {best['title']} (阅读: {best['read_num']})")
    print(f"\n💡 建议：")
    print(f"   - 复制'{best['title']}'的场景框架到新文章")
    print(f"   - 观察该文章的用户留言，了解读者痛点")


def process_inline(text):
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    return text


def markdown_to_html(md_text, search_dirs, publisher):
    """将Markdown转为公众号HTML"""
    lines = md_text.split('\n')
    html_parts = []
    in_table = in_ul = False
    table_rows = []

    def close_ul():
        nonlocal in_ul
        if in_ul:
            html_parts.append('</ul>')
            in_ul = False

    def close_table():
        nonlocal in_table, table_rows
        if in_table and table_rows:
            header = table_rows[0]
            html_parts.append('<table style="width:100%;border-collapse:collapse;margin:10px 0;font-size:14px;">')
            cells = [c.strip() for c in header.split('|') if c.strip()]
            html_parts.append('<tr>')
            for c in cells:
                c = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', c)
                cls = f'th style="border:1px solid #ddd;padding:8px;background:{GREEN};color:#fff;text-align:left;"' if THEME["table_style"] == "colored_header" else 'th style="border:1px solid #ddd;padding:8px;background:#f5f5f5;color:#333;text-align:left;"'
                html_parts.append(f'<{cls}>{c}</th>')
            html_parts.append('</tr>')
            for row in table_rows[1:]:
                if re.match(r'^[\s|:-]+$', row):
                    continue
                cells = [c.strip() for c in row.split('|') if c.strip()]
                html_parts.append('<tr>')
                for c in cells:
                    c = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', c)
                    html_parts.append(f'<td style="border:1px solid #ddd;padding:8px;">{c}</td>')
                html_parts.append('</tr>')
            html_parts.append('</table>')
            table_rows = []
            in_table = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            close_ul(); close_table()
            continue

        # 图片标注
        img_match = re.match(r'\[📎插入图片[：:](.+?)\]', stripped)
        if img_match:
            close_ul(); close_table()
            img_filename = img_match.group(1).strip()
            img_path = find_image(img_filename, search_dirs)
            if not img_path:
                unsplash_kws = config["image_search"].get("unsplash_keywords", {})
                keyword = next((kw for sc, kw in unsplash_kws.items() if sc in img_filename.lower()), None)
                if keyword and search_dirs:
                    save_dir = search_dirs[0]
                    os.makedirs(save_dir, exist_ok=True)
                    downloaded = search_and_download_image(keyword, save_dir, img_filename)
                    if downloaded:
                        img_path = downloaded
            if img_path and publisher:
                img_url = publisher.upload_image_for_content(img_path)
                if img_url:
                    html_parts.append(f'<p style="text-align:center;"><img src="{img_url}" style="max-width:100%;"/></p>')
                    continue
            html_parts.append(f'<p>[图片: {img_filename}]</p>')
            continue

        # 标题
        heading_map = {'### ': 'h3', '## ': 'h2', '# ': 'h1'}
        for prefix, tag in heading_map.items():
            if stripped.startswith(prefix):
                close_ul(); close_table()
                text = stripped[len(prefix):].strip()
                style = THEME["heading_style"]
                color = GREEN if style in ("colored", "large") else "#333"
                size = {"h3": ("16px", "18px"), "h2": ("18px", "20px"), "# ": ("22px", "26px")}[tag]
                align = 'center' if THEME["alignment"] == 'center' else 'left'
                html_parts.append(f'<{tag} style="font-size:{size[1] if style=="large" else size[0]};font-weight:bold;margin:20px 0 10px;color:{color};text-align:{align};">{text}</{tag}>')
                break
        else:
            close_ul()

            # 分隔线
            if stripped == '---':
                close_table()
                if THEME["separator_style"] == "line":
                    html_parts.append(f'<hr style="border:none;height:2px;background:{GREEN};margin:20px 0;"/>')
                elif THEME["separator_style"] == "dotted":
                    html_parts.append(f'<hr style="border:none;border-top:2px dashed {GREEN};margin:20px 0;"/>')
                else:
                    html_parts.append('<p style="margin:20px 0;">&nbsp;</p>')

            # 表格
            elif stripped.startswith('|') and '|' in stripped:
                close_table()
                table_rows.append(stripped)
                in_table = True

            # 列表
            elif stripped.startswith('- '):
                close_table()
                item_text = process_inline(stripped[2:])
                if not in_ul:
                    html_parts.append('<ul style="margin:8px 0;padding-left:20px;">')
                    in_ul = True
                html_parts.append(f'<li style="margin:4px 0;line-height:1.8;">{item_text}</li>')

            else:
                # 数据来源
                if stripped.startswith('数据来源：') or stripped.startswith('数据来源:'):
                    html_parts.append(f'<p style="font-size:12px;color:#999;margin:5px 0;">{stripped}</p>')
                # 品牌签名（通用：含品牌名 或 promise关键词）
                elif (BRAND_NAME and BRAND_NAME in stripped) or (BRAND_PROMISE and any(p.strip() in stripped for p in BRAND_PROMISE.split('|') if p.strip())):
                    align = 'center' if THEME["alignment"] == 'center' else 'left'
                    html_parts.append(f'<p style="text-align:{align};font-size:13px;color:{GREEN};margin:20px 0;letter-spacing:1px;">{stripped}</p>')
                # 小程序/商城链接
                elif '小程序' in stripped or '商城' in stripped or (BRAND_MINIPROGRAM and BRAND_MINIPROGRAM in stripped):
                    stripped = process_inline(stripped)
                    if THEME["button_style"] == "filled":
                        html_parts.append(f'<p style="text-align:center;margin:15px 0;"><span style="display:inline-block;padding:10px 20px;background:{GREEN};color:#fff;border-radius:20px;font-size:14px;">{stripped}</span></p>')
                    elif THEME["button_style"] == "outline":
                        html_parts.append(f'<p style="text-align:center;margin:15px 0;"><span style="display:inline-block;padding:10px 20px;border:2px solid {GREEN};color:{GREEN};border-radius:20px;font-size:14px;">{stripped}</span></p>')
                    else:
                        html_parts.append(f'<p style="text-align:center;margin:15px 0;color:{GREEN};font-weight:bold;">{stripped}</p>')
                # 普通段落
                else:
                    stripped = process_inline(stripped)
                    html_parts.append(f'<p style="margin:10px 0;line-height:1.8;">{stripped}</p>')

    close_ul(); close_table()

    # 追加品牌结尾图（仅当已配置且文件存在时）
    if BRAND_FOOTER_IMAGE and os.path.exists(BRAND_FOOTER_IMAGE) and publisher:
        footer_url = publisher.upload_image_for_content(BRAND_FOOTER_IMAGE)
        if footer_url:
            html_parts.append(f'<p style="text-align:center;margin:25px 0 10px;"><img src="{footer_url}" style="max-width:100%;"/></p>')

    return '\n'.join(html_parts)


class WeChatPublisher:
    def __init__(self, appid, appsecret):
        self.appid = appid
        self.appsecret = appsecret
        self.access_token = self._get_access_token()
        self.media_cache = load_media_cache() if config["advanced"]["use_media_cache"] else {}

    def _get_access_token(self):
        url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={self.appid}&secret={self.appsecret}"
        data = requests.get(url).json()
        if "access_token" in data:
            print("[OK] access_token")
            return data["access_token"]
        raise Exception(f"access_token failed: {data}")

    def upload_image_for_content(self, image_path):
        if not os.path.exists(image_path):
            return None
        filename = os.path.basename(image_path)
        if filename in self.media_cache:
            print(f"  [IMG] {filename} -> cached")
            return self.media_cache[filename]
        url = f"https://api.weixin.qq.com/cgi-bin/media/uploadimg?access_token={self.access_token}"
        try:
            with open(image_path, "rb") as f:
                data = requests.post(url, files={"media": f}).json()
            if "url" in data:
                print(f"  [IMG] {filename} -> uploaded")
                self.media_cache[filename] = data["url"]
                save_media_cache(self.media_cache)
                return data["url"]
            print(f"  [ERR] {filename}: {data}")
            return None
        except Exception as e:
            print(f"  [ERR] {filename}: {e}")
            return None

    def upload_image_for_thumb(self, image_path):
        if not os.path.exists(image_path):
            return None
        filename = os.path.basename(image_path)
        cache_key = f"thumb_{filename}"
        if cache_key in self.media_cache:
            print(f"[COVER] {filename} -> cached")
            return self.media_cache[cache_key]
        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={self.access_token}&type=image"
        try:
            with open(image_path, "rb") as f:
                data = requests.post(url, files={"media": f}).json()
            if "media_id" in data:
                print(f"[COVER] {filename} -> uploaded")
                self.media_cache[cache_key] = data["media_id"]
                save_media_cache(self.media_cache)
                return data["media_id"]
            print(f"[ERR] cover: {data}")
            return None
        except Exception as e:
            print(f"[ERR] cover: {e}")
            return None

    def create_draft(self, title, html_content, thumb_media_id):
        url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={self.access_token}"
        data = {
            "articles": [{
                "article_type": "news",
                "title": title,
                "content": html_content,
                "thumb_media_id": thumb_media_id,
                "digest": "",
                "content_source_url": "",
                "need_open_comment": 0,
                "only_fans_can_comment": 0
            }]
        }
        resp = requests.post(url, data=json.dumps(data, ensure_ascii=False).encode('utf-8'),
                             headers={'Content-Type': 'application/json; charset=utf-8'})
        result = resp.json()
        if "media_id" in result:
            print(f"[DRAFT] OK, media_id: {result['media_id']}")
            return result["media_id"]
        print(f"[ERR] draft: {result}")
        return None


def find_image(filename, search_dirs):
    for d in search_dirs:
        path = os.path.join(d, filename)
        if os.path.exists(path):
            return path
    return None


def select_mode():
    """让用户选择发布方式"""
    print(f"\n{'='*50}")
    print(f"  chatwx-fwh 公众号发布脚本 v8")
    print(f"{'='*50}")
    print("\n请选择发布方式：\n")
    print("  A. 自动发布到草稿箱")
    print("     需要配置 AppID/Secret，一键发布到公众号草稿箱")
    print()
    print("  B. 导出 Markdown（手动复制到编辑器）")
    print("     不需要配置 API，直接生成排版好的 Markdown")
    print("     复制到任意 Markdown 编辑器（如 https://md.doocs.org/）后替换图片发布")
    print()
    while True:
        choice = input("请输入 A 或 B [默认B]：").strip().upper()
        if not choice:
            choice = "B"
        if choice in ["A", "B"]:
            return choice
        print("⚠️  请输入 A 或 B")


def export_to_markdown(article_file, image_dirs, title, brand_name, brand_product):
    """导出为 Markdown（手动模式）"""
    print(f"\n{'='*50}")
    print(f"  导出 Markdown（手动模式）")
    print(f"{'='*50}")

    with open(article_file, "r", encoding="utf-8") as f:
        md_content = f.read()

    # 收集图片信息
    images_found = []
    for d in image_dirs:
        if not os.path.exists(d):
            continue
        for img in list(Path(d).glob("*.jpg")) + list(Path(d).glob("*.jpeg")) + list(Path(d).glob("*.png")) + list(Path(d).glob("*.gif")):
            images_found.append(str(img))

    # 生成带图片标注的 Markdown
    output_lines = []
    output_lines.append(f"# {title}\n")

    # 提取图片标注行并重排
    lines = md_content.split("\n")
    for line in lines:
        if "[📎插入图片：" in line or "![image]" in line.lower():
            # 提取图片文件名
            match = re.search(r'\[📎插入图片：(.+?)\]', line)
            if match:
                fname = match.group(1)
                # 查找对应文件
                matched = None
                for img in images_found:
                    if fname in img or os.path.basename(img).startswith(fname.split(".")[0]):
                        matched = img
                        break
                if matched:
                    output_lines.append(f"\n📎 【{fname}】 → 请在编辑器中插入：{os.path.basename(matched)}\n")
                    images_found.remove(matched) if matched in images_found else None
                else:
                    output_lines.append(f"\n📎 【{fname}】 → ⚠️ 未找到对应图片\n")
            else:
                output_lines.append(f"\n📎 图片占位符\n")
        else:
            output_lines.append(line)

    output_lines.append(f"\n\n---\n")
    output_lines.append(f"*{brand_name} · {brand_product}*\n")

    final_md = "\n".join(output_lines)

    print(f"\n📄 Markdown 已生成（见下方）")
    print(f"\n{'='*50}")
    print(final_md)
    print(f"{'='*50}")

    # 输出图片清单
    if images_found:
        print(f"\n📷 本次找到的图片（共 {len(images_found)} 张）：")
        for i, img in enumerate(images_found, 1):
            print(f"   {i}. {img}")
        print(f"\n💡 在编辑器中按序号替换对应位置的图片即可")

    print(f"\n✅ 完成！复制上方 Markdown 内容，粘贴到编辑器（如 https://md.doocs.org/）发布")
    print(f"{'='*50}\n")


def main():
    # 先选择发布方式
    mode = select_mode()

    print(f"\n{'='*50}")
    print(f"  chatwx-fwh 公众号发布脚本 v8")
    print(f"{'='*50}")

    article_file = config["article"]["file"]
    if not article_file:
        print("[ERROR] article.file 未设置，请修改 config.yaml")
        sys.exit(1)
    if not os.path.exists(article_file):
        print(f"[ERROR] File not found: {article_file}")
        print("[ERROR] 请确认 article.file 路径正确")
        sys.exit(1)

    image_dirs = config["image_dirs"]
    title = config["article"]["title"]
    filename = os.path.basename(article_file)

    # 手动模式：导出 Markdown
    if mode == "B":
        export_to_markdown(
            article_file,
            image_dirs,
            title,
            BRAND_NAME,
            BRAND_PRODUCT
        )
        sys.exit(0)

    print(f"\nArticle : {filename}")
    print(f"Title   : {title}")
    print(f"Theme   : {THEME['name']} ({GREEN})")
    print(f"Brand   : {BRAND_NAME} · {BRAND_PRODUCT}")

    with open(article_file, "r", encoding="utf-8") as f:
        md_content = f.read()

    if seo_enabled:
        seo = generate_seo_meta(md_content)
        print(f"\n[SEO] {seo['description'][:60]}...")
        print(f"[SEO] Keywords: {', '.join(seo['keywords'][:5])}")

    print(f"\nConnecting to WeChat...")
    publisher = WeChatPublisher(config["wechat"]["appid"], config["wechat"]["secret"])

    # 找封面图
    cover_image = None
    for d in image_dirs:
        if not os.path.exists(d):
            continue
        for cname in ["cover.jpg", "cover.jpeg", "cover.png", "封面.jpg", "封面.jpeg"]:
            path = os.path.join(d, cname)
            if os.path.exists(path):
                cover_image = path
                break
        if cover_image:
            break
        if not cover_image:
            for f in list(Path(d).glob("*.jpg")) + list(Path(d).glob("*.jpeg")) + list(Path(d).glob("*.png")):
                cover_image = str(f)
                break
        if cover_image:
            break

    if not cover_image:
        print("[ERR] No cover image found.")
        print(f"[INFO] 请在以下目录放置封面图（cover.jpg）：")
        for d in image_dirs:
            print(f"       - {d}")
        sys.exit(1)

    print(f"\nCover  : {os.path.basename(cover_image)}")
    print("Uploading cover...")
    thumb_media_id = publisher.upload_image_for_thumb(cover_image)
    if not thumb_media_id:
        print("[ERR] Cover upload failed")
        sys.exit(1)

    print("\nConverting Markdown -> HTML...")
    html_content = markdown_to_html(md_content, image_dirs, publisher)

    print("Creating draft...")
    media_id = publisher.create_draft(title, html_content, thumb_media_id)

    if media_id:
        print(f"\n{'='*50}")
        print(f"  ✅ DONE — 草稿已创建")
        print(f"  登录公众号后台 → 草稿箱 → 审核发布")
        print(f"{'='*50}")
    else:
        print(f"\n{'='*50}")
        print(f"  ❌ 发布失败")
        print(f"")
        print(f"  💡 兜底方案：Markdown 编辑器手动发布")
        print(f"     1. 复制 Markdown 文件内容，粘贴到编辑器（如 https://md.doocs.org/）")
        print(f"     2. 配图从以下目录选取：")
        for d in image_dirs:
            if os.path.exists(d):
                print(f"        - {d}")
        print(f"     3. 修改标题后发布")
        print(f"")
        print(f"  💡 永久解决：添加IP白名单")
        print(f"     公众号后台 → 设置与开发 → 基本配置 → IP白名单")
        print(f"     当前IP：https://myip.ipip.net")
        print(f"{'='*50}")


if __name__ == "__main__":
    main()
