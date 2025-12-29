from __future__ import annotations # 允许在类内部直接引用类名
import math

class Attribute:
    def __init__(self, main_base, main_skill, main_percent, main_notper,
                 sub_base, sub_skill, sub_percent, sub_notper):
        self.main_base = main_base
        self.main_skill = main_skill
        self.main_percent = main_percent
        self.main_notper = main_notper
        self.sub_base = sub_base
        self.sub_skill = sub_skill
        self.sub_percent = sub_percent
        self.sub_notper = sub_notper

    # Use for combat power calculation
    def calculate(self):
        main_value = math.floor((self.main_base - self.main_skill) * (1 + self.main_percent)) + self.main_notper
        sub_value = math.floor((self.sub_base - self.sub_skill) * (1 + self.sub_percent)) + self.sub_notper
        total_attribute = (main_value * 4 + sub_value) / 100
        return total_attribute
    
    # Use for damage output calculation
    def calculate_damage_output(self):
        main_attribute = math.floor(self.main_base * (1 + self.main_percent) + self.main_notper)
        sub_attribute = math.floor(self.sub_base * (1 + self.sub_percent) + self.sub_notper)
        attribute = (4 * main_attribute + \
                     sub_attribute) / 100
        return attribute
    
    def compare(self, another: Attribute):
        self_value = self.calculate_damage_output()
        another_value = another.calculate_damage_output()
        return (another_value - self_value) / self_value
    
class Attack:
    def __init__(self, attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper):
        self.attack_base = attack_base
        self.attack_skill = attack_skill
        self.empress_blessing = empress_blessing
        self.weapon_fix = weapon_fix
        self.attack_percet = attack_percet
        self.attack_notper = attack_notper

    # Use for combat power calculation
    def calculate(self):
        if self.weapon_fix is None:
            raise ValueError("weapon_fix 不能为空，计算攻击力前请先设置 weapon_fix。")
        total_attack = math.floor((self.attack_base - self.attack_skill + self.empress_blessing + self.weapon_fix) * (1 + self.attack_percet))
        return total_attack
    
    def calculate_damage_output(self):
        attack = math.floor((self.attack_base - self.attack_notper) * (1 + self.attack_percet) + self.attack_notper)
        return attack
    
    def compare(self, another: Attack):
        self_value = self.calculate_damage_output()
        another_value = another.calculate_damage_output()
        return (another_value - self_value) / self_value
    
class Damage:
    def __init__(self, dmg, dmg_skill, bossdmg, bossdmg_skill, cridmg, cridmg_skill, final_damage):
        self.dmg = dmg
        self.dmg_skill = dmg_skill
        self.bossdmg = bossdmg
        self.bossdmg_skill = bossdmg_skill
        self.cridmg = cridmg
        self.cridmg_skill = cridmg_skill
        self.final_damage = final_damage

    def calculate(self):
        damage_multiplier = (1 + self.dmg - self.dmg_skill + self.bossdmg - self.bossdmg_skill)
        crit_multiplier = (1.35 + self.cridmg - self.cridmg_skill)
        return damage_multiplier * crit_multiplier
    
class CombatPower:
    def __init__(self, attribute, attack, damage, gwp_fd, mst_fd):
        self.attribute = attribute
        self.attack = attack
        self.damage = damage
        self.gwp_fd = gwp_fd
        self.mst_fd = mst_fd

    def calculate_combat_power(self):
        combat_power = self.attribute.calculate() * \
                self.attack.calculate() * \
                self.damage.calculate() * \
                (1 + self.gwp_fd) * \
                (1 + self.mst_fd)
        return round(combat_power)
    
    def calculate_weapon_fix(self, target_combat_power):
        if self.attack.weapon_fix is not None:
            raise ValueError("weapon_fix 已经有值，不需要计算。")
        total_attribute = self.attribute.calculate()
        damage_multiplier = self.damage.calculate()
        base_attack = target_combat_power / (total_attribute * damage_multiplier * (1 + self.gwp_fd) * (1 + self.mst_fd))
        weapon_fix = base_attack / (1 + self.attack.attack_percet) - self.attack.attack_base + self.attack.attack_skill - self.attack.empress_blessing
        return weapon_fix
    
    def calculate_mianban(self):
        weapon_rate = 1.2
        damage = (1 + self.damage.dmg) * (1 + self.damage.final_damage)
        return round(self.attribute.calculate_damage_output() * weapon_rate * self.attack.calculate_damage_output() * damage)

    # deprecated
    def calculate_damage_output(self):
        weapon_rate = 1.2
        final_damage = (1 + self.damage.final_damage)
        damage = (1 + self.damage.dmg + self.damage.bossdmg)
        cridmg = (1 + self.damage.cridmg)
        skilldmg = 0
        igndef = 0

        return round(self.attribute.calculate_damage_output() * weapon_rate * self.attack.calculate_damage_output() * final_damage * damage * cridmg)


