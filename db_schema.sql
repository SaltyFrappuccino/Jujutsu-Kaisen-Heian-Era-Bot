-- vk_rp_bot/db_schema.sql
CREATE TABLE IF NOT EXISTS characters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_vk_id INTEGER NOT NULL,
    full_name TEXT NOT NULL,
    age INTEGER,
    gender TEXT,
    faction TEXT,
    appearance TEXT,
    cursed_technique_description TEXT,
    equipment TEXT,
    rp_points INTEGER DEFAULT 0,
    balance INTEGER DEFAULT 0,

    level_cursed_energy_reserve INTEGER DEFAULT 0,
    level_cursed_energy_output INTEGER DEFAULT 0,
    level_cursed_energy_control INTEGER DEFAULT 0,
    level_base_strength INTEGER DEFAULT 0,
    level_base_durability INTEGER DEFAULT 0,
    level_base_speed INTEGER DEFAULT 0,
    level_stamina INTEGER DEFAULT 0,
    level_cursed_technique_mastery INTEGER DEFAULT 0,
    level_territory_refinement INTEGER DEFAULT 0,
    level_territory_barrier_strength INTEGER DEFAULT 0,
    level_reverse_cursed_technique_output INTEGER DEFAULT 0,
    level_reverse_cursed_technique_efficiency INTEGER DEFAULT 0,
    level_black_flash_chance INTEGER DEFAULT 0,
    level_black_flash_limit INTEGER DEFAULT 0,
    -- Дополнительные уровни, которые не были в базовом списке, но есть в прокачке
    level_absolute_void_weaving INTEGER DEFAULT 0, -- Уровень Сплетения Абсолютной Пустоты
    level_falling_emotions_flower INTEGER DEFAULT 0, -- Уровень Цветка Падающих Эмоций


    has_simple_domain BOOLEAN DEFAULT FALSE,
    has_falling_blossom_emotion_sense BOOLEAN DEFAULT FALSE, -- Чувства Опадающего Цветка
    has_black_flash_learned BOOLEAN DEFAULT FALSE, -- Чёрная Вспышка (изучение как таковое)
    has_reverse_cursed_technique_learned BOOLEAN DEFAULT FALSE, -- Обратная Проклятая Техника (изучение)
    has_reverse_cursed_technique_output_learned BOOLEAN DEFAULT FALSE, -- Выброс ОПТ (изучение)
    has_incomplete_domain_expansion BOOLEAN DEFAULT FALSE,
    has_domain_expansion BOOLEAN DEFAULT FALSE,
    has_domain_amplification BOOLEAN DEFAULT FALSE,
    has_barrierless_domain_expansion BOOLEAN DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS user_states (
    vk_id INTEGER PRIMARY KEY,
    state TEXT,
    data TEXT -- JSON-строка для хранения временных данных
);

CREATE TABLE IF NOT EXISTS pending_text ( -- Для сбора длинных текстов
    vk_id INTEGER PRIMARY KEY,
    text_type TEXT, -- 'cursed_technique' или 'equipment'
    content TEXT,
    target_char_id INTEGER DEFAULT NULL -- Для редактирования существующего
);

CREATE TABLE IF NOT EXISTS user_nicks (
    vk_id INTEGER PRIMARY KEY,
    nick TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS user_stats (
    vk_id INTEGER PRIMARY KEY,
    wins INTEGER DEFAULT 0,
    losses INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS user_wallets (
    vk_id INTEGER PRIMARY KEY,
    balance INTEGER DEFAULT 0
);