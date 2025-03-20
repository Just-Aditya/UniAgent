import React, { useState } from "react";
import axios from "axios";

function Meeting() {
  const [meetingData, setMeetingData] = useState({
    mentor_id: "mentor_01",
    meeting_date: "",
    meeting_time: "",
    location: "",
    message: "",
  });

  const [message, setMessage] = useState("");

  const handleInputChange = (e) => {
    setMeetingData({ ...meetingData, [e.target.name]: e.target.value });
  };

  const scheduleMeeting = async () => {
    try {
      const response = await axios.post("http://127.0.0.1:8000/schedule_meeting", meetingData);
      setMessage(response.data.message);
    } catch (error) {
      setMessage("Error scheduling meeting.");
    }
  };

  return (
    <div className="meeting-container">
      <h2>Schedule Meeting</h2>
      <input type="date" name="meeting_date" onChange={handleInputChange} />
      <input type="time" name="meeting_time" onChange={handleInputChange} />
      <input type="text" name="location" placeholder="Location" onChange={handleInputChange} />
      <textarea name="message" placeholder="Meeting Details" onChange={handleInputChange}></textarea>
      <button onClick={scheduleMeeting}>Schedule</button>
      {message && <p>{message}</p>}
    </div>
  );
}

export default Meeting;
