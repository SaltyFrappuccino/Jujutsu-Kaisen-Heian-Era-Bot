import React, { useEffect, useState } from "react";
import { API_BASE_URL } from "../config";
import "./ProfilesPage.css";

export default function ProfilesPage() {
  const [profiles, setProfiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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

  return (
    <div className="jk-profiles-bg">
      {loading && <div className="jk-loading">Загрузка анкет...</div>}
      {error && <div className="jk-error">{error}</div>}
      <div className="jk-profiles-list">
        {profiles.map((profile) => (
          <div className="jk-profile-card" key={profile.id}>
            <div className="jk-profile-header">
              <span className="jk-profile-name">{profile.full_name}</span>
              <span className="jk-profile-age">{profile.age ? `${profile.age} лет` : "Возраст не указан"}</span>
            </div>
            <div className="jk-profile-row"><b>Пол:</b> {profile.gender || "-"}</div>
            <div className="jk-profile-row"><b>Фракция:</b> {profile.faction || "-"}</div>
            <div className="jk-profile-row"><b>Проклятая техника:</b> {profile.cursed_technique_description || "-"}</div>
            <div className="jk-profile-row"><b>ОР:</b> {profile.rp_points}</div>
            <div className="jk-profile-row"><b>Баланс:</b> {profile.balance} ¥</div>
            <div className="jk-profile-row"><b>Внешность:</b> <span className="jk-profile-appearance">{profile.appearance || "-"}</span></div>
          </div>
        ))}
      </div>
    </div>
  );
} 