import React, { useState } from "react";
import axios from "axios";

function ScheduleMeeting({ user }) {
  const [date, setDate] = useState("");
  const [time, setTime] = useState("");
  const [location, setLocation] = useState("");
  const [message, setMessage] = useState("");

  const scheduleMeeting = async () => {
    if (!date || !time || !location || !message) {
      alert("Please fill in all fields.");
      return;
    }

    try {
      await axios.post("http://127.0.0.1:8000/schedule_meeting", {
        mentor_id: user.userId,
        meeting_date: date,
        meeting_time: time,
        location: location,
        message: message,
      });

      alert("Meeting scheduled and invitations sent!");
    } catch (error) {
      console.error("Error scheduling meeting:", error);
      alert("Failed to schedule meeting.");
    }
  };

  return (
    <div>
      <h3>Schedule a Meeting</h3>
      <input
        type="date"
        value={date}
        onChange={(e) => setDate(e.target.value)}
      />
      <input
        type="time"
        value={time}
        onChange={(e) => setTime(e.target.value)}
      />
      <input
        type="text"
        placeholder="Meeting Location"
        value={location}
        onChange={(e) => setLocation(e.target.value)}
      />
      <input
        type="text"
        placeholder="Meeting Message"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
      />
      <button onClick={scheduleMeeting}>Schedule Meeting</button>
    </div>
  );
}

export default ScheduleMeeting;
