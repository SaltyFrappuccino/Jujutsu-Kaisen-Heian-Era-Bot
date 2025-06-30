import vk_api
from vk_api.utils import get_random_id
import json
from database import (
    set_user_state, get_user_state, clear_user_state, add_character,
    get_all_characters, get_character_by_id, update_character_field,
    start_pending_text, append_pending_text, get_pending_text_info, clear_pending_text,
    update_character_multiple_fields
)
from keyboards import (
    get_admin_panel_keyboard,
    get_text_input_done_keyboard, get_gender_selection_keyboard,
    get_admin_character_list_keyboard,
    get_admin_edit_character_actions_keyboard,
    get_admin_edit_general_info_fields_keyboard, get_admin_edit_stat_fields_keyboard,
    get_admin_edit_learned_techniques_keyboard, get_back_to_admin_panel_keyboard
)
from utils import (
    parse_user_mention, split_message, get_all_stat_keys, get_stat_display_name,
    get_all_learned_technique_keys, get_learned_technique_display_name
)
from config import *
from character_actions import get_default_stats_for_creation, format_character_full_info


def send_admin_message_parts(vk, user_id, text, keyboard=None):
    parts = split_message(text)
    for i, part in enumerate(parts):
        current_keyboard = keyboard if i == len(parts) - 1 else None
        try:
            vk.messages.send(user_id=user_id, message=part, random_id=get_random_id(), keyboard=current_keyboard)
        except vk_api.exceptions.ApiError as e:
            print(f"[ERROR] Ошибка отправки админ сообщения пользователю {user_id}: {e}")
            if i == 0: vk.messages.send(user_id=user_id, message="Не удалось отобразить информацию для администратора.", random_id=get_random_id())
            break

def _go_to_admin_panel(user_id, vk):
    set_user_state(user_id, STATE_ADMIN_PANEL, {})
    send_admin_message_parts(vk, user_id, "Админ Панель.", get_admin_panel_keyboard())

def _go_to_char_selection(user_id, vk, for_action="edit", current_page=0):
    state_to_set = STATE_ADMIN_EDIT_CHOOSE_CHAR if for_action == "edit" else STATE_ADMIN_VIEW_CHOOSE_CHAR
    set_user_state(user_id, state_to_set, {"page": current_page, "for_action": for_action})
    characters = get_all_characters()
    if not characters:
        action_text_none = "редактирования" if for_action == "edit" else "просмотра"
        send_admin_message_parts(vk, user_id, f"Нет персонажей для {action_text_none}.", get_admin_panel_keyboard())
        _go_to_admin_panel(user_id, vk); return
    action_text_list = "редактирования" if for_action == "edit" else "просмотра"
    try:
        kb = get_admin_character_list_keyboard(characters, for_action=for_action, current_page=current_page)
    except Exception as e:
        print(f"[ERROR] Ошибка в get_admin_character_list_keyboard: {e}")
        send_admin_message_parts(vk, user_id, f"Ошибка формирования клавиатуры: {e}", get_admin_panel_keyboard())
        _go_to_admin_panel(user_id, vk); return
    send_admin_message_parts(vk, user_id, f"Выберите персонажа для {action_text_list} (Стр. {current_page + 1}):", kb)

def _go_to_edit_char_actions(user_id, vk, char_id, state_data_ref=None):
    state_data_to_use = state_data_ref.copy() if state_data_ref else {}
    character_row = get_character_by_id(char_id)
    character_name = character_row['full_name'] if character_row else f"ID {char_id} (не найден)"
    updated_state_data = {'edit_char_id': char_id}
    if 'page' in state_data_to_use and state_data_to_use.get('for_action') == 'edit':
        updated_state_data['page'] = state_data_to_use['page']
    updated_state_data.pop('admin_stat_page', None)
    set_user_state(user_id, STATE_ADMIN_EDIT_CHOOSE_ACTION, updated_state_data)
    send_admin_message_parts(vk, user_id, f"Редактирование: {character_name}. Выберите действие:", get_admin_edit_character_actions_keyboard(char_id))


