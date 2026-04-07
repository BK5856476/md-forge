import os
import re
import urllib.request
import urllib.parse
import ssl

# 忽略 SSL 证书验证，避免因证书问题导致无法下载 HTTPS 链接的图片
ssl._create_default_https_context = ssl._create_unverified_context

# 获取当前脚本的运行目录作为基础路径
base_dir = os.path.dirname(os.path.abspath(__file__))

# 定义两个主要文件夹路径
processing_dir = os.path.join(base_dir, "Clippings")
assets_dir = os.path.join(processing_dir, "assets")

# 如果 `Clippings` 或 `assets` 目录不存在，则自动建立
os.makedirs(processing_dir, exist_ok=True)
os.makedirs(assets_dir, exist_ok=True)

# 编译正则表达式，用于匹配 markdown 和 html 语法的图片链接
md_pattern = re.compile(r'!\[.*?\]\((.*?)\)')
html_pattern = re.compile(r'<img\s+[^>]*src="([^"]+)"')

processed_count = 0

print("🚀 开始扫描并处理文档...\n")

# 获取目前 Clippings 里有效的 MD 文件所对应的干净名字列表
active_md_names = []
for filename in os.listdir(processing_dir):
    if filename.lower().endswith('.md'):
        active_md_names.append(os.path.splitext(filename)[0])

import shutil
deleted_count = 0
# 检查 assets 文件夹，寻找孤儿资源目录并删除
for asset_folder in os.listdir(assets_dir):
    folder_path = os.path.join(assets_dir, asset_folder)
    # 只处理文件夹
    if os.path.isdir(folder_path):
        # 如果这个文件夹的名字不在当前的 MD 文件名列表里，就果断删掉整个文件夹
        if asset_folder not in active_md_names:
            try:
                shutil.rmtree(folder_path)
                print(f"🗑️ 发现多余资源文件夹，已删除: assets/{asset_folder}")
                deleted_count += 1
            except Exception as e:
                print(f"⚠️ 删除文件夹 assets/{asset_folder} 失败: {e}")

if deleted_count > 0:
    print(f"\n✅ 自动清理完毕，共删除了 {deleted_count} 个无效的独立资源文件夹。\n")

