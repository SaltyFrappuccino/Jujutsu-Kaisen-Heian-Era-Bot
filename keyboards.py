from vk_api.keyboard import VkKeyboard, VkKeyboardColor

STATS_PER_PAGE = 7
ADMIN_ITEMS_PER_PAGE = 8
ADMIN_STATS_PER_PAGE = 7

def get_main_menu_keyboard(is_admin=False):
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Просмотреть всю Анкету", color=VkKeyboardColor.PRIMARY); keyboard.add_line()
    keyboard.add_button("Просмотреть основную информацию", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("Просмотреть характеристики", color=VkKeyboardColor.SECONDARY); keyboard.add_line()
    keyboard.add_button("Просмотреть Проклятую Технику", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("Просмотреть Снаряжение", color=VkKeyboardColor.SECONDARY); keyboard.add_line()
    keyboard.add_button("Изученные Общие Техники", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("Потратить ОР", color=VkKeyboardColor.POSITIVE); keyboard.add_line()
    keyboard.add_button("Маркет (Магазин)", color=VkKeyboardColor.SECONDARY)
    keyboard.add_button("Узнать баланс", color=VkKeyboardColor.PRIMARY)
    if is_admin: keyboard.add_line(); keyboard.add_button("Админ Панель", color=VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()

def get_admin_panel_keyboard():
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Добавить Персонажа", color=VkKeyboardColor.POSITIVE)
    keyboard.add_button("Редактировать Персонажа", color=VkKeyboardColor.PRIMARY); keyboard.add_line()
    keyboard.add_button("Просмотреть Анкеты", color=VkKeyboardColor.PRIMARY); keyboard.add_line()
    keyboard.add_button("Назад в Главное Меню", color=VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()

def get_back_to_main_menu_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Назад в Главное Меню", color=VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()

def get_back_to_admin_panel_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Назад в Админ Панель", color=VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()

def get_skip_button_keyboard():
    keyboard = VkKeyboard(one_time=True); keyboard.add_button("Пропустить", color=VkKeyboardColor.SECONDARY); return keyboard.get_keyboard()

def get_confirm_cancel_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Подтвердить", color=VkKeyboardColor.POSITIVE); keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()

def get_text_input_done_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Готово (сохранить текст)", color=VkKeyboardColor.POSITIVE); keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()

def get_user_character_selection_keyboard(characters_list, action_to_perform):
    keyboard = VkKeyboard(one_time=True)
    if not characters_list: keyboard.add_button("У вас нет персонажей", color=VkKeyboardColor.NEGATIVE)
    else:
        for i, char_data in enumerate(characters_list):
            if i >= 9: keyboard.add_button("Больше персонажей...", VkKeyboardColor.DEFAULT); keyboard.add_line(); break
            label = char_data['full_name']
            if len(label) > 35: label = label[:32] + "..."
            keyboard.add_button(label, color=VkKeyboardColor.PRIMARY, payload={"action": "user_select_char", "char_id": char_data['id'], "next_action": action_to_perform})
            keyboard.add_line()
    keyboard.add_button("Отмена", color=VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()

def get_admin_character_list_keyboard(characters_list, for_action="view", current_page=0):
    keyboard = VkKeyboard(one_time=True)
    payload_action_prefix = "admin_select_char_view" if for_action == "view" else "select_char_edit"
    total_items = len(characters_list)
    start_index = current_page * ADMIN_ITEMS_PER_PAGE
    end_index = start_index + ADMIN_ITEMS_PER_PAGE
    paginated_list = characters_list[start_index:end_index]

    if not paginated_list and current_page == 0:
        keyboard.add_button("Нет персонажей", color=VkKeyboardColor.NEGATIVE); keyboard.add_line()
    else:
        for char_data in paginated_list:
            label = f"{char_data['full_name']} (ID: {char_data['id']})"
            if len(label) > 35: label = label[:32] + "..."
            keyboard.add_button(label, color=VkKeyboardColor.PRIMARY, payload={"action": payload_action_prefix, "char_id": char_data['id']})
            keyboard.add_line()
    nav_buttons_row = []
    if current_page > 0:
        nav_buttons_row.append({"label": "<< Назад", "payload": {"action": "admin_char_list_page", "page": current_page - 1, "for_action": for_action}})
    if end_index < total_items:
        nav_buttons_row.append({"label": "Вперед >>", "payload": {"action": "admin_char_list_page", "page": current_page + 1, "for_action": for_action}})
    if nav_buttons_row:
        for btn in nav_buttons_row: keyboard.add_button(btn["label"], color=VkKeyboardColor.SECONDARY, payload=btn["payload"])
        if not keyboard.lines[-1]:
            pass
        else:
            keyboard.add_line()
    elif paginated_list and keyboard.lines and keyboard.lines[-1]:
         pass
    keyboard.add_button("Назад в Админ Панель", color=VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()

def get_stat_selection_keyboard(character_all_data_dict, available_rp, current_page=0):
    from utils import get_stat_display_name, get_stat_upgrade_cost, get_all_stat_keys
    keyboard = VkKeyboard(one_time=True)
    if character_all_data_dict is None:
        keyboard.add_button("Ошибка данных персонажа", VkKeyboardColor.NEGATIVE); keyboard.add_line()
        keyboard.add_button("Назад в Главное Меню", VkKeyboardColor.SECONDARY); return keyboard.get_keyboard()
    eligible_stats = []
    all_stat_keys_ordered = get_all_stat_keys()
    stat_dependencies = {
        "level_falling_emotions_flower": "has_falling_blossom_emotion_sense",
        "level_territory_refinement": "has_incomplete_domain_expansion",
        "level_territory_barrier_strength": "has_incomplete_domain_expansion",
        "level_reverse_cursed_technique_output": "has_reverse_cursed_technique_learned",
        "level_reverse_cursed_technique_efficiency": "has_reverse_cursed_technique_learned",
        "level_black_flash_chance": "has_black_flash_learned", "level_black_flash_limit": "has_black_flash_learned",
    }
    for stat_key in all_stat_keys_ordered:
        if stat_key not in character_all_data_dict: continue
        dependency_field = stat_dependencies.get(stat_key)
        if dependency_field and not character_all_data_dict.get(dependency_field, False): continue
        current_level = character_all_data_dict[stat_key]; cost_next_level = get_stat_upgrade_cost(stat_key, current_level)
        if cost_next_level != float('inf') and cost_next_level <= available_rp:
            eligible_stats.append({"key": stat_key, "label": f"{get_stat_display_name(stat_key)} ({current_level})", "payload": {"action": "spend_rp_select_stat", "stat": stat_key}})
    total_eligible_stats = len(eligible_stats)
    start_index = current_page * STATS_PER_PAGE; end_index = start_index + STATS_PER_PAGE
    stats_on_this_page = eligible_stats[start_index:end_index]
    for stat_info in stats_on_this_page:
        label_to_show = stat_info["label"];
        if len(label_to_show) > 40: label_to_show = label_to_show[:37] + "..."
        keyboard.add_button(label_to_show, color=VkKeyboardColor.PRIMARY, payload=stat_info["payload"]); keyboard.add_line()
    if not stats_on_this_page and total_eligible_stats == 0 : print("DEBUG KEYBOARDS: No eligible stats to display for user spend RP.")
    nav_buttons_current_row = []
    if current_page > 0: nav_buttons_current_row.append({"label": "<< Назад (статы)", "color": VkKeyboardColor.SECONDARY, "payload": {"action": "stat_page", "page": current_page - 1}})
    if end_index < total_eligible_stats: nav_buttons_current_row.append({"label": "Вперед (статы) >>", "color": VkKeyboardColor.SECONDARY, "payload": {"action": "stat_page", "page": current_page + 1}})
    if nav_buttons_current_row:
        for btn_info in nav_buttons_current_row: keyboard.add_button(btn_info["label"], color=btn_info["color"], payload=btn_info["payload"])
        keyboard.add_line()
    keyboard.add_button("Назад в Главное Меню", color=VkKeyboardColor.SECONDARY)
    return keyboard.get_keyboard()

def get_admin_edit_character_actions_keyboard(char_id):
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button("Изменить Общую Информацию", color=VkKeyboardColor.PRIMARY, payload={"action": "edit_char_info_menu", "char_id": char_id}); keyboard.add_line()
    keyboard.add_button("Изменить Стат", color=VkKeyboardColor.PRIMARY, payload={"action": "edit_char_stat_menu", "char_id": char_id, "page": 0}); keyboard.add_line()
    keyboard.add_button("Выдать/Забрать ОР", color=VkKeyboardColor.POSITIVE, payload={"action": "edit_char_rp", "char_id": char_id})
    keyboard.add_button("Выдать/Забрать Валюту", color=VkKeyboardColor.POSITIVE, payload={"action": "edit_char_balance", "char_id": char_id}); keyboard.add_line()
    keyboard.add_button("Изменить Проклятую Технику", color=VkKeyboardColor.PRIMARY, payload={"action": "edit_char_ct", "char_id": char_id})
    keyboard.add_button("Изменить Снаряжение", color=VkKeyboardColor.PRIMARY, payload={"action": "edit_char_equip", "char_id": char_id}); keyboard.add_line()
    keyboard.add_button("Изменить Изученные Техники", color=VkKeyboardColor.PRIMARY, payload={"action": "edit_char_learned_tech_menu", "char_id": char_id}); keyboard.add_line()
    keyboard.add_button("Назад к выбору персонажа", color=VkKeyboardColor.SECONDARY, payload={"action": "back_to_char_select_edit"})
    return keyboard.get_keyboard()

def get_admin_edit_general_info_fields_keyboard(char_id):
    keyboard = VkKeyboard(one_time=True)
    fields = {"full_name": "Полное Имя", "age": "Возраст", "gender": "Пол", "faction": "Фракция", "appearance": "Внешность"}
    for i, (field_key, field_name) in enumerate(fields.items()):
        if i >= 9: break
        keyboard.add_button(field_name, color=VkKeyboardColor.PRIMARY, payload={"action": "select_edit_field", "char_id": char_id, "field": field_key}); keyboard.add_line()
    keyboard.add_button("Назад (к действиям с персонажем)", color=VkKeyboardColor.SECONDARY, payload={"action": "back_to_edit_actions", "char_id": char_id})
    return keyboard.get_keyboard()

def get_admin_edit_stat_fields_keyboard(char_id, character_data_dict, current_page=0):
    from utils import get_stat_display_name, get_all_stat_keys
    keyboard = VkKeyboard(one_time=True)
    all_stat_keys_ordered = get_all_stat_keys()
    eligible_stats_for_edit = []
    if character_data_dict:
        for stat_key in all_stat_keys_ordered:
            if stat_key in character_data_dict: eligible_stats_for_edit.append(stat_key)
    total_stats = len(eligible_stats_for_edit)
    start_index = current_page * ADMIN_STATS_PER_PAGE; end_index = start_index + ADMIN_STATS_PER_PAGE
    stats_on_this_page_keys = eligible_stats_for_edit[start_index:end_index]

    if character_data_dict is None: keyboard.add_button("Ошибка: нет данных персонажа", VkKeyboardColor.NEGATIVE); keyboard.add_line()
    elif not stats_on_this_page_keys and current_page == 0: keyboard.add_button("Нет статов для редактирования", VkKeyboardColor.DEFAULT); keyboard.add_line()
    else:
        for stat_key in stats_on_this_page_keys:
            level = character_data_dict.get(stat_key, 0)
            label = f"{get_stat_display_name(stat_key)}: {level}"
            if len(label) > 40: label = label[:37]+"..."
            keyboard.add_button(label, color=VkKeyboardColor.PRIMARY, payload={"action": "select_edit_stat", "char_id": char_id, "stat": stat_key}); keyboard.add_line()
    nav_buttons_row = []
    if current_page > 0: nav_buttons_row.append({"label": "<< Назад (статы)", "payload": {"action": "admin_edit_stat_page", "char_id": char_id, "page": current_page - 1}})
    if end_index < total_stats: nav_buttons_row.append({"label": "Вперед (статы) >>", "payload": {"action": "admin_edit_stat_page", "char_id": char_id, "page": current_page + 1}})
    if nav_buttons_row:
        for btn_info in nav_buttons_row: keyboard.add_button(btn_info["label"], color=VkKeyboardColor.SECONDARY, payload=btn_info["payload"])
        keyboard.add_line()
    keyboard.add_button("Назад (к действиям с персонажем)", color=VkKeyboardColor.SECONDARY, payload={"action": "back_to_edit_actions", "char_id": char_id})
    return keyboard.get_keyboard()

def get_admin_edit_learned_techniques_keyboard(char_id, character_data_dict):
    from utils import get_learned_technique_display_name, get_all_learned_technique_keys
    keyboard = VkKeyboard(one_time=True)
    buttons_added = 0; ordered_tech_keys = get_all_learned_technique_keys()
    if character_data_dict is None: keyboard.add_button("Ошибка: нет данных персонажа", VkKeyboardColor.NEGATIVE); keyboard.add_line()
    else:
        for tech_key in ordered_tech_keys:
            if tech_key not in character_data_dict: continue
            if buttons_added >= 9 : break
            is_learned = character_data_dict.get(tech_key, False)
            status_emoji = "✅" if is_learned else "❌"
            label = f"{status_emoji} {get_learned_technique_display_name(tech_key)}"
            if len(label)>40: label = label[:37]+"..."
            keyboard.add_button(label, color=VkKeyboardColor.PRIMARY, payload={"action": "toggle_learned_tech", "char_id": char_id, "tech": tech_key}); keyboard.add_line()
            buttons_added +=1
    keyboard.add_button("Назад (к действиям с персонажем)", color=VkKeyboardColor.SECONDARY, payload={"action": "back_to_edit_actions", "char_id": char_id})
    return keyboard.get_keyboard()

def get_gender_selection_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Мужской", color=VkKeyboardColor.PRIMARY); keyboard.add_button("Женский", color=VkKeyboardColor.PRIMARY); keyboard.add_button("Иное", color=VkKeyboardColor.PRIMARY)
    keyboard.add_line(); keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()

def get_cancel_keyboard():
    keyboard = VkKeyboard(one_time=True)
    keyboard.add_button("Отмена", color=VkKeyboardColor.NEGATIVE)
    return keyboard.get_keyboard()