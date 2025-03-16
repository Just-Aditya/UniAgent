import React, { useState } from "react";
import axios from "axios";
import "./Chatbot.css"; // Import the CSS file


function App() {
  const [university, setUniversity] = useState("");
  const [input, setInput] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!university) {
      alert("Please select a university!");
      return;
    }
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input };
    setChat([...chat, userMessage]);

    setLoading(true);

    try {
      const res = await axios.post("http://127.0.0.1:8000/query", {
        university_name: university,
        query: input,
      });

      const botMessage = { role: "assistant", content: res.data.response };
      setChat([...chat, userMessage, botMessage]);
    } catch (error) {
      console.error("Error fetching response:", error);
    }

    setInput("");
    setLoading(false);
  };

  return (
    <div className="chat-container">
      <h1>University AI Chatbot</h1>

      <select value={university} onChange={(e) => setUniversity(e.target.value)}>
        <option value="">Select University</option>
        <option value="KIIT">KIIT</option>
        <option value="ABC University">ABC University</option>
      </select>

      <div className="chat-box">
        {chat.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            {message.content}
          </div>
        ))}
      </div>

      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Ask something..."
      />
      <button onClick={sendMessage} disabled={loading}>
        {loading ? "Thinking..." : "Send"}
      </button>
    </div>
  );
}

export default App;
