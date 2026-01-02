from __future__ import annotations

from calculator import (
    Attribute,
    Attack,
    CombatPower,
    Damage,
    IGN,
    plan_to_target,
    recommend_next_upgrade,
)


def build_sample_state():
    # Example values from calculator.py __main__ block.
    main_base = 5635
    main_skill = 448
    main_percent = 5.23
    main_notper = 27465

    sub_base = 2991
    sub_skill = 144
    sub_percent = 0.72
    sub_notper = 540

    attack_base = 3740
    attack_skill = 190
    empress_blessing = 23
    weapon_fix = -109
    attack_percet = 1.39
    attack_notper = 0
    attack_shitu = 7

    dmg = 1.41
    dmg_skill = 0.7
    bossdmg = 4.63
    bossdmg_skill = 0.63
    # Percent-based fields should be in ratio form (e.g., 7% -> 0.07).
    dmg_shitu = 0.07
    cridmg = 1.126
    cridmg_skill = 0.17
    final_damage = 0.54

    ign = 0.9
    p2 = 0.1
    boss_def = 3.0

    gwp_fd = 0.1
    mst_fd = 0.0
    weapon_rate = 1.2

    return {
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


def compute_metrics(values):
    damage = Damage(
        values["dmg"],
        values["dmg_skill"],
        values["bossdmg"],
        values["bossdmg_skill"],
        values["dmg_shitu"],
        values["cridmg"],
        values["cridmg_skill"],
        values["final_damage"],
    )
    attribute = Attribute(
        values["main_base"],
        values["main_skill"],
        values["main_percent"],
        values["main_notper"],
        values["sub_base"],
        values["sub_skill"],
        values["sub_percent"],
        values["sub_notper"],
    )
    attack = Attack(
        values["attack_base"],
        values["attack_skill"],
        values["empress_blessing"],
        values["weapon_fix"],
        values["attack_percet"],
        values["attack_notper"],
        values["attack_shitu"],
    )
    ign_obj = IGN(values["ign"], values["p2"])
    combat = CombatPower(
        attribute,
        attack,
        damage,
        ign_obj,
        values["gwp_fd"],
        values["mst_fd"],
        values["weapon_rate"],
    )
    return {
        "combat_power": combat.calculate_combat_power(),
        "panel": combat.calculate_mianban(),
        "damage_output": combat.calculate_damage_output(values["boss_def"]),
    }


def main():
    values = build_sample_state()
    metrics = compute_metrics(values)
    print(values)
    print(metrics)

    for metric in ("combat_power", "panel", "damage_output"):
        rec = recommend_next_upgrade(
            metric,
            values["main_base"], values["main_skill"], values["main_percent"], values["main_notper"],
            values["sub_base"], values["sub_skill"], values["sub_percent"], values["sub_notper"],
            values["attack_base"], values["attack_skill"], values["empress_blessing"], values["weapon_fix"],
            values["attack_percet"], values["attack_notper"], values["attack_shitu"],
            values["dmg"], values["dmg_skill"], values["bossdmg"], values["bossdmg_skill"],
            values["dmg_shitu"], values["cridmg"], values["cridmg_skill"], values["final_damage"],
            values["ign"], values["p2"], values["boss_def"],
            values["gwp_fd"], values["mst_fd"], values["weapon_rate"],
            step=1.0,
        )
        assert rec is not None, f"{metric}: no recommendation"
        assert "field" in rec and "percent" in rec, f"{metric}: invalid recommendation"

        target = metrics[metric] + 10000000000000000
        print(f"{metric}: planning to reach target {target}")
        plan = plan_to_target(
            metric,
            target,
            values["main_base"], values["main_skill"], values["main_percent"], values["main_notper"],
            values["sub_base"], values["sub_skill"], values["sub_percent"], values["sub_notper"],
            values["attack_base"], values["attack_skill"], values["empress_blessing"], values["weapon_fix"],
            values["attack_percet"], values["attack_notper"], values["attack_shitu"],
            values["dmg"], values["dmg_skill"], values["bossdmg"], values["bossdmg_skill"],
            values["dmg_shitu"], values["cridmg"], values["cridmg_skill"], values["final_damage"],
            values["ign"], values["p2"], values["boss_def"],
            values["gwp_fd"], values["mst_fd"], values["weapon_rate"],
            step=1.0,
            max_steps=1000,
        )
        assert isinstance(plan, dict), f"{metric}: plan_to_target should return dict"
        assert "reached" in plan and "steps" in plan, f"{metric}: plan_to_target missing keys"

    print("tester finished: recommend_next_upgrade and plan_to_target look OK")
    print(rec)
    print(plan)


if __name__ == "__main__":
    main()
