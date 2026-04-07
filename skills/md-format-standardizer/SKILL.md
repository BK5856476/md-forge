---
name: "MarkdownFormatStandardizer"
description: "Markdown 格式自动化规整工具，支持清理多余空行、修复标点符号及优化文档布局。"
---

# MarkdownFormatStandardizer 技能说明

本技能旨在将非标准或格式混乱的 Markdown 文档调整为符合规范的统一样式。

## 核心功能
1. **空行清理**：自动压缩文档中连续出现的三个或以上空行为两个。
2. **符号修复**：支持正则匹配并修复常见的排版错误（待后续扩展）。
3. **全局应用**：基于仓库根目录的 `Clippings/` 全局共享区，一次处理所有待归档文档。

## 目录规范
- **根目录下 /Clippings/**: 全局共享输入区，存放待处理的 `.md` 文档。
- **scripts/**: 包含核心处理逻辑 `standardize.py`。

## 如何运行
// turbo
- **自动化运行**：执行 `python scripts/standardize.py`。
- **手动双击**：运行本目录下的 `process_format.bat`。

## 注意事项
- 由于涉及到直接修改源文件，建议在执行前对 `Clippings/` 目录进行备份。
- 此技能执行后，可以配合 `md-image-forge` 进行后续的图像归档工作。
