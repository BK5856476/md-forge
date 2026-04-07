import os
import re
import subprocess
import sys

# 依赖检查：确保 emoji 库已安装
try:
    import emoji
except ImportError:
    print("正在安装必要依赖: emoji...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "emoji", "-q"])
    import emoji

def process_content(content):
    """
    核心格式规整引擎：依次执行 7 项自动化规则。
    """
    # 1. 优先扫描并删除开头的“Clippings 字典元数据块”
    # 逻辑：匹配文件开头可能存在的 ---，接着匹配包含 title:, source:, author:, tags: 等关键词的块，直到 tags 后的内容结束
    content = re.sub(r'(?s)^---?\s*title:.*?tags:.*?\n\s*---?\n?', '', content, count=1)
    
    # 2. 接着删除文中其余所有独立的 --- 分隔符行
    # 只要一行里只有 ---（允许前后有空格），就把整行及其换行符删除
    content = re.sub(r'(?m)^\s*-{3,}\s*$\n?', '', content)
    
    # 3. 提取末尾剪藏信息中的作者并删除这整个冗余尾巴
    author_name = ""
    # 匹配模式：查找以 "> 作者：" 开头的行，支持 [姓名](链接) 或 纯姓名 格式
    m_author = re.search(r'(?m)^>\s*作者：\s*(?:\[([^\]]+)\]|([^\n]+))', content)
    if m_author:
        author_name = (m_author.group(1) or m_author.group(2)).strip()
        
    # 删除剪藏工具附带的引用块（通常包含 Thoughts Memo 标识、原作者声明或发布于信息）
    content = re.sub(r'(?s)\n(>\s*\[?Thoughts Memo.*)$', '', content)  # 删去 Thoughts Memo 起始直到最后的整个块
    content = re.sub(r'(?s)\n+(>\s*(?:原)?作者：.*)$', '', content)     # 或者任何包含作者开始的末尾块
    content = re.sub(r'(?s)\n+(发布于[^\n]*)$', '', content)           # 删去“发布于 XX”这一整行
    # 3.x 删除以 '编辑于' 开头的尾部块（包括后面的链接说明）
    # 匹配从 '编辑于' 开始到下一个空行或文件结束的所有内容
    content = re.sub(r'(?s)编辑于\s*\d{4}-\d{2}-\d{2}\s*\d{2}:\d{2}.*?(?:\n\s*\n|$)', '', content)
    # 3.x 删除包含 '链接：'、'提取码：' 以及后续方括号链接块的尾部内容
    # 匹配从 '链接：' 开始到对应的 Markdown 链接结束的所有内容
    content = re.sub(
        r'(?s)链接：\s*.*?提取码：\s*.*?\[\s*.*?\s*\]\(\s*https?://[^)]+\s*\)',
        '',
        content
    )


    # 将提取出的干净作者名重新补充到文末
    if author_name:
        content = content.strip() + f"\n\n作者：{author_name}\n"

    # 4. 去除外部链接的 Markdown 格式，只保留方括号里的可见文字（跳过图片链接）
    # 目的：将 [pan.baidu.com/s/1deK5w_](https://...) 这种杂乱链接简化为可见文本，保留 ![...](...) 的图片链接
    content = re.sub(r'(?<!\!)\[(.*?)\]\((https?://[^)]+)\)', r'\1', content)
    
    # 5. 修复代码块的语言标签
    # 逻辑：将孤立在代码块上方一行的语言标识（如 Python）自动合并到紧随其后的 ``` 后
    content = re.sub(
        r'(?im)^([a-z0-9+#-]+)\s*\n+```\s*$', 
        lambda m: f"```{m.group(1).lower()}", 
        content
    )

    # 6. 使用专业库移除所有表情符号 (Emojis)
    # 利用 emoji 库进行深度扫描，确保不遗留任何 Unicode 表情符号
    content = emoji.replace_emoji(content, replace='')

    # 7. 列表紧凑化处理
    # 规则：如果两个连续的列表项（以 -/1. 等开头）之间有空行，则删除该空行以保持紧凑
    content = re.sub(r'(?m)^([ \t]*([-*+]|\d+\.)\s+.*)\n+[ \t]*\n(?=[ \t]*([-*+]|\d+\.)\s+)', r'\1\n', content)

    return content.strip() + "\n"

def main():
    # 获取全局仓库根目录 (向上回退 3 级：scripts -> md-format-standardizer -> skills -> repo_root)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    skill_root = os.path.dirname(script_dir)
    skills_dir = os.path.dirname(skill_root)
    base_dir = os.path.dirname(skills_dir)

    # 定义处理目录 (共享工作区 Clippings 位于仓库根目录)
    processing_dir = os.path.join(base_dir, "Clippings")

    if not os.path.exists(processing_dir):
        print(f"❌ 错误：未找到全局工作区目录 {processing_dir}")
        return

    print("🚀 开始执行 Markdown 格式规整 (全局共享模式)...")
    print(f"📂 正在扫描目录: {processing_dir}\n")

    processed_count = 0
    change_count = 0

    # 遍历 Clippings/ 目录下的所有 .md 文件
    for filename in os.listdir(processing_dir):
        if filename.lower().endswith(".md"):
            file_path = os.path.join(processing_dir, filename)
            print(f"📄 正在检查: {filename}")

            with open(file_path, "r", encoding="utf-8") as f:
                original_content = f.read()

            # 调用处理引擎执行规整操作
            new_content = process_content(original_content)

            # 如果内容发生了变化，则执行写回
            if new_content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                print(f"   ✨ 格式已优化！")
                change_count += 1
            
            processed_count += 1

    print(f"\n🎉 处理完毕！扫描了 {processed_count} 个文件，其中 {change_count} 个已更新格式。")

if __name__ == "__main__":
    main()
