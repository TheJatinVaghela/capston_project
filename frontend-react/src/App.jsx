import { useState, useEffect, useCallback } from 'react'
import { Box, Container, Alert, Snackbar, useMediaQuery, useTheme } from '@mui/material'
import ChatHeader from './components/ChatHeader'
import ChatWindow from './components/ChatWindow'
import ChatInput from './components/ChatInput'
import StatsPanel from './components/StatsPanel'
import { useSession } from './hooks/useSession'
import {
  sendChatMessage,
  getSessionMessages,
  getStats,
  getModels,
  clearLogs,
} from './api/chatApi'

const WELCOME_MESSAGE = {
  id: 'welcome',
  role: 'bot',
  content:
    "Welcome to TechFlow Electronics Support! I'm powered by Ollama AI (Mistral/Llama2). I can help with:\n\n" +
    "- Product information (laptops, phones, accessories)\n" +
    "- Shipping & delivery questions\n" +
    "- Returns & refunds\n" +
    "- Payment & account issues\n" +
    "- Warranty information\n" +
    "- Loyalty programs\n\n" +
    'Ask me anything about our products or services!',
  intent: 'greeting',
  confidence: 1.0,
  model_used: 'system',
  timestamp: new Date().toISOString(),
}

export default function App() {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'))
  const { sessionId, resetSession } = useSession()
  const [messages, setMessages] = useState([WELCOME_MESSAGE])
  const [model, setModel] = useState('mistral')
  const [aiModeEnabled, setAiModeEnabled] = useState(true)
  const [isTyping, setIsTyping] = useState(false)
  const [stats, setStats] = useState(null)
  const [error, setError] = useState(null)
  const [ollamaStatus, setOllamaStatus] = useState(null)

  const refreshStats = useCallback(async () => {
    const data = await getStats()
    if (data) setStats(data)
  }, [])

  useEffect(() => {
    getModels().then(setOllamaStatus).catch(() => setOllamaStatus({ ollama_available: false }))
    refreshStats()
  }, [refreshStats])

  useEffect(() => {
    if (!sessionId) return
    getSessionMessages(sessionId).then((data) => {
      if (data.messages && data.messages.length > 0) {
        setMessages([
          WELCOME_MESSAGE,
          ...data.messages.map((m, i) => ({
            id: `hist-${i}`,
            role: m.role,
            content: m.content,
            intent: m.intent,
            confidence: m.confidence,
            model_used: m.model_used,
            timestamp: m.timestamp,
          })),
        ])
      }
    })
  }, [sessionId])

  const handleSend = async (text) => {
    const userMsg = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, userMsg])
    setIsTyping(true)
    setError(null)

    try {
      const data = await sendChatMessage({
        message: text,
        model,
        useAi: aiModeEnabled ? null : false,
        sessionId,
      })

      const botMsg = {
        id: `bot-${Date.now()}`,
        role: 'bot',
        content: data.response,
        intent: data.intent,
        confidence: data.confidence,
        model_used: data.model_used,
        timestamp: data.timestamp,
      }
      setMessages((prev) => [...prev, botMsg])
      refreshStats()
    } catch (err) {
      setError(
        err.message ||
          'Connection error. Make sure backend is running at http://127.0.0.1:5000 and Ollama is started (ollama serve).'
      )
    } finally {
      setIsTyping(false)
    }
  }

  const handleClear = async () => {
    try {
      await clearLogs()
    } catch {
      // non-fatal
    }
    resetSession()
    setMessages([WELCOME_MESSAGE])
    refreshStats()
  }

  const handleModelChange = (newModel) => {
    setModel(newModel)
    setMessages((prev) => [
      ...prev,
      {
        id: `sys-${Date.now()}`,
        role: 'bot',
        content: `Switched to ${newModel} model.`,
        intent: 'system',
        confidence: 1.0,
        model_used: 'system',
        timestamp: new Date().toISOString(),
      },
    ])
  }

  return (
    <Box
      sx={{
        minHeight: '100vh',
        bgcolor: 'background.default',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        p: { xs: 0, sm: 2 },
      }}
    >
      <Container
        maxWidth="md"
        disableGutters={isMobile}
        sx={{
          height: { xs: '100vh', sm: '90vh' },
          maxHeight: 800,
          display: 'flex',
          flexDirection: 'column',
          bgcolor: 'background.paper',
          borderRadius: { xs: 0, sm: 3 },
          overflow: 'hidden',
          boxShadow: { xs: 'none', sm: 6 },
        }}
      >
        <ChatHeader
          model={model}
          onModelChange={handleModelChange}
          aiModeEnabled={aiModeEnabled}
          onAiModeChange={setAiModeEnabled}
          onClear={handleClear}
        />

        {ollamaStatus && !ollamaStatus.ollama_available && (
          <Alert severity="warning" sx={{ borderRadius: 0 }}>
            Ollama is not running. FAQ and pattern matching still work. Start with: ollama serve
          </Alert>
        )}

        <Box sx={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
          <ChatWindow messages={messages} isTyping={isTyping} />
          <StatsPanel stats={stats} />
        </Box>

        <Box sx={{ p: { xs: 1.5, sm: 2 }, borderTop: '1px solid', borderColor: 'divider' }}>
          <ChatInput onSend={handleSend} disabled={isTyping} />
        </Box>
      </Container>

      <Snackbar
        open={!!error}
        autoHideDuration={6000}
        onClose={() => setError(null)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert severity="error" onClose={() => setError(null)} sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>
    </Box>
  )
}
