import React, { useState } from "react";
import axios from "axios";

function Leave() {
  const [leaveType, setLeaveType] = useState("");
  const [message, setMessage] = useState("");

  const handleLeaveRequest = async () => {
    try {
      const response = await axios.post("http://127.0.0.1:8000/leave", {
        university_name: "Your University",
        employee_id: "mentee_01",
        leave_type: leaveType,
      });

      setMessage(response.data.message);
    } catch (error) {
      setMessage("Error submitting leave request.");
    }
  };

  return (
    <div className="leave-container">
      <h2>Request Leave</h2>
      <select value={leaveType} onChange={(e) => setLeaveType(e.target.value)}>
        <option value="">Select Leave Type</option>
        <option value="Casual">Casual</option>
        <option value="Sick">Sick</option>
      </select>
      <button onClick={handleLeaveRequest}>Submit</button>
      {message && <p>{message}</p>}
    </div>
  );
}

export default Leave;
