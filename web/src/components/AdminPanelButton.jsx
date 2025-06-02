import React, { useState } from "react";
import "./AdminPanelButton.css";

export default function AdminPanelButton() {
  const [showModal, setShowModal] = useState(false);
  const [input, setInput] = useState("");
  const [error, setError] = useState("");

  const handleOpen = () => {
    setShowModal(true);
    setInput("");
    setError("");
  };
  const handleClose = () => {
    setShowModal(false);
    setInput("");
    setError("");
  };
  const handleSubmit = (e) => {
    e.preventDefault();
    if (input === "18012005") {
      alert("Доступ к админ-панели получен! (Панель в разработке)");
      handleClose();
    } else {
      setError("Неверный ключ!");
    }
  };

  return (
    <>
      <button className="jk-admin-btn" onClick={handleOpen}>
        Админ-Панель
      </button>
      {showModal && (
        <div className="jk-modal-bg">
          <div className="jk-modal">
            <h2>Вход в Админ-Панель</h2>
            <form onSubmit={handleSubmit}>
              <input
                type="password"
                placeholder="Secret-Key"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                className="jk-admin-input"
                autoFocus
              />
              <button type="submit" className="jk-admin-submit">Войти</button>
              <button type="button" className="jk-admin-cancel" onClick={handleClose}>Отмена</button>
            </form>
            {error && <div className="jk-admin-error">{error}</div>}
          </div>
        </div>
      )}
    </>
  );
} 