import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import time
import traceback

from config import VK_TOKEN, ADMIN_IDS, STATE_MAIN_MENU, STATE_ADMIN_PANEL
from database import get_user_state, set_user_state, clear_user_state, clear_pending_text
from user_handlers import handle_start, handle_user_message
from admin_handlers import handle_admin_command
from chat_commands import handle_chat_command
from admin_chat_commands import handle_admin_chat_command
from battle_system import handle_battle_command, active_battles, BATTLE_STATE_ACTIVE, BATTLE_STATE_WAITING, BATTLE_ACTIONS, CURSED_TECHNIQUES
from keyboards import get_main_menu_keyboard

def is_battle_related_command(command_key, peer_id):
    if command_key in ['бой', 'принять', 'отклонить', 'отменить']:
        return True

    battle = active_battles.get(peer_id)
    if battle and (battle.state == BATTLE_STATE_ACTIVE or battle.state == BATTLE_STATE_WAITING):
        if command_key in BATTLE_ACTIONS:
            return True
        
        player1_data = battle.get_player_data(battle.challenger_id)
        player2_data = battle.get_player_data(battle.target_id)
        
        if player1_data and command_key in CURSED_TECHNIQUES[player1_data['technique_id']]['moves']:
            return True
        if player2_data and command_key in CURSED_TECHNIQUES[player2_data['technique_id']]['moves']:
            return True
            
    return False

def main():
    if not VK_TOKEN:
        print("Ошибка: Токен VK не найден. Проверьте файл .env")
        return

    vk_session = vk_api.VkApi(token=VK_TOKEN)
    try:
        group_info = vk_session.method('groups.getById')
        if not group_info:
            print("Ошибка: Не удалось получить ID группы. Проверьте токен и права бота.")
            return
        group_id = group_info[0]['id']
        vk = vk_session.get_api()

    except vk_api.exceptions.ApiError as e:
        print(f"Ошибка API при получении ID группы: {e}. Проверьте токен и права.")
        return
        
    longpoll = VkBotLongPoll(vk_session, group_id=group_id)

    print("Бот запущен...")

    for event in longpoll.listen():
        try:
            if event.type == VkBotEventType.MESSAGE_NEW and event.obj.message and event.obj.message.get('text') is not None:
                user_id = event.obj.message['from_id']
                text_original = event.obj.message['text']
                text_stripped_for_command_check = text_original.lstrip() 
                peer_id = event.obj.message['peer_id']

                if text_stripped_for_command_check.startswith('='):
                    command_full_text = text_stripped_for_command_check[1:]
                    command_key = command_full_text.split()[0].lower() if command_full_text else ""
                    
                    if peer_id >= 2000000000:
                        if is_battle_related_command(command_key, peer_id):
                            handle_battle_command(vk, event, command_full_text)
                        else:
                            handle_chat_command(vk, event)
                    continue 

                if text_stripped_for_command_check.startswith('~!'):
                    if peer_id >= 2000000000:
                        handle_admin_chat_command(vk, event)
                    continue

                if peer_id < 2000000000:
                    text_for_handler = text_original.strip()
                    current_state, _ = get_user_state(user_id)
                    is_admin_user = user_id in ADMIN_IDS

                    if text_for_handler.lower() in ["начать", "старт", "/start", "ghbdtn", "привет"]:
                        handle_start(vk, event)
                        continue
                    
                    if is_admin_user and (text_for_handler == "Админ Панель" or (current_state and current_state.startswith("admin_"))):
                        if text_for_handler == "Админ Панель" and not (current_state and current_state.startswith("admin_")):
                            set_user_state(user_id, STATE_ADMIN_PANEL, {})
                        handle_admin_command(vk, event)
                    else:
                        handle_user_message(vk, event)

        except Exception as e:
            print(f"Произошла КРИТИЧЕСКАЯ ошибка в главном цикле: {e}")
            traceback.print_exc()
            try:
                error_user_id_ex = ADMIN_IDS[0] if ADMIN_IDS else None
                error_peer_id_ex = error_user_id_ex
                if event.obj and event.obj.message:
                     error_user_id_ex = event.obj.message.get('from_id', error_user_id_ex)
                     error_peer_id_ex = event.obj.message.get('peer_id', error_peer_id_ex if error_peer_id_ex else error_user_id_ex)

                if error_peer_id_ex and error_peer_id_ex < 2000000000: 
                    error_is_admin = error_user_id_ex in ADMIN_IDS
                    vk.messages.send(
                        user_id=error_user_id_ex,
                        message="Произошла внутренняя ошибка бота. Ваше текущее действие сброшено. Попробуйте снова или свяжитесь с администрацией.",
                        random_id=vk_api.utils.get_random_id(),
                        keyboard=get_main_menu_keyboard(error_is_admin)
                    )
                    if error_user_id_ex:
                        clear_user_state(error_user_id_ex)
                        clear_pending_text(error_user_id_ex)
                        set_user_state(error_user_id_ex, STATE_MAIN_MENU)
                elif error_peer_id_ex and error_peer_id_ex >= 2000000000:
                     vk.messages.send(
                        peer_id=error_peer_id_ex,
                        message="Произошла внутренняя ошибка бота при обработке команды. Попробуйте позже.",
                        random_id=vk_api.utils.get_random_id()
                    )
            except Exception as e_send:
                print(f"Не удалось отправить сообщение об ошибке: {e_send}")
        time.sleep(0.1)

if __name__ == '__main__':
    main()