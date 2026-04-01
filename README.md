# chatwx-fwh · AI 写公众号 · 一键发草稿箱

> 告诉 AI 你卖什么，它帮你写完整文章，再一键发到公众号草稿箱。
>
> 支持**任何品牌/品类**。4 步配置，无需写代码。

[![GitHub stars](https://img.shields.io/github/stars/wdgdd/chatwx-fwh-community?style=flat-square)](https://github.com/wdgdd/chatwx-fwh-community)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

---

## 核心功能

| 功能 | 说明 |
|------|------|
| 🤖 **AI 帮写** | 告诉 AI 品牌+产品，它帮你定选题、写全文、配图方案 |
| ✅ **合规自检** | 写完自动 6 项检查（数据/措辞/同行对比等） |
| 🎨 **6 套排版主题** | 简约/居中/温暖/绿色/装饰/大标题，一键切换 |
| 📤 **一键发草稿箱** | 配置 AppID/Secret 后，一行命令自动发布 |
| 📋 **导出 Markdown** | 不配 API 也能用，导出后粘贴到任意编辑器发布 |

---

## 快速开始

### 第一步：下载

```powershell
git clone https://github.com/wdgdd/chatwx-fwh-community.git
# 或到 GitHub 页面下载 zip
```

### 第二步：放到技能目录（WorkBuddy 用户）

如果你使用 [WorkBuddy](https://www.codebuddy.cn)，把下载好的所有文件放到技能目录：

- **Linux / Mac**：`~/.workbuddy/skills/chatwx-fwh/`
- **Windows**：`C:\Users\你的用户名\.workbuddy\skills\chatwx-fwh\`

> 如果目录不存在，手动创建即可。非 WorkBuddy 用户可跳过此步，把文件放任意位置即可。

### 第三步：填 4 项配置

```powershell
# 进入脚本所在目录（根据你实际放置的位置）
python wechat_publish.py --setup
```

回答 4 个问题：
- 品牌名称（如：`瑞幸咖啡`）
- 产品名称（如：`生椰拿铁`）
- AppID（公众号后台 → 基本配置）
- AppSecret（同上页面，点「重置」）

### 第四步：让 AI 写文章

在支持 AI 技能的助手（如 WorkBuddy）中说：

```
帮我写一篇公众号文章，品牌是瑞幸咖啡，产品是生椰拿铁
```

AI 全程搞定：选题 → 写全文 → 合规自检 → 排版。

### 第五步：发布

```powershell
python wechat_publish.py
```

选 **A** → 一键发到草稿箱

或选 **B** → 导出 Markdown → 复制到任意编辑器发布

---

## 不想配 API？用 Markdown 方式

不需要 AppID/Secret：

```powershell
python wechat_publish.py
# 选 B → 导出 Markdown
```

然后：
1. 打开任意 Markdown 编辑器（如 [🔗 https://md.doocs.org/](https://md.doocs.org/)）
2. 粘贴 Markdown 内容
3. 按图片序号替换图片
4. 复制全文 → 公众号后台粘贴发布

---

## 常见问题

**报错「access_token failed」** → AppID 或 AppSecret 填错了，重新复制。

**报错「IP白名单」（errcode 40164）** → 公众号后台 → 基本配置 → IP白名单 → 添加你的 IP（查 IP：https://myip.ipip.net）

**想用手动方式发** → 选 B 导出 Markdown，用任意编辑器粘贴发布。

---

## 文件结构

```
chatwx-fwh/
├── config.yaml           ← 只需改这里（4项必填）
├── wechat_publish.py     ← 发布脚本，直接运行
├── themes.yaml           ← 6套排版主题
└── articles/             ← 把你的文章放这里
```

> 📌 WorkBuddy 用户：文件放到 `~/.workbuddy/skills/chatwx-fwh/` 即可被自动识别。其他用户把文件放任意位置，手动运行 `python wechat_publish.py` 即可。
