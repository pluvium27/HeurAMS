#!/usr/bin/env python3
"""
将符合条件的CSV转为符合Payload需要的TOML格式

使用命令: python3 csv2payload.py <CSV路径> <生成TOML路径, 默认为文件名相同, 后缀为toml的TOML文件>


转换规则:
1. `ident` 列用作 TOML 的 section 标题(`[ident]`)
2. 若某行的 `ident` 为空，则自动按顺序生成标识符，例如 `idx_1`、`idx_2` 等
3. 所有其他列(除 `ident` 外)都作为该 section 下的键值对
4. 所有列都是可选的，但 `ident` 为空时会自动生成

示例 CSV:
```csv
ident, content, meaning, ...
"Fox", "Fox", "狐狸(一种动物)", ...
"Dog", "Dog", "狗(一种比猫聪明的动物)", ...
"Cat", "Cat", "猫(一种不如狗聪明的动物)", ...
"Dolphin", "Dolphin", "一种很聪明的海洋哺乳动物", ...
, "Duck", "一种扁嘴水禽"
, "Meow", "猫发出的声音"
"Doge", "Doge", "神烦狗(一张搞笑狗狗表情包的代称)", ...
, "Woof", "狗发出的声音"
```

转换后的 TOML: 
```toml
[Fox]
content = "Fox"
meaning = "狐狸(一种动物)"

[Dog]
content = "Dog"
meaning = "狗(一种比猫聪明的动物)"

[Cat]
content = "Cat"
meaning = "猫(一种不如狗聪明的动物)"

[Dolphin]
content = "Dolphin"
meaning = "一种很聪明的海洋哺乳动物"

[idx_1]
content = "Duck"
meaning = "一种扁嘴水禽"

[idx_2]
content = "Meow"
meaning = "猫发出的声音"

[Doge]
content = "Doge"
meaning = "神烦狗(一张搞笑狗狗表情包的代称)"

[idx_3]
content = "Woof"
meaning = "狗发出的声音"
```

补充说明：
- 自动生成的标识符使用 `idx_` 前缀加数字序列
- 生成序列基于原始 CSV 中 `ident` 为空的行出现的顺序
- 所有值都保留为字符串类型，符合 TOML 字符串格式要求
- 如果 CSV 包含更多列，它们也会以相同方式转换为键值对
"""
import csv
import sys
import os
from pathlib import Path

def csv_to_toml(csv_path, toml_path=None):
    """
    将CSV文件转换为TOML格式
    
    Args:
        csv_path (str): 输入CSV文件路径
        toml_path (str): 输出TOML文件路径，默认为相同目录下同名文件
    """
    # 检查CSV文件是否存在
    csv_file = Path(csv_path)
    if not csv_file.exists():
        print(f"错误: CSV文件不存在 - {csv_path}")
        sys.exit(1)
    
    # 确定输出TOML文件路径
    if toml_path is None:
        toml_path = csv_file.with_suffix('.toml')
    else:
        toml_path = Path(toml_path)
    
    # 读取CSV文件
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
    except Exception as e:
        print(f"错误: 无法读取CSV文件 - {e}")
        sys.exit(1)
    
    # 检查CSV文件是否有数据
    if not rows:
        print("错误: CSV文件为空或格式不正确")
        sys.exit(1)
    
    # 生成TOML内容
    toml_content = []
    idx_counter = 1
    
    for row in rows:
        # 处理ident列，为空时生成自动标识符
        ident = row.get('ident', '').strip()
        if not ident:
            ident = f"idx_{idx_counter}"
            idx_counter += 1
        
        # 添加section标题
        toml_content.append(f"[{ident}]")
        
        # 添加所有其他列作为键值对（排除ident列）
        for key, value in row.items():
            if key == 'ident':
                continue
            
            # 确保值存在且不为空
            if value is not None and str(value).strip() != '':
                # 转义特殊字符并添加引号
                escaped_value = str(value).replace('"', '\\"')
                toml_content.append(f'"{key}" = "{escaped_value}"')
        
        # section之间添加空行
        toml_content.append("")
    
    # 写入TOML文件
    try:
        with open(toml_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(toml_content).strip())
        print(f"成功: 已生成TOML文件 - {toml_path}")
    except Exception as e:
        print(f"错误: 无法写入TOML文件 - {e}")
        sys.exit(1)

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 csv2payload.py <CSV路径> [<TOML路径>]")
        print("示例: python3 csv2payload.py input.csv output.toml")
        print("示例: python3 csv2payload.py input.csv  # 自动生成input.toml")
        sys.exit(1)
    
    csv_path = sys.argv[1]
    toml_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    csv_to_toml(csv_path, toml_path)

if __name__ == "__main__":
    main()