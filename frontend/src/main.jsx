import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import ChatbotUI from './ChatbotUI.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <ChatbotUI />
  </StrictMode>,
)
