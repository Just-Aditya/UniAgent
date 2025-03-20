import React from "react";
import Chatbot from "./Chatbot";
import Leave from "./Leave";
import Certificate from "./Certificate";
import Documents from "./Documents";
import "./styles/Dashboard.css";

function MenteeDashboard({ user }) {
  return (
    <div className="dashboard">
      <h2>Welcome, {user.userId} (Mentee)</h2>
      <Chatbot user={user} />
      <Leave user={user} />
      <Certificate user={user} />
      <Documents user={user} />
    </div>
  );
}

export default MenteeDashboard;
