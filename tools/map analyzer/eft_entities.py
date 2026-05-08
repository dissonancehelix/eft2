from __future__ import annotations

from typing import Any

EFT_CLASSES = {
    "prop_ball",
    "info_player_red",
    "info_player_blue",
    "info_player_spectator",
    "trigger_goal",
    "trigger_ballreset",
    "trigger_hurt",
    "trigger_jumppad",
    "trigger_abspush",
    "trigger_powerup",
    "trigger_knockdown",
    "prop_goal",
    "logic_teamscore",
    "env_teamsound",
    "func_rotating",
}

TRIGGER_CLASSES = {
    "trigger_goal",
    "trigger_ballreset",
    "trigger_hurt",
    "trigger_jumppad",
    "trigger_abspush",
    "trigger_powerup",
    "trigger_knockdown",
    "trigger_multiple",
}


def classify_entities(entities: list[dict[str, Any]]) -> dict[str, Any]:
    by_class: dict[str, list[dict[str, Any]]] = {}
    relevant = []
    for ent in entities:
        cls = ent.get("classname", "")
        by_class.setdefault(cls, []).append(ent)
        if cls in EFT_CLASSES or cls in TRIGGER_CLASSES:
            relevant.append(_slim(ent))
    counts = {cls: len(items) for cls, items in sorted(by_class.items())}
    eft_counts = {cls: len(items) for cls, items in sorted(by_class.items()) if cls in EFT_CLASSES or cls in TRIGGER_CLASSES}
    return {"class_counts": counts, "eft_class_counts": eft_counts, "entities": relevant}


def _slim(ent: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": ent.get("id"),
        "classname": ent.get("classname"),
        "targetname": ent.get("targetname"),
        "origin": ent.get("origin"),
        "angles": ent.get("angles"),
        "keyvalues": ent.get("keyvalues", {}),
        "outputs": ent.get("outputs", []),
        "bounds": ent.get("bounds"),
    }

