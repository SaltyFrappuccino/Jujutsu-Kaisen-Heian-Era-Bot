import re
from database import set_user_balance, set_user_nick, ensure_user_wallet_exists
from vk_api.utils import get_random_id
from config import ADMIN_IDS

ADMIN_COMMANDS = [
    '~!editbalance',
    '~!setnick',
]

def handle_admin_chat_command(vk, event):
    text = event.obj.message['text'].strip()
    peer_id = event.obj.message['peer_id']
    user_id = event.obj.message['from_id']
    message_id = event.obj.message['id']

    if not any(text.lower().startswith(cmd) for cmd in ADMIN_COMMANDS):
        return False
    if user_id not in ADMIN_IDS:
        vk.messages.send(peer_id=peer_id, message="Нет прав.", random_id=get_random_id(), reply_to=message_id)
        return True

    if text.lower().startswith('~!editbalance'):
        match = re.match(r'~!editbalance\s+(\d+)\s+(-?\d+)', text, re.IGNORECASE)
        if not match:
            vk.messages.send(peer_id=peer_id, message="Формат: ~!editbalance <vk_id> <новый_баланс>", random_id=get_random_id(), reply_to=message_id)
            return True
        target_id = int(match.group(1))
        new_balance = int(match.group(2))
        ensure_user_wallet_exists(target_id)
        set_user_balance(target_id, new_balance)
        vk.messages.send(peer_id=peer_id, message=f"Баланс пользователя {target_id} теперь {new_balance} ¥", random_id=get_random_id(), reply_to=message_id)
        return True

    if text.lower().startswith('~!setnick'):
        match = re.match(r'~!setnick\s+(\d+)\s+(.+)', text, re.IGNORECASE)
        if not match:
            vk.messages.send(peer_id=peer_id, message="Формат: ~!setnick <vk_id> <новый_ник>", random_id=get_random_id(), reply_to=message_id)
            return True
        target_id = int(match.group(1))
        new_nick = match.group(2).strip()
        if not new_nick or len(new_nick) > 32:
            vk.messages.send(peer_id=peer_id, message="Некорректный ник (1-32 символа)", random_id=get_random_id(), reply_to=message_id)
            return True
        set_user_nick(target_id, new_nick)
        vk.messages.send(peer_id=peer_id, message=f"Ник пользователя {target_id} теперь: {new_nick}", random_id=get_random_id(), reply_to=message_id)
        return True

    return False 