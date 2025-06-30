
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import sqlite3
import json


DATABASE_URL = "rp_bot.db"

def get_db_connection():
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    return conn


class CharacterBase(BaseModel):
    owner_vk_id: int
    full_name: str
    age: Optional[int] = None
    gender: Optional[str] = None
    faction: Optional[str] = None
    appearance: Optional[str] = None
    cursed_technique_description: Optional[str] = None
    equipment: Optional[str] = None
    rp_points: int = Field(default=0)
    balance: int = Field(default=0)
    level_cursed_energy_reserve: int = Field(default=0)
    level_cursed_energy_output: int = Field(default=0)
    level_cursed_energy_control: int = Field(default=0)
    level_base_strength: int = Field(default=0)
    level_base_durability: int = Field(default=0)
    level_base_speed: int = Field(default=0)
    level_stamina: int = Field(default=0)
    level_cursed_technique_mastery: int = Field(default=0)
    level_territory_refinement: int = Field(default=0)
    level_territory_barrier_strength: int = Field(default=0)
    level_reverse_cursed_technique_output: int = Field(default=0)
    level_reverse_cursed_technique_efficiency: int = Field(default=0)
    level_black_flash_chance: int = Field(default=0)
    level_black_flash_limit: int = Field(default=0)
    level_absolute_void_weaving: int = Field(default=0)
    level_falling_emotions_flower: int = Field(default=0)
    has_simple_domain: bool = Field(default=False)
    has_falling_blossom_emotion_sense: bool = Field(default=False)
    has_black_flash_learned: bool = Field(default=False)
    has_reverse_cursed_technique_learned: bool = Field(default=False)
    has_reverse_cursed_technique_output_learned: bool = Field(default=False)
    has_incomplete_domain_expansion: bool = Field(default=False)
    has_domain_expansion: bool = Field(default=False)
    has_domain_amplification: bool = Field(default=False)
    has_barrierless_domain_expansion: bool = Field(default=False)

class CharacterCreate(CharacterBase):
    pass

class CharacterUpdate(BaseModel):
    owner_vk_id: Optional[int] = None
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    faction: Optional[str] = None
    appearance: Optional[str] = None
    cursed_technique_description: Optional[str] = None
    equipment: Optional[str] = None
    rp_points: Optional[int] = None
    balance: Optional[int] = None
    level_cursed_energy_reserve: Optional[int] = None
    level_cursed_energy_output: Optional[int] = None
    level_cursed_energy_control: Optional[int] = None
    level_base_strength: Optional[int] = None
    level_base_durability: Optional[int] = None
    level_base_speed: Optional[int] = None
    level_stamina: Optional[int] = None
    level_cursed_technique_mastery: Optional[int] = None
    level_territory_refinement: Optional[int] = None
    level_territory_barrier_strength: Optional[int] = None
    level_reverse_cursed_technique_output: Optional[int] = None
    level_reverse_cursed_technique_efficiency: Optional[int] = None
    level_black_flash_chance: Optional[int] = None
    level_black_flash_limit: Optional[int] = None
    level_absolute_void_weaving: Optional[int] = None
    level_falling_emotions_flower: Optional[int] = None
    has_simple_domain: Optional[bool] = None
    has_falling_blossom_emotion_sense: Optional[bool] = None
    has_black_flash_learned: Optional[bool] = None
    has_reverse_cursed_technique_learned: Optional[bool] = None
    has_reverse_cursed_technique_output_learned: Optional[bool] = None
    has_incomplete_domain_expansion: Optional[bool] = None
    has_domain_expansion: Optional[bool] = None
    has_domain_amplification: Optional[bool] = None
    has_barrierless_domain_expansion: Optional[bool] = None

class Character(CharacterBase):
    id: int
    class Config:
        orm_mode = True


class UserStateBase(BaseModel):
    vk_id: int
    state: Optional[str] = None
    data: Optional[Dict[str, Any]] = None

class UserStateCreate(UserStateBase):
    pass

class UserState(UserStateBase):
    
    class Config:
        orm_mode = True


app = FastAPI(title="RP Bot Admin API", description="API для управления базой данных RP бота")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://185.188.182.11:5173"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.post("/characters/", response_model=Character, status_code=status.HTTP_201_CREATED, summary="Создать нового персонажа")
def create_character_api(character: CharacterCreate, db: sqlite3.Connection = Depends(get_db_connection)):
    char_data = character.dict()
    cursor = db.cursor()
    columns = ', '.join(f'"{key}"' for key in char_data.keys())
    placeholders = ', '.join('?' * len(char_data))
    sql = f"INSERT INTO characters ({columns}) VALUES ({placeholders})"
    try:
        cursor.execute(sql, tuple(char_data.values()))
        db.commit()
        created_id = cursor.lastrowid
    
        cursor.execute("SELECT * FROM characters WHERE id = ?", (created_id,))
        new_char_row = cursor.fetchone()
        if new_char_row is None:
            raise HTTPException(status_code=500, detail="Не удалось получить созданного персонажа")
        return Character(**dict(new_char_row)) # Преобразуем sqlite3.Row в dict, затем в Pydantic модель
    except sqlite3.IntegrityError as e:
        raise HTTPException(status_code=409, detail=f"Ошибка целостности данных: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {e}")
    finally:
        db.close()


