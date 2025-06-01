import vk_api
from vk_api.utils import get_random_id
from utils import split_message, parse_user_mention
import random
from config import ADMIN_IDS
from database import get_user_nick, get_character_by_owner_id, add_win, add_loss

BATTLE_STATE_WAITING = "waiting"
BATTLE_STATE_ACTIVE = "active"
BATTLE_STATE_FINISHED = "finished"

BATTLE_ACTIONS = {
    "атака": {
        "name": "⚔️ Обычная атака",
        "description": "Простая физическая атака.",
        "energy_cost": 0,
        "damage_min": 8, 
        "damage_max": 18,
        "type": "attack"
    },
    "усилатака": {
        "name": "💫 Усиленная атака ПЭ",
        "description": "Атака, усиленная проклятой энергией.",
        "energy_cost": 30,
        "damage_min": 20,
        "damage_max": 40,
        "type": "attack"
    },
    "защита": {
        "name": "🛡️ Защита",
        "description": "Сконцентрироваться на обороне, уменьшая получаемый урон и немного восстанавливая ПЭ.",
        "energy_cost": 0,
        "energy_regen_min": 5,
        "energy_regen_max": 15,
        "damage_reduction_percent": 0.3,
        "duration": 1, 
        "type": "defense_buff"
    },
    "опт": {
        "name": "✨ Обратная Проклятая Техника",
        "description": "Использовать ОПТ для исцеления.",
        "energy_cost": 70,
        "heal_min": 25, 
        "heal_max": 80,
        "success_chance": 0.8,
        "type": "heal"
    },
    "чв": {
        "name": "⚡ Чёрная Вспышка",
        "description": "Мощнейшая атака, возникающая при идеальном вложении ПЭ. Увеличивает концентрацию.",
        "energy_cost": 100,
        "damage_min": 50,
        "damage_max": 100,
        "success_chance": 0.20,
        "on_success_buff": {"name": "Зона", "duration": 3, "damage_boost_percent": 25},
        "type": "special_attack"
    },
    "рт": {
        "name": "🌌 Расширение Территории",
        "description": "Попытка активировать Расширение Территории своей техники.",
        "energy_cost_multiplier": 1.0,
        "success_chance": 0.75,
        "type": "domain_expansion"
    },
    "отдых": {
        "name": "🧘 Отдых",
        "description": "Восстановить часть проклятой энергии.",
        "energy_cost": 0, 
        "energy_regen_min": 15, 
        "energy_regen_max": 40,
        "type": "utility"
    }
}

