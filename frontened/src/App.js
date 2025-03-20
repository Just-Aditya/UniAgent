import React, { useState } from "react";
import Login from "./Login";
import MentorDashboard from "./MentorDashboard";
import MenteeDashboard from "./MenteeDashboard";
import "./styles/App.css";

function App() {
  const [user, setUser] = useState(null);

  return (
    <div className="app-container">
      {!user ? (
        <Login setUser={setUser} />
      ) : user.role === "mentor" ? (
        <MentorDashboard user={user} />
      ) : (
        <MenteeDashboard user={user} />
      )}
    </div>
  );
}

export default App;
