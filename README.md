# chatwx-fwh · 公众号发布工具（通用社区版）

> 小白也能用。支持任何品牌/品类。以下示例仅供参考：
> - 示例品牌：瑞幸咖啡、生椰拿铁、旺旺大礼包……
> - **方式一**：让我帮你写文章 → 导出 Markdown → 复制到 WeMark
> - **方式二**：一键自动发布到草稿箱（需要配 API）

---

## 🚀 三种用法

### ① 让我帮你写文章（最简单）

直接说：
```
"帮我写一篇关于XX的公众号文章，品牌是瑞幸咖啡，产品是生椰拿铁"
```

---

### ② 你有写好的 .md 文件

```powershell
cd ~/.workbuddy/skills/chatwx-fwh/
python wechat_publish.py
```
选 **B** → 导出 Markdown → 复制到 WeMark

---

### ③ 一键自动发布到草稿箱

```powershell
python wechat_publish.py --setup  # 首次配置
python wechat_publish.py          # 选 A 自动发布
```

---

## 4步上手

1. 安装到技能目录：`~/.workbuddy/skills/chatwx-fwh/`
2. 填4项必填（`brand.name`、`brand.product`、`wechat.appid`、`wechat.secret`）
3. 把文章放到 `articles/` 目录
4. 运行 `python wechat_publish.py`

---

## 常见问题

**报错「access_token failed」**：AppID 或 AppSecret 填错了。

**报错「IP白名单」**：公众号后台 → 基本配置 → IP白名单 → 添加你的IP。
