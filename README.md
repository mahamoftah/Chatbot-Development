# 📌 Chatbot Development

## 🚀 Overview
This project is a **document-based chatbot** that allows users to upload PDF files and ask questions based on the extracted content. The chatbot uses **LLM** to process user queries and provide relevant responses.

---

## ⚙️ Features
✅ **PDF Upload** - Users can upload multiple PDF documents.  
✅ **Text Extraction** - Extracts content from uploaded documents.  
✅ **AI-Powered Q&A** - Answers user questions based on document content.  
✅ **Embeddings & Vector Search** - Uses embeddings and a vector database for efficient search.  
✅ **FastAPI Backend** - Provides API endpoints for document upload and chatbot interactions.  
✅ **React Frontend** - Simple UI for uploading files and chatting with the bot.  
✅ **Docker Support** - Easily deployable with Docker.  

---

## 🛠 Setup Instructions
### **1️⃣ Backend (FastAPI)**
#### **📌 Prerequisites:**
- Python 3.11
- Docker (if using containerization)

#### **📌 Installation:**
```bash
# Clone the repository
git clone https://github.com/mahamoftah/Chatbot-Development.git
cd Chatbot-Development

# Install dependencies
pip install -r requirements.txt
```

#### **📌 Run the FastAPI Server:**
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### **2️⃣ Frontend (React + Vite)**
#### **📌 Installation:**
```bash
cd frontend
npm install
```

#### **📌 Run the Frontend:**
```bash
npm run dev
```

---

## 📡 API Documentation
### **1️⃣ Upload Documents**
**Endpoint:** `POST /api/upload-documents`
- **Description:** Uploads PDF files and extracts text.
- **Request:** `multipart/form-data`
- **Response:** JSON with file processing details.

### **2️⃣ Ask a Question**
**Endpoint:** `POST /api/chat/ask`
- **Description:** Queries the chatbot based on uploaded documents.
- **Request Body:**
```json
{
  "query": "What is the leave policy?"
}
```
- **Response:**
```json
{
  "response": "Employees are entitled to 20 leave days per year."
}
```

---

## 🐳 Docker Deployment
### **1️⃣ Build & Run the Docker Container**
```bash
docker build -t Chatbot-Development .
docker run -p 8000:8000 Chatbot-Development.
```

### **2️⃣ Run with `docker-compose`**
```bash
docker-compose up --build
```

---

## 📌 Author
- **Maha Moftah**
