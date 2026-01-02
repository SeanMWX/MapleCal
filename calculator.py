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
    def __init__(self, attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu):
        self.attack_base = attack_base
        self.attack_skill = attack_skill
        self.empress_blessing = empress_blessing
        self.weapon_fix = weapon_fix
        self.attack_percet = attack_percet
        self.attack_notper = attack_notper
        self.attack_shitu = attack_shitu

    # Use for combat power calculation
    def calculate(self):
        if self.weapon_fix is None:
            raise ValueError("weapon_fix 不能为空，计算攻击力前请先设置 weapon_fix。")
        total_attack = math.floor((self.attack_base - self.attack_skill + self.empress_blessing - self.attack_shitu + self.weapon_fix) * (1 + self.attack_percet))
        return total_attack
    
    def calculate_damage_output(self):
        attack = math.floor((self.attack_base) * (1 + self.attack_percet) + self.attack_notper)
        return attack
    
    def compare(self, another: Attack):
        self_value = self.calculate_damage_output()
        another_value = another.calculate_damage_output()
        return (another_value - self_value) / self_value
    
class Damage:
    def __init__(self, dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage):
        self.dmg = dmg
        self.dmg_skill = dmg_skill
        self.bossdmg = bossdmg
        self.bossdmg_skill = bossdmg_skill
        self.dmg_shitu = dmg_shitu
        self.cridmg = cridmg
        self.cridmg_skill = cridmg_skill
        self.final_damage = final_damage

    def calculate(self):
        damage_multiplier = (1 + self.dmg - self.dmg_skill + self.bossdmg - self.bossdmg_skill - self.dmg_shitu)
        crit_multiplier = (1.35 + self.cridmg - self.cridmg_skill)
        return damage_multiplier * crit_multiplier
    
class IGN:
    def __init__(self, ign, p2):
        self.ign = ign
        self.p2 = p2

    def calculate_damage_out(self, boss_def):
        if 1 - boss_def * (1 - self.ign) < 0:
            return 0.00000000000000000000000000000000001
        return (1 - boss_def * (1 - self.ign)) * (1 - 0.5 * (1 - self.p2))
    
class CombatPower:
    def __init__(self, attribute, attack, damage, ign, gwp_fd, mst_fd, weapon_rate=1.2):
        self.attribute = attribute
        self.attack = attack
        self.damage = damage
        self.ign = ign
        self.gwp_fd = gwp_fd
        self.mst_fd = mst_fd
        self.weapon_rate = weapon_rate

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
        weapon_fix = base_attack / (1 + self.attack.attack_percet) - self.attack.attack_base + self.attack.attack_skill - self.attack.empress_blessing + self.attack.attack_shitu
        return weapon_fix
    
    def calculate_mianban(self):
        damage = (1 + self.damage.dmg) * (1 + self.damage.final_damage)
        return round(self.attribute.calculate_damage_output() * self.weapon_rate * self.attack.calculate_damage_output() * damage)

    # deprecated
    def calculate_damage_output(self, boss_def):
        final_damage = (1 + self.damage.final_damage)
        damage = (1 + self.damage.dmg + self.damage.bossdmg)
        cridmg = (1 + self.damage.cridmg)
        skilldmg = 0

        return round(self.attribute.calculate_damage_output() * self.weapon_rate * self.attack.calculate_damage_output() * final_damage * damage * cridmg) * self.ign.calculate_damage_out(boss_def)



def calculate_damage_output_value(
    main_base, main_skill, main_percent, main_notper,
    sub_base, sub_skill, sub_percent, sub_notper,
    attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
    dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
    ign, p2, boss_def,
    gwp_fd, mst_fd, weapon_rate
):
    damage = Damage(dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage)
    attribute = Attribute(main_base, main_skill, main_percent, main_notper,
                          sub_base, sub_skill, sub_percent, sub_notper)
    attack = Attack(attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu)
    ign_obj = IGN(ign, p2)
    combat = CombatPower(attribute, attack, damage, ign_obj, gwp_fd, mst_fd, weapon_rate)
    return combat.calculate_damage_output(boss_def)


