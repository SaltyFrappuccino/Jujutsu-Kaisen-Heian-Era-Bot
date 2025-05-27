from utils import calculate_actual_stats, get_stat_display_name, get_learned_technique_display_name, get_all_learned_technique_keys

def format_character_full_info(char_data_row):
    if not char_data_row:
        return "Персонаж не найден."
    char_data = dict(char_data_row) 

    actual_stats = calculate_actual_stats(char_data) 
    info = []
    info.append(f"👤 Полное Имя: {char_data['full_name']}")
    info.append(f"🎂 Возраст: {char_data.get('age', 'Не указан')}")
    info.append(f"🚻 Пол: {char_data.get('gender', 'Не указан')}")
    info.append(f"🚩 Принадлежность/Фракция: {char_data.get('faction', 'Не указана')}")
    info.append("\n📜 Внешность:")
    info.append(f"{char_data.get('appearance', 'Описание отсутствует.')}")

    info.append("\n📊 Характеристики Персонажа:")
    info.append("  Развитие Проклятой Энергии:")
    info.append(f"    Уровень Запаса ПЭ: [{char_data['level_cursed_energy_reserve']}] (Макс. CP: {actual_stats['max_cp']})")
    info.append(f"    Уровень Выброса ПЭ: [{char_data['level_cursed_energy_output']}] (Лимит CP за действие: {actual_stats['max_cp_output']})")
    info.append(f"    Уровень Контроля ПЭ: [{char_data['level_cursed_energy_control']}] (Область усиления: {actual_stats['cursed_energy_control_area']})")

    info.append("  Физическое Развитие:")
    info.append(f"    Уровень Базовой Силы: [{char_data['level_base_strength']}] (S: {actual_stats['base_strength_value']})")
    info.append(f"    Уровень Базовой Прочности: [{char_data['level_base_durability']}] (S: {actual_stats['base_durability_value']})")
    info.append(f"    Уровень Базовой Скорости: [{char_data['level_base_speed']}] (V: {actual_stats['base_speed_value']} м/с)")
    info.append(f"    Уровень Стойкости: [{char_data['level_stamina']}] (Снижение штрафа: {actual_stats['stamina_penalty_reduction']*100}%)")

    info.append("  Мастерство Проклятой Техники:")
    info.append(f"    Уровень Мастерства Техники: [{char_data['level_cursed_technique_mastery']}]")
    info.append(f"    Уровень Сплетения Абсолютной Пустоты: [{char_data['level_absolute_void_weaving']}] (Сила: {actual_stats['absolute_void_weaving_power']} CP)")
    info.append(f"    Уровень Цветка Падающих Эмоций: [{char_data['level_falling_emotions_flower']}] (Сила: {actual_stats['falling_emotions_flower_power']} CP)")


    info.append("  Развитие Барьерных Техник и РТ:")
    info.append(f"    Уровень Утончённости Территории: [{char_data['level_territory_refinement']}] (Сила РТ: {actual_stats['territory_refinement_power']} CP)")
    info.append(f"    Уровень Прочности Барьера РТ: [{char_data['level_territory_barrier_strength']}] (Внешн: {actual_stats['territory_barrier_strength_outside']} S / Внутр: {actual_stats['territory_barrier_strength_inside']} S)")

    info.append("  Развитие Обратной Проклятой Техники (ОПТ):")
    info.append(f"    Уровень Выброса ОПТ: [{char_data['level_reverse_cursed_technique_output']}] (Лимит генерации P+: {actual_stats['reverse_cursed_technique_output_value']})")
    info.append(f"    Уровень Эффективности ОПТ: [{char_data['level_reverse_cursed_technique_efficiency']}]")

    info.append("  Развитие Боевого Мастерства:")
    info.append(f"    Уровень Чёрной Вспышки (Шанс): [{char_data['level_black_flash_chance']}] (Нужен бросок ≤ {actual_stats['black_flash_chance_roll_needed']} на d20)")
    info.append(f"    Уровень Чёрной Вспышки (Лимит): [{char_data['level_black_flash_limit']}] (Лимит за бой: {actual_stats['black_flash_limit_value']})")

    info.append("\n🌀 Проклятая Техника:")
    info.append(f"{char_data.get('cursed_technique_description', 'Описание отсутствует.')}")

    info.append("\n🎒 Снаряжение:")
    info.append(f"{char_data.get('equipment', 'Снаряжение отсутствует.')}")

    info.append("\n💡 Изученные Общие Техники:")
    learned_any = False
    for tech_key in get_all_learned_technique_keys():
        if char_data.get(tech_key, False): 
            info.append(f"  - {get_learned_technique_display_name(tech_key)}")
            learned_any = True
    if not learned_any:
        info.append("  Нет изученных общих техник.")

    info.append(f"\n✨ Очки Развития (ОР): {char_data.get('rp_points', 0)}")
    info.append(f"💰 Баланс: {char_data.get('balance', 0)} ¥")

    return "\n".join(info)

def format_character_basic_info(char_data_row):
    if not char_data_row:
        return "Персонаж не найден."
    char_data = dict(char_data_row) 
    info = [
        f"👤 Полное Имя: {char_data['full_name']}",
        f"🎂 Возраст: {char_data.get('age', 'Не указан')}",
        f"🚻 Пол: {char_data.get('gender', 'Не указан')}",
        f"🚩 Принадлежность/Фракция: {char_data.get('faction', 'Не указана')}",
        "\n📜 Внешность:",
        f"{char_data.get('appearance', 'Описание отсутствует.')}"
    ]
    return "\n".join(info)

