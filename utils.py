import json
import os

def find_base_by_searching_history(target_level, current_stars, current_attack):
    with open('star.json', 'r') as f:
        high_star_data = json.load(f)
    with open('lowstar.json', 'r') as f:
        low_star_history = json.load(f)

    temp_attack = current_attack
    level_str = str(target_level)

    # 第一步：如果是16星以上，先倒扣到15星
    if current_stars > 15:
        for s in range(current_stars, 15, -1):
            temp_attack -= high_star_data[level_str][str(s)]["att"]
    
    target_15_att = temp_attack
    print(f"目标 15星 攻击力为: {target_15_att}")

    # 第二步：遍历数据库，寻找谁的 15星 数值匹配
    possible_bases = []
    for base_val, history in low_star_history.items():
        if history[15] == target_15_att:
            possible_bases.append(base_val)

    if possible_bases:
        print(f"匹配成功！可能的 0星 底子为: {possible_bases}")
        # 顺便打印出 325 的成长过程给你看
        if "325" in possible_bases:
            print(f"325 的 0-15星 成长过程: {low_star_history['325']}")
    else:
        print("未能在数据库中找到匹配路径。")

def forward_star_force(target_level, base_attack, target_stars):
    """
    根据底子正推到目标星级的攻击力
    target_level: 武器等级 (150, 160, 200)
    base_attack: 0星时的原始攻击+卷攻击
    target_stars: 想要推算到的星级 (最大25)
    """
    # 1. 加载数据库
    if not os.path.exists('lowstar.json') or not os.path.exists('star.json'):
        print("错误：请确保 lowstar.json 和 star.json 存在。")
        return

    with open('lowstar.json', 'r') as f:
        low_star_db = json.load(f)
    with open('star.json', 'r') as f:
        high_star_db = json.load(f)

    # 2. 0-15星阶段：直接查表
    base_str = str(base_attack)
    if base_str not in low_star_db:
        print(f"错误：底子 {base_attack} 不在 lowstar 数据库中。")
        return

    # 获取 0-15 星的完整列表
    full_history = low_star_db[base_str] 
    
    print(f"--- 武器正推报告: {target_level}级武器 ---")
    print(f"0星底子: {base_attack}")
    
    # 3. 处理 1-15 星的显示
    limit_15 = min(target_stars, 15)
    for s in range(1, limit_15 + 1):
        prev_att = full_history[s-1]
        curr_att = full_history[s]
        print(f"第 {s} 星: {prev_att} -> {curr_att} (提升 {curr_att - prev_att})")

    # 4. 16-25星阶段：动态累加
    if target_stars > 15:
        level_str = str(target_level)
        current_att = full_history[15] # 15星时的攻击
        
        for s in range(16, target_stars + 1):
            bonus = high_star_db[level_str][str(s)]["att"]
            new_att = current_att + bonus
            print(f"第 {s} 星: {current_att} -> {new_att} (提升 {bonus} [固定])")
            current_att = new_att
            full_history.append(current_att)

    print("-" * 30)
    print(f"目标 {target_stars} 星最终攻击力为: {full_history[target_stars]}")
    return full_history[target_stars]

# --- 运行测试 ---
# 运行反推
find_base_by_searching_history(200, 22, 572)

# 例子：底子 325，200级武器，正推到 22 星
forward_star_force(target_level=200, base_attack=325, target_stars=22)