CURSED_TECHNIQUES = {
    'shrine': {
        'name': 'Храм (Рёмен Сукуна)',
        'description': 'Техника Сукуны, позволяющая создавать невидимые разрезы и управлять адским пламенем.',
        'moves': {
            'рассечение': {
                'name': 'Рассечение',
                'description': 'Невидимый разрез.',
                'ce_cost': 20, 'damage_min': 20, 'damage_max': 40, 'type': 'attack'
            },
            'расщепление': {
                'name': 'Расщепление',
                'description': 'Мощный разрез, адаптирующийся под прочность цели.',
                'ce_cost': 25, 'damage_min': 25, 'damage_max': 50, 'type': 'attack'
            },
            'пламя': {
                'name': 'Пламенная Стрела',
                'description': 'Создаёт стрелу из пламени, наносящую огромный урон.',
                'ce_cost': 40, 'damage_min': 35, 'damage_max': 75, 'type': 'attack'
            }
        },
        'domain_expansion': {
            'name': 'Злонамеренный Храм',
            'description': 'Безбарьерное РТ, гарантированно поражающее всё в радиусе до 200м непрерывными атаками Рассечением и Расщеплением.',
            'ce_cost': 350, 'duration': 3,
            'effect_description': "Цель получает урон от разрезов каждый ход (20-30 ед.).",
            'damage_per_turn_min': 20, 'damage_per_turn_max': 30, 'type': 'damage_over_time'
        }
    },
    'limitless': {
        'name': 'Безграничность (Сатору Годжо)',
        'description': 'Техника, позволяющая манипулировать пространством на атомарном уровне через концепцию бесконечности.',
        'moves': {
            'бесконечность': {
                'name': 'Бесконечность',
                'description': 'Создаёт барьер, останавливающий атаки. (+70% уклонения на 1 ход).',
                'ce_cost': 30, 'duration': 1, 'evasion_boost': 0.7, 'type': 'buff_defense'
            },
            'синий': {
                'name': 'Синий',
                'description': 'Создаёт точку мощного притяжения.',
                'ce_cost': 35, 'damage_min': 30, 'damage_max': 45, 'type': 'attack'
            },
            'красный': {
                'name': 'Красный',
                'description': 'Создаёт мощную отталкивающую силу.',
                'ce_cost': 40, 'damage_min': 35, 'damage_max': 50, 'type': 'attack'
            },
            'фиолетовый': {
                'name': 'Фиолетовый',
                'description': 'Столкновение Синего и Красного, создающее разрушительную воображаемую массу.',
                'ce_cost': 120, 'damage_min': 70, 'damage_max': 100, 'type': 'attack'
            }
        },
        'domain_expansion': {
            'name': 'Необъятная Бездна',
            'description': 'Затопляет разум цели бесконечным потоком информации, парализуя её.',
            'ce_cost': 400, 'duration': 2,
            'effect_description': "Цель парализована (90% шанс) и не может действовать 2 хода.",
            'stun_chance': 0.9, 'type': 'stun'
        }
    },
    'ten_shadows': {
        'name': 'Техника Десяти Теней (Мэгуми Фушигуро)',
        'description': 'Позволяет призывать и управлять десятью различными шикигами, используя тени как проводник.',
        'moves': {
            'псы': {
                'name': 'Божественные Псы: Тотальность',
                'description': 'Призывает двух псов для атаки.',
                'ce_cost': 25, 'damage_min': 20, 'damage_max': 30, 'type': 'attack_summon'
            },
            'нуэ': {
                'name': 'Нуэ',
                'description': 'Призывает крылатого шикигами, атакующего электричеством.',
                'ce_cost': 30, 'damage_min': 25, 'damage_max': 35, 'type': 'attack_summon'
            },
            'жаба': {
                'name': 'Жаба',
                'description': 'Призывает жабу. Может схватить цель или помочь в защите.',
                'ce_cost': 20, 'damage_min': 10, 'damage_max': 15, 'type': 'utility_summon'
            }
        },
        'domain_expansion': {
            'name': 'Сад Теневых Химер',
            'description': 'Затопляет территорию тенями, позволяя свободно призывать и усиливать шикигами Десяти Теней.',
            'ce_cost': 300, 'duration': 3,
            'effect_description': "Усиливает урон от призывов на 50% и позволяет использовать одного доп. шикигами без затрат ПЭ каждый ход (3 хода).",
            'summon_damage_boost': 1.5, 'type': 'buff_summons'
        }
    },
    'ice_formation': {
        'name': 'Ледяное Формирование (Ураумэ)',
        'description': 'Техника, позволяющая создавать и контролировать лёд с невероятной скоростью и мощью.',
        'moves': {
            'морозный_штиль': {
                'name': 'Морозный Штиль',
                'description': 'Облако ледяного тумана. Шанс замедлить цель (30% на 2 хода).',
                'ce_cost': 30, 'damage_min': 15, 'damage_max': 25, 'slow_chance': 0.3, 'slow_duration': 2, 'type': 'attack_debuff'
            },
            'ледопад': {
                'name': 'Ледопад',
                'description': 'Обрушивает на цель массивные ледяные глыбы.',
                'ce_cost': 40, 'damage_min': 30, 'damage_max': 45, 'type': 'attack'
            },
            'ледяной_шип': {
                'name': 'Пронзающий Лед',
                'description': 'Создает острые ледяные шипы для атаки.',
                'ce_cost': 25, 'damage_min': 20, 'damage_max': 30, 'type': 'attack'
            }
        },
        'domain_expansion': {
            'name': 'Ледяное Чистилище',
            'description': 'Территория покрывается льдом, замораживая проклятую энергию противника и нанося урон холодом.',
            'ce_cost': 320, 'duration': 3,
            'effect_description': "Цель получает урон холодом (10-20 ед.) и её затраты ПЭ увеличены на 25% (3 хода).",
            'damage_per_turn_min': 10, 'damage_per_turn_max': 20, 'ce_cost_increase_debuff': 1.25, 'type': 'damage_debuff_over_time'
        }
    },
    'disaster_flames': {
        'name': 'Пламя Бедствия (Дзёго)',
        'description': 'Техника, основанная на управлении огнем и вулканической активностью.',
        'moves': {
            'извержение': {
                'name': 'Извержение Угля',
                'description': 'Атакует градом раскаленных камней.',
                'ce_cost': 30, 'damage_min': 25, 'damage_max': 35, 'type': 'attack'
            },
            'метеор': {
                'name': 'Метеор',
                'description': 'Создает огромный огненный метеор.',
                'ce_cost': 100, 'damage_min': 60, 'damage_max': 80, 'type': 'attack'
            },
            'огненный_вихрь': {
                'name': 'Огненный Вихрь',
                'description': 'Окружает цель огненным вихрем (2 хода).',
                'ce_cost': 40, 'damage_min': 20, 'damage_max': 30, 'duration': 2, 'type': 'attack_dot_self_target'
            }
        },
        'domain_expansion': {
            'name': 'Гроб Стальной Горы',
            'description': 'Создает внутри вулкана, где гарантированно попадает по цели своими атаками.',
            'ce_cost': 380, 'duration': 3,
            'effect_description': "Цель получает сильный урон от жара (25-35 ед.) каждый ход. Атаки Дзёго усилены на 20% (3 хода).",
            'damage_per_turn_min': 25, 'damage_per_turn_max': 35, 'user_damage_boost': 1.2, 'type': 'damage_buff_over_time'
        }
    },
    'cursed_plant_manipulation': {
        'name': 'Техника Проклятых Растений (Ханами)',
        'description': 'Позволяет управлять растениями, питающимися проклятой энергией.',
        'moves': {
            'снаряды': {
                'name': 'Древесные Снаряды',
                'description': 'Выпускает острые деревянные шипы в цель.',
                'ce_cost': 20, 'damage_min': 18, 'damage_max': 28, 'type': 'attack'
            },
            'корень_ловушка': {
                'name': 'Корень Ловушка',
                'description': 'Корни сковывают цель. Снижает уклонение цели (-30% на 2 хода).',
                'ce_cost': 30, 'damage_min': 10, 'damage_max': 15, 'evasion_debuff': 0.3, 'duration': 2, 'type': 'attack_debuff'
            },
            'поле_иллюзий': {
                'name': 'Поле Цветов Иллюзий',
                'description': 'Ослабляет волю противника (-15% шанс успеха действий на 3 хода).',
                'ce_cost': 35, 'success_chance_debuff': 0.15, 'duration': 3, 'type': 'debuff'
            }
        },
        'domain_expansion': {
            'name': 'Церемониальное Море Света',
            'description': 'Территория превращается в густой лес, где Ханами может свободно атаковать и высасывать энергию.',
            'ce_cost': 330, 'duration': 3,
            'effect_description': "Цель получает урон от растений (15-20 ед.) каждый ход, Ханами восстанавливает 10 ПЭ (3 хода).",
            'damage_per_turn_min': 15, 'damage_per_turn_max': 20, 'ce_regen_per_turn': 10, 'type': 'damage_regen_over_time'
        }
    },
    'disaster_tides': {
        'name': 'Техника Приливного Бедствия (Дагон)',
        'description': 'Позволяет управлять водой и призывать морских существ.',
        'moves': {
            'смертельный_рой': {
                'name': 'Смертельный Рой',
                'description': 'Призывает стаю рыб-шикигами для массированной атаки.',
                'ce_cost': 35, 'damage_min': 25, 'damage_max': 40, 'type': 'attack_summon'
            },
            'водяной_вихрь': {
                'name': 'Водяной Вихрь',
                'description': 'Создает мощный водяной вихрь.',
                'ce_cost': 30, 'damage_min': 20, 'damage_max': 30, 'type': 'attack'
            },
            'приливная_волна': {
                'name': 'Приливная Волна',
                'description': 'Обрушивает на цель волну воды.',
                'ce_cost': 50, 'damage_min': 30, 'damage_max': 40, 'type': 'attack'
            }
        },
        'domain_expansion': {
            'name': 'Сочи', 
            'description': 'Создает пляж с морем, откуда Дагон призывает бесконечный поток морских шикигами, гарантированно попадающих по цели.',
            'ce_cost': 370, 'duration': 3,
            'effect_description': "Цель получает постоянный урон от атак шикигами (20-35 ед.) каждый ход (3 хода).",
            'damage_per_turn_min': 20, 'damage_per_turn_max': 35, 'type': 'damage_over_time'
        }
    },
    'idle_transfiguration': {
        'name': 'Праздная Трансфигурация (Махито)',
        'description': 'Позволяет изменять форму души, как своей, так и чужой, касанием.',
        'moves': {
            'искажение_души': {
                'name': 'Искажение Души',
                'description': 'Касание изменяет форму души цели.',
                'ce_cost': 30, 'damage_min': 35, 'damage_max': 50, 'type': 'attack_touch'
            },
            'трансформация_тела': {
                'name': 'Трансформация Тела',
                'description': 'Изменяет тело для усиления атаки (+15 урона) или защиты (снижение урона на 30%) на 1 ход.',
                'ce_cost': 25, 'type': 'buff_self_choice', 'attack_boost_value': 15, 'damage_reduction': 0.3, 'duration': 1
            },
            'разделение_души': {
                'name': 'Многоликий Дух (Буншин)',
                'description': 'Создает своего клона (усиленная атака).',
                'ce_cost': 60, 'damage_min': 40, 'damage_max': 55, 'type': 'attack'
            }
        },
        'domain_expansion': {
            'name': 'Самовоплощение Совершенства',
            'description': 'Гарантирует Махито возможность коснуться души любого в пределах территории.',
            'ce_cost': 360, 'duration': 1, 
            'effect_description': "Махито гарантированно касается души цели, нанося огромный урон (80-120 ед.).",
            'damage_min': 80, 'damage_max': 120, 'type': 'insta_damage'
        }
    },
    'blood_manipulation': {
        'name': 'Управление Кровью (Чосо)',
        'description': 'Техника, позволяющая манипулировать собственной кровью для различных атак.',
        'moves': {
            'пронзающая_кровь': {
                'name': 'Пронзающая Кровь',
                'description': 'Сжимает кровь и выстреливает ей на высокой скорости.',
                'ce_cost': 25, 'damage_min': 25, 'damage_max': 35, 'type': 'attack'
            },
            'сверхновая': {
                'name': 'Сверхновая',
                'description': 'Разбрасывает множество сгустков крови, которые взрываются (требует 10 HP).',
                'ce_cost': 40, 'hp_cost': 10, 'damage_min': 30, 'damage_max': 45, 'type': 'attack_aoe_hpcost'
            },
            'кровавый_щит': {
                'name': 'Кровавый Щит',
                'description': 'Создает щит из крови, блокирующий 10-20 урона (1 ход).',
                'ce_cost': 20, 'damage_reduction_min': 10, 'damage_reduction_max': 20, 'duration': 1, 'type': 'defense'
            },
            'сходящееся_лезвие': {
                'name': 'Сходящееся Лезвие Крови',
                'description': 'Формирует из крови острое лезвие для ближней атаки.',
                'ce_cost': 15, 'damage_min': 15, 'damage_max': 25, 'type': 'attack'
            }
        },
        'domain_expansion': None
    },
    'projection_sorcery': {
        'name': 'Техника Проекции (Наоя Дзенин)',
        'description': 'Разделяет секунду на 24 кадра, планируя движения. Касание цели замораживает её, если она не следует правилу.',
        'moves': {
            'кадр_атаки': {
                'name': 'Атака на Кадре',
                'description': 'Быстрая атака с шансом "заморозить" цель (25% шанс, 1 ход).',
                'ce_cost': 25, 'damage_min': 20, 'damage_max': 30, 'freeze_chance': 0.25, 'freeze_duration': 1, 'type': 'attack_debuff'
            },
            'ускорение_проекции': {
                'name': 'Ускорение Проекции',
                'description': 'Увеличивает уклонение (+20%) и шанс крит. удара (+15%) на 3 хода.',
                'ce_cost': 30, 'evasion_boost': 0.2, 'crit_chance_boost': 0.15, 'duration': 3, 'type': 'buff_self'
            },
            'серия_кадров': {
                'name': 'Серия Кадров',
                'description': 'Наносит 2-4 быстрых удара по 8-12 урона каждый.',
                'ce_cost': 40, 'num_hits_min': 2, 'num_hits_max': 4, 'damage_per_hit_min': 8, 'damage_per_hit_max': 12, 'type': 'multi_attack'
            }
        },
        'domain_expansion': None
    }
}


