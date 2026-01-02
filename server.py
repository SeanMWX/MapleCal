from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from calculator import (
    Attribute,
    Attack,
    CombatPower,
    Damage,
    IGN,
    calculate_equivalent_increase,
    calculate_damage_output_percent_increase,
)

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent
INDEX_FILE = BASE_DIR / "assets" / "index.html"
COMPARE_FILE = BASE_DIR / "assets" / "compare.html"

app.mount("/assets", StaticFiles(directory=BASE_DIR / "assets"), name="assets")


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
    attack_shitu: float
    weapon_fix: Optional[float] = None
    attack_percet: float
    attack_notper: float
    dmg: float
    dmg_skill: float
    bossdmg: float
    bossdmg_skill: float
    dmg_shitu: float
    cridmg: float
    cridmg_skill: float
    final_damage: float
    gwp_fd: float
    mst_fd: float
    ign: float
    p2: float
    boss_def: float
    weapon_rate: float
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
        data.attack_shitu,
    )


def build_damage(data: CalcInput) -> Damage:
    return Damage(
        data.dmg,
        data.dmg_skill,
        data.bossdmg,
        data.bossdmg_skill,
        data.dmg_shitu,
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
        {"key": "ign", "label": "无视防御%"},
        {"key": "p2", "label": "全属性防御穿透%"},
    ]


def equivalent_fields() -> List[Dict[str, str]]:
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
        {"key": "ign", "label": "无视防御%"},
        {"key": "p2", "label": "全属性防御穿透%"},
    ]


def normalize_percent(data: CalcInput) -> CalcInput:
    normalized = data.model_copy()
    percent_fields = [
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
    ]
    for field in percent_fields:
        setattr(normalized, field, getattr(normalized, field) / 100)
    return normalized


@app.get("/", response_class=HTMLResponse)
def home() -> HTMLResponse:
    return HTMLResponse(INDEX_FILE.read_text(encoding="utf-8"))


@app.get("/compare", response_class=HTMLResponse)
def compare_page() -> HTMLResponse:
    return HTMLResponse(COMPARE_FILE.read_text(encoding="utf-8"))


@app.post("/api/calc")
def api_calc(data: CalcInput) -> Dict[str, object]:
    normalized = normalize_percent(data)
    attribute = build_attribute(normalized)
    attack = build_attack(normalized)
    damage = build_damage(normalized)
    ign_obj = IGN(normalized.ign, normalized.p2)
    combat = CombatPower(attribute, attack, damage, ign_obj, normalized.gwp_fd, normalized.mst_fd, data.weapon_rate)

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
    output = combat.calculate_damage_output(normalized.boss_def)

    step = data.delta_step if data.delta_step and data.delta_step > 0 else 1.0
    percent_increase = calculate_damage_output_percent_increase(
        normalized.main_base, normalized.main_skill, normalized.main_percent, normalized.main_notper,
        normalized.sub_base, normalized.sub_skill, normalized.sub_percent, normalized.sub_notper,
        normalized.attack_base, normalized.attack_skill, normalized.empress_blessing, normalized.weapon_fix, normalized.attack_percet, normalized.attack_notper, normalized.attack_shitu,
        normalized.dmg, normalized.dmg_skill, normalized.bossdmg, normalized.bossdmg_skill, normalized.dmg_shitu, normalized.cridmg, normalized.cridmg_skill, normalized.final_damage,
        normalized.ign, normalized.p2, normalized.boss_def,
        normalized.gwp_fd, normalized.mst_fd, data.weapon_rate,
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
    normalized = normalize_percent(data)
    equivalents = calculate_equivalent_increase(
        normalized.main_base, normalized.main_skill, normalized.main_percent, normalized.main_notper,
        normalized.sub_base, normalized.sub_skill, normalized.sub_percent, normalized.sub_notper,
        normalized.attack_base, normalized.attack_skill, normalized.empress_blessing, normalized.weapon_fix, normalized.attack_percet, normalized.attack_notper, normalized.attack_shitu,
        normalized.dmg, normalized.dmg_skill, normalized.bossdmg, normalized.bossdmg_skill, normalized.dmg_shitu, normalized.cridmg, normalized.cridmg_skill, normalized.final_damage,
        normalized.ign, normalized.p2, normalized.boss_def,
        normalized.gwp_fd, normalized.mst_fd, data.weapon_rate,
        base_field=base_field,
        step=1.0,
    )
    items = []
    for item in equivalent_fields():
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
    normalized = normalize_percent(data)
    attribute = build_attribute(normalized)
    damage = build_damage(normalized)
    attack = build_attack(normalized, weapon_fix=None)
    ign_obj = IGN(normalized.ign, normalized.p2)
    combat = CombatPower(attribute, attack, damage, ign_obj, normalized.gwp_fd, normalized.mst_fd, data.weapon_rate)
    weapon_fix = combat.calculate_weapon_fix(data.known_cp)
    return {"weapon_fix": weapon_fix}
