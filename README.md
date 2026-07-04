# 轻松文件整理助手 — Easy File Organizer

> Windows 桌面文件批量操作工具 — 批量改名、分类整理、清理查重、数据导出，一站式解决文件混乱问题。

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

## 功能特性

| 功能 | 说明 |
|------|------|
| 批量改名 | 前缀文本 / 日期标记 / 编号排序 / 保留原名，支持预览 |
| 分类整理 | 按文件类型或修改日期自动归类到文件夹 |
| 文件操作 | 批量移动、批量复制、一键 ZIP 备份 |
| 清理查重 | MD5 去重（保留最新）/ 清理空文件夹 / 清理冗余文件 |
| 数据导出 | TXT 目录清单 / Excel 表格导出 |

## 免费版 vs Pro 版

| 功能 | 免费版 | Pro 版 |
|------|:------:|:------:|
| 批量改名 | ✅ | ✅ |
| 分类整理 | ✅ | ✅ |
| 文件操作（移动/复制） | ✅ | ✅ |
| TXT 导出 | ✅ | ✅ |
| Excel 导出 | ❌ | ✅ |
| MD5 去重 | ❌ | ✅ |
| ZIP 备份 | ❌ | ✅ |
| 撤销系统（5步） | ❌ | ✅ |

> 免费版已覆盖核心文件整理需求。Pro 版提供更高阶的批量能力。
> 
> **获取 Pro 版：** [Gumroad](https://) · [闲鱼](https://)

## 快速开始

```bash
# 克隆仓库
git clone https://github.com/MRQC-st/easy-file-organizer.git
cd easy-file-organizer

# 安装依赖
pip install -r requirements.txt

# 启动
python main.py
```

## 打包为 EXE

```bash
pip install pyinstaller
pyinstaller --onefile --windowed main.py
```

打包后的 `dist/main.exe` 可直接在 Windows 上运行，无需 Python 环境。

## 系统要求

- Windows 10 / 11
- Python 3.8+（源码运行）
- 无其他特殊要求

## 免责声明

> 本工具执行批量文件操作，操作前请备份重要文件。批量操作具有不可逆性，建议先使用预览功能确认后再执行。使用本软件产生的任何数据丢失或损坏，开发者不承担责任。

## License

MIT © 2026 MRQC-st
