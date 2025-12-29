from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from calculator import (
    Attribute,
    Attack,
    CombatPower,
    Damage,
    calculate_equivalent_increase,
    calculate_damage_output_percent_increase,
)

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
INDEX_FILE = BASE_DIR / "index.html"


class CalcInput(BaseModel):
    main_base: float
    main_skill: float
    main_percent: float
    main_notper: float
    sub_base: float
    sub_skill: float
    sub_percent: float
    sub_notper: float
    attack_base: float
    attack_skill: float
    empress_blessing: float
    weapon_fix: Optional[float] = None
    attack_percet: float
    attack_notper: float
    dmg: float
    dmg_skill: float
    bossdmg: float
    bossdmg_skill: float
    cridmg: float
    cridmg_skill: float
    final_damage: float
    gwp_fd: float
    mst_fd: float
    delta_step: float = 1.0


class WeaponFixInput(CalcInput):
    known_cp: float


def build_attribute(data: CalcInput) -> Attribute:
    return Attribute(
        data.main_base,
        data.main_skill,
        data.main_percent,
        data.main_notper,
        data.sub_base,
        data.sub_skill,
        data.sub_percent,
        data.sub_notper,
    )


def build_attack(data: CalcInput, weapon_fix: Optional[float] = None) -> Attack:
    return Attack(
        data.attack_base,
        data.attack_skill,
        data.empress_blessing,
        weapon_fix if weapon_fix is not None else data.weapon_fix,
        data.attack_percet,
        data.attack_notper,
    )


def build_damage(data: CalcInput) -> Damage:
    return Damage(
        data.dmg,
        data.dmg_skill,
        data.bossdmg,
        data.bossdmg_skill,
        data.cridmg,
        data.cridmg_skill,
        data.final_damage,
    )


def delta_fields() -> List[Dict[str, str]]:
    return [
        {"key": "main_base", "label": "主属性基础值"},
        {"key": "main_percent", "label": "主属性%"},
        {"key": "main_notper", "label": "主属性非%加成"},
        {"key": "sub_base", "label": "副属性基础值"},
        {"key": "sub_percent", "label": "副属性%"},
        {"key": "sub_notper", "label": "副属性非%加成"},
        {"key": "attack_base", "label": "攻击力基础值"},
        {"key": "attack_percet", "label": "攻击力%"},
        {"key": "attack_notper", "label": "攻击力非%加成"},
        {"key": "dmg", "label": "伤害%"},
        {"key": "bossdmg", "label": "Boss伤%"},
        {"key": "cridmg", "label": "暴伤%"},
        {"key": "final_damage", "label": "最终伤害%"},
        {"key": "mst_fd", "label": "怪物最终伤害"},
    ]


@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    return HTMLResponse(INDEX_FILE.read_text(encoding="utf-8"))


@app.post("/api/calc")
def api_calc(data: CalcInput) -> Dict[str, object]:
    attribute = build_attribute(data)
    attack = build_attack(data)
    damage = build_damage(data)
    combat = CombatPower(attribute, attack, damage, data.gwp_fd, data.mst_fd)

    combat_power = None
    warning = None
    if data.weapon_fix is None:
        warning = "weapon_fix 为空时无法计算战斗力，但面板和输出仍可计算。"
    else:
        try:
            combat_power = combat.calculate_combat_power()
        except ValueError as exc:
            warning = str(exc)

    panel = combat.calculate_mianban()
    output = combat.calculate_damage_output()

    step = data.delta_step if data.delta_step and data.delta_step > 0 else 1.0
    percent_increase = calculate_damage_output_percent_increase(
        data.main_base, data.main_skill, data.main_percent, data.main_notper,
        data.sub_base, data.sub_skill, data.sub_percent, data.sub_notper,
        data.attack_base, data.attack_skill, data.empress_blessing, data.weapon_fix, data.attack_percet, data.attack_notper,
        data.dmg, data.dmg_skill, data.bossdmg, data.bossdmg_skill, data.cridmg, data.cridmg_skill, data.final_damage,
        data.gwp_fd, data.mst_fd,
        step=step,
    )
    delta_items = []
    for item in delta_fields():
        key = item["key"]
        delta_items.append(
            {
                "key": key,
                "label": item["label"],
                "step": step,
                "percent": percent_increase.get(key, 0.0),
            }
        )

    return {
        "combat_power": combat_power,
        "panel": panel,
        "damage_output": output,
        "warning": warning,
        "delta_items": delta_items,
    }


@app.post("/api/equivalent")
def api_equivalent(data: CalcInput, base_field: str) -> Dict[str, object]:
    equivalents = calculate_equivalent_increase(
        data.main_base, data.main_skill, data.main_percent, data.main_notper,
        data.sub_base, data.sub_skill, data.sub_percent, data.sub_notper,
        data.attack_base, data.attack_skill, data.empress_blessing, data.weapon_fix, data.attack_percet, data.attack_notper,
        data.dmg, data.dmg_skill, data.bossdmg, data.bossdmg_skill, data.cridmg, data.cridmg_skill, data.final_damage,
        data.gwp_fd, data.mst_fd,
        base_field=base_field,
        step=1.0,
    )
    items = []
    for item in delta_fields():
        key = item["key"]
        items.append(
            {
                "key": key,
                "label": item["label"],
                "amount": equivalents.get(key),
            }
        )

    return {
        "base_field": base_field,
        "items": items,
    }


@app.post("/api/weapon-fix")
def api_weapon_fix(data: WeaponFixInput) -> Dict[str, float]:
    attribute = build_attribute(data)
    damage = build_damage(data)
    attack = build_attack(data, weapon_fix=None)
    combat = CombatPower(attribute, attack, damage, data.gwp_fd, data.mst_fd)
    weapon_fix = combat.calculate_weapon_fix(data.known_cp)
    return {"weapon_fix": weapon_fix}
