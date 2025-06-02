import React from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import ProfilesPage from "./components/ProfilesPage";
import AdminPanelButton from "./components/AdminPanelButton";
import "./App.css";

export default function App() {
  return (
    <Router>
      <div className="jk-manga-bg">
        <header className="jk-header">
          <h1 className="jk-title">Jujutsu Kaisen RP — Анкеты</h1>
          <AdminPanelButton />
        </header>
        <main>
          <Routes>
            <Route path="/" element={<ProfilesPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}