def calculate_damage_output_value(
    main_base, main_skill, main_percent, main_notper,
    sub_base, sub_skill, sub_percent, sub_notper,
    attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper,
    dmg, dmg_skill, bossdmg, bossdmg_skill, cridmg, cridmg_skill, final_damage,
    gwp_fd, mst_fd
):
    damage = Damage(dmg, dmg_skill, bossdmg, bossdmg_skill, cridmg, cridmg_skill, final_damage)
    attribute = Attribute(main_base, main_skill, main_percent, main_notper,
                          sub_base, sub_skill, sub_percent, sub_notper)
    attack = Attack(attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper)
    combat = CombatPower(attribute, attack, damage, gwp_fd, mst_fd)
    return combat.calculate_damage_output()


def calculate_damage_output_percent_increase(
    main_base, main_skill, main_percent, main_notper,
    sub_base, sub_skill, sub_percent, sub_notper,
    attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper,
    dmg, dmg_skill, bossdmg, bossdmg_skill, cridmg, cridmg_skill, final_damage,
    gwp_fd, mst_fd,
    step=1.0
):
    if step <= 0:
        step = 1.0
    if weapon_fix is None:
        weapon_fix = 0
    base_output = calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper,
        dmg, dmg_skill, bossdmg, bossdmg_skill, cridmg, cridmg_skill, final_damage,
        gwp_fd, mst_fd
    )

    def pct(new_value):
        return (new_value - base_output) / base_output * 100

    results = {}

    results["main_base"] = pct(calculate_damage_output_value(
        main_base + step, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper,
        dmg, dmg_skill, bossdmg, bossdmg_skill, cridmg, cridmg_skill, final_damage,
        gwp_fd, mst_fd
    ))
    results["main_skill"] = pct(calculate_damage_output_value(
        main_base, main_skill + step, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper,
        dmg, dmg_skill, bossdmg, bossdmg_skill, cridmg, cridmg_skill, final_damage,
        gwp_fd, mst_fd
    ))
    results["main_percent"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent + step, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper,
        dmg, dmg_skill, bossdmg, bossdmg_skill, cridmg, cridmg_skill, final_damage,
        gwp_fd, mst_fd
    ))
    results["main_notper"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper + step,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper,
        dmg, dmg_skill, bossdmg, bossdmg_skill, cridmg, cridmg_skill, final_damage,
        gwp_fd, mst_fd
    ))
    results["sub_base"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base + step, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper,
        dmg, dmg_skill, bossdmg, bossdmg_skill, cridmg, cridmg_skill, final_damage,
        gwp_fd, mst_fd
    ))
    results["sub_skill"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill + step, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper,
        dmg, dmg_skill, bossdmg, bossdmg_skill, cridmg, cridmg_skill, final_damage,
        gwp_fd, mst_fd
    ))
    results["sub_percent"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent + step, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper,
        dmg, dmg_skill, bossdmg, bossdmg_skill, cridmg, cridmg_skill, final_damage,
        gwp_fd, mst_fd
    ))
    results["sub_notper"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper + step,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper,
        dmg, dmg_skill, bossdmg, bossdmg_skill, cridmg, cridmg_skill, final_damage,
        gwp_fd, mst_fd
    ))
    results["attack_base"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base + step, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper,
        dmg, dmg_skill, bossdmg, bossdmg_skill, cridmg, cridmg_skill, final_damage,
        gwp_fd, mst_fd
    ))
    results["attack_skill"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill + step, empress_blessing, weapon_fix, attack_percet, attack_notper,
        dmg, dmg_skill, bossdmg, bossdmg_skill, cridmg, cridmg_skill, final_damage,
        gwp_fd, mst_fd
    ))
    results["empress_blessing"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing + step, weapon_fix, attack_percet, attack_notper,
        dmg, dmg_skill, bossdmg, bossdmg_skill, cridmg, cridmg_skill, final_damage,
        gwp_fd, mst_fd
    ))
    results["weapon_fix"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix + step, attack_percet, attack_notper,
        dmg, dmg_skill, bossdmg, bossdmg_skill, cridmg, cridmg_skill, final_damage,
        gwp_fd, mst_fd
    ))
    results["attack_percet"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet + step, attack_notper,
        dmg, dmg_skill, bossdmg, bossdmg_skill, cridmg, cridmg_skill, final_damage,
        gwp_fd, mst_fd
    ))
    results["attack_notper"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper + step,
        dmg, dmg_skill, bossdmg, bossdmg_skill, cridmg, cridmg_skill, final_damage,
        gwp_fd, mst_fd
    ))
    results["dmg"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper,
        dmg + step, dmg_skill, bossdmg, bossdmg_skill, cridmg, cridmg_skill, final_damage,
        gwp_fd, mst_fd
    ))
    results["dmg_skill"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper,
        dmg, dmg_skill + step, bossdmg, bossdmg_skill, cridmg, cridmg_skill, final_damage,
        gwp_fd, mst_fd
    ))
    results["bossdmg"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper,
        dmg, dmg_skill, bossdmg + step, bossdmg_skill, cridmg, cridmg_skill, final_damage,
        gwp_fd, mst_fd
    ))
    results["bossdmg_skill"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper,
        dmg, dmg_skill, bossdmg, bossdmg_skill + step, cridmg, cridmg_skill, final_damage,
        gwp_fd, mst_fd
    ))
    results["cridmg"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper,
        dmg, dmg_skill, bossdmg, bossdmg_skill, cridmg + step, cridmg_skill, final_damage,
        gwp_fd, mst_fd
    ))
    results["cridmg_skill"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper,
        dmg, dmg_skill, bossdmg, bossdmg_skill, cridmg, cridmg_skill + step, final_damage,
        gwp_fd, mst_fd
    ))
    results["final_damage"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper,
        dmg, dmg_skill, bossdmg, bossdmg_skill, cridmg, cridmg_skill, final_damage + step,
        gwp_fd, mst_fd
    ))
    results["gwp_fd"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper,
        dmg, dmg_skill, bossdmg, bossdmg_skill, cridmg, cridmg_skill, final_damage,
        gwp_fd + step, mst_fd
    ))
    results["mst_fd"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper,
        dmg, dmg_skill, bossdmg, bossdmg_skill, cridmg, cridmg_skill, final_damage,
        gwp_fd, mst_fd + step
    ))

    return results


