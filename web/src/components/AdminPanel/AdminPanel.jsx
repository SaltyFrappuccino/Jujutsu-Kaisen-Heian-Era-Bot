import React, { useEffect, useState } from "react";
import { API_BASE_URL } from "../../config";
import "./AdminPanel.css";

const emptyCharacter = {
  owner_vk_id: 0,
  full_name: "",
  age: 0,
  gender: "",
  faction: "",
  appearance: "",
  cursed_technique_description: "",
  equipment: "",
  rp_points: 0,
  balance: 0,
  level_cursed_energy_reserve: 0,
  level_cursed_energy_output: 0,
  level_cursed_energy_control: 0,
  level_base_strength: 0,
  level_base_durability: 0,
  level_base_speed: 0,
  level_stamina: 0,
  level_cursed_technique_mastery: 0,
  level_territory_refinement: 0,
  level_territory_barrier_strength: 0,
  level_reverse_cursed_technique_output: 0,
  level_reverse_cursed_technique_efficiency: 0,
  level_black_flash_chance: 0,
  level_black_flash_limit: 0,
  level_absolute_void_weaving: 0,
  level_falling_emotions_flower: 0,
  has_simple_domain: false,
  has_falling_blossom_emotion_sense: false,
  has_black_flash_learned: false,
  has_reverse_cursed_technique_learned: false,
  has_reverse_cursed_technique_output_learned: false,
  has_incomplete_domain_expansion: false,
  has_domain_expansion: false,
  has_domain_amplification: false,
  has_barrierless_domain_expansion: false
};

