import { useState } from "react";
import axios from "axios";

export default function ChatbotUI() {
  const [selectedFiles, setSelectedFiles] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleFileChange = (event) => {
    setSelectedFiles(event.target.files);
  };

  const handleUpload = async () => {
    if (!selectedFiles) return;
    setUploading(true);
    const formData = new FormData();
    for (const file of selectedFiles) {
      formData.append("files", file);
    }

    try {
      await axios.post("http://localhost:8000/api/upload-documents", formData);
      alert("Files uploaded successfully!");
    } catch (error) {
      alert("No valid PDF files uploaded.");
      console.error(error);
    } finally {
      setUploading(false);
    }
  };

  const handleChatSubmit = async () => {
    if (!chatInput.trim()) return;
    setLoading(true);
    setChatHistory([...chatHistory, { role: "user", content: chatInput }]);

    try {
      const response = await axios.post("http://localhost:8000/api/chat/ask", {
        query: chatInput,
      });

      setChatHistory((prev) => [
        ...prev,
        { role: "ai", content: response.data.response },
      ]);
    } catch (error) {
      alert("Error getting response");
      console.error(error);
    } finally {
      setLoading(false);
      setChatInput("");
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <img src="src/assets/lo.png" alt="Chatbot Logo" className="chat-logo" />
        <h1>Chatbot UI</h1>
      </div>

      <div className="upload-section">
        <h2>Upload PDF Documents</h2>
        <input type="file" multiple onChange={handleFileChange} />
        <button onClick={handleUpload} disabled={uploading}>
          {uploading ? "Uploading..." : "Upload PDFs"}
        </button>
      </div>

      <div className="chat-box">
        {chatHistory.map((msg, index) => (
          <div key={index} className={`message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
      </div>

      <div className="chat-input-container">
        <input
          type="text"
          value={chatInput}
          onChange={(e) => setChatInput(e.target.value)}
          placeholder="Ask a question..."
        />
        <button onClick={handleChatSubmit} disabled={loading}>
          {loading ? "Thinking..." : "Send"}
        </button>
      </div>
    </div>
  );
}