def calculate_equivalent_increase(
    main_base, main_skill, main_percent, main_notper,
    sub_base, sub_skill, sub_percent, sub_notper,
    attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper,
    dmg, dmg_skill, bossdmg, bossdmg_skill, cridmg, cridmg_skill, final_damage,
    gwp_fd, mst_fd,
    base_field,
    step=1.0
):
    percent_increase = calculate_damage_output_percent_increase(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper,
        dmg, dmg_skill, bossdmg, bossdmg_skill, cridmg, cridmg_skill, final_damage,
        gwp_fd, mst_fd,
        step=step,
    )
    base_percent = percent_increase.get(base_field)
    if base_percent is None or base_percent == 0:
        return {}

    equivalents = {}
    for key, value in percent_increase.items():
        if value == 0:
            equivalents[key] = None
        else:
            equivalents[key] = base_percent / value * step
    return equivalents


# Combat Power (CP value) and Damage Output
combat_power = 0
damage_output = 0

if __name__ == '__main__':
    ## user inputs
    # attributes
    main_base = 5635
    main_skill = 448
    main_percent = 5.23
    main_notper = 27465

    sub_base = 2991
    sub_skill = 144
    sub_percent = 0.72
    sub_notper = 540

    # attack
    attack_base = 3740
    attack_skill = 190
    empress_blessing = 30
    weapon_fix = -109
    attack_percet = 1.39
    attack_notper = 0

    # damage
    dmg = 1.41
    dmg_skill = 0.7
    bossdmg = 4.63
    bossdmg_skill = 0.63
    cridmg = 1.126
    cridmg_skill = 0.17
    final_damage = 0.54

    # genesis weapon
    gwp_fd = 0.1

    # monster 
    mst_fd = 0

    # combat power
    cp = 293820984

    damage = Damage(dmg, dmg_skill, bossdmg, bossdmg_skill, cridmg, cridmg_skill, final_damage)
    attribute = Attribute(main_base, main_skill, main_percent, main_notper,
                      sub_base, sub_skill, sub_percent, sub_notper)
    attack = Attack(attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper)
    combat_power = CombatPower(attribute, attack, damage, gwp_fd, mst_fd)

    # Output
    # weapon_fix = combat_power.calculate_weapon_fix(cp)
    # print(f"计算得到的 weapon_fix 为: {weapon_fix}" )

    # 计算战斗力
    print(attribute.calculate())
    print(attack.calculate())
    print(damage.calculate())
    print("战斗力：", combat_power.calculate_combat_power())
    print("面板：", combat_power.calculate_mianban())
    print("伤害输出：", combat_power.calculate_damage_output())

    # 属性对比
    attribute = Attribute(main_base, main_skill, main_percent, main_notper,
                      sub_base, sub_skill, sub_percent, sub_notper)
    attribute2 = Attribute(main_base, main_skill, main_percent+1, main_notper,
                      sub_base, sub_skill, sub_percent, sub_notper)

    print("属性对比：", attribute.compare(attribute2))

    print(((4 * 63571 + 5684) - (4 * 62571 + 5684)) / (4 * 62571 + 5684))

    # 攻击对比
    attack = Attack(attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper)
    attack2 = Attack(attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet+1, attack_notper)

    print("攻击对比：", attack.compare(attack2))

    print((math.floor(3840 * ( 1 + 2.39)) - math.floor(3740 * (1 + 1.39))) / math.floor(3740 * (1 + 1.39)))

    print(attack_base)