export default function AdminPanel() {
  const [characters, setCharacters] = useState([]);
  const [form, setForm] = useState(emptyCharacter);
  const [editId, setEditId] = useState(null);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetch(`${API_BASE_URL}/characters/`)
      .then(res => res.json())
      .then(setCharacters);
  }, [message]);

  const handleChange = e => {
    const { name, value, type, checked } = e.target;
    setForm(f => ({
      ...f,
      [name]: type === "checkbox" ? checked : value
    }));
  };

  const handleSubmit = e => {
    e.preventDefault();
    setMessage("");
    const method = editId ? "PUT" : "POST";
    const url = editId ? `${API_BASE_URL}/characters/${editId}` : `${API_BASE_URL}/characters/`;
    const body = { ...form };
    if (editId) delete body.owner_vk_id;
    fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    })
      .then(res => res.json())
      .then(data => {
        setMessage(editId ? "Персонаж обновлён" : "Персонаж создан");
        setForm(emptyCharacter);
        setEditId(null);
      })
      .catch(() => setMessage("Ошибка при сохранении"));
  };

  const handleEdit = char => {
    setForm({ ...char });
    setEditId(char.id);
  };

  const handleCancel = () => {
    setForm(emptyCharacter);
    setEditId(null);
    setMessage("");
  };

  return (
    <div className="admin-panel">

      <div className="admin-panel-list">
        <h3>Существующие персонажи</h3>
        <ul>
          {characters.map(char => (
            <li key={char.id}>
              <button onClick={() => handleEdit(char)}>
                {char.full_name} (id: {char.id})
              </button>
            </li>
          ))}
        </ul>
      </div>
      <div className="admin-panel-form">
        <h3>{editId ? "Редактировать персонажа" : "Создать нового персонажа"}</h3>
        <form onSubmit={handleSubmit}>
          <label>VK ID владельца: <input name="owner_vk_id" type="number" value={form.owner_vk_id} onChange={handleChange} disabled={!!editId} /></label><br />
          <label>Имя: <input name="full_name" value={form.full_name} onChange={handleChange} /></label><br />
          <label>Возраст: <input name="age" type="number" value={form.age} onChange={handleChange} /></label><br />
          <label>Пол: <input name="gender" value={form.gender} onChange={handleChange} /></label><br />
          <label>Фракция: <input name="faction" value={form.faction} onChange={handleChange} /></label><br />
          <label>Внешность: <textarea name="appearance" value={form.appearance} onChange={handleChange} /></label><br />
          <label>Проклятая техника: <textarea name="cursed_technique_description" value={form.cursed_technique_description} onChange={handleChange} /></label><br />
          <label>Снаряжение: <textarea name="equipment" value={form.equipment} onChange={handleChange} /></label><br />
          <label>ОР: <input name="rp_points" type="number" value={form.rp_points} onChange={handleChange} /></label><br />
          <label>Баланс: <input name="balance" type="number" value={form.balance} onChange={handleChange} /></label><br />
          <label>Запас ПЭ: <input name="level_cursed_energy_reserve" type="number" value={form.level_cursed_energy_reserve} onChange={handleChange} /></label><br />
          <label>Выброс ПЭ: <input name="level_cursed_energy_output" type="number" value={form.level_cursed_energy_output} onChange={handleChange} /></label><br />
          <label>Контроль ПЭ: <input name="level_cursed_energy_control" type="number" value={form.level_cursed_energy_control} onChange={handleChange} /></label><br />
          <label>Сила: <input name="level_base_strength" type="number" value={form.level_base_strength} onChange={handleChange} /></label><br />
          <label>Прочность: <input name="level_base_durability" type="number" value={form.level_base_durability} onChange={handleChange} /></label><br />
          <label>Скорость: <input name="level_base_speed" type="number" value={form.level_base_speed} onChange={handleChange} /></label><br />
          <label>Выносливость: <input name="level_stamina" type="number" value={form.level_stamina} onChange={handleChange} /></label><br />
          <label>Мастерство техники: <input name="level_cursed_technique_mastery" type="number" value={form.level_cursed_technique_mastery} onChange={handleChange} /></label><br />
          <label>Тонкая настройка территории: <input name="level_territory_refinement" type="number" value={form.level_territory_refinement} onChange={handleChange} /></label><br />
          <label>Прочность барьера: <input name="level_territory_barrier_strength" type="number" value={form.level_territory_barrier_strength} onChange={handleChange} /></label><br />
          <label>Выброс обратной техники: <input name="level_reverse_cursed_technique_output" type="number" value={form.level_reverse_cursed_technique_output} onChange={handleChange} /></label><br />
          <label>Эффективность обратной техники: <input name="level_reverse_cursed_technique_efficiency" type="number" value={form.level_reverse_cursed_technique_efficiency} onChange={handleChange} /></label><br />
          <label>Шанс Чёрной Вспышки: <input name="level_black_flash_chance" type="number" value={form.level_black_flash_chance} onChange={handleChange} /></label><br />
          <label>Лимит Чёрной Вспышки: <input name="level_black_flash_limit" type="number" value={form.level_black_flash_limit} onChange={handleChange} /></label><br />
          <label>Сплетение Абсолютной Пустоты: <input name="level_absolute_void_weaving" type="number" value={form.level_absolute_void_weaving} onChange={handleChange} /></label><br />
          <label>Чувства Опадающего Цветка: <input name="level_falling_emotions_flower" type="number" value={form.level_falling_emotions_flower} onChange={handleChange} /></label><br />
          <label><input name="has_simple_domain" type="checkbox" checked={form.has_simple_domain} onChange={handleChange} /> Simple Domain</label><br />
          <label><input name="has_falling_blossom_emotion_sense" type="checkbox" checked={form.has_falling_blossom_emotion_sense} onChange={handleChange} /> Falling Blossom Emotion Sense</label><br />
          <label><input name="has_black_flash_learned" type="checkbox" checked={form.has_black_flash_learned} onChange={handleChange} /> Black Flash Learned</label><br />
          <label><input name="has_reverse_cursed_technique_learned" type="checkbox" checked={form.has_reverse_cursed_technique_learned} onChange={handleChange} /> Reverse Cursed Technique Learned</label><br />
          <label><input name="has_reverse_cursed_technique_output_learned" type="checkbox" checked={form.has_reverse_cursed_technique_output_learned} onChange={handleChange} /> Reverse Cursed Technique Output Learned</label><br />
          <label><input name="has_incomplete_domain_expansion" type="checkbox" checked={form.has_incomplete_domain_expansion} onChange={handleChange} /> Incomplete Domain Expansion</label><br />
          <label><input name="has_domain_expansion" type="checkbox" checked={form.has_domain_expansion} onChange={handleChange} /> Domain Expansion</label><br />
          <label><input name="has_domain_amplification" type="checkbox" checked={form.has_domain_amplification} onChange={handleChange} /> Domain Amplification</label><br />
          <label><input name="has_barrierless_domain_expansion" type="checkbox" checked={form.has_barrierless_domain_expansion} onChange={handleChange} /> Barrierless Domain Expansion</label><br />
          <button type="submit">{editId ? "Сохранить изменения" : "Создать персонажа"}</button>
          {editId && <button type="button" onClick={handleCancel}>Отмена</button>}
        </form>
        {message && <div className="admin-panel-message">{message}</div>}
      </div>
    </div>
  );
} 