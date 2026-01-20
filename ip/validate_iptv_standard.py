#!/usr/bin/env python3
import re
import urllib.parse

def validate_iptv_standard():
    errors = []
    warnings = []
    
    with open('./SHIPTV2026-7.m3u', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Check M3U header
    if not lines[0].strip().startswith('#EXTM3U'):
        errors.append("缺少必需的 #EXTM3U 头部")
    
    entry_count = 0
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith('#EXTINF:'):
            entry_count += 1
            
            # Check EXTINF format
            if not re.match(r'^#EXTINF:-?\d+', line):
                errors.append(f"行 {i+1}: EXTINF格式错误，应为 #EXTINF:duration")
            
            # Check required attributes
            if 'tvg-name=' not in line:
                warnings.append(f"行 {i+1}: 缺少 tvg-name 属性")
            
            if 'group-title=' not in line:
                warnings.append(f"行 {i+1}: 缺少 group-title 属性")
            
            # Check channel name at end
            if ',' not in line:
                errors.append(f"行 {i+1}: 缺少频道名称（逗号后的内容）")
            
            # Check next line (URL)
            if i + 1 >= len(lines):
                errors.append(f"行 {i+1}: EXTINF后缺少URL")
            else:
                url_line = lines[i + 1].strip()
                if not url_line:
                    errors.append(f"行 {i+2}: URL为空")
                elif not (url_line.startswith('http://') or url_line.startswith('https://') or url_line.startswith('udp://') or url_line.startswith('rtmp://')):
                    warnings.append(f"行 {i+2}: URL格式可能不标准: {url_line[:50]}...")
            
            i += 2
        elif line.startswith('#'):
            # Comment line - skip
            i += 1
        elif line == '':
            # Empty line - skip
            i += 1
        else:
            # Non-empty, non-comment, non-EXTINF line
            if not (line.startswith('http://') or line.startswith('https://') or line.startswith('udp://') or line.startswith('rtmp://')):
                warnings.append(f"行 {i+1}: 未知内容: {line[:50]}...")
            i += 1
    
    print("=== IPTV播放列表规范检查 ===")
    print(f"文件: SHIPTV2026-7.m3u")
    print(f"总行数: {len(lines)}")
    print(f"频道条目数: {entry_count}")
    
    if errors:
        print(f"\n❌ 发现 {len(errors)} 个错误:")
        for error in errors[:10]:
            print(f"  {error}")
        if len(errors) > 10:
            print(f"  ... 还有 {len(errors) - 10} 个错误")
    else:
        print("\n✅ 未发现格式错误")
    
    if warnings:
        print(f"\n⚠️  发现 {len(warnings)} 个警告:")
        for warning in warnings[:10]:
            print(f"  {warning}")
        if len(warnings) > 10:
            print(f"  ... 还有 {len(warnings) - 10} 个警告")
    else:
        print("\n✅ 未发现格式警告")
    
    # Overall compliance
    if not errors and len(warnings) <= 5:
        print("\n🎉 文件符合IPTV播放列表规范")
    elif not errors:
        print("\n✅ 文件基本符合IPTV播放列表规范（有少量警告）")
    else:
        print("\n❌ 文件不符合IPTV播放列表规范")
    
    return len(errors) == 0

if __name__ == "__main__":
    validate_iptv_standard()