@app.get("/characters/{character_id}", response_model=Character, summary="Получить персонажа по ID")
def read_character_api(character_id: int, db: sqlite3.Connection = Depends(get_db_connection)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM characters WHERE id = ?", (character_id,))
    char_row = cursor.fetchone()
    db.close()
    if char_row is None:
        raise HTTPException(status_code=404, detail="Персонаж не найден")
    return Character(**dict(char_row))

@app.get("/characters/", response_model=List[Character], summary="Получить список всех персонажей")
def read_characters_api(skip: int = 0, limit: int = 100, db: sqlite3.Connection = Depends(get_db_connection)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM characters ORDER BY full_name LIMIT ? OFFSET ?", (limit, skip))
    characters_rows = cursor.fetchall()
    db.close()
    return [Character(**dict(row)) for row in characters_rows]

@app.put("/characters/{character_id}", response_model=Character, summary="Обновить персонажа по ID")
def update_character_api(character_id: int, character_update: CharacterUpdate, db: sqlite3.Connection = Depends(get_db_connection)):
    update_data = character_update.dict(exclude_unset=True) # Только те поля, что были переданы
    if not update_data:
        raise HTTPException(status_code=400, detail="Нет данных для обновления")

    set_clauses = [f'"{key}" = ?' for key in update_data.keys()]
    values = list(update_data.values())
    values.append(character_id)

    sql = f"UPDATE characters SET {', '.join(set_clauses)} WHERE id = ?"
    
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM characters WHERE id = ?", (character_id,)) # Проверяем существование
        if cursor.fetchone() is None:
            db.close()
            raise HTTPException(status_code=404, detail="Персонаж для обновления не найден")
        
        cursor.execute(sql, tuple(values))
        db.commit()
        
        cursor.execute("SELECT * FROM characters WHERE id = ?", (character_id,)) # Возвращаем обновленного
        updated_char_row = cursor.fetchone()
        if updated_char_row is None: # Маловероятно, если обновление прошло успешно
             raise HTTPException(status_code=500, detail="Не удалось получить обновленного персонажа")
        return Character(**dict(updated_char_row))
    except sqlite3.Error as e:
        db.rollback() # Откатываем изменения в случае ошибки
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных при обновлении: {e}")
    finally:
        db.close()


@app.delete("/characters/{character_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить персонажа по ID")
def delete_character_api(character_id: int, db: sqlite3.Connection = Depends(get_db_connection)):
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM characters WHERE id = ?", (character_id,))
        if cursor.fetchone() is None:
            db.close()
            raise HTTPException(status_code=404, detail="Персонаж для удаления не найден")

        cursor.execute("DELETE FROM characters WHERE id = ?", (character_id,))
        db.commit()
        if cursor.rowcount == 0: # Если ничего не было удалено (маловероятно после проверки выше)
            raise HTTPException(status_code=404, detail="Персонаж не найден или уже удален")
        
    except sqlite3.Error as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных при удалении: {e}")
    finally:
        db.close()
    return {"detail": "Персонаж успешно удален"} # Можно вернуть и так, или просто status_code=204




@app.post("/user_states/", response_model=UserState, status_code=status.HTTP_201_CREATED, summary="Создать/Обновить состояние пользователя")
def create_or_update_user_state_api(user_state: UserStateCreate, db: sqlite3.Connection = Depends(get_db_connection)):

    sql = "INSERT OR REPLACE INTO user_states (vk_id, state, data) VALUES (?, ?, ?)"
    state_data_json = json.dumps(user_state.data) if user_state.data is not None else None
    try:
        cursor = db.cursor()
        cursor.execute(sql, (user_state.vk_id, user_state.state, state_data_json))
        db.commit()
    
        cursor.execute("SELECT vk_id, state, data FROM user_states WHERE vk_id = ?", (user_state.vk_id,))
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=500, detail="Не удалось получить состояние пользователя после операции")
        

        data_dict = json.loads(row["data"]) if row["data"] else None
        return UserState(vk_id=row["vk_id"], state=row["state"], data=data_dict)
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    finally:
        db.close()

@app.get("/user_states/{vk_id}", response_model=UserState, summary="Получить состояние пользователя по VK ID")
def read_user_state_api(vk_id: int, db: sqlite3.Connection = Depends(get_db_connection)):
    cursor = db.cursor()
    cursor.execute("SELECT vk_id, state, data FROM user_states WHERE vk_id = ?", (vk_id,))
    row = cursor.fetchone()
    db.close()
    if row is None:
        raise HTTPException(status_code=404, detail="Состояние пользователя не найдено")
    data_dict = json.loads(row["data"]) if row["data"] else None
    return UserState(vk_id=row["vk_id"], state=row["state"], data=data_dict)

@app.delete("/user_states/{vk_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить состояние пользователя по VK ID")
def delete_user_state_api(vk_id: int, db: sqlite3.Connection = Depends(get_db_connection)):
    cursor = db.cursor()
    try:
        cursor.execute("DELETE FROM user_states WHERE vk_id = ?", (vk_id,))
        db.commit()
        if cursor.rowcount == 0:
     
             pass # Можно и 404, но 204 тоже ок
    except sqlite3.Error as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Ошибка базы данных: {e}")
    finally:
        db.close()
    return 



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # или ["*"] для всех, но лучше явно
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(app, host="0.0.0.0", port=8000)