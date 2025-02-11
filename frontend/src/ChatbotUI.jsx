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
    } finally {
      setLoading(false);
      setChatInput("");
    }
  };

  return (
    <div className="flex flex-col items-center p-6 bg-gray-100 min-h-screen">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">Chatbot UI</h1>

      {/* File Upload Section */}
      <div className="bg-white p-4 rounded-lg shadow-md w-full max-w-lg">
        <h2 className="text-lg font-semibold mb-2">Upload PDF Documents</h2>
        <input
          type="file"
          multiple
          onChange={handleFileChange}
          className="mb-2 border p-2 w-full"
        />
        <button
          onClick={handleUpload}
          disabled={uploading}
          className="bg-blue-500 text-white px-4 py-2 rounded w-full hover:bg-blue-600 transition"
        >
          {uploading ? "Uploading..." : "Upload PDFs"}
        </button>
      </div>

      {/* Chat Section */}
      <div className="bg-white p-4 rounded-lg shadow-md w-full max-w-lg mt-6">
        <h2 className="text-lg font-semibold mb-2">Chat with the Bot</h2>
        <div className="h-64 overflow-y-auto border p-2 bg-gray-50 rounded-lg">
          {chatHistory.map((msg, index) => (
            <p
              key={index}
              className={`p-2 rounded my-1 ${
                msg.role === "user"
                  ? "bg-gray-200 text-right"
                  : "bg-green-100 text-left"
              }`}
            >
              {msg.content}
            </p>
          ))}
        </div>
        <div className="mt-2 flex">
          <input
            type="text"
            value={chatInput}
            onChange={(e) => setChatInput(e.target.value)}
            className="flex-1 border p-2 rounded focus:outline-none focus:ring focus:border-blue-300"
            placeholder="Ask a question..."
          />
          <button
            onClick={handleChatSubmit}
            disabled={loading}
            className="bg-green-500 text-white px-4 py-2 ml-2 rounded hover:bg-green-600 transition"
          >
            {loading ? "Thinking..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}
