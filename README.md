# 📚 ArXiv 论文爬虫

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

一个专门用于抓取 arXiv 上最新扩散模型(Diffusion Models)和图像/视频生成相关论文的爬虫程序。支持 Windows 和 Linux 系统,提供多种下载加速方案。

## ✨ 特性

- 🔍 智能搜索和过滤相关论文
- 📥 支持多线程并行下载
- 🚀 Windows 下使用 IDM 加速下载
- 🚄 Linux 下使用 aria2 加速下载
- 📂 自动整理论文到日期文件夹
- 📝 生成带摘要的 Markdown 文档
- 🔄 支持断点续传和自动重试

## 🛠️ 安装

### 基础依赖
```bash
pip install -r requirements.txt
```

### Windows 用户
1. 安装 [Internet Download Manager (IDM)](https://www.internetdownloadmanager.com/)
2. 确保 IDM 已添加到系统环境变量

### Linux 用户
```bash
# Ubuntu/Debian
sudo apt install aria2

# CentOS/RHEL
sudo yum install aria2

# Arch Linux
sudo pacman -S aria2
```

## 🚀 使用方法

### Windows
```bash
# 基本使用
python arxiv_crawler_windows.py

# 自定义参数
python arxiv_crawler_windows.py --days 14 --dir "D:/papers" --workers 5
```

### Linux
```bash
# 基本使用
python arxiv_crawler_linux.py

# 自定义参数
python arxiv_crawler_linux.py --days 14 --dir "~/papers" --workers 5
```

## ⚙️ 参数说明

| 参数 | 说明 | 默认值 | 示例 |
|------|------|--------|------|
| `--days` | 向前查找的天数 | 14 | `--days 30` |
| `--dir` | 保存目录 | Windows: D:/papers<br>Linux: ~/papers | `--dir "E:/Research/Papers"` |
| `--workers` | 并行下载线程数 | 5 | `--workers 8` |

## 📁 目录结构

```
save_dir/
├── pdfs/           # PDF文件
│   └── YYYY-MM-DD/ # 按发布日期分类
├── info/           # 论文元数据(JSON)
│   └── YYYY-MM-DD/
└── markdown/       # 生成的markdown文档
```

## 🔍 搜索范围

### 主要关键词 (必须包含其中之一)
- diffusion model
- score based
- generative model

### 次要关键词 (可选)
- image generation
- text to image
- video generation
- 3d generation

### 学科分类
- cs.CV (计算机视觉)
- cs.LG (机器学习)
- cs.AI (人工智能)

## 📝 输出示例

### JSON 元数据
```json
{
  "id": "2412.12345",
  "title": "Paper Title",
  "authors": ["Author 1", "Author 2"],
  "abstract": "Paper abstract...",
  "categories": ["cs.CV", "cs.LG"],
  "pdf_url": "https://arxiv.org/pdf/2412.12345.pdf",
  "published": "2024-12-20",
  "updated": "2024-12-22"
}
```

### Markdown 文档
- 按日期分组的论文列表
- 包含标题、作者、链接
- 完整摘要和分类信息
- 下载统计和时间范围

## ⚠️ 注意事项

### Windows 用户
- 确保 IDM 正确安装并可以通过命令行调用
- 如果 IDM 下载失败会自动切换到普通下载
- 建议在系统代理或 VPN 环境下运行

### Linux 用户
- 确保已正确安装 aria2
- 可以通过配置 aria2 参数优化下载速度
- 如果下载速度慢,建议配置代理

### 通用建议
- 确保网络连接稳定
- 确保有足够的磁盘空间
- 确保目标目录具有写入权限
- 网络不稳定时建议减少并行数

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🤝 贡献

欢迎提交 Issue 和 Pull Request!

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交改动 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request
