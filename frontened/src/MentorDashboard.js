import React from "react";
import Chatbot from "./Chatbot";
import Documents from "./Documents";
import ScheduleMeeting from "./ScheduleMeeting";
import "./styles/Dashboard.css";

function MentorDashboard({ user }) {
  return (
    <div className="dashboard">
      <h2>Welcome, {user.userId} (Mentor)</h2>
      <Chatbot user={user} />
      <Documents user={user} />
      <ScheduleMeeting user={user} />
    </div>
  );
}

export default MentorDashboard;
