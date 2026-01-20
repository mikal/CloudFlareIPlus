#!/usr/bin/env python3

def group_channels_by_name(input_file, output_file, start_line=262):
    """Group channels with same names together from specified line"""
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Keep lines before start_line unchanged
    before_lines = []
    channels_to_group = []
    
    line_count = 0
    i = 0
    
    # Count actual content lines (skip empty lines and comments that aren't EXTINF)
    while i < len(lines):
        line = lines[i].strip()
        if line.startswith('#EXTINF:'):
            line_count += 1
            if line_count < (start_line // 2):  # Each channel = 2 lines
                before_lines.append(lines[i])
                if i + 1 < len(lines):
                    before_lines.append(lines[i + 1])
                    i += 2
                else:
                    i += 1
            else:
                # Collect channels to group
                extinf_line = lines[i]
                if i + 1 < len(lines):
                    url_line = lines[i + 1]
                    # Extract channel name
                    if ',' in extinf_line:
                        channel_name = extinf_line.split(',')[-1].strip()
                        channels_to_group.append((channel_name, extinf_line, url_line))
                    i += 2
                else:
                    i += 1
        elif line.startswith('#') or not line:
            if line_count < (start_line // 2):
                before_lines.append(lines[i])
            i += 1
        else:
            if line_count < (start_line // 2):
                before_lines.append(lines[i])
            i += 1
    
    # Group channels by name
    name_groups = {}
    for name, extinf, url in channels_to_group:
        if name not in name_groups:
            name_groups[name] = []
        name_groups[name].append((extinf, url))
    
    # Write output file
    with open(output_file, 'w', encoding='utf-8') as f:
        # Write lines before grouping point
        for line in before_lines:
            f.write(line)
        
        # Write grouped channels
        for name in sorted(name_groups.keys()):
            for extinf, url in name_groups[name]:
                f.write(extinf)
                f.write(url)
    
    # Count groups
    grouped_count = sum(len(channels) for channels in name_groups.values() if len(channels) > 1)
    single_count = sum(1 for channels in name_groups.values() if len(channels) == 1)
    
    return len(name_groups), grouped_count, single_count

def main():
    input_file = '/home/mike/iptv/SHIPTV2026-10.m3u'
    output_file = '/home/mike/iptv/SHIPTV2026-11.m3u'
    
    total_groups, grouped_channels, single_channels = group_channels_by_name(input_file, output_file)
    
    print(f"已处理完成，保存为: {output_file}")
    print(f"从第262行开始重新排列")
    print(f"共 {total_groups} 个不同的频道名")
    print(f"其中 {grouped_channels} 个频道有相同名字被分组")
    print(f"另有 {single_channels} 个频道名字唯一")

if __name__ == "__main__":
    main()
