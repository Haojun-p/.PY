"""
数据清洗脚本：从 SONG_train.json 中提取 assistant 回复
用于训练聊天机器人模仿"宋曙延"的说话风格
"""

import json
import os
from collections import Counter

def clean_song_data(input_file, output_file, min_length=1, max_length=500):
    """
    清洗 SONG_train.json 数据，提取所有 assistant 的回复
    
    参数：
    - input_file: 输入的 JSON 文件路径
    - output_file: 输出的 JSON 文件路径
    - min_length: 最小文本长度（过滤太短的回复）
    - max_length: 最大文本长度（过滤太长的回复）
    """
    
    print(f"[读取] 正在读取文件: {input_file}")
    
    # 读取原始数据
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"[成功] 已加载 {len(data)} 个对话对象")
    
    # 提取所有 assistant 的回复
    assistant_replies = []
    stats = {
        'total_conversations': len(data),
        'total_assistant_messages': 0,
        'filtered_short': 0,
        'filtered_long': 0,
        'filtered_empty': 0,
        'final_count': 0
    }
    
    # ========== 数据清洗要点 ==========
    # 1. 遍历所有对话对象
    for conv_idx, conversation in enumerate(data):
        if 'messages' not in conversation:
            print(f"⚠ 警告：对话 {conv_idx} 缺少 'messages' 字段")
            continue
        
        messages = conversation['messages']
        
        # 2. 提取所有 assistant 角色的消息
        for msg in messages:
            if msg.get('role') == 'assistant':
                content = msg.get('content', '').strip()
                stats['total_assistant_messages'] += 1
                
                # 3. 数据清洗检查点
                # 检查点1：过滤空内容
                if not content:
                    stats['filtered_empty'] += 1
                    continue
                
                # 检查点2：过滤太短的回复（可能是误输入或无效数据）
                if len(content) < min_length:
                    stats['filtered_short'] += 1
                    continue
                
                # 检查点3：过滤太长的回复（可能是异常数据）
                if len(content) > max_length:
                    stats['filtered_long'] += 1
                    continue
                
                # 检查点4：过滤纯符号或特殊字符（可选）
                # 如果内容只包含标点符号，可以过滤掉
                if content.replace(' ', '').replace('，', '').replace('。', '').replace('！', '').replace('？', '').replace(',', '').replace('.', '').replace('!', '').replace('?', '').replace('[', '').replace(']', '').strip() == '':
                    stats['filtered_empty'] += 1
                    continue
                
                # 通过所有检查，添加到列表
                assistant_replies.append({"content": content})
                stats['final_count'] += 1
    
    # 4. 去重（可选）：如果同一句话出现多次，可以只保留一次
    # 注意：对于说话风格学习，重复的句子可能也有价值，所以这里不去重
    # 如果需要去重，可以取消下面的注释：
    # seen = set()
    # unique_replies = []
    # for reply in assistant_replies:
    #     content = reply['content']
    #     if content not in seen:
    #         seen.add(content)
    #         unique_replies.append(reply)
    # assistant_replies = unique_replies
    
    # 5. 保存清洗后的数据
    print(f"\n[统计] 数据清洗统计：")
    print(f"  - 总对话数: {stats['total_conversations']}")
    print(f"  - 总 assistant 消息数: {stats['total_assistant_messages']}")
    print(f"  - 过滤空内容: {stats['filtered_empty']}")
    print(f"  - 过滤过短内容: {stats['filtered_short']}")
    print(f"  - 过滤过长内容: {stats['filtered_long']}")
    print(f"  - 最终保留: {stats['final_count']} 条")
    
    # 保存为 JSON 文件（符合 clonebot 期望的格式）
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(assistant_replies, f, ensure_ascii=False, indent=2)
    
    print(f"\n[成功] 已保存清洗后的数据到: {output_file}")
    
    # 6. 显示一些示例（前5条）
    print(f"\n[示例] 数据示例（前5条）：")
    for i, reply in enumerate(assistant_replies[:5], 1):
        content = reply['content']
        # 处理 Windows 控制台编码问题：移除无法编码的字符
        try:
            preview = content[:50].encode('gbk', errors='ignore').decode('gbk')
            if len(content) > 50:
                preview += '...'
            print(f"  {i}. {preview}")
        except Exception:
            # 如果还是失败，只显示长度
            print(f"  {i}. [内容长度: {len(content)} 字符]")
    
    return assistant_replies

def analyze_data_quality(input_file):
    """
    分析数据质量，帮助确定清洗参数
    """
    print(f"\n[分析] 正在分析数据质量...")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    lengths = []
    empty_count = 0
    
    for conversation in data:
        if 'messages' not in conversation:
            continue
        for msg in conversation['messages']:
            if msg.get('role') == 'assistant':
                content = msg.get('content', '').strip()
                if not content:
                    empty_count += 1
                else:
                    lengths.append(len(content))
    
    if lengths:
        print(f"  - 平均长度: {sum(lengths) / len(lengths):.1f} 字符")
        print(f"  - 最短: {min(lengths)} 字符")
        print(f"  - 最长: {max(lengths)} 字符")
        print(f"  - 中位数: {sorted(lengths)[len(lengths)//2]} 字符")
    
    print(f"  - 空内容数量: {empty_count}")
    
    # 显示长度分布
    if lengths:
        length_ranges = {
            '1-10': sum(1 for l in lengths if 1 <= l <= 10),
            '11-50': sum(1 for l in lengths if 11 <= l <= 50),
            '51-100': sum(1 for l in lengths if 51 <= l <= 100),
            '101-200': sum(1 for l in lengths if 101 <= l <= 200),
            '200+': sum(1 for l in lengths if l > 200),
        }
        print(f"\n  长度分布:")
        for range_name, count in length_ranges.items():
            print(f"    {range_name}: {count} 条")

if __name__ == "__main__":
    # 配置路径
    input_file = r"SONG(wxid_om003yeh0v6c22)\SONG_train.json"
    output_file = r"4.2_memory_clonebot\songshuyan_memory.json"
    
    # 先分析数据质量
    analyze_data_quality(input_file)
    
    # 执行数据清洗
    # 参数说明：
    # - min_length=1: 保留所有非空内容（可以根据分析结果调整）
    # - max_length=500: 过滤超过500字符的回复（可以根据分析结果调整）
    clean_song_data(
        input_file=input_file,
        output_file=output_file,
        min_length=1,      # 可以根据数据质量分析结果调整
        max_length=500      # 可以根据数据质量分析结果调整
    )
    
    print("\n[完成] 数据清洗完成！")

