import re
from config import MAX_MESSAGE_LENGTH

def split_message(text, max_length=MAX_MESSAGE_LENGTH):
    parts = []
    if not text: 
        return [""]
    while len(text) > max_length:
        split_pos = text.rfind('\n', 0, max_length)
        if split_pos == -1: 
            split_pos = max_length
        parts.append(text[:split_pos])
        text = text[split_pos:].lstrip('\n') 
    parts.append(text)
    return parts

def parse_user_mention(mention_text):
    match = re.search(r"\[id(\d+)\|.*?\]", mention_text)
    if match:
        return int(match.group(1))
    return None

def get_stat_display_name(stat_key):
    names = {
        "level_cursed_energy_reserve": "Уровень Запаса ПЭ",
        "level_cursed_energy_output": "Уровень Выброса ПЭ",
        "level_cursed_energy_control": "Уровень Контроля ПЭ",
        "level_base_strength": "Уровень Базовой Силы",
        "level_base_durability": "Уровень Базовой Прочности",
        "level_base_speed": "Уровень Базовой Скорости",
        "level_stamina": "Уровень Стойкости",
        "level_cursed_technique_mastery": "Уровень Мастерства Техники",
        "level_absolute_void_weaving": "Уровень Сплетения Абсолютной Пустоты",
        "level_falling_emotions_flower": "Уровень Цветка Падающих Эмоций",
        "level_territory_refinement": "Уровень Утончённости Территории",
        "level_territory_barrier_strength": "Уровень Прочности Барьера РТ",
        "level_reverse_cursed_technique_output": "Уровень Выброса ОПТ",
        "level_reverse_cursed_technique_efficiency": "Уровень Эффективности ОПТ",
        "level_black_flash_chance": "Уровень Чёрной Вспышки (Шанс)",
        "level_black_flash_limit": "Уровень Чёрной Вспышки (Лимит)",
        "full_name": "Полное Имя", "age": "Возраст", "gender": "Пол",
        "faction": "Фракция", "appearance": "Внешность"
    }
    return names.get(stat_key, stat_key.replace("level_", "").replace("_", " ").capitalize())

def get_learned_technique_display_name(tech_key):
    names = {
        "has_simple_domain": "Простая Территория",
        "has_falling_blossom_emotion_sense": "Чувства Опадающего Цветка",
        "has_black_flash_learned": "Чёрная Вспышка",
        "has_reverse_cursed_technique_learned": "Обратная Проклятая Техника",
        "has_reverse_cursed_technique_output_learned": "Выброс Обратной Проклятой Техники",
        "has_incomplete_domain_expansion": "Неполноценное Расширение Территории",
        "has_domain_expansion": "Расширение Территории",
        "has_domain_amplification": "Усиление Территории",
        "has_barrierless_domain_expansion": "Безбарьерное Расширение Территории"
    }
    return names.get(tech_key, tech_key.replace("has_", "").replace("_", " ").capitalize())

def get_all_stat_keys(): 
    return [
        "level_cursed_energy_reserve", 
        "level_cursed_energy_output", 
        "level_cursed_energy_control",
        "level_base_strength", 
        "level_base_durability", 
        "level_base_speed", 
        "level_stamina",
        "level_cursed_technique_mastery", 
        "level_absolute_void_weaving", 
        "level_falling_emotions_flower",
        "level_territory_refinement", 
        "level_territory_barrier_strength",
        "level_reverse_cursed_technique_output", 
        "level_reverse_cursed_technique_efficiency",
        "level_black_flash_chance", 
        "level_black_flash_limit"
    ]

def get_all_learned_technique_keys():
    return [
        "has_simple_domain", "has_falling_blossom_emotion_sense", "has_black_flash_learned",
        "has_reverse_cursed_technique_learned", "has_reverse_cursed_technique_output_learned",
        "has_incomplete_domain_expansion", "has_domain_expansion", "has_domain_amplification",
        "has_barrierless_domain_expansion"
    ]

def get_stat_upgrade_cost(stat_key, current_level):
    max_levels = {
        "level_cursed_energy_control": 4,
         "level_black_flash_chance": 19, 
    }

    if stat_key in max_levels and current_level >= max_levels[stat_key]:
        print(f"DEBUG UTILS (get_stat_upgrade_cost): Stat '{stat_key}' at max level ({current_level}). Cost is infinite.")
        return float('inf')

    base_costs = {
        "level_cursed_energy_reserve": lambda lvl: 1,
        "level_cursed_energy_output": lambda lvl: 1,
        "level_cursed_energy_control": lambda lvl: 5,
        "level_base_strength": lambda lvl: 1,
        "level_base_durability": lambda lvl: 1,
        "level_base_speed": lambda lvl: 1,
        "level_stamina": lambda lvl: 5 + lvl * 5, 
        "level_cursed_technique_mastery": lambda lvl: 5 + lvl * 5,
        "level_absolute_void_weaving": lambda lvl: 3 + lvl * 3,
        "level_falling_emotions_flower": lambda lvl: 3 + lvl * 3,
        "level_territory_refinement": lambda lvl: 5 + lvl * 5,
        "level_territory_barrier_strength": lambda lvl: 5 + lvl * 5,
        "level_reverse_cursed_technique_output": lambda lvl: 2,
        "level_reverse_cursed_technique_efficiency": lambda lvl: 5 + lvl * 5, 
        "level_black_flash_chance": lambda lvl: 5 + lvl * 5, 
        "level_black_flash_limit": lambda lvl: 5 + lvl * 5,  
    }
    cost_func = base_costs.get(stat_key)
    if cost_func:
        return cost_func(current_level)
    else:
        print(f"WARNING UTILS (get_stat_upgrade_cost): No cost function found for stat_key '{stat_key}'. Returning infinite cost.")
        return float('inf') 