class Battle:
    def __init__(self, challenger_id, target_id, chat_id):
        self.challenger_id = challenger_id
        self.target_id = target_id
        self.chat_id = chat_id
        self.state = BATTLE_STATE_WAITING
        self.current_turn = challenger_id
        
        self.player_data = {
            challenger_id: {
                'id': challenger_id, 'name_cached': None,
                'hp': 100, 'max_hp': 100,
                'ce': 100, 'max_ce': 100,
                'technique_id': random.choice(list(CURSED_TECHNIQUES.keys())),
                'active_effects': {}
            },
            target_id: {
                'id': target_id, 'name_cached': None,
                'hp': 100, 'max_hp': 100,
                'ce': 100, 'max_ce': 100,
                'technique_id': random.choice(list(CURSED_TECHNIQUES.keys())),
                'active_effects': {}
            }
        }
        self.log = []

    def _add_log(self, message):
        self.log.append(message)
        if len(self.log) > 15:
            self.log.pop(0)

    def get_player_data(self, user_id):
        return self.player_data.get(user_id)

    def get_opponent_id(self, user_id):
        return self.target_id if user_id == self.challenger_id else self.challenger_id
    
    def _get_player_name(self, user_id, vk_handle):
        player = self.get_player_data(user_id)
        if player.get('name_cached'):
            return player['name_cached']
        try:
            nick = get_user_nick(user_id)
            if nick:
                name = f"[id{user_id}|{nick}]"
            else:
                char_row = get_character_by_owner_id(user_id)
                if char_row and 'full_name' in dict(char_row):
                    name = f"[id{user_id}|{dict(char_row)['full_name']}]"
                else:
                    name = f"[id{user_id}|{user_id}]"
            player['name_cached'] = name
            return name
        except Exception:
            name = f"[id{user_id}|{user_id}]"
            player['name_cached'] = name
            return name


    def _apply_and_tick_effects(self, current_player_id, vk_handle):
        log_messages = []
        
        player = self.get_player_data(current_player_id)
        opponent_id = self.get_opponent_id(current_player_id)
        opponent = self.get_player_data(opponent_id)

        active_domain_effect_player = player['active_effects'].get('active_domain')
        if active_domain_effect_player and active_domain_effect_player.get('user_id') == current_player_id:
            tech_details_player = CURSED_TECHNIQUES[player['technique_id']]
            domain_stats_player = tech_details_player.get('domain_expansion')
            if domain_stats_player:
                if domain_stats_player['type'] in ['damage_over_time', 'damage_buff_over_time', 'damage_debuff_over_time', 'damage_regen_over_time']:
                    if 'damage_per_turn_min' in domain_stats_player and 'damage_per_turn_max' in domain_stats_player:
                        damage = random.randint(domain_stats_player['damage_per_turn_min'], domain_stats_player['damage_per_turn_max'])
                        opponent['hp'] = max(0, opponent['hp'] - damage)
                        log_messages.append(f"Территория '{domain_stats_player['name']}' наносит {damage} урона {self._get_player_name(opponent_id, vk_handle)}.")
                    if domain_stats_player['type'] == 'damage_regen_over_time' and 'ce_regen_per_turn' in domain_stats_player:
                        regen_ce = domain_stats_player['ce_regen_per_turn']
                        player['ce'] = min(player['max_ce'], player['ce'] + regen_ce)
                        log_messages.append(f"Территория '{domain_stats_player['name']}' восстанавливает {regen_ce} ПЭ {self._get_player_name(current_player_id, vk_handle)}.")

        active_domain_effect_opponent = opponent['active_effects'].get('active_domain')
        if active_domain_effect_opponent and active_domain_effect_opponent.get('user_id') == opponent_id: 
            tech_details_opponent = CURSED_TECHNIQUES[opponent['technique_id']]
            domain_stats_opponent = tech_details_opponent.get('domain_expansion')
            if domain_stats_opponent:
                if domain_stats_opponent['type'] in ['damage_over_time', 'damage_buff_over_time', 'damage_debuff_over_time', 'damage_regen_over_time']:
                    if 'damage_per_turn_min' in domain_stats_opponent and 'damage_per_turn_max' in domain_stats_opponent:
                        damage_from_opponent_rt = random.randint(domain_stats_opponent['damage_per_turn_min'], domain_stats_opponent['damage_per_turn_max'])
                        player['hp'] = max(0, player['hp'] - damage_from_opponent_rt)
                        log_messages.append(f"Территория оппонента '{domain_stats_opponent['name']}' наносит {damage_from_opponent_rt} урона {self._get_player_name(current_player_id, vk_handle)}.")
                    if domain_stats_opponent['type'] == 'damage_regen_over_time' and 'ce_regen_per_turn' in domain_stats_opponent:
                        regen_ce_opponent = domain_stats_opponent['ce_regen_per_turn']
                        opponent['ce'] = min(opponent['max_ce'], opponent['ce'] + regen_ce_opponent)
                        log_messages.append(f"Территория оппонента '{domain_stats_opponent['name']}' восстанавливает {regen_ce_opponent} ПЭ {self._get_player_name(opponent_id, vk_handle)}.")
        
        for p_id in [self.challenger_id, self.target_id]:
            p_data_for_tick = self.get_player_data(p_id)
            effects_to_remove = []
            for effect_name, effect_data in list(p_data_for_tick['active_effects'].items()):
                if 'duration' in effect_data:
                    effect_data['duration'] -= 1
                    if effect_data['duration'] <= 0:
                        effects_to_remove.append(effect_name)
                        log_messages.append(f"Эффект '{effect_data.get('display_name', effect_name)}' закончился для {self._get_player_name(p_id, vk_handle)}.")
                        if effect_name == 'active_domain':
                            if effect_data.get('stun_target_id'): 
                                stunned_player_data = self.get_player_data(effect_data['stun_target_id'])
                                if stunned_player_data and 'stunned' in stunned_player_data['active_effects'] and \
                                   stunned_player_data['active_effects']['stunned'].get('source_domain') == effect_data['name']:
                                    del stunned_player_data['active_effects']['stunned']
                                    log_messages.append(f"{self._get_player_name(effect_data['stun_target_id'], vk_handle)} больше не парализован эффектом РТ '{effect_data['name']}'.")
            
            for eff_name in effects_to_remove:
                if eff_name in p_data_for_tick['active_effects']:
                     del p_data_for_tick['active_effects'][eff_name]
        
        for msg in log_messages:
            self._add_log(msg)
        return log_messages

    def can_perform_action(self, user_id, action_key):
        if self.state != BATTLE_STATE_ACTIVE: return False, "Бой не активен."
        if user_id != self.current_turn: return False, "Сейчас не ваш ход."

        player = self.get_player_data(user_id)
        if 'stunned' in player['active_effects']: return False, "Вы парализованы и не можете действовать!"

        action_key = action_key.lower()
        if action_key in BATTLE_ACTIONS:
            action_data = BATTLE_ACTIONS[action_key]
            cost = action_data.get('energy_cost', 0)
            if action_key == 'рт': 
                tech_details = CURSED_TECHNIQUES[player['technique_id']]
                if not tech_details.get('domain_expansion'): return False, "У вашей техники нет Расширения Территории."
                cost = tech_details['domain_expansion']['ce_cost']
                if 'active_domain' in player['active_effects'] or 'active_domain' in self.get_player_data(self.get_opponent_id(user_id))['active_effects']:
                    return False, "Расширение Территории уже активно в этом бою."

            if player['ce'] < cost: return False, f"Недостаточно ПЭ (нужно {cost}, у вас {player['ce']})."
            return True, "Действие доступно."

        tech_id = player['technique_id']
        technique_moves = CURSED_TECHNIQUES[tech_id]['moves']
        if action_key in technique_moves:
            move_data = technique_moves[action_key]
            cost = move_data.get('ce_cost', 0)
            if player['ce'] < cost: return False, f"Недостаточно ПЭ для '{move_data['name']}' (нужно {cost}, у вас {player['ce']})."
            return True, "Приём доступен."

        return False, f"Неизвестное действие или приём: {action_key}"

    def perform_action(self, user_id, action_key_original, vk_handle):
        action_key = action_key_original.lower()
        can_act, message = self.can_perform_action(user_id, action_key)
        if not can_act:
            return message

        player = self.get_player_data(user_id)
        opponent_id = self.get_opponent_id(user_id)
        opponent = self.get_player_data(opponent_id)
        
        action_log = []
        player_name_str = self._get_player_name(user_id, vk_handle)
        opponent_name_str = self._get_player_name(opponent_id, vk_handle)

        base_crit_chance = 0.05
        crit_multiplier = 1.5
        
        damage_boost_percent = player['active_effects'].get('Зона', {}).get('damage_boost_percent', 0)
        
        user_domain_active = player['active_effects'].get('active_domain')
        domain_damage_boost = 1.0
        if user_domain_active and user_domain_active.get('user_id') == user_id:
            player_tech_details_for_rt = CURSED_TECHNIQUES[player['technique_id']]
            player_domain_stats = player_tech_details_for_rt.get('domain_expansion')
            if player_domain_stats and player_domain_stats.get('user_damage_boost'):
                domain_damage_boost = player_domain_stats['user_damage_boost']

        opponent_evasion_boost = opponent['active_effects'].get('evasion_buff', {}).get('evasion_boost', 0)
        opponent_evasion_boost += opponent['active_effects'].get('projection_speed', {}).get('evasion_boost',0)
        
        opponent_accuracy_debuff = opponent['active_effects'].get('accuracy_debuff',{}).get('value',0)
        
        opponent_defense_reduction_value = 0
        opponent_defense_reduction_percent = 0
        
        if 'blood_shield' in opponent['active_effects']:
            opponent_defense_reduction_value += opponent['active_effects']['blood_shield']['reduction']
            del opponent['active_effects']['blood_shield'] 
            action_log.append(f"Кровавый щит {opponent_name_str} поглощает часть урона!")
        if 'body_transform_defense' in opponent['active_effects']:
             opponent_defense_reduction_value += opponent['active_effects']['body_transform_defense']['reduction_value']
             del opponent['active_effects']['body_transform_defense']
             action_log.append(f"Трансформация тела {opponent_name_str} поглощает часть урона!")
        if 'defense_stance' in opponent['active_effects']:
            opponent_defense_reduction_percent += opponent['active_effects']['defense_stance']['reduction_percent']
            action_log.append(f"{opponent_name_str} в защитной стойке!")


        if action_key in BATTLE_ACTIONS:
            action_data = BATTLE_ACTIONS[action_key]
            
            actual_cost = action_data.get('energy_cost', 0)
            if action_key == 'рт':
                 tech_details_for_rt_cost = CURSED_TECHNIQUES[player['technique_id']]
                 actual_cost = tech_details_for_rt_cost['domain_expansion']['ce_cost']
            player['ce'] = max(0, player['ce'] - actual_cost)


            if action_data['type'] == 'attack' or action_data['type'] == 'special_attack':
                damage = 0
                is_crit = random.random() < (base_crit_chance + player['active_effects'].get('projection_speed',{}).get('crit_chance_boost',0))
                
                if action_key == 'чв':
                    if random.random() < (action_data['success_chance'] - opponent_accuracy_debuff):
                        damage = random.randint(action_data['damage_min'], action_data['damage_max'])
                        action_log.append(f"⚡ {player_name_str} использует Чёрную Вспышку!")
                        buff = action_data['on_success_buff']
                        player['active_effects']['Зона'] = {'duration': buff['duration'] + 1, 'damage_boost_percent': buff['damage_boost_percent'], 'display_name': 'Зона Концентрации'}
                        action_log.append(f"{player_name_str} вошёл в 'Зону'! Урон увеличен на {buff['damage_boost_percent']}% на {buff['duration']} хода.")
                    else:
                        action_log.append(f"⚡ {player_name_str} попытался выполнить Чёрную Вспышку, но потерпел неудачу!")
                else: 
                    if random.random() < (1.0 - opponent_evasion_boost - opponent['active_effects'].get('evasion_debuff_applied',{}).get('value_reduction',0)):
                        damage = random.randint(action_data['damage_min'], action_data['damage_max'])
                        action_log.append(f"{player_name_str} использует '{action_data['name']}'.")
                    else:
                        action_log.append(f"{player_name_str} использует '{action_data['name']}', но {opponent_name_str} уклоняется!")
                        damage = 0


                if damage > 0:
                    final_damage = damage
                    final_damage *= (1 + damage_boost_percent / 100.0)
                    final_damage *= domain_damage_boost
                    if 'body_transform_attack' in player['active_effects']:
                        final_damage += player['active_effects']['body_transform_attack']['damage_bonus']
                        del player['active_effects']['body_transform_attack']
                    if is_crit: final_damage *= crit_multiplier
                    
                    final_damage_after_percent_reduction = final_damage * (1 - opponent_defense_reduction_percent)
                    final_damage_after_all_reduction = max(0, round(final_damage_after_percent_reduction) - round(opponent_defense_reduction_value))
                    
                    opponent['hp'] = max(0, opponent['hp'] - final_damage_after_all_reduction)
                    action_log.append(f"Нанесено {final_damage_after_all_reduction} урона {opponent_name_str}." + (" (Критический удар!)" if is_crit and final_damage_after_all_reduction > 0 else ""))

            elif action_data['type'] == 'defense_buff':
                player['active_effects']['defense_stance'] = {
                    'duration': action_data['duration'] + 1, 
                    'reduction_percent': action_data['damage_reduction_percent'],
                    'display_name': 'Защитная Стойка'
                }
                regen = random.randint(action_data['energy_regen_min'], action_data['energy_regen_max'])
                player['ce'] = min(player['max_ce'], player['ce'] + regen)
                action_log.append(f"🛡️ {player_name_str} встаёт в защитную стойку! Следующий урон будет снижен на {action_data['damage_reduction_percent']*100}%. Восстановлено {regen} ПЭ.")


            elif action_data['type'] == 'heal':
                if random.random() < (action_data['success_chance'] - opponent_accuracy_debuff):
                    heal_amount = random.randint(action_data['heal_min'], action_data['heal_max'])
                    player['hp'] = min(player['max_hp'], player['hp'] + heal_amount)
                    action_log.append(f"✨ {player_name_str} использует ОПТ и восстанавливает {heal_amount} HP.")
                else:
                    action_log.append(f"✨ {player_name_str} попытался использовать ОПТ, но не смог сконцентрироваться.")
            
            elif action_data['type'] == 'domain_expansion':
                tech_details = CURSED_TECHNIQUES[player['technique_id']]
                domain_data = tech_details['domain_expansion']

                if 'active_domain' in opponent['active_effects']:
                    action_log.append(f"🌌 {player_name_str} пытается раскрыть '{domain_data['name']}' против активной территории {opponent_name_str}!")
                    opponent_rt_data = CURSED_TECHNIQUES[opponent['technique_id']]['domain_expansion']
                    player_wins_clash = False
                    if domain_data['ce_cost'] > opponent_rt_data['ce_cost']: player_wins_clash = True
                    elif domain_data['ce_cost'] == opponent_rt_data['ce_cost']: player_wins_clash = random.random() < 0.5
                    
                    if player_wins_clash:
                        action_log.append(f"Территория {player_name_str} '{domain_data['name']}' доминирует и разрушает территорию оппонента!")
                        if 'active_domain' in opponent['active_effects']: 
                            if opponent['active_effects']['active_domain'].get('stun_target_id') == player['id']: 
                                if 'stunned' in player['active_effects'] and player['active_effects']['stunned'].get('source_domain') == opponent['active_effects']['active_domain']['name']:
                                    del player['active_effects']['stunned']
                                    action_log.append(f"{player_name_str} освобождается от паралича РТ '{opponent['active_effects']['active_domain']['name']}'.")
                            del opponent['active_effects']['active_domain']
                        
                        player['active_effects']['active_domain'] = {
                            'name': domain_data['name'], 'duration': domain_data['duration'] + 1, 
                            'user_id': user_id, 'display_name': f"РТ: {domain_data['name']}"}
                        action_log.append(f"Эффект '{domain_data['name']}': {domain_data['effect_description']}")
                        if domain_data['type'] == 'insta_damage':
                            rt_damage = random.randint(domain_data['damage_min'], domain_data['damage_max'])
                            opponent['hp'] = max(0, opponent['hp'] - rt_damage)
                            action_log.append(f"'{domain_data['name']}' немедленно наносит {rt_damage} урона {opponent_name_str}.")
                        elif domain_data['type'] == 'stun':
                            if random.random() < domain_data.get('stun_chance', 1.0):
                                opponent['active_effects']['stunned'] = {'duration': domain_data['duration'] +1, 'display_name': 'Паралич от РТ', 'source_domain': domain_data['name']}
                                player['active_effects']['active_domain']['stun_target_id'] = opponent_id
                                action_log.append(f"{opponent_name_str} парализован на {domain_data['duration']} хода!")
                    else:
                        action_log.append(f"Территория оппонента оказалась сильнее! '{domain_data['name']}' не смогла раскрыться.")
                
                elif random.random() < (action_data.get('success_chance', 0.75) - opponent_accuracy_debuff): 
                    action_log.append(f"🌌 {player_name_str} активирует Расширение Территории: '{domain_data['name']}'!")
                    action_log.append(f"Эффект: {domain_data['effect_description']}")
                    
                    player['active_effects']['active_domain'] = {
                        'name': domain_data['name'], 'duration': domain_data['duration'] + 1, 
                        'user_id': user_id, 'display_name': f"РТ: {domain_data['name']}"}
                    if domain_data['type'] == 'insta_damage':
                        rt_damage = random.randint(domain_data['damage_min'], domain_data['damage_max'])
                        opponent['hp'] = max(0, opponent['hp'] - rt_damage)
                        action_log.append(f"'{domain_data['name']}' немедленно наносит {rt_damage} урона {opponent_name_str}.")
                    elif domain_data['type'] == 'stun':
                        if random.random() < domain_data.get('stun_chance', 1.0):
                            opponent['active_effects']['stunned'] = {'duration': domain_data['duration'] +1, 'display_name': 'Паралич от РТ', 'source_domain': domain_data['name']}
                            player['active_effects']['active_domain']['stun_target_id'] = opponent_id
                            action_log.append(f"{opponent_name_str} парализован на {domain_data['duration']} хода!")
                        else:
                            action_log.append(f"{opponent_name_str} сопротивляется парализующему эффекту РТ!")
                else:
                    action_log.append(f"🌌 {player_name_str} попытался активировать РТ, но не смог раскрыть территорию!")
            
            elif action_data['type'] == 'utility': 
                ce_regen = random.randint(action_data['energy_regen_min'], action_data['energy_regen_max'])
                player['ce'] = min(player['max_ce'], player['ce'] + ce_regen)
                action_log.append(f"🧘 {player_name_str} отдыхает и восстанавливает {ce_regen} ПЭ.")

        elif action_key in CURSED_TECHNIQUES[player['technique_id']]['moves']:
            move_data = CURSED_TECHNIQUES[player['technique_id']]['moves'][action_key]
            player['ce'] = max(0, player['ce'] - move_data['ce_cost'])
            
            action_log.append(f"{player_name_str} использует '{move_data['name']}'.")

            if move_data['type'].startswith('attack'):
                damage = 0
                if random.random() < (1.0 - opponent_evasion_boost - opponent['active_effects'].get('evasion_debuff_applied',{}).get('value_reduction',0)):
                    damage = random.randint(move_data['damage_min'], move_data['damage_max'])
                else:
                    action_log.append(f"Но {opponent_name_str} уклоняется!")
                    damage = 0
                
                is_crit = random.random() < (base_crit_chance + player['active_effects'].get('projection_speed',{}).get('crit_chance_boost',0))

                if move_data['type'] == 'attack_aoe_hpcost' and 'hp_cost' in move_data:
                    player['hp'] = max(0, player['hp'] - move_data['hp_cost'])
                    action_log.append(f"Приём требует {move_data['hp_cost']} HP от {player_name_str}.")
                
                if damage > 0:
                    final_damage = damage 
                    final_damage *= (1 + damage_boost_percent / 100.0)
                    final_damage *= domain_damage_boost
                    if 'body_transform_attack' in player['active_effects']:
                        final_damage += player['active_effects']['body_transform_attack']['damage_bonus']
                        del player['active_effects']['body_transform_attack']
                    if is_crit: final_damage *= crit_multiplier

                    final_damage_after_percent_reduction = final_damage * (1 - opponent_defense_reduction_percent)
                    final_damage_after_all_reduction = max(0, round(final_damage_after_percent_reduction) - round(opponent_defense_reduction_value))

                    opponent['hp'] = max(0, opponent['hp'] - final_damage_after_all_reduction)
                    action_log.append(f"Нанесено {final_damage_after_all_reduction} урона {opponent_name_str}." + (" (Критический удар!)" if is_crit and final_damage_after_all_reduction > 0 else ""))

                if move_data['type'] == 'attack_debuff' and damage > 0: 
                    if 'slow_chance' in move_data and random.random() < (move_data['slow_chance'] - opponent_accuracy_debuff):
                        opponent['active_effects']['slowed'] = {'duration': move_data['slow_duration'] + 1, 'display_name': 'Замедление'}
                        action_log.append(f"{opponent_name_str} замедлен на {move_data['slow_duration']} хода!")
                    if 'evasion_debuff' in move_data : 
                        opponent['active_effects']['evasion_debuff_applied'] = {'duration': move_data['duration'] + 1, 'value_reduction': move_data['evasion_debuff'], 'display_name': 'Снижение уклонения'}
                        action_log.append(f"Уклонение {opponent_name_str} снижено на {move_data['evasion_debuff']*100}% на {move_data['duration']} хода.")
                    if 'freeze_chance' in move_data and random.random() < (move_data['freeze_chance'] - opponent_accuracy_debuff):
                        opponent['active_effects']['stunned'] = {'duration': move_data['freeze_duration'] + 1, 'display_name': 'Заморозка'}
                        action_log.append(f"{opponent_name_str} 'заморожен' и пропускает {move_data['freeze_duration']} ход!")
            
            elif move_data['type'] == 'multi_attack':
                num_hits = random.randint(move_data['num_hits_min'], move_data['num_hits_max'])
                total_damage_dealt = 0
                action_log.append(f"Приём '{move_data['name']}' наносит {num_hits} удар(а/ов):")
                for i in range(num_hits):
                    hit_damage_val = 0
                    if random.random() < (1.0 - opponent_evasion_boost - opponent['active_effects'].get('evasion_debuff_applied',{}).get('value_reduction',0)):
                        hit_damage_val = random.randint(move_data['damage_per_hit_min'], move_data['damage_per_hit_max'])
                    else:
                         action_log.append(f" - Удар {i+1}: {opponent_name_str} уклоняется!")
                         continue 

                    is_crit_multi = random.random() < (base_crit_chance + player['active_effects'].get('projection_speed',{}).get('crit_chance_boost',0))
                    
                    final_hit_damage = hit_damage_val
                    final_hit_damage *= (1 + damage_boost_percent / 100.0)
                    final_hit_damage *= domain_damage_boost
                    if 'body_transform_attack' in player['active_effects']: 
                        final_hit_damage += player['active_effects']['body_transform_attack']['damage_bonus']
                    if is_crit_multi: final_hit_damage *= crit_multiplier
                    
                    hit_damage_after_percent_reduction = final_hit_damage * (1 - opponent_defense_reduction_percent)
                    actual_hit_damage = max(0, round(hit_damage_after_percent_reduction) - round(opponent_defense_reduction_value / num_hits)) 
                    
                    total_damage_dealt += actual_hit_damage
                    action_log.append(f" - Удар {i+1}: {actual_hit_damage} урона" + (" (крит!)" if is_crit_multi and actual_hit_damage >0 else ""))
                
                if 'body_transform_attack' in player['active_effects']: del player['active_effects']['body_transform_attack'] 
                
                opponent['hp'] = max(0, opponent['hp'] - total_damage_dealt)
                if total_damage_dealt > 0: action_log.append(f"Всего нанесено {total_damage_dealt} урона {opponent_name_str}.")


            elif move_data['type'] == 'buff_defense': 
                player['active_effects']['evasion_buff'] = {'duration': move_data['duration'] + 1, 'evasion_boost': move_data['evasion_boost'], 'display_name': f"{move_data['name']}"}
                action_log.append(f"Активирована '{move_data['name']}'. Шанс уклонения повышен на {move_data['evasion_boost']*100}% на {move_data['duration']} ход.")

            elif move_data['type'] == 'debuff': 
                 if 'success_chance_debuff' in move_data:
                    opponent['active_effects']['accuracy_debuff'] = {'duration': move_data['duration'] + 1, 'value': move_data['success_chance_debuff'], 'display_name': 'Снижение точности'}
                    action_log.append(f"Точность действий {opponent_name_str} снижена на {move_data['success_chance_debuff']*100}% на {move_data['duration']} хода.")

            elif move_data['type'] == 'buff_self_choice': 
                player['active_effects']['body_transform_attack'] = {'duration': move_data['duration'] + 1, 'damage_bonus': move_data['attack_boost_value'], 'display_name': 'Трансф. Тела (Атака)'}
                action_log.append(f"Следующая атака {player_name_str} будет усилена на {move_data['attack_boost_value']} ед. урона.")
                # player['active_effects']['body_transform_defense'] = {'duration': move_data['duration'] + 1, 'reduction_value': round(player['hp'] * move_data['damage_reduction']), 'display_name': 'Трансф. Тела (Защита)'}
                # action_log.append(f"Следующая атака по {player_name_str} будет ослаблена (щит на {round(player['hp'] * move_data['damage_reduction'])}).")


            elif move_data['type'] == 'buff_self': 
                if 'evasion_boost' in move_data and 'crit_chance_boost' in move_data:
                    player['active_effects']['projection_speed'] = {
                        'duration': move_data['duration'] + 1, 'evasion_boost': move_data['evasion_boost'], 
                        'crit_chance_boost': move_data['crit_chance_boost'], 'display_name': 'Ускорение Проекции'
                    }
                    action_log.append(f"Уклонение {player_name_str} увеличено на {move_data['evasion_boost']*100}%, шанс крита на {move_data['crit_chance_boost']*100}% на {move_data['duration']} хода.")
            
            elif move_data['type'] == 'defense': 
                reduction = random.randint(move_data['damage_reduction_min'], move_data['damage_reduction_max'])
                player['active_effects']['blood_shield'] = {'duration': move_data['duration'] + 1, 'reduction': reduction, 'display_name': 'Кровавый Щит'}
                action_log.append(f"Активирован '{move_data['name']}'. Следующая атака по {player_name_str} будет ослаблена на {reduction} урона.")
        
        if 'defense_stance' in opponent['active_effects']:
            del opponent['active_effects']['defense_stance']

        tick_log = self._apply_and_tick_effects(user_id, vk_handle) 
        action_log.extend(tick_log)

        next_turn_player_id = opponent_id
        if 'stunned' in opponent['active_effects'] and opponent['active_effects']['stunned']['duration'] > 0 : 
             action_log.append(f"{opponent_name_str} парализован и пропускает ход!")
             next_turn_player_id = user_id 
        self.current_turn = next_turn_player_id

        for msg_val in action_log: 
            self._add_log(f"{msg_val}") 

        if player['hp'] <= 0 or opponent['hp'] <= 0:
            self.state = BATTLE_STATE_FINISHED
            final_log_message = ""
            if player['hp'] <= 0 and opponent['hp'] <= 0:
                final_log_message = f"⚔️ Бой окончен! Ничья между {player_name_str} и {opponent_name_str}!"
            elif opponent['hp'] <= 0:
                final_log_message = f"⚔️ Бой окончен! Победитель: {player_name_str}!"
                add_win(user_id)
                add_loss(opponent_id)
            else:
                final_log_message = f"⚔️ Бой окончен! Победитель: {opponent_name_str}!"
                add_win(opponent_id)
                add_loss(user_id)
            action_log.append(final_log_message)
            self._add_log(f"*** {final_log_message} ***")

        return "\n".join(action_log)

    def get_battle_status_text(self, vk_api_handle):
        c_name = self._get_player_name(self.challenger_id, vk_api_handle)
        t_name = self._get_player_name(self.target_id, vk_api_handle)
        
        challenger_data = self.get_player_data(self.challenger_id)
        target_data = self.get_player_data(self.target_id)

        status_lines = [f"Текущий бой: {c_name} vs {t_name}"]
        
        c_effects_list = [f"{eff_data.get('display_name', eff_name)} ({eff_data['duration']-1}х)" 
                          for eff_name, eff_data in challenger_data['active_effects'].items() if 'duration' in eff_data and eff_data['duration'] > 0 and eff_data.get('display_name')]
        c_effects = ", ".join(c_effects_list) or "нет"
        status_lines.append(f"{c_name} ({CURSED_TECHNIQUES[challenger_data['technique_id']]['name']}): "
                            f"{challenger_data['hp']}/{challenger_data['max_hp']} HP, "
                            f"{challenger_data['ce']}/{challenger_data['max_ce']} ПЭ. Эффекты: {c_effects}")

        t_effects_list = [f"{eff_data.get('display_name', eff_name)} ({eff_data['duration']-1}х)"
                          for eff_name, eff_data in target_data['active_effects'].items() if 'duration' in eff_data and eff_data['duration'] > 0 and eff_data.get('display_name')]
        t_effects = ", ".join(t_effects_list) or "нет"
        status_lines.append(f"{t_name} ({CURSED_TECHNIQUES[target_data['technique_id']]['name']}): "
                            f"{target_data['hp']}/{target_data['max_hp']} HP, "
                            f"{target_data['ce']}/{target_data['max_ce']} ПЭ. Эффекты: {t_effects}")
        
        if self.state == BATTLE_STATE_ACTIVE:
            current_turn_name = self._get_player_name(self.current_turn, vk_api_handle)
            status_lines.append(f"\nСейчас ход: {current_turn_name}")
        elif self.state == BATTLE_STATE_FINISHED:
             status_lines.append("\nБой завершен.")
        
        return "\n".join(status_lines)

    def get_available_moves_text(self, user_id, vk_handle):
        if self.current_turn != user_id or self.state != BATTLE_STATE_ACTIVE:
            return "Сейчас не ваш ход или бой не активен."

        player_data = self.get_player_data(user_id)
        if 'stunned' in player_data['active_effects']:
            return f"{self._get_player_name(user_id, vk_handle)}, вы парализованы и не можете выбрать действие."
            
        tech_id = player_data['technique_id']
        technique = CURSED_TECHNIQUES[tech_id]
        
        output_lines = [f"{self._get_player_name(user_id, vk_handle)}, ваши доступные действия:"]
        
        output_lines.append("\nОсновные действия:")
        for action_key, action_info in BATTLE_ACTIONS.items():
            actual_cost = action_info.get('energy_cost',0)
            if action_key == 'рт':
                if technique.get('domain_expansion'):
                    actual_cost = technique['domain_expansion']['ce_cost']
                else: continue 
            
            cost_str = f"{actual_cost} ПЭ"
            can_do, reason = self.can_perform_action(user_id, action_key)
            emoji_status = "✅" if can_do else "❌"
            
            action_details_str = f"`={action_key}` - {action_info['name']} ({cost_str}). {action_info['description']}"
            
            if action_info['type'] == "attack" or action_info['type'] == "special_attack":
                action_details_str += f" Урон: {action_info['damage_min']}-{action_info['damage_max']}."
            if action_info['type'] == "heal":
                action_details_str += f" Исцеление: {action_info['heal_min']}-{action_info['heal_max']}. Шанс: {action_info['success_chance']*100:.0f}%."
            if action_info['type'] == "defense_buff":
                 action_details_str += f" Снижение урона: {action_info['damage_reduction_percent']*100:.0f}%. Восст. ПЭ: {action_info['energy_regen_min']}-{action_info['energy_regen_max']}."
            if action_key == 'чв': 
                action_details_str += f" Шанс успеха: {action_info['success_chance']*100:.0f}%."
                buff = action_info['on_success_buff']
                action_details_str += f" При успехе: '{buff['name']}' (+{buff['damage_boost_percent']}% урона на {buff['duration']} хода)."
            if action_key == 'рт':
                action_details_str += f" Шанс активации: {action_info.get('success_chance', 0.75)*100:.0f}%."
                if technique.get('domain_expansion'):
                    action_details_str += f" Эффект РТ ({technique['domain_expansion']['name']}): {technique['domain_expansion']['effect_description']}"
            if action_key == 'отдых':
                action_details_str += f" Восст. ПЭ: {action_info['energy_regen_min']}-{action_info['energy_regen_max']}."

            output_lines.append(f"  {emoji_status} {action_details_str}")


        output_lines.append(f"\nПриёмы техники '{technique['name']}':")
        if not technique['moves']:
            output_lines.append("  У этой техники нет активных приёмов.")
        else:
            for move_key, move_info in technique['moves'].items():
                cost_str = f"{move_info['ce_cost']} ПЭ"
                can_do, reason = self.can_perform_action(user_id, move_key)
                emoji_status = "✅" if can_do else "❌"

                move_details_str = f"`={move_key}` - {move_info['name']} ({cost_str}). {move_info['description']}"

                if 'damage_min' in move_info and 'damage_max' in move_info:
                    move_details_str += f" Урон: {move_info['damage_min']}-{move_info['damage_max']}."
                if 'hp_cost' in move_info:
                    move_details_str += f" Затраты HP: {move_info['hp_cost']}."
                if 'evasion_boost' in move_info: 
                     move_details_str += f" Даёт +{move_info['evasion_boost']*100:.0f}% уклонения на {move_info['duration']} ход."
                if 'slow_chance' in move_info: 
                    move_details_str += f" Шанс замедления: {move_info['slow_chance']*100:.0f}% на {move_info['slow_duration']} хода."
                if 'evasion_debuff' in move_info: 
                    move_details_str += f" Снижает уклонение цели на {move_info['evasion_debuff']*100:.0f}% на {move_info['duration']} хода."
                if 'success_chance_debuff' in move_info: 
                    move_details_str += f" Снижает шанс успеха действий цели на {move_info['success_chance_debuff']*100:.0f}% на {move_info['duration']} хода."
                if move_info['type'] == 'buff_self_choice': 
                    move_details_str += f" Усиление след. атаки на {move_info['attack_boost_value']} ИЛИ снижение урона по себе на {move_info['damage_reduction']*100:.0f}% (1 ход)."
                if 'freeze_chance' in move_info: 
                    move_details_str += f" Шанс заморозки: {move_info['freeze_chance']*100:.0f}% на {move_info['freeze_duration']} ход."
                if move_info['type'] == 'buff_self' and 'crit_chance_boost' in move_info : 
                    move_details_str += f" +{move_info['evasion_boost']*100:.0f}% уклонения, +{move_info['crit_chance_boost']*100:.0f}% шанс крита на {move_info['duration']} хода."
                if move_info['type'] == 'multi_attack':
                     move_details_str += f" Удары: {move_info['num_hits_min']}-{move_info['num_hits_max']} по {move_info['damage_per_hit_min']}-{move_info['damage_per_hit_max']} урона."
                if move_info['type'] == 'defense' and 'damage_reduction_min' in move_info: 
                    move_details_str += f" Снижение урона от след. атаки: {move_info['damage_reduction_min']}-{move_info['damage_reduction_max']} (1 ход)."
                
                output_lines.append(f"  {emoji_status} {move_details_str}")
        
        return "\n".join(output_lines)