def format_character_stats_info(char_data_row):
    if not char_data_row:
        return "Персонаж не найден."
    char_data = dict(char_data_row)

    actual_stats = calculate_actual_stats(char_data) 
    info = ["📊 Характеристики Персонажа:"]
    info.append("  Развитие Проклятой Энергии:")
    info.append(f"    Уровень Запаса ПЭ: [{char_data['level_cursed_energy_reserve']}] (Макс. CP: {actual_stats['max_cp']})")
    info.append(f"    Уровень Выброса ПЭ: [{char_data['level_cursed_energy_output']}] (Лимит CP за действие: {actual_stats['max_cp_output']})")
    info.append(f"    Уровень Контроля ПЭ: [{char_data['level_cursed_energy_control']}] (Область усиления: {actual_stats['cursed_energy_control_area']})")

    info.append("  Физическое Развитие:")
    info.append(f"    Уровень Базовой Силы: [{char_data['level_base_strength']}] (S: {actual_stats['base_strength_value']})")
    info.append(f"    Уровень Базовой Прочности: [{char_data['level_base_durability']}] (S: {actual_stats['base_durability_value']})")
    info.append(f"    Уровень Базовой Скорости: [{char_data['level_base_speed']}] (V: {actual_stats['base_speed_value']} м/с)")
    info.append(f"    Уровень Стойкости: [{char_data['level_stamina']}] (Снижение штрафа: {actual_stats['stamina_penalty_reduction']*100}%)")

    info.append("  Мастерство Проклятой Техники:")
    info.append(f"    Уровень Мастерства Техники: [{char_data['level_cursed_technique_mastery']}]")
    info.append(f"    Уровень Сплетения Абсолютной Пустоты: [{char_data['level_absolute_void_weaving']}] (Сила: {actual_stats['absolute_void_weaving_power']} CP)")
    info.append(f"    Уровень Цветка Падающих Эмоций: [{char_data['level_falling_emotions_flower']}] (Сила: {actual_stats['falling_emotions_flower_power']} CP)")


    info.append("  Развитие Барьерных Техник и РТ:")
    info.append(f"    Уровень Утончённости Территории: [{char_data['level_territory_refinement']}] (Сила РТ: {actual_stats['territory_refinement_power']} CP)")
    info.append(f"    Уровень Прочности Барьера РТ: [{char_data['level_territory_barrier_strength']}] (Внешн: {actual_stats['territory_barrier_strength_outside']} S / Внутр: {actual_stats['territory_barrier_strength_inside']} S)")

    info.append("  Развитие Обратной Проклятой Техники (ОПТ):")
    info.append(f"    Уровень Выброса ОПТ: [{char_data['level_reverse_cursed_technique_output']}] (Лимит генерации P+: {actual_stats['reverse_cursed_technique_output_value']})")
    info.append(f"    Уровень Эффективности ОПТ: [{char_data['level_reverse_cursed_technique_efficiency']}]")

    info.append("  Развитие Боевого Мастерства:")
    info.append(f"    Уровень Чёрной Вспышки (Шанс): [{char_data['level_black_flash_chance']}] (Нужен бросок ≤ {actual_stats['black_flash_chance_roll_needed']} на d20)")
    info.append(f"    Уровень Чёрной Вспышки (Лимит): [{char_data['level_black_flash_limit']}] (Лимит за бой: {actual_stats['black_flash_limit_value']})")

    return "\n".join(info)

def format_cursed_technique_info(char_data_row):
    if not char_data_row:
        return "Персонаж не найден."
    char_data = dict(char_data_row) 
    return f"🌀 Проклятая Техника:\n{char_data.get('cursed_technique_description', 'Описание отсутствует.')}"

def format_equipment_info(char_data_row):
    if not char_data_row:
        return "Персонаж не найден."
    char_data = dict(char_data_row) 
    return f"🎒 Снаряжение:\n{char_data.get('equipment', 'Снаряжение отсутствует.')}"

def format_learned_techniques_info(char_data_row):
    if not char_data_row:
        return "Персонаж не найден."
    char_data = dict(char_data_row) 

    info = ["💡 Изученные Общие Техники:"]
    learned_any = False
    for tech_key in get_all_learned_technique_keys():
        if char_data.get(tech_key, False): 
            info.append(f"  - {get_learned_technique_display_name(tech_key)}")
            learned_any = True
    if not learned_any:
        info.append("  Нет изученных общих техник.")
    return "\n".join(info)

def get_default_stats_for_creation():
    return {
        "level_cursed_energy_reserve": 2,
        "level_cursed_energy_output": 2,
        "level_cursed_energy_control": 1,
        "level_base_strength": 1,
        "level_base_durability": 1,
        "level_base_speed": 10,
        "level_stamina": 0,
        "level_cursed_technique_mastery": 0,
        "level_territory_refinement": 0,
        "level_territory_barrier_strength": 0,
        "level_reverse_cursed_technique_output": 0,
        "level_reverse_cursed_technique_efficiency": 0,
        "level_black_flash_chance": 0,
        "level_black_flash_limit": 0,
        "level_absolute_void_weaving": 0,
        "level_falling_emotions_flower": 0,
    }