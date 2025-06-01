# vk_rp_bot/user_handlers.py
import vk_api
from vk_api.utils import get_random_id
import json
from database import (
    get_character_by_id, get_characters_by_owner_id, get_character_by_owner_id, # get_characters_by_owner_id возвращает СПИСОК
    set_user_state, get_user_state, clear_user_state,
    update_character_multiple_fields
)
from keyboards import (
    get_main_menu_keyboard, get_stat_selection_keyboard,
    get_confirm_cancel_keyboard, get_user_character_selection_keyboard # Клавиатура для выбора персонажа
)
from character_actions import (
    format_character_full_info, format_character_basic_info,
    format_character_stats_info, format_cursed_technique_info,
    format_equipment_info, format_learned_techniques_info
)
from utils import split_message, get_stat_upgrade_cost, get_stat_display_name, get_all_stat_keys # get_all_learned_technique_keys не используется здесь напрямую
from config import (
    ADMIN_IDS, STATE_MAIN_MENU,
    STATE_USER_SPEND_RP_CHOOSE_STAT, STATE_USER_SPEND_RP_CONFIRM,
    STATE_USER_CHOOSE_CHARACTER_ACTION # Состояние для выбора персонажа
)

def send_message_parts(vk, user_id, text, keyboard=None):
    parts = split_message(text)
    for i, part in enumerate(parts):
        current_keyboard = keyboard if i == len(parts) - 1 else None
        try:
            vk.messages.send(
                user_id=user_id,
                message=part,
                random_id=get_random_id(),
                keyboard=current_keyboard
            )
        except vk_api.exceptions.ApiError as e:
            print(f"Ошибка отправки сообщения пользователю {user_id}: {e}")
            if i == 0 :
                 vk.messages.send(
                    user_id=user_id,
                    message="Произошла ошибка при отображении. Попробуйте позже.",
                    random_id=get_random_id()
                )
            break

def handle_start(vk, event):
    user_id = event.obj.message['from_id']
    is_admin = user_id in ADMIN_IDS
    clear_user_state(user_id)
    set_user_state(user_id, STATE_MAIN_MENU)
    send_message_parts(vk, user_id, "Добро пожаловать! Выберите действие:", get_main_menu_keyboard(is_admin))

def _handle_action_with_character_selection(vk, user_id, text_command, action_name, character_list_rows, is_admin):
    """
    Вспомогательная функция для обработки действий, требующих выбора персонажа.
    character_list_rows - список объектов sqlite3.Row.
    """
    if not character_list_rows:
        send_message_parts(vk, user_id, "У вас еще нет персонажей.", get_main_menu_keyboard(is_admin))
        return

    # Преобразуем sqlite3.Row в список словарей для клавиатуры и дальнейшей обработки
    characters_as_dicts = [dict(row) for row in character_list_rows]

    if len(characters_as_dicts) == 1:
        selected_char_dict = characters_as_dicts[0]
        print(f"DEBUG USER_HANDLER: Auto-selected single character ID: {selected_char_dict['id']} for action: {action_name}")
        _process_user_action_for_character(vk, user_id, selected_char_dict, action_name, is_admin, state_data=None)
    else:
        set_user_state(user_id, STATE_USER_CHOOSE_CHARACTER_ACTION, {"pending_action": action_name, "action_text_command": text_command})
        keyboard = get_user_character_selection_keyboard(characters_as_dicts, action_name) # Передаем список словарей
        send_message_parts(vk, user_id, f"У вас несколько персонажей. Выберите, для какого персонажа выполнить действие '{text_command}':", keyboard)

