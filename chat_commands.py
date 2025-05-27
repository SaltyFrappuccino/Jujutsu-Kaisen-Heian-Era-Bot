import vk_api
from vk_api.utils import get_random_id
from database import get_character_by_owner_id
from character_actions import format_character_full_info
from utils import split_message
import random

def send_chat_message_parts(vk, target_peer_id, text, reply_to=None):
    parts = split_message(text)
    for i, part in enumerate(parts):
        try:
            vk.messages.send(
                peer_id=target_peer_id, 
                message=part,
                random_id=get_random_id(),
                reply_to=reply_to if i == 0 else None,
                disable_mentions=1
            )
        except vk_api.exceptions.ApiError as e:
            print(f"Ошибка отправки сообщения в peer_id {target_peer_id}: {e}")
            if i == 0:
                vk.messages.send(
                    peer_id=target_peer_id,
                    message="Произошла ошибка при отображении сообщения. Попробуйте позже.",
                    random_id=get_random_id(),
                    reply_to=reply_to,
                    disable_mentions=1
                )
            break

def handle_chat_command(vk, event):
    if not event.obj.message or not event.obj.message.get('text'):
        return
        
    full_text_original = event.obj.message['text']
    command_text_with_potential_prefix = full_text_original.lstrip()
    
    if not command_text_with_potential_prefix.startswith('='):
        return 
    
    command_text_stripped = command_text_with_potential_prefix[1:].strip()

    peer_id = event.obj.message['peer_id']
    user_id = event.obj.message['from_id']
    message_id = event.obj.message['id']
    
    if peer_id < 2000000000: 
        return 

    if command_text_stripped.lower() == 'анкета':
        character_row = get_character_by_owner_id(user_id)
        if character_row:
            try:
                character_dict = dict(character_row)
                info = format_character_full_info(character_dict)
                send_chat_message_parts(vk, peer_id, info, reply_to=message_id)
            except Exception as e:
                print(f"Ошибка форматирования анкеты для {user_id}: {e}")
                send_chat_message_parts(vk, peer_id, "Ошибка при отображении анкеты.", reply_to=message_id)
        else:
            send_chat_message_parts(vk, peer_id, f"[id{user_id}|Вам] необходимо создать персонажа через личные сообщения с ботом.", reply_to=message_id)
        return
            
    if 'd' in command_text_stripped.lower():
        try:
            dice_expr = command_text_stripped.lower()
            original_dice_expr_for_log = command_text_stripped 
            
            modifier = 0
            mod_char = ''
            
            if '+' in dice_expr:
                parts_plus = dice_expr.split('+')
                if len(parts_plus) > 1 and parts_plus[-1].strip().isdigit():
                    mod_str = parts_plus[-1].strip()
                    modifier = int(mod_str)
                    dice_expr = '+'.join(parts_plus[:-1]) 
                    mod_char = '+'
            
            if '-' in dice_expr: 
                parts_minus = dice_expr.split('-')
                if len(parts_minus) > 1 and parts_minus[-1].strip().isdigit():
                    potential_dice_part = parts_minus[-2] if len(parts_minus) >1 else parts_minus[0]
                    if 'd' in potential_dice_part and any(char.isdigit() for char in potential_dice_part.split('d')[-1]):
                        mod_str = parts_minus[-1].strip()
                        modifier = -int(mod_str)
                        dice_expr = '-'.join(parts_minus[:-1])
                        mod_char = '-'
            
            if dice_expr.startswith('d'):
                dice_expr = '1' + dice_expr
                
            parts_d = dice_expr.split('d')
            if len(parts_d) != 2:
                raise ValueError("Неверный формат NdM")
                
            n_str, m_str = parts_d[0].strip(), parts_d[1].strip()
            if not n_str.isdigit() or not m_str.isdigit():
                 raise ValueError("N и M должны быть числами.")

            n = int(n_str)
            m = int(m_str)
            
            if not (1 <= n <= 20 and 1 <= m <= 1000):
                raise ValueError("Кубики: 1-20, Грани: 1-1000.")
                
            results = [random.randint(1, m) for _ in range(n)]
            total_sum_dice = sum(results)
            final_total = total_sum_dice + modifier
            
            roller_name_display = f"[id{user_id}|Игрок]"
            try:
                user_info = vk.users.get(user_ids=[user_id])[0]
                roller_name_display = f"[id{user_id}|{user_info['first_name']}]"
            except: pass

            result_text = f"🎲 {roller_name_display} бросает {original_dice_expr_for_log}:\n"
            
            if n > 1 or modifier != 0 :
                 result_text += f"Результаты: {', '.join(map(str, results))}"
                 if modifier != 0: result_text += f" (Сумма: {total_sum_dice})"
                 result_text += f"\nИтог: {final_total}"
            else:
                result_text += f"Результат: {final_total}"

            send_chat_message_parts(vk, peer_id, result_text, reply_to=message_id)
        except ValueError as e_val:
            send_chat_message_parts(vk, peer_id, f"Ошибка броска: {e_val}. Формат: `=NdM[+/-X]`", reply_to=message_id)
        except Exception as e_dice_general:
            print(f"Непредвиденная ошибка в броске кубиков ({command_text_stripped}): {e_dice_general}")
            send_chat_message_parts(vk, peer_id, "Произошла ошибка при обработке броска кубиков.", reply_to=message_id)
        return