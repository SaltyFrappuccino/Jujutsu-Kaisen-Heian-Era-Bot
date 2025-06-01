import vk_api
from vk_api.utils import get_random_id
import random
from database import get_character_by_owner_id, update_character_field, get_user_nick, get_user_balance, set_user_balance, add_user_balance, ensure_user_wallet_exists
from keyboards import get_game_keyboard
from utils import split_message

def send_game_message_parts(vk, chat_id, text, reply_to=None):
    parts = split_message(text)
    for i, part in enumerate(parts):
        try:
            vk.messages.send(
                chat_id=chat_id,
                message=part,
                random_id=get_random_id(),
                reply_to=reply_to if i == 0 else None
            )
        except vk_api.exceptions.ApiError as e:
            print(f"Ошибка отправки сообщения в чат {chat_id}: {e}")
            if i == 0:
                vk.messages.send(
                    chat_id=chat_id,
                    message="Произошла ошибка при отображении. Попробуйте позже.",
                    random_id=get_random_id(),
                    reply_to=reply_to
                )
            break

def handle_game_command(vk, event):
    if not event.obj.message.get('text'):
        return
        
    text = event.obj.message['text'].strip()
    peer_id = event.obj.message['peer_id']
    
    if peer_id < 2000000000:
        return
        
    chat_id = peer_id - 2000000000
    user_id = event.obj.message['from_id']
    message_id = event.obj.message['id']
    
    if text == '=Игры':
        send_game_message_parts(vk, chat_id, "Выберите игру:", get_game_keyboard(), reply_to=message_id)
        return
        
    if text.startswith('=Кости'):
        ensure_user_wallet_exists(user_id)
        current_balance = get_user_balance(user_id)
        try:
            bet = int(text.split()[0])
            if bet <= 0:
                raise ValueError
        except (ValueError, IndexError):
            send_game_message_parts(vk, chat_id, "Укажите корректную ставку перед командой. Например: 100 =Кости", reply_to=message_id)
            return
        if bet > current_balance:
            send_game_message_parts(vk, chat_id, f"Недостаточно средств. Ваш баланс: {current_balance} ¥", reply_to=message_id)
            return
        roll = random.randint(1, 6)
        if roll >= 4:
            win = bet
            result = "выиграл"
        else:
            win = -bet
            result = "проиграл"
        new_balance = current_balance + win
        set_user_balance(user_id, new_balance)
        result_text = f"🎲 Бросок кубика: {roll}\n"
        result_text += f"Вы {result} {abs(win)} ¥\n"
        result_text += f"Новый баланс: {new_balance} ¥"
        send_game_message_parts(vk, chat_id, result_text, reply_to=message_id)
        return
    elif text.startswith('=Рулетка'):
        ensure_user_wallet_exists(user_id)
        current_balance = get_user_balance(user_id)
        try:
            bet = int(text.split()[0])
            if bet <= 0:
                raise ValueError
        except (ValueError, IndexError):
            send_game_message_parts(vk, chat_id, "Укажите корректную ставку перед командой. Например: 100 =Рулетка", reply_to=message_id)
            return
        if bet > current_balance:
            send_game_message_parts(vk, chat_id, f"Недостаточно средств. Ваш баланс: {current_balance} ¥", reply_to=message_id)
            return
        number = random.randint(0, 36)
        if number == 0:
            win = bet * 35
        elif number % 2 == 0:
            win = bet
        else:
            win = -bet
        new_balance = current_balance + win
        set_user_balance(user_id, new_balance)
        result_text = f"🎯 Рулетка: {number}\n"
        if number == 0:
            result_text += "Выпало зеро! x35\n"
        result_text += f"Вы {'выиграл' if win > 0 else 'проиграл'} {abs(win)} ¥\n"
        result_text += f"Новый баланс: {new_balance} ¥"
        send_game_message_parts(vk, chat_id, result_text, reply_to=message_id)
        return
    elif text.startswith('=Дуэль'):
        try:
            opponent_mention = text.split()[0]
            if not opponent_mention.startswith('[') or not opponent_mention.endswith(']'):
                raise ValueError
        except (ValueError, IndexError):
            send_game_message_parts(vk, chat_id, "Укажите противника через упоминание перед командой. Например: [id123|@user] =Дуэль", reply_to=message_id)
            return
        opponent_id = None
        try:
            opponent_id = int(opponent_mention.split('|')[0][4:])
        except (ValueError, IndexError):
            send_game_message_parts(vk, chat_id, "Некорректное упоминание противника.", reply_to=message_id)
            return
        ensure_user_wallet_exists(user_id)
        ensure_user_wallet_exists(opponent_id)
        current_balance = get_user_balance(user_id)
        opponent_balance = get_user_balance(opponent_id)
        if current_balance < 100 or opponent_balance < 100:
            send_game_message_parts(vk, chat_id, "Для дуэли каждому участнику нужно минимум 100 ¥", reply_to=message_id)
            return
        character_row = get_character_by_owner_id(user_id)
        opponent_row = get_character_by_owner_id(opponent_id)
        if not character_row or not opponent_row:
            send_game_message_parts(vk, chat_id, "Один из участников дуэли не имеет персонажа.", reply_to=message_id)
            return
        character_dict = dict(character_row)
        opponent_dict = dict(opponent_row)
        player_strength = character_dict.get('level_base_strength', 0)
        opponent_strength = opponent_dict.get('level_base_strength', 0)
        player_roll = random.randint(1, 20)
        opponent_roll = random.randint(1, 20)
        player_total = player_strength + player_roll
        opponent_total = opponent_strength + opponent_roll
        if player_total > opponent_total:
            winner_id = user_id
            loser_id = opponent_id
        elif opponent_total > player_total:
            winner_id = opponent_id
            loser_id = user_id
        else:
            send_game_message_parts(vk, chat_id, "Дуэль закончилась вничью!", reply_to=message_id)
            return
        set_user_balance(winner_id, get_user_balance(winner_id) + 100)
        set_user_balance(loser_id, get_user_balance(loser_id) - 100)
        player_nick = get_user_nick(user_id) or character_dict['full_name']
        opponent_nick = get_user_nick(opponent_id) or opponent_dict['full_name']
        winner_nick = get_user_nick(winner_id) or (character_dict['full_name'] if winner_id == user_id else opponent_dict['full_name'])
        result_text = f"⚔️ Дуэль:\n"
        result_text += f"{player_nick}: {player_strength} + {player_roll} = {player_total}\n"
        result_text += f"{opponent_nick}: {opponent_strength} + {opponent_roll} = {opponent_total}\n"
        result_text += f"Победитель: {winner_nick}!\n"
        result_text += f"Выигрыш: 100 ¥\n"
        result_text += f"Новый баланс победителя: {get_user_balance(winner_id)} ¥"
        send_game_message_parts(vk, chat_id, result_text, reply_to=message_id)
        return 