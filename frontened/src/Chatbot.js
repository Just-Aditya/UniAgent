import React, { useState } from "react";
import axios from "axios";
import "./styles/Chatbot.css";

function Chatbot({ user }) {
  const [query, setQuery] = useState("");
  const [chat, setChat] = useState([]);

  const sendQuery = async () => {
    if (!query.trim()) return;

    const userMessage = { role: "user", content: query };
    setChat([...chat, userMessage]);

    try {
      const res = await axios.post("http://127.0.0.1:8000/query", {
        university_name: "Your University",
        query: query,
      });

      const botMessage = { role: "assistant", content: res.data.response };
      setChat([...chat, userMessage, botMessage]);
    } catch (error) {
      console.error("Error fetching response:", error);
    }

    setQuery("");
  };

  return (
    <div className="chat-container">
      <h2>University Chatbot</h2>
      <div className="chat-box">
        {chat.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
      </div>
      <input
        type="text"
        placeholder="Ask something..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <button onClick={sendQuery}>Send</button>
    </div>
  );
}

export default Chatbot;
