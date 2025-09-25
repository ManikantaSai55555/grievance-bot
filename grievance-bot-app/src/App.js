import React, { useState } from "react";
import axios from "axios";

function App() {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Hi! Please describe your grievance." },
  ]);
  const [input, setInput] = useState("");

  const sendMessage = async () => {
    if (!input.trim()) return;

    // Show user message
    setMessages([...messages, { sender: "user", text: input }]);

    try {
      // Send grievance to backend
      const res = await axios.post("http://127.0.0.1:8000/tickets", {
        grievance_text: input,
      });

      // Chatbot response
      const botReply = `Your grievance has been recorded. 
      Ticket ID: #${res.data.id}, 
      Assigned Team: ${res.data.assigned_team}, 
      Status: ${res.data.status}`;

      setMessages((prev) => [...prev, { sender: "bot", text: botReply }]);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Oops! Something went wrong." },
      ]);
    }

    setInput("");
  };

  return (
    <div style={styles.container}>
      <h2 style={styles.title}>Grievance Chatbot</h2>
      <div style={styles.chatBox}>
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              ...styles.message,
              alignSelf: msg.sender === "user" ? "flex-end" : "flex-start",
              backgroundColor:
                msg.sender === "user" ? "#d1e7ff" : "#e9ecef",
            }}
          >
            {msg.text}
          </div>
        ))}
      </div>
      <div style={styles.inputBox}>
        <input
          style={styles.input}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Type your grievance..."
        />
        <button style={styles.button} onClick={sendMessage}>
          Send
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: { width: "400px", margin: "50px auto", fontFamily: "Arial" },
  title: { textAlign: "center" },
  chatBox: {
    display: "flex",
    flexDirection: "column",
    border: "1px solid #ccc",
    padding: "10px",
    height: "400px",
    overflowY: "scroll",
    borderRadius: "8px",
  },
  message: {
    margin: "5px",
    padding: "10px",
    borderRadius: "8px",
    maxWidth: "70%",
  },
  inputBox: { display: "flex", marginTop: "10px" },
  input: {
    flex: 1,
    padding: "10px",
    borderRadius: "5px",
    border: "1px solid #ccc",
  },
  button: {
    marginLeft: "5px",
    padding: "10px 15px",
    border: "none",
    background: "#007bff",
    color: "white",
    borderRadius: "5px",
    cursor: "pointer",
  },
};

export default App;