def _process_user_action_for_character(vk, user_id, character_dict, action_name, is_admin, state_data):
    """
    Обрабатывает конкретное действие пользователя для выбранного персонажа.
    character_dict - словарь с данными персонажа.
    state_data - может содержать доп. информацию, например, для пагинации.
    """
    print(f"DEBUG USER_HANDLER (_process_user_action_for_character): Char ID: {character_dict.get('id')}, Action: {action_name}")
    # Убедимся, что character_dict не None
    if not character_dict:
        send_message_parts(vk, user_id, "Ошибка: данные персонажа не найдены.", get_main_menu_keyboard(is_admin))
        clear_user_state(user_id); set_user_state(user_id, STATE_MAIN_MENU)
        return

    # Важно: все функции format_* и get_stat_selection_keyboard должны принимать СЛОВАРЬ character_dict

    if action_name == "view_full_profile":
        info = format_character_full_info(character_dict)
        send_message_parts(vk, user_id, f"Полная анкета персонажа: {character_dict.get('full_name', '')}\n\n{info}", get_main_menu_keyboard(is_admin))
    elif action_name == "view_basic_info":
        info = format_character_basic_info(character_dict)
        send_message_parts(vk, user_id, f"Основная информация ({character_dict.get('full_name', '')}):\n\n{info}", get_main_menu_keyboard(is_admin))
    elif action_name == "view_stats":
        info = format_character_stats_info(character_dict)
        send_message_parts(vk, user_id, f"Характеристики ({character_dict.get('full_name', '')}):\n\n{info}", get_main_menu_keyboard(is_admin))
    elif action_name == "view_cursed_technique":
        info = format_cursed_technique_info(character_dict)
        send_message_parts(vk, user_id, f"Проклятая Техника ({character_dict.get('full_name', '')}):\n\n{info}", get_main_menu_keyboard(is_admin))
    elif action_name == "view_equipment":
        info = format_equipment_info(character_dict)
        send_message_parts(vk, user_id, f"Снаряжение ({character_dict.get('full_name', '')}):\n\n{info}", get_main_menu_keyboard(is_admin))
    elif action_name == "view_learned_techniques":
        info = format_learned_techniques_info(character_dict)
        send_message_parts(vk, user_id, f"Изученные техники ({character_dict.get('full_name', '')}):\n\n{info}", get_main_menu_keyboard(is_admin))
    elif action_name == "spend_rp":
        current_page = state_data.get("stat_page", 0) if state_data and state_data.get("char_id") == character_dict.get('id') else 0
        set_user_state(user_id, STATE_USER_SPEND_RP_CHOOSE_STAT, {"char_id": character_dict['id'], "stat_page": current_page})
        available_rp_value = character_dict.get('rp_points', 0)
        # character_dict уже словарь, передаем его напрямую
        keyboard_to_send = get_stat_selection_keyboard(character_dict, available_rp_value, current_page=current_page)
        send_message_parts(vk, user_id, f"Персонаж: {character_dict['full_name']}\nВыберите характеристику для улучшения (Стр. {current_page + 1}). У вас {available_rp_value} ОР.", keyboard_to_send)
        return # Не сбрасываем состояние здесь, т.к. перешли в другое
    elif action_name == "view_balance":
        send_message_parts(vk, user_id, f"Баланс персонажа {character_dict['full_name']}: {character_dict.get('balance', 0)} ¥", get_main_menu_keyboard(is_admin))
    else:
        send_message_parts(vk, user_id, "Неизвестное действие для персонажа.", get_main_menu_keyboard(is_admin))

    # После большинства действий просмотра, сбрасываем состояние и возвращаем в главное меню
    if action_name not in ["spend_rp"]: # spend_rp переводит в другое состояние
        clear_user_state(user_id); set_user_state(user_id, STATE_MAIN_MENU)