active_battles = {}

def handle_battle_command(vk, event, text_command_stripped):
    user_id = event.obj.message['from_id']
    peer_id = event.obj.message['peer_id']
    
    is_admin = user_id in ADMIN_IDS 
    
    command_parts = text_command_stripped.lower().split()
    main_command = command_parts[0] if command_parts else ""

    def get_display_name(vk_id):
        nick = get_user_nick(vk_id)
        if nick:
            return f"[id{vk_id}|{nick}]"
        char_row = get_character_by_owner_id(vk_id)
        if char_row and 'full_name' in dict(char_row):
            return f"[id{vk_id}|{dict(char_row)['full_name']}]"
        return f"[id{vk_id}|{vk_id}]"

    player_name_display = get_display_name(user_id)

    if main_command == 'бой':
        if peer_id < 2000000000:
            send_battle_message(vk, peer_id, "Бои можно начинать только в беседах.")
            return

        if peer_id in active_battles and active_battles[peer_id].state != BATTLE_STATE_FINISHED:
            send_battle_message(vk, peer_id, "В этом чате уже идет или ожидается бой.")
            return

        target_id = parse_user_mention(event.obj.message['text'])
        if not target_id:
            send_battle_message(vk, peer_id, "Укажите противника: `=Бой @упоминание`")
            return
        if target_id == user_id:
            send_battle_message(vk, peer_id, "Вы не можете вызвать на бой самого себя!")
            return
        
        target_name_display = get_display_name(target_id)

        active_battles[peer_id] = Battle(user_id, target_id, peer_id)
        active_battles[peer_id]._get_player_name(user_id, vk) 
        active_battles[peer_id]._get_player_name(target_id, vk)

        send_battle_message(vk, peer_id, 
            f"⚔️ {player_name_display} вызывает на бой {target_name_display}!\n"
            f"{target_name_display}, используйте `=Принять` чтобы начать, или `=Отклонить` для отмены."
        )
        return

    battle = active_battles.get(peer_id)
    if not battle:
        return 

    if main_command == 'отменить':
        if user_id == battle.challenger_id or user_id == battle.target_id or is_admin: 
            challenger_name_on_cancel = get_display_name(battle.challenger_id)
            target_name_on_cancel = get_display_name(battle.target_id)
            del active_battles[peer_id]
            send_battle_message(vk, peer_id, f"⚔️ Бой между {challenger_name_on_cancel} и {target_name_on_cancel} отменен {player_name_display}.")
        else:
            send_battle_message(vk, peer_id, "Только участники или администратор могут отменить бой.")
        return
    
    if battle.state == BATTLE_STATE_WAITING:
        if main_command == 'принять':
            if user_id == battle.target_id:
                battle.state = BATTLE_STATE_ACTIVE
                c_data = battle.get_player_data(battle.challenger_id)
                t_data = battle.get_player_data(battle.target_id)
                
                challenger_name = battle._get_player_name(battle.challenger_id, vk)
                target_name = battle._get_player_name(battle.target_id, vk)

                msg = (f"⚔️ {target_name} принимает вызов! Бой начался!\n\n"
                       f"{challenger_name} использует технику: {CURSED_TECHNIQUES[c_data['technique_id']]['name']}\n"
                       f"{target_name} использует технику: {CURSED_TECHNIQUES[t_data['technique_id']]['name']}\n\n"
                       f"{battle.get_battle_status_text(vk)}\n\n"
                       f"{battle.get_available_moves_text(battle.current_turn, vk)}")
                send_battle_message(vk, peer_id, msg)
            else:
                send_battle_message(vk, peer_id, f"{player_name_display}, вы не являетесь целью этого вызова.")
            return
        elif main_command == 'отклонить':
            if user_id == battle.target_id:
                challenger_name_on_decline = get_display_name(battle.challenger_id)
                target_name_on_decline = get_display_name(battle.target_id)
                del active_battles[peer_id]
                send_battle_message(vk, peer_id, f"⚔️ {target_name_on_decline} отклонил вызов на бой от {challenger_name_on_decline}.")
            else:
                send_battle_message(vk, peer_id, f"{player_name_display}, вы не являетесь целью этого вызова.")
            return
        else:
            send_battle_message(vk, peer_id, f"Бой ожидает принятия. {battle._get_player_name(battle.target_id,vk)} должен использовать `=Принять` или `=Отклонить`.")
            return

    if battle.state == BATTLE_STATE_ACTIVE:
        if user_id != battle.current_turn:
            send_battle_message(vk, peer_id, f"Сейчас не ваш ход, {player_name_display}. Ходит {battle._get_player_name(battle.current_turn,vk)}.")
            return

        is_valid_battle_action = False
        can_act_check, _ = battle.can_perform_action(user_id, main_command)
        if can_act_check:
            is_valid_battle_action = True
        
        if is_valid_battle_action:
            action_result_message = battle.perform_action(user_id, main_command, vk)
            
            full_message = action_result_message + "\n\n"
            full_message += battle.get_battle_status_text(vk)

            if battle.state == BATTLE_STATE_ACTIVE :
                full_message += "\n\n" + battle.get_available_moves_text(battle.current_turn, vk)
            
            send_battle_message(vk, peer_id, full_message)

            if battle.state == BATTLE_STATE_FINISHED:
                if peer_id in active_battles: 
                    del active_battles[peer_id]
        else:
            _, reason_cant_act = battle.can_perform_action(user_id, main_command)
            available_moves = battle.get_available_moves_text(user_id, vk)
            send_battle_message(vk, peer_id, f"Не удалось выполнить '{main_command}'. Причина: {reason_cant_act}\n{available_moves}")
        return

    if battle.state == BATTLE_STATE_FINISHED:
        send_battle_message(vk, peer_id, "Этот бой уже завершен. Начните новый: `=Бой @соперник`")
        if peer_id in active_battles:
            del active_battles[peer_id]
        return

def send_battle_message(vk, peer_id_target, text, reply_to=None, keyboard=None):
    parts = split_message(text)
    for i, part in enumerate(parts):
        try:
            vk.messages.send(
                peer_id=peer_id_target,
                message=part,
                random_id=get_random_id(),
                reply_to=reply_to if i == 0 else None,
                keyboard=keyboard if i == len(parts) - 1 else None,
                disable_mentions=1 
            )
        except vk_api.exceptions.ApiError as e:
            print(f"Ошибка отправки сообщения в peer_id {peer_id_target}: {e}")
            if i == 0: 
                try:
                    vk.messages.send(
                        peer_id=peer_id_target,
                        message="Произошла ошибка при отображении сообщения боя. Попробуйте позже.",
                        random_id=get_random_id(),
                        reply_to=reply_to,
                        disable_mentions=1
                    )
                except Exception as e_inner:
                     print(f"Не удалось отправить даже сообщение об ошибке в peer_id {peer_id_target}: {e_inner}")
            break