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

我会帮你：
1. 确认选题和场景
2. 写完整文章（含配图标注）
3. 生成排版好的 Markdown

你复制到 WeMark 粘贴，按提示替换图片即可。

---

### ② 你有写好的 .md 文件

运行：
```powershell
cd C:\Users\你的用户名\.workbuddy\skills\chatwx-fwh\
python wechat_publish.py
```
选 **B** → 导出 Markdown → 复制到 WeMark

---

### ③ 一键自动发布到草稿箱

需要先配置（回答4个问题）：
```powershell
python wechat_publish.py --setup
```

然后运行：
```powershell
python wechat_publish.py
```
选 **A** → 自动发布到草稿箱

---

## 3步上手

### 第一步：填4项必填（不想手动填？用上面的 --setup 引导）

用记事本打开 `config.yaml`，找到以下4项并填写：

| 配置项 | 怎么填 | 示例 |
|--------|--------|------|
| `brand.name` | 你的品牌名 | `瑞幸咖啡` |
| `brand.product` | 你的产品名 | `生椰拿铁` |
| `wechat.appid` | 见下方获取教程 | `wx1234567890abcdef` |
| `wechat.secret` | 见下方获取教程 | `a1b2c3d4e5f6g7h8i9j0` |

---

#### 🔑 AppID 和 AppSecret 怎么找？

1. 打开微信公众平台：**https://mp.weixin.qq.com**
2. 登录你的公众号
3. 点击左侧菜单 **「设置与开发」** → **「基本配置」**
4. 找到 **「AppID」** 和 **「AppSecret」**（AppSecret 需要点「重置」并验证管理员微信）
5. 复制粘贴到 config.yaml 对应位置

---

### 第二步：选择发布方式

运行脚本时会让你选择：

```
请选择发布方式：

  A. 自动发布到草稿箱
     需要配置 AppID/Secret，一键发布到公众号草稿箱

  B. 导出 Markdown（手动复制到 WeMark）
     不需要配置 API，直接生成排版好的 Markdown
     你复制到 WeMark 后手动替换图片
```

---

### 第三步：去公众号后台发布

**方式A（自动）**：登录草稿箱，修改标题后发布。

**方式B（手动）**：复制生成的 Markdown → 打开 [WeMark](https://www.we-mark.com) → 粘贴 → 按图片序号替换图片 → 发布。

---

## 常见问题

### ❌ 报错「IP白名单」（errcode 40164）
当前电脑的IP不在公众号后台白名单里：
- **临时方案**：用 WeMark 手动发（功能一样）
- **永久方案**：
  1. 打开 https://myip.ipip.net 看你的IP
  2. 公众号后台 → 设置与开发 → 基本配置 → IP白名单 → 添加IP

---

## 目录结构

```
chatwx-fwh/
├── config.yaml           ← ⚠️ 只需改这里（4项必填）
├── wechat_publish.py     ← 发布脚本，直接运行
├── themes.yaml           ← 排版主题（不用改）
├── README.md             ← 你在这里
└── articles/
    └── 01-example.md     ← 把你的文章放这里
```