def handle_admin_command(vk, event):
    user_id = event.obj.message['from_id']
    text_original = event.obj.message['text']; text = text_original.strip()
    raw_payload = event.obj.message.get('payload'); payload = None
    if isinstance(raw_payload, str):
        try: payload = json.loads(raw_payload)
        except json.JSONDecodeError: print(f"ADMIN_HANDLER: Warn: Could not decode payload: {raw_payload}")
    elif isinstance(raw_payload, dict): payload = raw_payload
    current_state, state_data = get_user_state(user_id); state_data = state_data or {}

    print(f"DEBUG ADMIN_HANDLER: User {user_id} State: {current_state}, Text='{text}', Payload='{payload}'")

    if payload and payload.get("action") == "admin_char_list_page":
        new_page = payload.get("page", 0)
        for_action = payload.get("for_action", state_data.get("for_action", "edit"))
        _go_to_char_selection(user_id, vk, for_action=for_action, current_page=new_page); return
    if payload and payload.get("action") == "admin_edit_stat_page":
        char_id_stat_page = payload.get("char_id", state_data.get("edit_char_id"))
        new_page_stat = payload.get("page", 0)
        if char_id_stat_page:
            character_row = get_character_by_id(char_id_stat_page)
            if character_row:
                state_data["admin_stat_page"] = new_page_stat
                set_user_state(user_id, STATE_ADMIN_EDIT_CHOOSE_ACTION, state_data)
                send_admin_message_parts(vk, user_id, f"Редактирование статов (Стр. {new_page_stat + 1}):", get_admin_edit_stat_fields_keyboard(char_id_stat_page, dict(character_row), current_page=new_page_stat))
            else: _go_to_admin_panel(user_id, vk)
        else: _go_to_admin_panel(user_id, vk)
        return

    if text.lower() == "назад в главное меню": from user_handlers import handle_start; clear_user_state(user_id); handle_start(vk, event); return
    if text.lower() == "назад в админ панель" or (payload and payload.get("action") == "back_to_admin_panel"): _go_to_admin_panel(user_id, vk); return
    if payload and payload.get("action") == "back_to_char_select_edit": _go_to_char_selection(user_id, vk, for_action="edit", current_page=state_data.get("page",0)); return
    if payload and payload.get("action") == "back_to_edit_actions":
        char_id_nav = payload.get("char_id", state_data.get("edit_char_id"))
        if char_id_nav: _go_to_edit_char_actions(user_id, vk, char_id_nav, state_data); return
        else: _go_to_admin_panel(user_id, vk); return

    if current_state and (current_state.startswith("admin_add_char_") or current_state.startswith("admin_edit_")):
        if text.lower() == "отмена":
            clear_pending_text(user_id)
            edit_char_id_on_cancel = state_data.get("edit_char_id")
            if current_state in [STATE_ADMIN_EDIT_FIELD_VALUE, STATE_ADMIN_EDIT_STAT_VALUE, STATE_ADMIN_EDIT_RP_POINTS, STATE_ADMIN_EDIT_BALANCE, STATE_ADMIN_EDIT_CURSED_TECHNIQUE, STATE_ADMIN_EDIT_EQUIPMENT, STATE_ADMIN_EDIT_LEARNED_TECHNIQUE] and edit_char_id_on_cancel:
                _go_to_edit_char_actions(user_id, vk, edit_char_id_on_cancel, state_data)
            elif current_state == STATE_ADMIN_EDIT_CHOOSE_ACTION and edit_char_id_on_cancel:
                 _go_to_char_selection(user_id, vk, for_action="edit", current_page=state_data.get("page",0))
            elif current_state == STATE_ADMIN_EDIT_CHOOSE_CHAR or current_state == STATE_ADMIN_VIEW_CHOOSE_CHAR:
                _go_to_admin_panel(user_id,vk)
            elif current_state.startswith("admin_add_char_"):
                _go_to_admin_panel(user_id, vk)
            else: _go_to_admin_panel(user_id, vk)
            return

    if current_state == STATE_ADMIN_ADD_CHAR_TAG:
        if text.lower() == "отмена": _go_to_admin_panel(user_id,vk); return
        owner_vk_id = parse_user_mention(text);
        if owner_vk_id: state_data['owner_vk_id'] = owner_vk_id; set_user_state(user_id, STATE_ADMIN_ADD_CHAR_NAME, state_data); send_admin_message_parts(vk, user_id, "Полное Имя персонажа:\n[Имя Фамилия | Прозвище]\nИли 'Отмена'")
        else: send_admin_message_parts(vk, user_id, "Некорректный тэг. Введите тэг (@tag) или [id123|@tag].\nИли 'Отмена'")
        return
    elif current_state == STATE_ADMIN_ADD_CHAR_NAME:
        if text.lower() == "отмена": _go_to_admin_panel(user_id,vk); return
        state_data['full_name'] = text; set_user_state(user_id, STATE_ADMIN_ADD_CHAR_AGE, state_data); send_admin_message_parts(vk, user_id, "Возраст персонажа (число):\nИли 'Отмена'")
        return 
    elif current_state == STATE_ADMIN_ADD_CHAR_AGE:
        if text.lower() == "отмена": _go_to_admin_panel(user_id,vk); return
        try: age_val = int(text)
        except ValueError: send_admin_message_parts(vk, user_id, "Некорректный возраст. Введите число или 'Отмена'."); return
        if age_val < 0: send_admin_message_parts(vk, user_id, "Возраст не может быть отрицательным."); return
        state_data['age'] = age_val; set_user_state(user_id, STATE_ADMIN_ADD_CHAR_GENDER, state_data); send_admin_message_parts(vk, user_id, "Выберите Пол персонажа (или 'Отмена'):", get_gender_selection_keyboard())
        return
    elif current_state == STATE_ADMIN_ADD_CHAR_GENDER:
        if text.lower() == "отмена": _go_to_admin_panel(user_id,vk); return
        if text in ["Мужской", "Женский", "Иное"]: state_data['gender'] = text; set_user_state(user_id, STATE_ADMIN_ADD_CHAR_FACTION, state_data); send_admin_message_parts(vk, user_id, "Принадлежность/Фракция:\nИли 'Отмена'")
        else: send_admin_message_parts(vk, user_id, "Выберите пол из предложенных или 'Отмена'.", get_gender_selection_keyboard())
        return
    elif current_state == STATE_ADMIN_ADD_CHAR_FACTION:
        if text.lower() == "отмена": _go_to_admin_panel(user_id,vk); return
        state_data['faction'] = text; set_user_state(user_id, STATE_ADMIN_ADD_CHAR_APPEARANCE, state_data); send_admin_message_parts(vk, user_id, "Внешность (текст):\nИли 'Отмена'")
        return 
    elif current_state == STATE_ADMIN_ADD_CHAR_APPEARANCE:
        if text.lower() == "отмена": _go_to_admin_panel(user_id,vk); return
        state_data['appearance'] = text; state_data.update(get_default_stats_for_creation()); set_user_state(user_id, STATE_ADMIN_ADD_CHAR_CURSED_TECHNIQUE, state_data)
        start_pending_text(user_id, PENDING_TEXT_CURSED_TECHNIQUE); send_admin_message_parts(vk, user_id, "Описание Проклятой Техники (затем 'Готово').\nЕсли нет - сразу 'Готово'.\nИли 'Отмена'", get_text_input_done_keyboard())
        return 
    elif current_state == STATE_ADMIN_ADD_CHAR_CURSED_TECHNIQUE:
        if text.lower() == "отмена": clear_pending_text(user_id); _go_to_admin_panel(user_id,vk); return
        if text == "Готово (сохранить текст)":
            pending_info = get_pending_text_info(user_id); state_data['cursed_technique_description'] = pending_info['content'] if pending_info else ""
            clear_pending_text(user_id); set_user_state(user_id, STATE_ADMIN_ADD_CHAR_EQUIPMENT, state_data); start_pending_text(user_id, PENDING_TEXT_EQUIPMENT)
            send_admin_message_parts(vk, user_id, "Снаряжение (затем 'Готово').\nЕсли нет - сразу 'Готово'.\nИли 'Отмена'", get_text_input_done_keyboard())
        else: append_pending_text(user_id, text); send_admin_message_parts(vk, user_id, "Текст для Проклятой Техники добавлен. Еще или 'Готово'.", get_text_input_done_keyboard())
        return 
    elif current_state == STATE_ADMIN_ADD_CHAR_EQUIPMENT:
        if text.lower() == "отмена": clear_pending_text(user_id); _go_to_admin_panel(user_id,vk); return
        if text == "Готово (сохранить текст)":
            pending_info = get_pending_text_info(user_id); state_data['equipment'] = pending_info['content'] if pending_info else ""
            clear_pending_text(user_id);
            for tech_key in get_all_learned_technique_keys(): state_data[tech_key] = False
            state_data['rp_points'] = state_data.get('rp_points', 0); state_data['balance'] = state_data.get('balance', 0)
            char_id = add_character(state_data);
            send_admin_message_parts(vk, user_id, f"Персонаж '{state_data['full_name']}' добавлен с ID: {char_id}!"); _go_to_admin_panel(user_id, vk)
        else: append_pending_text(user_id, text); send_admin_message_parts(vk, user_id, "Текст для Снаряжения добавлен. Еще или 'Готово'.", get_text_input_done_keyboard())
        return 

    char_id_being_edited = state_data.get('edit_char_id')

    if current_state == STATE_ADMIN_EDIT_CHOOSE_CHAR:
        if payload and payload.get("action") == "select_char_edit": _go_to_edit_char_actions(user_id, vk, payload.get("char_id"), state_data)
        elif not payload and text: _go_to_char_selection(user_id, vk, for_action="edit", current_page=state_data.get("page",0))
        return

    if current_state == STATE_ADMIN_EDIT_CHOOSE_ACTION:
        if not char_id_being_edited: _go_to_char_selection(user_id, vk, for_action="edit", current_page=state_data.get("page",0)); return
        action_payload = payload.get("action") if payload else None
        char_data_row = get_character_by_id(char_id_being_edited); char_dict = dict(char_data_row) if char_data_row else None
        if not char_dict: send_admin_message_parts(vk, user_id, "Персонаж не найден."); _go_to_char_selection(user_id, vk, for_action="edit", current_page=state_data.get("page",0)); return
        current_admin_stat_page = state_data.get("admin_stat_page", payload.get("page", 0))

        if action_payload == "edit_char_info_menu": send_admin_message_parts(vk, user_id, "Какое поле изменить? (или 'Отмена')", get_admin_edit_general_info_fields_keyboard(char_id_being_edited))
        elif action_payload == "edit_char_stat_menu": send_admin_message_parts(vk, user_id, f"Какой стат изменить? (Стр. {current_admin_stat_page+1})", get_admin_edit_stat_fields_keyboard(char_id_being_edited, char_dict, current_page=current_admin_stat_page))
        elif action_payload == "edit_char_learned_tech_menu": set_user_state(user_id, STATE_ADMIN_EDIT_LEARNED_TECHNIQUE, state_data); send_admin_message_parts(vk, user_id, "Изменить статус техник: (или 'Отмена')", get_admin_edit_learned_techniques_keyboard(char_id_being_edited, char_dict))
        elif action_payload == "edit_char_rp": state_data['edit_target'] = 'rp_points'; set_user_state(user_id, STATE_ADMIN_EDIT_RP_POINTS, state_data); send_admin_message_parts(vk, user_id, f"Текущее ОР: {char_dict.get('rp_points',0)}. Новое значение (или 'Отмена'):")
        elif action_payload == "edit_char_balance": state_data['edit_target'] = 'balance'; set_user_state(user_id, STATE_ADMIN_EDIT_BALANCE, state_data); send_admin_message_parts(vk, user_id, f"Текущий баланс: {char_dict.get('balance',0)}. Новое значение (или 'Отмена'):")
        elif action_payload == "edit_char_ct": state_data['edit_target'] = 'cursed_technique_description'; set_user_state(user_id, STATE_ADMIN_EDIT_CURSED_TECHNIQUE, state_data); start_pending_text(user_id, PENDING_TEXT_CURSED_TECHNIQUE, char_id_being_edited); send_admin_message_parts(vk, user_id,f"Текущая ПТ:\n{char_dict.get('cursed_technique_description','')}\n\nНовое описание (затем 'Готово' или 'Отмена').", get_text_input_done_keyboard())
        elif action_payload == "edit_char_equip": state_data['edit_target'] = 'equipment'; set_user_state(user_id, STATE_ADMIN_EDIT_EQUIPMENT, state_data); start_pending_text(user_id, PENDING_TEXT_EQUIPMENT, char_id_being_edited); send_admin_message_parts(vk, user_id,f"Текущее Снаряжение:\n{char_dict.get('equipment','')}\n\nНовое описание (затем 'Готово' или 'Отмена').", get_text_input_done_keyboard())
        elif payload and payload.get("action") == "select_edit_field": state_data['edit_field'] = payload['field']; set_user_state(user_id, STATE_ADMIN_EDIT_FIELD_VALUE, state_data); send_admin_message_parts(vk, user_id, f"Текущее '{get_stat_display_name(payload['field'])}': {char_dict.get(payload['field'],'')}\nНовое значение (или 'Отмена'):")
        elif payload and payload.get("action") == "select_edit_stat": state_data['edit_stat'] = payload['stat']; set_user_state(user_id, STATE_ADMIN_EDIT_STAT_VALUE, state_data); send_admin_message_parts(vk, user_id, f"Текущий '{get_stat_display_name(payload['stat'])}': {char_dict.get(payload['stat'],0)}\nНовый уровень (или 'Отмена'):")
        elif not payload and text: _go_to_edit_char_actions(user_id, vk, char_id_being_edited, state_data)
        return

    if current_state == STATE_ADMIN_EDIT_FIELD_VALUE:
        if not char_id_being_edited or not state_data.get('edit_field'): _go_to_char_selection(user_id, vk, for_action="edit", current_page=state_data.get("page",0)); return
        field_to_edit = state_data['edit_field']; new_value = text
        if field_to_edit == 'age':
            try: new_value = int(text)
            except ValueError: send_admin_message_parts(vk, user_id, "Возраст должен быть числом. Попробуйте еще раз."); return
            if new_value < 0: send_admin_message_parts(vk, user_id, "Возраст не может быть отрицательным."); return
        update_character_field(char_id_being_edited, field_to_edit, new_value); send_admin_message_parts(vk, user_id, "Поле обновлено."); _go_to_edit_char_actions(user_id, vk, char_id_being_edited, state_data); return

    if current_state == STATE_ADMIN_EDIT_STAT_VALUE:
        if not char_id_being_edited or not state_data.get('edit_stat'): _go_to_char_selection(user_id, vk, for_action="edit", current_page=state_data.get("page",0)); return
        stat_to_edit = state_data['edit_stat']
        try: new_level = int(text)
        except ValueError: send_admin_message_parts(vk, user_id, "Уровень должен быть числом."); return
        if new_level < 0: send_admin_message_parts(vk, user_id, "Уровень не может быть отрицательным."); return
        update_character_field(char_id_being_edited, stat_to_edit, new_level); send_admin_message_parts(vk, user_id, "Стат обновлен."); _go_to_edit_char_actions(user_id, vk, char_id_being_edited, state_data); return

    if current_state == STATE_ADMIN_EDIT_RP_POINTS:
        if not char_id_being_edited: _go_to_char_selection(user_id, vk, for_action="edit", current_page=state_data.get("page",0)); return
        try: new_rp = int(text); new_rp = max(0, new_rp)
        except ValueError: send_admin_message_parts(vk, user_id, "ОР должны быть числом."); return
        update_character_field(char_id_being_edited, 'rp_points', new_rp); send_admin_message_parts(vk, user_id, "ОР обновлены."); _go_to_edit_char_actions(user_id, vk, char_id_being_edited, state_data); return

    if current_state == STATE_ADMIN_EDIT_BALANCE:
        if not char_id_being_edited: _go_to_char_selection(user_id, vk, for_action="edit", current_page=state_data.get("page",0)); return
        try: new_balance = int(text)
        except ValueError: send_admin_message_parts(vk, user_id, "Баланс должен быть числом."); return
        update_character_field(char_id_being_edited, 'balance', new_balance); send_admin_message_parts(vk, user_id, "Баланс обновлен."); _go_to_edit_char_actions(user_id, vk, char_id_being_edited, state_data); return

    if current_state == STATE_ADMIN_EDIT_CURSED_TECHNIQUE or current_state == STATE_ADMIN_EDIT_EQUIPMENT:
        if not char_id_being_edited or not state_data.get('edit_target'): _go_to_char_selection(user_id, vk, for_action="edit", current_page=state_data.get("page",0)); return
        edit_target_field = state_data['edit_target']
        if text == "Готово (сохранить текст)":
            pending_info = get_pending_text_info(user_id)
            if pending_info and pending_info['target_char_id'] == char_id_being_edited: update_character_field(char_id_being_edited, edit_target_field, pending_info['content']); send_admin_message_parts(vk, user_id, "Текст обновлен.")
            else: send_admin_message_parts(vk, user_id, "Ошибка сохранения текста.")
            clear_pending_text(user_id); _go_to_edit_char_actions(user_id, vk, char_id_being_edited, state_data)
        else: append_pending_text(user_id, text); send_admin_message_parts(vk, user_id, "Текст добавлен. 'Готово' для сохранения.", get_text_input_done_keyboard())
        return

    if current_state == STATE_ADMIN_EDIT_LEARNED_TECHNIQUE:
        if not char_id_being_edited: _go_to_char_selection(user_id, vk, for_action="edit", current_page=state_data.get("page",0)); return
        char_data_row = get_character_by_id(char_id_being_edited); char_dict = dict(char_data_row) if char_data_row else None
        if not char_dict: send_admin_message_parts(vk, user_id, "Персонаж не найден."); _go_to_char_selection(user_id, vk, for_action="edit", current_page=state_data.get("page",0)); return
        if payload and payload.get("action") == "toggle_learned_tech":
            tech_key_to_toggle = payload.get('tech')
            if not tech_key_to_toggle or tech_key_to_toggle not in get_all_learned_technique_keys():
                send_admin_message_parts(vk, user_id, "Ошибка: неверный ключ техники."); _go_to_edit_char_actions(user_id, vk, char_id_being_edited, state_data); return
            current_status = char_dict.get(tech_key_to_toggle, False)
            new_status = not current_status
            update_character_field(char_id_being_edited, tech_key_to_toggle, new_status)
            refreshed_char_dict = dict(get_character_by_id(char_id_being_edited))
            message_text = f"Техника '{get_learned_technique_display_name(tech_key_to_toggle)}' теперь {'изучена' if new_status else 'не изучена'}."
            keyboard_to_send = get_admin_edit_learned_techniques_keyboard(char_id_being_edited, refreshed_char_dict)
            send_admin_message_parts(vk, user_id, message_text, keyboard_to_send)
        elif text.lower() == "назад (к действиям с персонажем)": _go_to_edit_char_actions(user_id, vk, char_id_being_edited, state_data)
        elif not payload: send_admin_message_parts(vk, user_id, "Используйте кнопки.", get_admin_edit_learned_techniques_keyboard(char_id_being_edited, char_dict))
        return

    if current_state == STATE_ADMIN_VIEW_CHOOSE_CHAR:
        if payload and payload.get("action") == "admin_select_char_view":
            char_id_view = payload.get("char_id")
            if char_id_view:
                char_row = get_character_by_id(char_id_view); char_dict_view = dict(char_row) if char_row else None
                if char_dict_view:
                    full_info = format_character_full_info(char_dict_view); owner = char_dict_view.get('owner_vk_id','?');
                    header = f"Анкета: {char_dict_view.get('full_name','N/A')} (ID: {char_id_view}, Владелец: [id{owner}|П])\n\n";
                    send_admin_message_parts(vk, user_id, header + full_info, get_back_to_admin_panel_keyboard())
                else: send_admin_message_parts(vk, user_id, "Персонаж не найден.", get_back_to_admin_panel_keyboard()); _go_to_admin_panel(user_id, vk)
            else: send_admin_message_parts(vk, user_id, "Ошибка выбора.", get_back_to_admin_panel_keyboard()); _go_to_admin_panel(user_id, vk)
        elif not payload: _go_to_char_selection(user_id, vk, for_action="view", current_page=   state_data.get("page",0))
        return

    if current_state == STATE_ADMIN_PANEL:
        if text == "Добавить Персонажа": set_user_state(user_id, STATE_ADMIN_ADD_CHAR_TAG, {}); send_admin_message_parts(vk, user_id, "Тэг игрока (@tag или [id123|@tag]) или 'Отмена':")
        elif text == "Редактировать Персонажа": _go_to_char_selection(user_id, vk, for_action="edit", current_page=0)
        elif text == "Просмотреть Анкеты": _go_to_char_selection(user_id, vk, for_action="view", current_page=0)
        elif text and not text.lower().startswith("назад в"): send_admin_message_parts(vk, user_id, "Неизвестная команда в Админ Панели.", get_admin_panel_keyboard())
        return

    if user_id in ADMIN_IDS and current_state:
        print(f"ADMIN_HANDLER: Unhandled state '{current_state}' for admin {user_id}. Defaulting to admin panel.")
        _go_to_admin_panel(user_id, vk)