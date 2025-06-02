import React, { useEffect, useState } from "react";
import "./ProfilesPage.css";
import { API_BASE_URL } from "../../config";

function CollapsibleSection({ title, children }) {
  const [open, setOpen] = useState(false);
  return (
    <div className="jk-collapsible-section">
      <div className="jk-collapsible-header" onClick={() => setOpen((v) => !v)}>
        <span>{title}</span>
        <span className="jk-collapsible-arrow">{open ? "▲" : "▼"}</span>
      </div>
      {open && <div className="jk-collapsible-content">{children}</div>}
    </div>
  );
}

export default function ProfilesPage() {
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    setLoading(true);
    fetch(`${API_BASE_URL}/characters/`)
      .then((res) => {
        if (!res.ok) throw new Error("Ошибка загрузки анкет");
        return res.json();
      })
      .then((data) => {
        setProfiles(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  const filtered = profiles.filter((profile) =>
    profile.full_name?.toLowerCase().includes(search.toLowerCase()) ||
    profile.faction?.toLowerCase().includes(search.toLowerCase()) ||
    profile.cursed_technique_description?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="jk-profiles-bg">
      <div className="jk-profiles-searchbar-wrap">
        <input
          className="jk-profiles-searchbar"
          type="text"
          placeholder="Поиск по имени, фракции или технике..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
      </div>
      {loading && <div className="jk-loading">Загрузка анкет...</div>}
      {error && <div className="jk-error">{error}</div>}
      <div className="jk-profiles-list">
        {filtered.map((profile) => (
          <div className="jk-profile-card" key={profile.id}>
            <div className="jk-profile-header">
              <span className="jk-profile-name">{profile.full_name}</span>
              <span className="jk-profile-age">{profile.age ? `${profile.age} лет` : "Возраст не указан"}</span>
            </div>
            <div className="jk-profile-row"><b>Пол:</b> {profile.gender || "-"}</div>
            <div className="jk-profile-row"><b>Фракция:</b> {profile.faction || "-"}</div>
            <CollapsibleSection title="Проклятая техника">
              <div className="jk-profile-row" dangerouslySetInnerHTML={{__html: (profile.cursed_technique_description || "-").replace(/\n/g, '<br />')}} />
            </CollapsibleSection>
            <CollapsibleSection title="Характеристики">
              <div className="jk-profile-row"><b>ОР:</b> {profile.rp_points}</div>
              <div className="jk-profile-row"><b>Баланс:</b> {profile.balance} ¥</div>
              <div className="jk-profile-row"><b>Запас проклятой энергии:</b> {profile.level_cursed_energy_reserve}</div>
              <div className="jk-profile-row"><b>Выброс проклятой энергии:</b> {profile.level_cursed_energy_output}</div>
              <div className="jk-profile-row"><b>Контроль проклятой энергии:</b> {profile.level_cursed_energy_control}</div>
              <div className="jk-profile-row"><b>Сила:</b> {profile.level_base_strength}</div>
              <div className="jk-profile-row"><b>Прочность:</b> {profile.level_base_durability}</div>
              <div className="jk-profile-row"><b>Скорость:</b> {profile.level_base_speed}</div>
              <div className="jk-profile-row"><b>Выносливость:</b> {profile.level_stamina}</div>
              <div className="jk-profile-row"><b>Мастерство техники:</b> {profile.level_cursed_technique_mastery}</div>
              <div className="jk-profile-row"><b>Тонкая настройка территории:</b> {profile.level_territory_refinement}</div>
              <div className="jk-profile-row"><b>Прочность барьера:</b> {profile.level_territory_barrier_strength}</div>
              <div className="jk-profile-row"><b>Выброс обратной техники:</b> {profile.level_reverse_cursed_technique_output}</div>
              <div className="jk-profile-row"><b>Эффективность обратной техники:</b> {profile.level_reverse_cursed_technique_efficiency}</div>
              <div className="jk-profile-row"><b>Шанс Чёрной Вспышки:</b> {profile.level_black_flash_chance}</div>
              <div className="jk-profile-row"><b>Лимит Чёрной Вспышки:</b> {profile.level_black_flash_limit}</div>
              <div className="jk-profile-row"><b>Сплетение Абсолютной Пустоты:</b> {profile.level_absolute_void_weaving}</div>
              <div className="jk-profile-row"><b>Чувства Опадающего Цветка:</b> {profile.level_falling_emotions_flower}</div>
            </CollapsibleSection>
            <CollapsibleSection title="Снаряжение">
              <div className="jk-profile-row" dangerouslySetInnerHTML={{__html: (profile.equipment || "-").replace(/\n/g, '<br />')}} />
            </CollapsibleSection>
            <CollapsibleSection title="Список изученных техник">
              {Object.entries(profile)
                .filter(([key, value]) => key.startsWith('has_') && value)
                .map(([key]) => (
                  <div className="jk-profile-row" key={key}>{key.replace('has_', '').replace(/_/g, ' ')}</div>
                ))
                .length === 0 ? (
                  <div className="jk-profile-row">Нет изученных техник</div>
                ) : null}
              {Object.entries(profile)
                .filter(([key, value]) => key.startsWith('has_') && value)
                .map(([key]) => (
                  <div className="jk-profile-row" key={key}>{key.replace('has_', '').replace(/_/g, ' ')}</div>
                ))}
            </CollapsibleSection>
            <CollapsibleSection title="Внешность">
              <div className="jk-profile-appearance" dangerouslySetInnerHTML={{__html: (profile.appearance || "-").replace(/\n/g, '<br />')}} />
            </CollapsibleSection>
          </div>
        ))}
      </div>
    </div>
  );
} 