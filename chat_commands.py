import vk_api
from vk_api.utils import get_random_id
from database import get_character_by_id, get_character_by_owner_id, get_characters_by_owner_id, get_user_nick, set_user_nick, get_user_stats, get_user_balance, ensure_user_wallet_exists
from character_actions import format_character_full_info
from utils import split_message, parse_user_mention
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

    command_parts = command_text_stripped.split(maxsplit=1)
    command_key = command_parts[0].lower() if command_parts else ""
    args_text = command_parts[1] if len(command_parts) > 1 else ""
    author_user_id = user_id

    if command_key == 'id': # Новая команда "=id"
        if not args_text:
            # Если аргументов нет, показываем ID автора команды
            send_chat_message_parts(vk, peer_id, f"Ваш VK ID: {author_user_id}", reply_to=message_id)
            return

        mentioned_id = parse_user_mention(args_text.strip())
        if mentioned_id:
            send_chat_message_parts(vk, peer_id, f"VK ID для {args_text.strip()}: {mentioned_id}", reply_to=message_id)
        else:
            send_chat_message_parts(vk, peer_id, "Не удалось распознать пользователя. Укажите корректный @тег. Пример: =id @durov", reply_to=message_id)
        return

    # Существующий код для команды "анкета"
    if command_key == 'анкета':
        target_vk_id_for_profile = author_user_id 
        character_to_display = None
        display_name_for_header = f"[id{author_user_id}|Вас]" 
        is_viewing_own_profile = True

        if args_text:
            # 1. Сначала проверяем, является ли аргумент просто числом (ID персонажа)
            if args_text.isdigit():
                char_id_from_arg = int(args_text)
                character_row_by_id = get_character_by_id(char_id_from_arg)
                if character_row_by_id:
                    character_to_display = dict(character_row_by_id)
                    is_viewing_own_profile = (author_user_id == character_to_display['owner_vk_id'])
                    if is_viewing_own_profile:
                        # Если это свой персонаж по ID, не меняем display_name_for_header, он уже "Вас"
                        # или можно установить имя персонажа, если нужно
                        display_name_for_header = f"[id{author_user_id}|Вашего персонажа '{character_to_display.get('full_name','')}']"
                    else:
                        owner_nick = get_user_nick(character_to_display['owner_vk_id'])
                        owner_display = f"[id{character_to_display['owner_vk_id']}|{owner_nick}]" if owner_nick else f"[id{character_to_display['owner_vk_id']}|Игрока]"
                        display_name_for_header = f"персонажа {owner_display}"
                else:
                    send_chat_message_parts(vk, peer_id, f"Персонаж с ID {char_id_from_arg} не найден.", reply_to=message_id)
                    return
            # 2. Если не число, пытаемся распознать как @тег
            else:
                mentioned_id = parse_user_mention(args_text.strip())
                if mentioned_id:
                    target_vk_id_for_profile = mentioned_id
                    is_viewing_own_profile = (author_user_id == target_vk_id_for_profile)
                    display_name_for_header = args_text.strip() 
                else:
                    # Если это не число и не @тег, значит формат неверный
                    send_chat_message_parts(vk, peer_id, "Неверный формат. Используйте: `=Анкета`, `=Анкета @тег` или `=Анкета [ID персонажа]` (число).", reply_to=message_id)
                    return
        
        # Если character_to_display еще не определен (т.е. не было ID персонажа и мы смотрим по target_vk_id_for_profile)
        if not character_to_display:
            characters_list_rows = get_characters_by_owner_id(target_vk_id_for_profile)
            
            if not characters_list_rows:
                if is_viewing_own_profile: # display_name_for_header здесь будет "Вас"
                    send_chat_message_parts(vk, peer_id, f"У {display_name_for_header} нет созданных персонажей. Создайте в ЛС бота.", reply_to=message_id)
                else: # display_name_for_header здесь будет @тег
                    send_chat_message_parts(vk, peer_id, f"У игрока {display_name_for_header} нет созданных персонажей.", reply_to=message_id)
                return
            
            if len(characters_list_rows) == 1:
                character_to_display = dict(characters_list_rows[0])
            else: # Несколько персонажей
                if is_viewing_own_profile: # display_name_for_header здесь будет "Вас"
                    message = f"У {display_name_for_header} несколько персонажей. Пожалуйста, укажите ID конкретного персонажа: `=Анкета [ID персонажа]`.\nВаши персонажи:\n"
                    for i, char_row in enumerate(characters_list_rows[:5]): 
                        char = dict(char_row)
                        message += f"{i+1}. {char.get('full_name', 'Без имени')} (ID: {char.get('id')})\n" # Убрал '#' из вывода ID
                    if len(characters_list_rows) > 5:
                        message += "И другие... (полный список и управление в ЛС бота)\n"
                    send_chat_message_parts(vk, peer_id, message, reply_to=message_id)
                else: # display_name_for_header здесь будет @тег
                    send_chat_message_parts(vk, peer_id, f"У игрока {display_name_for_header} несколько персонажей. Попросите его указать ID нужного персонажа.", reply_to=message_id)
                return

        if character_to_display:
            try:
                info = format_character_full_info(character_to_display)
                header = ""
                char_name_display = character_to_display.get('full_name', 'Без имени')
                char_id_display = character_to_display.get('id')

                if is_viewing_own_profile and target_vk_id_for_profile == author_user_id : # Если смотрели свою анкету (по ID или если она одна)
                    header = f"Анкета вашего персонажа '{char_name_display}' (ID: {char_id_display}):\n"
                elif not is_viewing_own_profile and target_vk_id_for_profile != author_user_id: # Если смотрели чужую по @тегу (и у него один перс)
                     header = f"Анкета персонажа '{char_name_display}' (ID: {char_id_display}) игрока {display_name_for_header}:\n"
                else: # Все остальные случаи (например, просмотр по ID чужого персонажа)
                     owner_nick = get_user_nick(character_to_display['owner_vk_id'])
                     owner_display_name = f"[id{character_to_display['owner_vk_id']}|{owner_nick}]" if owner_nick else f"[id{character_to_display['owner_vk_id']}|Игрока]"
                     header = f"Анкета персонажа '{char_name_display}' (ID: {char_id_display}), владелец {owner_display_name}:\n"
                
                send_chat_message_parts(vk, peer_id, header + info, reply_to=message_id)
            except Exception as e:
                print(f"Ошибка форматирования анкеты для ID персонажа {character_to_display.get('id')}: {e}\n{traceback.format_exc()}") # Добавил traceback
                send_chat_message_parts(vk, peer_id, "Ошибка при отображении анкеты.", reply_to=message_id)
        return

    if command_key == 'анкета':
        target_vk_id_for_profile = author_user_id
        is_viewing_own_profile = True
        display_name_for_header = f"[id{author_user_id}|Вам]"

        if args_text:
            mentioned_id = parse_user_mention(args_text.strip())
            if mentioned_id:
                target_vk_id_for_profile = mentioned_id
                is_viewing_own_profile = (author_user_id == target_vk_id_for_profile)
                # Используем исходный текст упоминания для отображения, если это возможно
                display_name_for_header = args_text.strip() 
            else:
                send_chat_message_parts(vk, peer_id, "Неверный формат. Для просмотра чужой анкеты укажите @тег игрока. Пример: =анкета @durov", reply_to=message_id)
                return

        character_row = get_character_by_owner_id(target_vk_id_for_profile)

        if character_row:
            try:
                character_dict = dict(character_row)
                info = format_character_full_info(character_dict)
                header = ""
                if not is_viewing_own_profile:
                    header = f"Анкета игрока {display_name_for_header}:\n"
                
                send_chat_message_parts(vk, peer_id, header + info, reply_to=message_id)
            except Exception as e:
                print(f"Ошибка форматирования анкеты для ID {target_vk_id_for_profile}: {e}")
                send_chat_message_parts(vk, peer_id, "Ошибка при отображении анкеты.", reply_to=message_id)
        else:
            if is_viewing_own_profile:
                send_chat_message_parts(vk, peer_id, f"{display_name_for_header} необходимо создать персонажа через личные сообщения с ботом.", reply_to=message_id)
            else:
                send_chat_message_parts(vk, peer_id, f"У игрока {display_name_for_header} нет созданных персонажей.", reply_to=message_id)
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
            
            if not (1 <= n <= 20 and 1 <= m <= 100):
                raise ValueError("Кубики: 1-20, Грани: 1-100.")
                
            results = [random.randint(1, m) for _ in range(n)]
            total_sum_dice = sum(results)
            final_total = total_sum_dice + modifier
            
            roller_name_display = f"[id{user_id}|Игрок]"
            try:
                nick = get_user_nick(user_id)
                roller_name_display = f"[id{user_id}|{nick}]" if nick else f"[id{user_id}|Игрок]"
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

    if command_text_stripped.lower().startswith('ник'):
        new_nick = command_text_stripped[3:].strip()
        if not new_nick:
            send_chat_message_parts(vk, peer_id, "Укажите ник после команды. Пример: =ник МойНик", reply_to=message_id)
            return
        if len(new_nick) > 32:
            send_chat_message_parts(vk, peer_id, "Ник не должен быть длиннее 32 символов.", reply_to=message_id)
            return
        set_user_nick(user_id, new_nick)
        send_chat_message_parts(vk, peer_id, f"Ваш ник успешно изменён на: {new_nick}", reply_to=message_id)
        return

    if command_text_stripped.lower() in ['баланс', 'balance', 'мой баланс']:
        ensure_user_wallet_exists(user_id)
        balance = get_user_balance(user_id)
        send_chat_message_parts(vk, peer_id, f"Ваш баланс: {balance} ¥", reply_to=message_id)
        return

    if command_text_stripped.lower() in ['профиль', 'profile', 'мой профиль']:
        character_row = get_character_by_owner_id(user_id)
        if not character_row:
            send_chat_message_parts(vk, peer_id, "У вас ещё нет персонажа. Создайте его в ЛС бота!", reply_to=message_id)
            return
        char = dict(character_row)
        nick = get_user_nick(user_id) or char.get('full_name', 'Безымянный герой')
        stats = get_user_stats(user_id)
        wins = stats.get('wins', 0)
        losses = stats.get('losses', 0)
        total = wins + losses
        winrate = f"{(wins/total*100):.1f}%" if total > 0 else "0%"
        reg_days = random.randint(7, 777)
        ensure_user_wallet_exists(user_id)
        balance = get_user_balance(user_id)
        fav_techs = [
            'Проклятая техника: "Пельмени Судьбы"',
            'Проклятая техника: "Гипнотический Кот"',
            'Проклятая техника: "Сила Мемов"',
            'Проклятая техника: "Кофейный Буст"',
            'Проклятая техника: "Сонный Удар"',
            'Проклятая техника: "Гипер-Уворот"',
            'Проклятая техника: "Печенька Судьбы"',
            'Проклятая техника: "Критический Рофл"',
            'Проклятая техника: "Тотальный Чилл"',
        ]
        fav_tech = random.choice(fav_techs)
        statuses = [
            '🦄 Легенда чата',
            '🐙 Осьминог удачи',
            '🍕 Пицца-мастер',
            '😎 Кибер-гуру',
            '🧃 Соковыжималка',
            '🦖 Динозавр RP',
            '🦆 Утка-маг',
            '👑 Король мемов',
            '🦥 Лорд Лени',
            '🦸 Герой без плаща',
            '🦝 Енот-воришка',
            '🦔 Ёжик в тумане',
            '🦋 Ловец багов',
            '🦜 Попугай-оракул',
            '🦢 Белый лебедь',
            '🦚 Павлин-эстет',
        ]
        status = random.choice(statuses)
        fun_facts = [
            'Любит считать до бесконечности, но сбивается на 7.',
            'Однажды победил босса, пока спал.',
            'Может проиграть даже самому себе.',
            'Пишет код быстрее, чем думает.',
            'Считает, что RP — это стиль жизни.',
            'Прокачал харизму до 99, но всё равно стесняется.',
            'Собирает коллекцию виртуальных тапок.',
            'Верит, что каждый баг — это скрытая фича.',
            'Победил в конкурсе на самый странный ник.',
            'Может вызвать дождь смеха одной шуткой.',
            'Знает секретный рецепт борща, но не расскажет.',
            'Пишет стихи о проклятых техниках.',
            'Мастерски проигрывает с улыбкой.',
            'Считает, что кнопка "Победа" где-то есть.',
            'Владеет техникой "Отмена" на уровне бога.',
            'Может найти баг даже в чайнике.',
        ]
        fun_fact = random.choice(fun_facts)
        profile = f"""🧾 Профиль игрока
Ник: {nick}
Победы: {wins}
Поражения: {losses}
Винрейт: {winrate}
Дней в RP: {reg_days}
{fav_tech}
Статус: {status}

Факт о тебе: {fun_fact}

💬 RP-имя: {char.get('full_name', '???')}
💰 Баланс: {balance} ¥
✨ ОР: {char.get('rp_points', 0)}

Пусть удача всегда будет на твоей стороне!"""
        send_chat_message_parts(vk, peer_id, profile, reply_to=message_id)
        return

    if command_text_stripped.lower() in ['помощь', 'help', 'справка']:
        help_text = (
            "📖 Возможности и команды бота:\n"
            "\n"
            "Основные команды:\n"
            "=Помощь — показать это меню\n"
            "=Профиль — ваш профиль, победы, поражения, статус и т.д.\n"
            "=Анкета — подробная анкета вашего персонажа\n"
            "=Ник <ваш_ник> — установить или сменить никнейм (до 32 символов)\n"
            "NdM[+/-X] — бросить кубики (пример: =2d6+3)\n"
            "\n"
            "Игровые команды (в беседах):\n"
            "100 =Кости — сыграть в кости на ставку (пример: 100 =Кости)\n"
            "100 =Рулетка — сыграть в рулетку на ставку (пример: 100 =Рулетка)\n"
            "[id123|@user] =Дуэль — дуэль на 100¥ (пример: [id123|@user] =Дуэль)\n"
            "=Игры — меню мини-игр\n"
            "\n"
            "Боевые команды (в беседах):\n"
            "=Бой @упоминание — вызвать игрока на бой\n"
            "=Принять — принять вызов\n"
            "=Отклонить — отклонить вызов\n"
            "=Отменить — отменить бой (участник или админ)\n"
            "\n"
            "Во время боя доступны команды:\n"
            "=Атака — обычная атака\n"
            "=Усилатака — усиленная атака ПЭ\n"
            "=Защита — защитная стойка\n"
            "=ОПТ — обратная проклятая техника (лечение)\n"
            "=РТ — раскрытие территории (если есть)\n"
            "=Отдых — восстановление ПЭ\n"
            "\n"
            "Также доступны уникальные приёмы вашей техники (см. список в бою).\n"
            "\n"
            "В ЛС доступны:\n"
            "Просмотреть всю Анкету — полная информация о персонаже\n"
            "Просмотреть основную информацию — кратко о персонаже\n"
            "Просмотреть характеристики — ваши статы\n"
            "Просмотреть Проклятую Технику — описание техники\n"
            "Просмотреть Снаряжение — ваш инвентарь\n"
            "Изученные Общие Техники — список изученных техник\n"
            "Потратить ОР — прокачка характеристик\n"
            "Маркет (Магазин) — магазин (в разработке)\n"
            "Узнать баланс — ваш баланс ¥\n"
            "\n"
            "Системные:\n"
            "Начать / Старт / /start — начать работу с ботом\n"
            "Отмена / Назад в главное меню — отменить действие\n"
            "\n"
            "❗ Для большинства команд требуется созданный персонаж.\n"
            "❗ В бою используйте только команды из списка доступных (см. подсказку в бою).\n"
            "\n"
            "Если остались вопросы — напишите админу или воспользуйтесь этой командой снова!\n"
        )
        send_chat_message_parts(vk, peer_id, help_text, reply_to=message_id)
        return