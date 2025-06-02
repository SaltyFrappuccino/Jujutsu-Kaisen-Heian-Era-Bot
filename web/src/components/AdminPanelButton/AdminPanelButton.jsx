import React from "react";
import { useNavigate } from "react-router-dom";
import "./AdminPanelButton.css";

export default function AdminPanelButton() {
  const navigate = useNavigate();
  return (
    <button className="jk-admin-btn" onClick={() => navigate("/admin")}>Админ-Панель</button>
  );
} 