# 遍历 `Clippings` 下的所有文件
for filename in os.listdir(processing_dir):
    if filename.lower().endswith('.md'):
        md_path = os.path.join(processing_dir, filename)
        
        # 剥离 .md 后缀，作为将要匹配创建的资源文件夹名字
        folder_name = os.path.splitext(filename)[0]
        target_folder = os.path.join(assets_dir, folder_name)
        
        # 在 assets 里面创建相同名字的文件夹
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
            print(f"📁 已创建对应资源文件夹: assets/{folder_name}")
            
        print(f"📄 正在解析: {filename}")
        
        # 读取此 Markdown 文档源码
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # 寻找该文档里的所有图片链接
        urls = md_pattern.findall(content) + html_pattern.findall(content)
        
        # 先去重
        unique_urls = list(set(urls))
        # 挑选出网络图片和本地图片
        valid_urls = [u for u in unique_urls if u.startswith('http')]
        local_urls = [u for u in unique_urls if not u.startswith('http') and not u.startswith('data:')]
        
        if not valid_urls and not local_urls:
            print("   -> 没有在这个文档里发现新的网络或本地图片链接。\n")
            continue
            
        print(f"   -> 共找出 {len(valid_urls)} 个网络链接，{len(local_urls)} 个本地链接。")
        new_content = content
        download_success = 0
        local_success = 0
        
        # 循环处理本地图片
        for url in local_urls:
            try:
                # 解析 URL 编码的相对路径（例如含空格）
                real_rel_path = urllib.parse.unquote(url)
                # 兼容不同操作系统的路径分隔符
                real_rel_path = real_rel_path.replace('\\', '/')
                
                # 若使用了相对 assets 的旧地址，也需判定，避免重复拷贝
                if real_rel_path.startswith(f"assets/{folder_name}/"):
                    continue
                    
                src_filepath = os.path.join(processing_dir, real_rel_path)
                
                # 检查是否存在
                if os.path.exists(src_filepath) and os.path.isfile(src_filepath):
                    img_filename = os.path.basename(src_filepath)
                    dst_filepath = os.path.join(target_folder, img_filename)
                    
                    if os.path.abspath(src_filepath) != os.path.abspath(dst_filepath):
                        # 同名冲突处理
                        counter = 1
                        base_name, ext = os.path.splitext(img_filename)
                        while os.path.exists(dst_filepath):
                            dst_filepath = os.path.join(target_folder, f"{base_name}_{counter}{ext}")
                            counter += 1
                        
                        shutil.copy2(src_filepath, dst_filepath)
                        
                    file_just_name = os.path.basename(dst_filepath)
                    print(f"      📂 [本地OK] {file_just_name}")
                    local_success += 1
                    
                    # 更新文档路径
                    rel_path = f"assets/{folder_name}/{file_just_name}"
                    encoded_rel_path = rel_path.replace(" ", "%20")
                    new_content = new_content.replace(url, encoded_rel_path)
            except Exception as e:
                print(f"      ❌ [本地失败] url: {url} -> 错误: {e}")
                
        # 循环下载网络图片
        for i, url in enumerate(valid_urls, 1):
            try:
                # 伪装请求头以防防盗链
                req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
                parsed = urllib.parse.urlparse(url)
                img_filename = os.path.basename(parsed.path)
                
                # 用户常遇到没有后缀、带 '@' 拓展参数等链接问题处理
                if not img_filename:
                    img_filename = f"image_{i}.png"
                if '@' in img_filename:
                    img_filename = img_filename.split('@')[0]
                    
                if not img_filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp', '.avif')):
                    if '.png' in img_filename:
                        img_filename = img_filename.split('.png')[0] + '.png'
                    elif '.jpg' in img_filename:
                        img_filename = img_filename.split('.jpg')[0] + '.jpg'
                    else:
                        img_filename += ".png"
                
                # 拼接图片将要保存在当前文档专属目录下的绝对路径
                filepath = os.path.join(target_folder, img_filename)
                
                # 同名判定：防止同一个链接生成的极简文件名在同文件夹内冲突
                counter = 1
                base_name, ext = os.path.splitext(img_filename)
                while os.path.exists(filepath):
                    filepath = os.path.join(target_folder, f"{base_name}_{counter}{ext}")
                    counter += 1
                
                # 真正下载图片
                with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
                    out_file.write(response.read())
                
                file_just_name = os.path.basename(filepath)
                print(f"      📥 [OK] {file_just_name}")
                download_success += 1
                
                # 更新文档里的图片链接。这里使用了兼容常规 markdown 软连的相对路径 
                # 因为文档在 Clippings 里，图片在 Clippings/assets/对应同名文件夹/里，
                # 所以相对路径变成了同级子目录：assets/文件夹名/图片名.png
                rel_path = f"assets/{folder_name}/{file_just_name}"
                # 仅将空格替换为 %20，以避免 Markdown 图片无法识别的问题
                encoded_rel_path = rel_path.replace(" ", "%20")
                new_content = new_content.replace(url, encoded_rel_path)
                
            except Exception as e:
                print(f"      ❌ [失败] url: {url} -> 错误: {e}")

        # 如果内容由于替换链接发生了改变，那么覆盖这篇原文档修改结果
        if content != new_content:
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"   ✨ 文档图片链接替换完毕！\n")
            
        processed_count += 1

print("\n🧹 开始清理原始本地图片和空文件夹...")
deleted_local_count = 0
image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.webp', '.avif', '.bmp', '.svg', '.tif', '.tiff'}

for root, dirs, files in os.walk(processing_dir, topdown=False):
    # 跳过 assets 目录
    if os.path.abspath(root) == os.path.abspath(assets_dir) or \
       os.path.commonpath([os.path.abspath(root), os.path.abspath(assets_dir)]) == os.path.abspath(assets_dir):
        continue
        
    for file in files:
        ext = os.path.splitext(file)[1].lower()
        if ext in image_extensions:
            file_path = os.path.join(root, file)
            try:
                os.remove(file_path)
                deleted_local_count += 1
            except Exception as e:
                print(f"⚠️ 删除本地图片失败 {file_path}: {e}")
                
    # 如果文件夹为空，且不是处理总目录，则删除
    if root != processing_dir and not os.listdir(root):
        try:
            os.rmdir(root)
        except Exception as e:
            pass
            
if deleted_local_count > 0:
    print(f"✅ 成功清理了 {deleted_local_count} 个原始/无用的本地图片（已被转移或未被引用）。\n")
    
print(f"🎉 运行结束！累计处理完成 {processed_count} 篇 MD 文档。")