def calculate_actual_stats(char_data_row): 
    char_data = dict(char_data_row) if not isinstance(char_data_row, dict) else char_data_row
    
    stats = {}
    stats['max_cp'] = char_data.get('level_cursed_energy_reserve', 0) * 2000
    stats['max_cp_output'] = char_data.get('level_cursed_energy_output', 0) * 500

    control_levels_map = {
        0: "Усиление недоступно (Контроль 0)", 
        1: "Точечно", 
        2: "Маленькие области", 
        3: "Средние области", 
        4: "Всё тело"
    }
    control_level_value = char_data.get('level_cursed_energy_control', 0)
    stats['cursed_energy_control_area'] = control_levels_map.get(control_level_value, f"Неизвестно (Уровень {control_level_value})")
    
    if control_level_value == 0 and \
       (char_data.get('level_cursed_energy_reserve', 0) > 0 or \
        char_data.get('level_cursed_energy_output', 0) > 0):
        stats['cursed_energy_control_area'] = "Усиление недоступно (Контроль 0)"


    stats['base_strength_value'] = char_data.get('level_base_strength', 0) * 250
    stats['base_durability_value'] = char_data.get('level_base_durability', 0) * 250
    stats['base_speed_value'] = char_data.get('level_base_speed', 0) * 0.5
    stats['stamina_penalty_reduction'] = char_data.get('level_stamina', 0) * 0.01 

    stats['absolute_void_weaving_power'] = char_data.get('level_absolute_void_weaving', 0) * 1000
    stats['falling_emotions_flower_power'] = char_data.get('level_falling_emotions_flower', 0) * 1000

    stats['territory_refinement_power'] = char_data.get('level_territory_refinement', 0) * 1000
    stats['territory_barrier_strength_inside'] = char_data.get('level_territory_barrier_strength', 0) * 20000
    stats['territory_barrier_strength_outside'] = char_data.get('level_territory_barrier_strength', 0) * 10000

    stats['reverse_cursed_technique_output_value'] = char_data.get('level_reverse_cursed_technique_output', 0) * 250
    
    black_flash_chance_level = char_data.get('level_black_flash_chance', 0)
    stats['black_flash_chance_roll_needed'] = max(1, 20 - black_flash_chance_level) 
    stats['black_flash_limit_value'] = char_data.get('level_black_flash_limit', 0)

    return stats

def calculate_total_upgrade_cost(stat_key, current_level, levels_to_add, available_rp):
    max_levels_map = {"level_cursed_energy_control": 4, "level_black_flash_chance": 19}
    total_cost = 0; simulated_level = current_level; actual_levels_added = 0
    for i in range(levels_to_add):
        if stat_key in max_levels_map and simulated_level >= max_levels_map[stat_key]:
            if i == 0: return 0, simulated_level, 0, f"'{get_stat_display_name(stat_key)}' уже на макс. уровне ({max_levels_map[stat_key]})."
            else: return total_cost, simulated_level, actual_levels_added, f"Можно улучшить только до ур. {simulated_level} (макс.). Это будет стоить {total_cost} ОР."
        cost_for_this_level = get_stat_upgrade_cost(stat_key, simulated_level)
        if cost_for_this_level == float('inf'):
            if i == 0: return 0, simulated_level, 0, f"'{get_stat_display_name(stat_key)}' не улучшается."
            else: return total_cost, simulated_level, actual_levels_added, f"Можно улучшить только до ур. {simulated_level}. Это будет стоить {total_cost} ОР."
        if total_cost + cost_for_this_level > available_rp:
            if i == 0: return 0, simulated_level, 0, f"Недостаточно ОР ({available_rp}) для улучшения '{get_stat_display_name(stat_key)}' на 1 ур. (нужно {cost_for_this_level} ОР)."
            else: return total_cost, simulated_level, actual_levels_added, f"Хватит ОР только на {actual_levels_added} ур. (до {simulated_level}). Это будет стоить {total_cost} ОР."
        total_cost += cost_for_this_level; simulated_level += 1; actual_levels_added += 1
    return total_cost, simulated_level, actual_levels_added, None