def calculate_damage_output_percent_increase(
    main_base, main_skill, main_percent, main_notper,
    sub_base, sub_skill, sub_percent, sub_notper,
    attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
    dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
    ign, p2, boss_def,
    gwp_fd, mst_fd, weapon_rate,
    step=1.0
):
    if step <= 0:
        step = 1.0
    step_percent = step / 100
    if weapon_fix is None:
        weapon_fix = 0
    base_output = calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
        dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
        ign, p2, boss_def,
        gwp_fd, mst_fd, weapon_rate
    )

    def pct(new_value):
        return (new_value - base_output) / base_output * 100

    results = {}

    results["main_base"] = pct(calculate_damage_output_value(
        main_base + step, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
        dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
        ign, p2, boss_def,
        gwp_fd, mst_fd, weapon_rate
    ))
    results["main_skill"] = pct(calculate_damage_output_value(
        main_base, main_skill + step, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
        dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
        ign, p2, boss_def,
        gwp_fd, mst_fd, weapon_rate
    ))
    results["main_percent"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent + step_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
        dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
        ign, p2, boss_def,
        gwp_fd, mst_fd, weapon_rate
    ))
    results["main_notper"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper + step,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
        dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
        ign, p2, boss_def,
        gwp_fd, mst_fd, weapon_rate
    ))
    results["sub_base"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base + step, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
        dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
        ign, p2, boss_def,
        gwp_fd, mst_fd, weapon_rate
    ))
    results["sub_skill"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill + step, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
        dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
        ign, p2, boss_def,
        gwp_fd, mst_fd, weapon_rate
    ))
    results["sub_percent"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent + step_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
        dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
        ign, p2, boss_def,
        gwp_fd, mst_fd, weapon_rate
    ))
    results["sub_notper"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper + step,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
        dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
        ign, p2, boss_def,
        gwp_fd, mst_fd, weapon_rate
    ))
    results["attack_base"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base + step, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
        dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
        ign, p2, boss_def,
        gwp_fd, mst_fd, weapon_rate
    ))
    results["attack_skill"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill + step, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
        dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
        ign, p2, boss_def,
        gwp_fd, mst_fd, weapon_rate
    ))
    results["empress_blessing"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing + step, weapon_fix, attack_percet, attack_notper, attack_shitu,
        dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
        ign, p2, boss_def,
        gwp_fd, mst_fd, weapon_rate
    ))
    results["weapon_fix"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix + step, attack_percet, attack_notper, attack_shitu,
        dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
        ign, p2, boss_def,
        gwp_fd, mst_fd, weapon_rate
    ))
    results["attack_percet"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet + step_percent, attack_notper, attack_shitu,
        dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
        ign, p2, boss_def,
        gwp_fd, mst_fd, weapon_rate
    ))
    results["attack_notper"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper + step, attack_shitu,
        dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
        ign, p2, boss_def,
        gwp_fd, mst_fd, weapon_rate
    ))
    results["attack_shitu"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu + step,
        dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
        ign, p2, boss_def,
        gwp_fd, mst_fd, weapon_rate
    ))
    results["dmg"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
        dmg + step_percent, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
        ign, p2, boss_def,
        gwp_fd, mst_fd, weapon_rate
    ))
    results["dmg_skill"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
        dmg, dmg_skill + step_percent, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
        ign, p2, boss_def,
        gwp_fd, mst_fd, weapon_rate
    ))
    results["bossdmg"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
        dmg, dmg_skill, bossdmg + step_percent, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
        ign, p2, boss_def,
        gwp_fd, mst_fd, weapon_rate
    ))
    results["bossdmg_skill"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
        dmg, dmg_skill, bossdmg, bossdmg_skill + step_percent, dmg_shitu, cridmg, cridmg_skill, final_damage,
        ign, p2, boss_def,
        gwp_fd, mst_fd, weapon_rate
    ))
    results["dmg_shitu"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
        dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu + step_percent, cridmg, cridmg_skill, final_damage,
        ign, p2, boss_def,
        gwp_fd, mst_fd, weapon_rate
    ))
    results["cridmg"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
        dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg + step_percent, cridmg_skill, final_damage,
        ign, p2, boss_def,
        gwp_fd, mst_fd, weapon_rate
    ))
    results["cridmg_skill"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
        dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill + step_percent, final_damage,
        ign, p2, boss_def,
        gwp_fd, mst_fd, weapon_rate
    ))
    results["final_damage"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
        dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage + step_percent,
        ign, p2, boss_def,
        gwp_fd, mst_fd, weapon_rate
    ))
    results["gwp_fd"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
        dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
        ign, p2, boss_def,
        gwp_fd + step_percent, mst_fd, weapon_rate
    ))
    results["mst_fd"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
        dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
        ign, p2, boss_def,
        gwp_fd, mst_fd + step_percent, weapon_rate
    ))
    ign_next = 1 - ((1 - ign) * (1 - step_percent))
    results["ign"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
        dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
        ign_next, p2, boss_def,
        gwp_fd, mst_fd, weapon_rate
    ))
    p2_next = 1 - ((1 - p2) * (1 - step_percent))
    results["p2"] = pct(calculate_damage_output_value(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
        dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
        ign, p2_next, boss_def,
        gwp_fd, mst_fd, weapon_rate
    ))

    return results