def handle_user_message(vk, event):
    user_id = event.obj.message['from_id']
    text_original = event.obj.message['text']
    text = text_original.strip()

    print(f"DEBUG USER_HANDLER: User {user_id} sent text='{text_original}' (stripped='{text}'), payload='{event.obj.message.get('payload')}'")

    raw_payload_from_event = event.obj.message.get('payload')
    payload = None
    if isinstance(raw_payload_from_event, str):
        try: payload = json.loads(raw_payload_from_event)
        except json.JSONDecodeError: print(f"USER_HANDLER: Warning: Could not decode payload string: {raw_payload_from_event}")
    elif isinstance(raw_payload_from_event, dict):
        payload = raw_payload_from_event

    is_admin = user_id in ADMIN_IDS
    current_state, state_data = get_user_state(user_id)
    state_data = state_data or {}

    user_characters_list_rows = get_characters_by_owner_id(user_id) # Список sqlite3.Row
    if user_characters_list_rows:
        print(f"DEBUG USER_HANDLER: User {user_id} has {len(user_characters_list_rows)} character(s).")
    else:
        print(f"DEBUG USER_HANDLER: User {user_id} has no characters.")

    if text.lower() == "отмена":
        if current_state == STATE_USER_CHOOSE_CHARACTER_ACTION: # Если отмена из выбора перса, просто в гл.меню
             clear_user_state(user_id); set_user_state(user_id, STATE_MAIN_MENU)
             send_message_parts(vk, user_id, "Выбор персонажа отменен. Главное меню.", get_main_menu_keyboard(is_admin))
        else: # Общая отмена
            clear_user_state(user_id); set_user_state(user_id, STATE_MAIN_MENU)
            send_message_parts(vk, user_id, "Действие отменено. Главное меню.", get_main_menu_keyboard(is_admin))
        return

    if current_state == STATE_USER_CHOOSE_CHARACTER_ACTION:
        if payload and payload.get("action") == "user_select_char":
            char_id_selected = payload.get("char_id")
            pending_action = payload.get("next_action") # Из payload кнопки выбора перса
            if not pending_action and state_data: pending_action = state_data.get("pending_action") # Запасной вариант

            if char_id_selected and pending_action:
                selected_character_row = get_character_by_id(char_id_selected)
                if selected_character_row and selected_character_row['owner_vk_id'] == user_id:
                    selected_character_dict = dict(selected_character_row)
                    _process_user_action_for_character(vk, user_id, selected_character_dict, pending_action, is_admin, state_data)
                else:
                    send_message_parts(vk, user_id, "Ошибка выбора персонажа или персонаж не найден.", get_main_menu_keyboard(is_admin))
                    clear_user_state(user_id); set_user_state(user_id, STATE_MAIN_MENU)
            else:
                send_message_parts(vk, user_id, "Ошибка при выборе персонажа. Попробуйте снова.", get_main_menu_keyboard(is_admin))
                clear_user_state(user_id); set_user_state(user_id, STATE_MAIN_MENU)
        elif text.lower() == "назад в главное меню": # Если пользователь нажал системную кнопку "Назад"
             clear_user_state(user_id); set_user_state(user_id, STATE_MAIN_MENU)
             send_message_parts(vk, user_id, "Главное меню.", get_main_menu_keyboard(is_admin))
        else: # Если текстовый ввод в состоянии выбора персонажа
            action_text_cmd = state_data.get("action_text_command", "выполнить действие") if state_data else "выполнить действие"
            characters_as_dicts_for_kb = [dict(row) for row in user_characters_list_rows] if user_characters_list_rows else []
            send_message_parts(vk, user_id, "Пожалуйста, выберите персонажа с помощью кнопок или нажмите 'Отмена'.",
                               get_user_character_selection_keyboard(characters_as_dicts_for_kb, state_data.get("pending_action", "unknown_action")))
        return

    if not current_state or current_state == STATE_MAIN_MENU :
        action_map = {
            "Просмотреть всю Анкету": "view_full_profile",
            "Просмотреть основную информацию": "view_basic_info",
            "Просмотреть характеристики": "view_stats",
            "Просмотреть Проклятую Технику": "view_cursed_technique",
            "Просмотреть Снаряжение": "view_equipment",
            "Изученные Общие Техники": "view_learned_techniques",
            "Потратить ОР": "spend_rp",
            "Узнать баланс": "view_balance"
        }
        requested_action_key = action_map.get(text)
        if requested_action_key:
            _handle_action_with_character_selection(vk, user_id, text, requested_action_key, user_characters_list_rows, is_admin)
        elif text == "Маркет (Магазин)":
            send_message_parts(vk, user_id, "Раздел 'Маркет' находится в разработке.", get_main_menu_keyboard(is_admin))
        elif text == "Админ Панель" and is_admin:
            from admin_handlers import handle_admin_command
            handle_admin_command(vk, event)
        elif text.lower() in ["начать", "старт", "/start"]:
            handle_start(vk, event)
        elif text and text.lower() != "назад в главное меню":
            if not (is_admin and text == "Админ Панель"):
                send_message_parts(vk, user_id, "Неизвестная команда. Используйте кнопки меню.", get_main_menu_keyboard(is_admin))
        return

    if current_state == STATE_USER_SPEND_RP_CHOOSE_STAT:
        char_id_for_rp = state_data.get("char_id")
        current_stat_page = state_data.get("stat_page", 0)
        active_character_row = get_character_by_id(char_id_for_rp) if char_id_for_rp else None
        active_character_dict = dict(active_character_row) if active_character_row else None

        if not active_character_dict:
            send_message_parts(vk, user_id, "Ошибка: не удалось найти данные персонажа для траты ОР.", get_main_menu_keyboard(is_admin))
            clear_user_state(user_id); set_user_state(user_id, STATE_MAIN_MENU); return

        if payload and payload.get("action") == "stat_page":
            new_page = payload.get("page", 0)
            set_user_state(user_id, STATE_USER_SPEND_RP_CHOOSE_STAT, {"char_id": char_id_for_rp, "stat_page": new_page})
            available_rp_value_state = active_character_dict.get('rp_points', 0)
            # Передаем active_character_dict (уже словарь)
            keyboard_to_send = get_stat_selection_keyboard(active_character_dict, available_rp_value_state, current_page=new_page)
            send_message_parts(vk, user_id, f"Персонаж: {active_character_dict['full_name']}\nВыберите характеристику (Стр. {new_page + 1}). У вас {available_rp_value_state} ОР.", keyboard_to_send)
        elif payload and payload.get("action") == "spend_rp":
            stat_to_upgrade = payload["stat"]
            if stat_to_upgrade not in active_character_dict:
                send_message_parts(vk, user_id, "Ошибка: выбранный стат не найден у персонажа.", get_main_menu_keyboard(is_admin))
                kb_err = get_stat_selection_keyboard(active_character_dict, active_character_dict.get('rp_points',0), current_page=current_stat_page)
                send_message_parts(vk, user_id, f"Выберите характеристику (Стр. {current_stat_page + 1}).", kb_err); return
            current_level = active_character_dict[stat_to_upgrade]
            cost = get_stat_upgrade_cost(stat_to_upgrade, current_level)
            if active_character_dict.get('rp_points', 0) >= cost:
                new_data_for_state = {"char_id": char_id_for_rp, "stat_to_upgrade": stat_to_upgrade, "cost": cost, "current_level": current_level, "previous_stat_page": current_stat_page}
                set_user_state(user_id, STATE_USER_SPEND_RP_CONFIRM, new_data_for_state)
                stat_name = get_stat_display_name(stat_to_upgrade)
                send_message_parts(vk, user_id, f"Персонаж: {active_character_dict['full_name']}\nУверены, что хотите улучшить '{stat_name}' (ур. {current_level} -> {current_level + 1}) за {cost} ОР?", get_confirm_cancel_keyboard())
            else:
                send_message_parts(vk, user_id, f"Недостаточно ОР. Требуется: {cost}, у вас: {active_character_dict.get('rp_points', 0)}.", get_main_menu_keyboard(is_admin))
                clear_user_state(user_id); set_user_state(user_id, STATE_MAIN_MENU)
        elif text.lower() == "назад в главное меню":
             clear_user_state(user_id); set_user_state(user_id, STATE_MAIN_MENU)
             send_message_parts(vk, user_id, "Главное меню.", get_main_menu_keyboard(is_admin))
        else:
            available_rp_value_state = active_character_dict.get('rp_points', 0)
            keyboard_to_send = get_stat_selection_keyboard(active_character_dict, available_rp_value_state, current_page=current_stat_page)
            send_message_parts(vk, user_id, f"Персонаж: {active_character_dict['full_name']}\nПожалуйста, выберите характеристику (Стр. {current_stat_page + 1}) или используйте кнопки навигации.", keyboard_to_send)
        return

    if current_state == STATE_USER_SPEND_RP_CONFIRM:
        char_id_for_confirm = state_data.get("char_id")
        previous_stat_page = state_data.get("previous_stat_page", 0)
        active_character_for_confirm_row = get_character_by_id(char_id_for_confirm) if char_id_for_confirm else None
        active_character_for_confirm_dict = dict(active_character_for_confirm_row) if active_character_for_confirm_row else None

        if not active_character_for_confirm_dict:
            send_message_parts(vk, user_id, "Ошибка: не удалось найти данные персонажа для подтверждения улучшения.", get_main_menu_keyboard(is_admin))
            clear_user_state(user_id); set_user_state(user_id, STATE_MAIN_MENU); return

        if text.lower() == "подтвердить":
            stat_to_upgrade = state_data.get("stat_to_upgrade")
            cost = state_data.get("cost"); current_level = state_data.get("current_level")
            if not all([stat_to_upgrade, isinstance(cost, (int, float)), isinstance(current_level, int)]):
                send_message_parts(vk, user_id, "Произошла ошибка (некорректные данные для подтверждения).", get_main_menu_keyboard(is_admin))
                clear_user_state(user_id); set_user_state(user_id, STATE_MAIN_MENU); return
            
            # Перепроверка ОР перед списанием (повторно получаем из БД, т.к. могли измениться)
            refreshed_char_row = get_character_by_id(char_id_for_confirm)
            if not refreshed_char_row: 
                send_message_parts(vk, user_id, "Ошибка: персонаж не найден для списания ОР.", get_main_menu_keyboard(is_admin)); 
                clear_user_state(user_id); set_user_state(user_id, STATE_MAIN_MENU); return
            refreshed_char_dict = dict(refreshed_char_row)

            if refreshed_char_dict.get('rp_points', 0) < cost:
                send_message_parts(vk, user_id, f"Недостаточно ОР ({refreshed_char_dict.get('rp_points', 'N/A')}). Улучшение отменено.", get_main_menu_keyboard(is_admin))
                clear_user_state(user_id); set_user_state(user_id, STATE_MAIN_MENU); return
            new_rp_points = refreshed_char_dict.get('rp_points', 0) - cost
            new_level = current_level + 1
            updates = { stat_to_upgrade: new_level, 'rp_points': new_rp_points }
            update_character_multiple_fields(refreshed_char_dict['id'], updates)
            stat_name = get_stat_display_name(stat_to_upgrade)
            send_message_parts(vk, user_id, f"Для персонажа {refreshed_char_dict['full_name']} характеристика '{stat_name}' улучшена до уровня {new_level}! Осталось ОР: {new_rp_points}.", get_main_menu_keyboard(is_admin))
            clear_user_state(user_id); set_user_state(user_id, STATE_MAIN_MENU)
        elif text.lower() == "отмена":
            set_user_state(user_id, STATE_USER_SPEND_RP_CHOOSE_STAT, {"char_id": char_id_for_confirm, "stat_page": previous_stat_page})
            rp_cancel = active_character_for_confirm_dict.get('rp_points', 0)
            kb_cancel = get_stat_selection_keyboard(active_character_for_confirm_dict, rp_cancel, current_page=previous_stat_page)
            send_message_parts(vk, user_id, f"Улучшение отменено. Персонаж: {active_character_for_confirm_dict['full_name']}\nВыберите характеристику (Стр. {previous_stat_page + 1}).", kb_cancel)
        else:
            send_message_parts(vk, user_id, "Пожалуйста, подтвердите или отмените действие.", get_confirm_cancel_keyboard())
        return

    if is_admin and current_state and current_state.startswith("admin_"):
        print(f"DEBUG USER_HANDLER: Passing to admin_handler for state {current_state}")
        from admin_handlers import handle_admin_command
        handle_admin_command(vk, event)
    elif current_state:
        print(f"DEBUG USER_HANDLER: Unhandled state '{current_state}' for user {user_id} with text '{text}'")
        send_message_parts(vk, user_id, "Произошла непредвиденная ситуация. Возврат в главное меню.", get_main_menu_keyboard(is_admin))
        clear_user_state(user_id); set_user_state(user_id, STATE_MAIN_MENU)