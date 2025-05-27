import vk_api
from vk_api.utils import get_random_id
import json 
from database import get_character_by_owner_id, set_user_state, get_user_state, clear_user_state, update_character_multiple_fields
from keyboards import get_main_menu_keyboard, get_stat_selection_keyboard, get_confirm_cancel_keyboard
from character_actions import (
    format_character_full_info, format_character_basic_info,
    format_character_stats_info, format_cursed_technique_info,
    format_equipment_info, format_learned_techniques_info
)
from utils import split_message, get_stat_upgrade_cost, get_stat_display_name, get_all_stat_keys, get_all_learned_technique_keys
from config import ADMIN_IDS, STATE_MAIN_MENU, STATE_USER_SPEND_RP_CHOOSE_STAT, STATE_USER_SPEND_RP_CONFIRM

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

def handle_user_message(vk, event):
    user_id = event.obj.message['from_id']
    text_original = event.obj.message['text'] 
    text = text_original.strip() 
    
    print(f"DEBUG USER_HANDLER: User {user_id} sent text='{text_original}' (stripped='{text}'), payload='{event.obj.message.get('payload')}'")

    raw_payload_from_event = event.obj.message.get('payload')
    payload = None

    if isinstance(raw_payload_from_event, str):
        try:
            payload = json.loads(raw_payload_from_event)
        except json.JSONDecodeError:
            print(f"USER_HANDLER: Warning: Could not decode payload string: {raw_payload_from_event}")
    elif isinstance(raw_payload_from_event, dict):
        payload = raw_payload_from_event
        
    is_admin = user_id in ADMIN_IDS
    current_state, state_data = get_user_state(user_id)
    state_data = state_data or {}

    character_row = get_character_by_owner_id(user_id)
    character_dict = None
    if character_row:
        character_dict = dict(character_row)
        print(f"DEBUG USER_HANDLER: Character data from DB: {character_dict}") 
    else:
        print(f"DEBUG USER_HANDLER: Character data is None for user {user_id}")


    if text.lower() == "отмена" or text.lower() == "назад в главное меню":
        clear_user_state(user_id) 
        set_user_state(user_id, STATE_MAIN_MENU)
        send_message_parts(vk, user_id, "Главное меню.", get_main_menu_keyboard(is_admin))
        return

    if not current_state or current_state == STATE_MAIN_MENU :
        if text == "Просмотреть всю Анкету":
            if not character_dict: send_message_parts(vk, user_id, "У вас еще нет персонажа.", get_main_menu_keyboard(is_admin)); return
            info = format_character_full_info(character_dict)
            send_message_parts(vk, user_id, info, get_main_menu_keyboard(is_admin))
        elif text == "Просмотреть основную информацию":
            if not character_dict: send_message_parts(vk, user_id, "У вас еще нет персонажа.", get_main_menu_keyboard(is_admin)); return
            info = format_character_basic_info(character_dict)
            send_message_parts(vk, user_id, info, get_main_menu_keyboard(is_admin))
        elif text == "Просмотреть характеристики": 
            if not character_dict: send_message_parts(vk, user_id, "У вас еще нет персонажа.", get_main_menu_keyboard(is_admin)); return
            info = format_character_stats_info(character_dict)
            send_message_parts(vk, user_id, info, get_main_menu_keyboard(is_admin))
        elif text == "Просмотреть Проклятую Технику":  
            if not character_dict: send_message_parts(vk, user_id, "У вас еще нет персонажа.", get_main_menu_keyboard(is_admin)); return
            info = format_cursed_technique_info(character_dict)
            send_message_parts(vk, user_id, info, get_main_menu_keyboard(is_admin))
        elif text == "Просмотреть Снаряжение":  
            if not character_dict: send_message_parts(vk, user_id, "У вас еще нет персонажа.", get_main_menu_keyboard(is_admin)); return
            info = format_equipment_info(character_dict)
            send_message_parts(vk, user_id, info, get_main_menu_keyboard(is_admin))
        elif text == "Изученные Общие Техники":
            if not character_dict: send_message_parts(vk, user_id, "У вас еще нет персонажа.", get_main_menu_keyboard(is_admin)); return
            info = format_learned_techniques_info(character_dict)
            send_message_parts(vk, user_id, info, get_main_menu_keyboard(is_admin))
        elif text == "Потратить ОР":
            if not character_dict:
                 send_message_parts(vk, user_id, "У вас еще нет персонажа.", get_main_menu_keyboard(is_admin))
                 return
            set_user_state(user_id, STATE_USER_SPEND_RP_CHOOSE_STAT, {"stat_page": 0}) 
            available_rp_value = character_dict.get('rp_points', 0)
            print(f"DEBUG USER_HANDLER (Потратить ОР): Passing to get_stat_selection_keyboard: character_all_data_dict={character_dict is not None}, available_rp_value={available_rp_value}")
            keyboard_to_send = get_stat_selection_keyboard(character_dict, available_rp_value, current_page=0)
            send_message_parts(vk, user_id, f"Выберите характеристику для улучшения (Стр. 1). У вас {available_rp_value} ОР.", keyboard_to_send)
        elif text == "Маркет (Магазин)":
            send_message_parts(vk, user_id, "Раздел 'Маркет' находится в разработке.", get_main_menu_keyboard(is_admin))
        elif text == "Узнать баланс":
            if not character_dict: send_message_parts(vk, user_id, "У вас еще нет персонажа.", get_main_menu_keyboard(is_admin)); return
            send_message_parts(vk, user_id, f"Ваш баланс: {character_dict.get('balance', 0)} ¥", get_main_menu_keyboard(is_admin))
        elif text == "Админ Панель" and is_admin:
            from admin_handlers import handle_admin_command
            handle_admin_command(vk, event) 
        elif text.lower() in ["начать", "старт", "/start"]:
            handle_start(vk, event)
        else:
            if not (is_admin and text == "Админ Панель"): 
                send_message_parts(vk, user_id, "Неизвестная команда. Используйте кнопки меню.", get_main_menu_keyboard(is_admin))
        return 

    if current_state == STATE_USER_SPEND_RP_CHOOSE_STAT:
        current_stat_page = state_data.get("stat_page", 0) if state_data else 0

        if payload and payload.get("action") == "stat_page": 
            new_page = payload.get("page", 0)
            set_user_state(user_id, STATE_USER_SPEND_RP_CHOOSE_STAT, {"stat_page": new_page}) 

            if character_dict:
                available_rp_value_state = character_dict.get('rp_points', 0)
                keyboard_to_send = get_stat_selection_keyboard(character_dict, available_rp_value_state, current_page=new_page)
                send_message_parts(vk, user_id, f"Выберите характеристику для улучшения (Стр. {new_page + 1}). У вас {available_rp_value_state} ОР.", keyboard_to_send)
            else: 
                send_message_parts(vk, user_id, "Произошла ошибка определения персонажа.", get_main_menu_keyboard(is_admin))
                clear_user_state(user_id); set_user_state(user_id, STATE_MAIN_MENU)
            return 

        elif payload and payload.get("action") == "spend_rp": 
            stat_to_upgrade = payload["stat"] 
            if not character_dict: 
                send_message_parts(vk, user_id, "У вас еще нет персонажа.", get_main_menu_keyboard(is_admin))
                clear_user_state(user_id); set_user_state(user_id, STATE_MAIN_MENU)
                return

            if stat_to_upgrade not in character_dict:
                send_message_parts(vk, user_id, "Ошибка: выбранный стат не найден у персонажа.", get_main_menu_keyboard(is_admin))
                kb_err = get_stat_selection_keyboard(character_dict, character_dict.get('rp_points',0) , current_page=current_stat_page)
                send_message_parts(vk, user_id, f"Выберите характеристику (Стр. {current_stat_page + 1}).", kb_err)
                return

            current_level = character_dict[stat_to_upgrade] 
            cost = get_stat_upgrade_cost(stat_to_upgrade, current_level)

            if character_dict.get('rp_points', 0) >= cost:
                new_data_for_state = {
                    "stat_to_upgrade": stat_to_upgrade, "cost": cost, 
                    "current_level": current_level, "previous_stat_page": current_stat_page
                } 
                set_user_state(user_id, STATE_USER_SPEND_RP_CONFIRM, new_data_for_state)
                stat_name = get_stat_display_name(stat_to_upgrade)
                send_message_parts(vk, user_id,
                                 f"Вы уверены, что хотите улучшить '{stat_name}' (ур. {current_level} -> {current_level + 1}) за {cost} ОР?",
                                 get_confirm_cancel_keyboard())
            else:
                send_message_parts(vk, user_id, f"Недостаточно ОР. Требуется: {cost}, у вас: {character_dict.get('rp_points', 0)}.",
                                 get_main_menu_keyboard(is_admin)) 
                clear_user_state(user_id); set_user_state(user_id, STATE_MAIN_MENU)
            return 

        else: 
            if character_dict: 
                available_rp_value_state = character_dict.get('rp_points', 0)
                keyboard_to_send = get_stat_selection_keyboard(character_dict, available_rp_value_state, current_page=current_stat_page)
                send_message_parts(vk, user_id, f"Пожалуйста, выберите характеристику (Стр. {current_stat_page + 1}) или используйте кнопки навигации.", keyboard_to_send)
            else: 
                send_message_parts(vk, user_id, "Произошла ошибка определения персонажа.", get_main_menu_keyboard(is_admin))
                clear_user_state(user_id); set_user_state(user_id, STATE_MAIN_MENU)
            return 
        
    if current_state == STATE_USER_SPEND_RP_CONFIRM:
        previous_stat_page = state_data.get("previous_stat_page", 0) if state_data else 0
        if text.lower() == "подтвердить":
            if not character_row or not state_data: 
                send_message_parts(vk, user_id, "Произошла ошибка (нет данных для подтверждения). Попробуйте снова.", get_main_menu_keyboard(is_admin))
                clear_user_state(user_id); set_user_state(user_id, STATE_MAIN_MENU)
                return
            
            stat_to_upgrade = state_data.get("stat_to_upgrade")
            cost = state_data.get("cost")
            current_level = state_data.get("current_level")

            if not all([stat_to_upgrade, isinstance(cost, (int, float)), isinstance(current_level, int)]): 
                send_message_parts(vk, user_id, "Произошла ошибка (некорректные данные для подтверждения). Попробуйте снова.", get_main_menu_keyboard(is_admin))
                clear_user_state(user_id); set_user_state(user_id, STATE_MAIN_MENU)
                return

            character_refreshed_row = get_character_by_owner_id(user_id)
            if not character_refreshed_row :
                send_message_parts(vk, user_id, "Ошибка: не удалось обновить данные персонажа.", get_main_menu_keyboard(is_admin))
                clear_user_state(user_id); set_user_state(user_id, STATE_MAIN_MENU)
                return
            character_refreshed_dict = dict(character_refreshed_row)


            if character_refreshed_dict.get('rp_points', 0) < cost:
                rp_val = character_refreshed_dict.get('rp_points', 'N/A')
                send_message_parts(vk, user_id, f"Недостаточно ОР ({rp_val}). Улучшение отменено.", get_main_menu_keyboard(is_admin))
                clear_user_state(user_id); set_user_state(user_id, STATE_MAIN_MENU)
                return
            
            new_rp_points = character_refreshed_dict.get('rp_points', 0) - cost
            new_level = current_level + 1
            updates = {
                stat_to_upgrade: new_level,
                'rp_points': new_rp_points
            }
            update_character_multiple_fields(character_refreshed_dict['id'], updates)
            stat_name = get_stat_display_name(stat_to_upgrade)
            send_message_parts(vk, user_id,
                                f"Характеристика '{stat_name}' улучшена до уровня {new_level}! Осталось ОР: {new_rp_points}.",
                                get_main_menu_keyboard(is_admin))
            clear_user_state(user_id); set_user_state(user_id, STATE_MAIN_MENU)
        elif text.lower() == "отмена":
            set_user_state(user_id, STATE_USER_SPEND_RP_CHOOSE_STAT, {"stat_page": previous_stat_page})
            if character_dict:
                rp_cancel = character_dict.get('rp_points', 0)
                kb_cancel = get_stat_selection_keyboard(character_dict, rp_cancel, current_page=previous_stat_page)
                send_message_parts(vk, user_id, f"Улучшение отменено. Выберите характеристику (Стр. {previous_stat_page + 1}).", kb_cancel)
            else: 
                clear_user_state(user_id); set_user_state(user_id, STATE_MAIN_MENU)
                send_message_parts(vk, user_id, "Улучшение отменено. Главное меню.", get_main_menu_keyboard(is_admin))
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