def calculate_equivalent_increase(
    main_base, main_skill, main_percent, main_notper,
    sub_base, sub_skill, sub_percent, sub_notper,
    attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
    dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
    ign, p2, boss_def,
    gwp_fd, mst_fd, weapon_rate,
    base_field,
    step=1.0
):
    percent_increase = calculate_damage_output_percent_increase(
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
        dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
        ign, p2, boss_def,
        gwp_fd, mst_fd, weapon_rate,
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
            equivalents[key] = base_percent / value
    return equivalents


DEFAULT_RECOMMEND_FIELDS = [
    "main_base",
    "main_percent",
    "main_notper",
    "sub_base",
    "sub_percent",
    "sub_notper",
    "attack_base",
    "attack_percet",
    "attack_notper",
    "dmg",
    "bossdmg",
    "cridmg",
    "final_damage",
    "ign",
    "p2",
]

PERCENT_FIELDS = {
    "main_percent",
    "sub_percent",
    "attack_percet",
    "dmg",
    "dmg_skill",
    "bossdmg",
    "bossdmg_skill",
    "dmg_shitu",
    "cridmg",
    "cridmg_skill",
    "final_damage",
    "gwp_fd",
    "mst_fd",
    "ign",
    "p2",
    "boss_def",
}


def _apply_step(field, value, step):
    step = 1.0 if step <= 0 else step
    if field in {"ign", "p2"}:
        step_percent = step / 100
        return 1 - ((1 - value) * (1 - step_percent))
    if field in PERCENT_FIELDS:
        return value + step / 100
    return value + step


def _calculate_metric_value(
    metric,
    main_base, main_skill, main_percent, main_notper,
    sub_base, sub_skill, sub_percent, sub_notper,
    attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
    dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
    ign, p2, boss_def,
    gwp_fd, mst_fd, weapon_rate,
):
    damage = Damage(dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage)
    attribute = Attribute(main_base, main_skill, main_percent, main_notper,
                          sub_base, sub_skill, sub_percent, sub_notper)
    attack = Attack(attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu)
    ign_obj = IGN(ign, p2)
    combat = CombatPower(attribute, attack, damage, ign_obj, gwp_fd, mst_fd, weapon_rate)

    if metric == "combat_power":
        if weapon_fix is None:
            raise ValueError("weapon_fix is required for combat_power")
        return combat.calculate_combat_power()
    if metric == "panel":
        return combat.calculate_mianban()
    if metric == "damage_output":
        return combat.calculate_damage_output(boss_def)
    raise ValueError(f"unsupported metric: {metric}")


def calculate_metric_percent_increase(
    metric,
    main_base, main_skill, main_percent, main_notper,
    sub_base, sub_skill, sub_percent, sub_notper,
    attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
    dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
    ign, p2, boss_def,
    gwp_fd, mst_fd, weapon_rate,
    step=1.0,
    fields=None,
):
    step = 1.0 if step <= 0 else step
    fields = fields or DEFAULT_RECOMMEND_FIELDS

    base_value = _calculate_metric_value(
        metric,
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
        dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
        ign, p2, boss_def,
        gwp_fd, mst_fd, weapon_rate,
    )
    if base_value in (None, 0):
        return {}

    values = {
        "main_base": main_base,
        "main_skill": main_skill,
        "main_percent": main_percent,
        "main_notper": main_notper,
        "sub_base": sub_base,
        "sub_skill": sub_skill,
        "sub_percent": sub_percent,
        "sub_notper": sub_notper,
        "attack_base": attack_base,
        "attack_skill": attack_skill,
        "empress_blessing": empress_blessing,
        "weapon_fix": weapon_fix,
        "attack_percet": attack_percet,
        "attack_notper": attack_notper,
        "attack_shitu": attack_shitu,
        "dmg": dmg,
        "dmg_skill": dmg_skill,
        "bossdmg": bossdmg,
        "bossdmg_skill": bossdmg_skill,
        "dmg_shitu": dmg_shitu,
        "cridmg": cridmg,
        "cridmg_skill": cridmg_skill,
        "final_damage": final_damage,
        "ign": ign,
        "p2": p2,
        "boss_def": boss_def,
        "gwp_fd": gwp_fd,
        "mst_fd": mst_fd,
        "weapon_rate": weapon_rate,
    }

    results = {}
    for field in fields:
        if field not in values:
            continue
        if field == "weapon_fix" and values[field] is None:
            continue

        next_values = dict(values)
        next_values[field] = _apply_step(field, values[field], step)

        next_value = _calculate_metric_value(
            metric,
            next_values["main_base"], next_values["main_skill"], next_values["main_percent"], next_values["main_notper"],
            next_values["sub_base"], next_values["sub_skill"], next_values["sub_percent"], next_values["sub_notper"],
            next_values["attack_base"], next_values["attack_skill"], next_values["empress_blessing"], next_values["weapon_fix"],
            next_values["attack_percet"], next_values["attack_notper"], next_values["attack_shitu"],
            next_values["dmg"], next_values["dmg_skill"], next_values["bossdmg"], next_values["bossdmg_skill"],
            next_values["dmg_shitu"], next_values["cridmg"], next_values["cridmg_skill"], next_values["final_damage"],
            next_values["ign"], next_values["p2"], next_values["boss_def"],
            next_values["gwp_fd"], next_values["mst_fd"], next_values["weapon_rate"],
        )
        results[field] = (next_value - base_value) / base_value * 100

    return results


def recommend_next_upgrade(
    metric,
    main_base, main_skill, main_percent, main_notper,
    sub_base, sub_skill, sub_percent, sub_notper,
    attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
    dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
    ign, p2, boss_def,
    gwp_fd, mst_fd, weapon_rate,
    step=1.0,
    fields=None,
):
    increases = calculate_metric_percent_increase(
        metric,
        main_base, main_skill, main_percent, main_notper,
        sub_base, sub_skill, sub_percent, sub_notper,
        attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
        dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
        ign, p2, boss_def,
        gwp_fd, mst_fd, weapon_rate,
        step=step,
        fields=fields,
    )
    if not increases:
        return None
    best_field = max(increases, key=increases.get)
    return {"field": best_field, "percent": increases[best_field], "step": step}


def plan_to_target(
    metric,
    target_value,
    main_base, main_skill, main_percent, main_notper,
    sub_base, sub_skill, sub_percent, sub_notper,
    attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu,
    dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage,
    ign, p2, boss_def,
    gwp_fd, mst_fd, weapon_rate,
    step=1.0,
    fields=None,
    max_steps=200,
):
    if target_value <= 0:
        raise ValueError("target_value must be positive")

    values = {
        "main_base": main_base,
        "main_skill": main_skill,
        "main_percent": main_percent,
        "main_notper": main_notper,
        "sub_base": sub_base,
        "sub_skill": sub_skill,
        "sub_percent": sub_percent,
        "sub_notper": sub_notper,
        "attack_base": attack_base,
        "attack_skill": attack_skill,
        "empress_blessing": empress_blessing,
        "weapon_fix": weapon_fix,
        "attack_percet": attack_percet,
        "attack_notper": attack_notper,
        "attack_shitu": attack_shitu,
        "dmg": dmg,
        "dmg_skill": dmg_skill,
        "bossdmg": bossdmg,
        "bossdmg_skill": bossdmg_skill,
        "dmg_shitu": dmg_shitu,
        "cridmg": cridmg,
        "cridmg_skill": cridmg_skill,
        "final_damage": final_damage,
        "ign": ign,
        "p2": p2,
        "boss_def": boss_def,
        "gwp_fd": gwp_fd,
        "mst_fd": mst_fd,
        "weapon_rate": weapon_rate,
    }

    current = _calculate_metric_value(
        metric,
        values["main_base"], values["main_skill"], values["main_percent"], values["main_notper"],
        values["sub_base"], values["sub_skill"], values["sub_percent"], values["sub_notper"],
        values["attack_base"], values["attack_skill"], values["empress_blessing"], values["weapon_fix"],
        values["attack_percet"], values["attack_notper"], values["attack_shitu"],
        values["dmg"], values["dmg_skill"], values["bossdmg"], values["bossdmg_skill"],
        values["dmg_shitu"], values["cridmg"], values["cridmg_skill"], values["final_damage"],
        values["ign"], values["p2"], values["boss_def"],
        values["gwp_fd"], values["mst_fd"], values["weapon_rate"],
    )

    steps = []
    if current >= target_value:
        return {"reached": True, "current": current, "steps": steps}

    fields = fields or DEFAULT_RECOMMEND_FIELDS
    for _ in range(max_steps):
        increases = calculate_metric_percent_increase(
            metric,
            values["main_base"], values["main_skill"], values["main_percent"], values["main_notper"],
            values["sub_base"], values["sub_skill"], values["sub_percent"], values["sub_notper"],
            values["attack_base"], values["attack_skill"], values["empress_blessing"], values["weapon_fix"],
            values["attack_percet"], values["attack_notper"], values["attack_shitu"],
            values["dmg"], values["dmg_skill"], values["bossdmg"], values["bossdmg_skill"],
            values["dmg_shitu"], values["cridmg"], values["cridmg_skill"], values["final_damage"],
            values["ign"], values["p2"], values["boss_def"],
            values["gwp_fd"], values["mst_fd"], values["weapon_rate"],
            step=step,
            fields=fields,
        )
        if not increases:
            break

        best_field = max(increases, key=increases.get)
        if increases[best_field] <= 0:
            break

        values[best_field] = _apply_step(best_field, values[best_field], step)
        current = _calculate_metric_value(
            metric,
            values["main_base"], values["main_skill"], values["main_percent"], values["main_notper"],
            values["sub_base"], values["sub_skill"], values["sub_percent"], values["sub_notper"],
            values["attack_base"], values["attack_skill"], values["empress_blessing"], values["weapon_fix"],
            values["attack_percet"], values["attack_notper"], values["attack_shitu"],
            values["dmg"], values["dmg_skill"], values["bossdmg"], values["bossdmg_skill"],
            values["dmg_shitu"], values["cridmg"], values["cridmg_skill"], values["final_damage"],
            values["ign"], values["p2"], values["boss_def"],
            values["gwp_fd"], values["mst_fd"], values["weapon_rate"],
        )
        steps.append(
            {
                "field": best_field,
                "step": step,
                "metric_value": current,
                "percent_gain": increases[best_field],
                "new_value": values[best_field],
            }
        )
        if current >= target_value:
            return {"reached": True, "current": current, "steps": steps}

    return {"reached": False, "current": current, "steps": steps}


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
    empress_blessing = 23
    weapon_fix = -109
    attack_percet = 1.39
    attack_notper = 0
    attack_shitu = 7

    # damage
    dmg = 1.41
    dmg_skill = 0.7
    bossdmg = 4.63
    bossdmg_skill = 0.63
    dmg_shitu = 7
    cridmg = 1.126
    cridmg_skill = 0.17
    final_damage = 0.54

    # ignore defense (percent inputs)
    ign_percent = 90
    p2_percent = 10
    boss_def_percent = 300
    ign = ign_percent / 100
    p2 = p2_percent / 100
    boss_def = boss_def_percent / 100

    # genesis weapon
    gwp_fd = 0.1

    # monster 
    mst_fd = 0

    # combat power
    cp = 293820984

    damage = Damage(dmg, dmg_skill, bossdmg, bossdmg_skill, dmg_shitu, cridmg, cridmg_skill, final_damage)
    attribute = Attribute(main_base, main_skill, main_percent, main_notper,
                      sub_base, sub_skill, sub_percent, sub_notper)
    attack = Attack(attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu)
    ign_obj = IGN(ign, p2)
    combat_power = CombatPower(attribute, attack, damage, ign_obj, gwp_fd, mst_fd, weapon_rate=1.2)

    # Output
    # weapon_fix = combat_power.calculate_weapon_fix(cp)
    # print(f"计算得到的 weapon_fix 为: {weapon_fix}" )

    # 计算战斗力
    print(attribute.calculate())
    print(attack.calculate())
    print(damage.calculate())
    print(ign_obj.calculate_damage_out(boss_def))
    print("战斗力：", combat_power.calculate_combat_power())
    print("面板：", combat_power.calculate_mianban())
    print("伤害输出：", combat_power.calculate_damage_output(boss_def))

    # 属性对比
    attribute = Attribute(main_base, main_skill, main_percent, main_notper,
                      sub_base, sub_skill, sub_percent, sub_notper)
    attribute2 = Attribute(main_base, main_skill, main_percent+1, main_notper,
                      sub_base, sub_skill, sub_percent, sub_notper)

    print("属性对比：", attribute.compare(attribute2))

    print(((4 * 63571 + 5684) - (4 * 62571 + 5684)) / (4 * 62571 + 5684))

    # 攻击对比
    attack = Attack(attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper, attack_shitu)
    attack2 = Attack(attack_base, attack_skill, empress_blessing, weapon_fix, attack_percet, attack_notper+1, attack_shitu)

    print("攻击对比：", attack.compare(attack2))

    print((math.floor(3840 * ( 1 + 2.39)) - math.floor(3740 * (1 + 1.39))) / math.floor(3740 * (1 + 1.39)))

    print(attack_base)
