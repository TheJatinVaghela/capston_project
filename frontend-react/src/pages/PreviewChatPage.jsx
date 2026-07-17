import { useState, useEffect, useCallback } from 'react'
import { Box, Container, Alert, Snackbar, Typography, Chip, Stack } from '@mui/material'
import ChatHeader from '../components/ChatHeader'
import ChatWindow from '../components/ChatWindow'
import ChatInput from '../components/ChatInput'
import SessionHistorySidebar from '../components/SessionHistorySidebar'
import { useSession } from '../hooks/useSession'
import { useAuth } from '../context/AuthContext'
import {
  sendChatMessageStream,
  getSessionMessages,
  getModels,
  listSessions,
  deleteSession,
} from '../api/client'

export default function PreviewChatPage({ demoMode = false }) {
  const { activeBusiness } = useAuth()
  const businessId = demoMode ? null : activeBusiness?.id
  const storageKey = demoMode ? 'sf_demo_session' : `sf_preview_${businessId || 'none'}`
  const { sessionId, resetSession, loadSession } = useSession(storageKey)

  const companyName = demoMode
    ? 'TechFlow Electronics'
    : activeBusiness?.name || 'your business'

  const chatColors = demoMode ? null : activeBusiness?.chat_colors

  const welcome = {
    id: 'welcome',
    role: 'bot',
    content:
      `Welcome to ${companyName} support! Ask me about products, shipping, returns, payments, or policies.\n\n` +
      (demoMode
        ? 'This is the public TechFlow demo. Try Spanish or French too — e.g. "Hola" or "Bonjour".'
        : 'You are previewing as a customer. Past chats are in the history panel.'),
    intent: 'greeting',
    confidence: 1,
    model_used: 'system',
    timestamp: new Date().toISOString(),
  }

  const [messages, setMessages] = useState([welcome])
  const [isTyping, setIsTyping] = useState(false)
  const [isBusy, setIsBusy] = useState(false)
  const [error, setError] = useState(null)
  const [ollamaStatus, setOllamaStatus] = useState(null)
  const [sessions, setSessions] = useState([])
  const [historyLoading, setHistoryLoading] = useState(false)
  const [historyReady, setHistoryReady] = useState(false)

  const refreshSessions = useCallback((opts = {}) => {
    const { showSpinner = false } = opts
    if (demoMode || !businessId) return Promise.resolve()
    if (showSpinner || !historyReady) setHistoryLoading(true)
    return listSessions(businessId)
      .then((data) => setSessions(data.sessions || []))
      .catch(() => setSessions([]))
      .finally(() => {
        setHistoryLoading(false)
        setHistoryReady(true)
      })
  }, [businessId, demoMode, historyReady])

  useEffect(() => {
    setMessages([welcome])
  }, [companyName])

  useEffect(() => {
    getModels().then(setOllamaStatus).catch(() => setOllamaStatus({ ollama_available: false }))
  }, [])

  useEffect(() => {
    refreshSessions({ showSpinner: true })
  }, [businessId, demoMode]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    // Session transcripts require auth + ownership (skip public demo)
    if (!sessionId || demoMode) return
    let cancelled = false
    getSessionMessages(sessionId)
      .then((data) => {
        if (cancelled) return
        if (data.messages?.length > 0) {
          setMessages([
            welcome,
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
        } else {
          setMessages([welcome])
        }
      })
      .catch(() => {
        if (!cancelled) setMessages([welcome])
      })
    return () => {
      cancelled = true
    }
  }, [sessionId, demoMode]) // welcome intentionally omitted — reset via setMessages

  if (!demoMode && !activeBusiness) {
    return (
      <Container sx={{ py: 4 }}>
        <Alert severity="info">Select a business to preview its chatbot.</Alert>
      </Container>
    )
  }

  const handleSend = async (text) => {
    const userMsg = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: text,
      timestamp: new Date().toISOString(),
    }
    const botId = `bot-${Date.now()}`
    setMessages((prev) => [...prev, userMsg])
    setIsTyping(true)
    setIsBusy(true)
    setError(null)
    try {
      const data = await sendChatMessageStream({
        message: text,
        sessionId,
        businessId: demoMode ? undefined : businessId,
        source: demoMode ? 'demo' : 'preview',
        onToken: (piece) => {
          setIsTyping(false)
          setMessages((prev) => {
            const existing = prev.find((m) => m.id === botId)
            if (!existing) {
              return [
                ...prev,
                {
                  id: botId,
                  role: 'bot',
                  content: piece,
                  intent: null,
                  confidence: null,
                  model_used: null,
                  timestamp: new Date().toISOString(),
                  streaming: true,
                },
              ]
            }
            return prev.map((m) =>
              m.id === botId ? { ...m, content: (m.content || '') + piece } : m
            )
          })
        },
        onMeta: (meta) => {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === botId
                ? {
                    ...m,
                    intent: meta.intent,
                    confidence: meta.confidence,
                    model_used: meta.model_used,
                  }
                : m
            )
          )
        },
      })
      setIsTyping(false)
      setMessages((prev) => {
        const existing = prev.find((m) => m.id === botId)
        const finished = {
          id: botId,
          role: 'bot',
          content: data.response || existing?.content || '',
          intent: data.intent,
          confidence: data.confidence,
          model_used: data.model_used,
          timestamp: data.timestamp || existing?.timestamp || new Date().toISOString(),
          streaming: false,
        }
        if (!existing) return [...prev, finished]
        return prev.map((m) => (m.id === botId ? finished : m))
      })
      refreshSessions({ showSpinner: false })
    } catch (err) {
      setError(err.message || 'Connection error')
      setMessages((prev) => prev.filter((m) => m.id !== botId))
    } finally {
      setIsTyping(false)
      setIsBusy(false)
    }
  }

  const handleNewChat = () => {
    // Instant local reset — do not block UI on history refetch
    setHistoryLoading(false)
    resetSession()
    setMessages([welcome])
  }

  const handleSelectSession = (id) => {
    if (id === sessionId) return
    loadSession(id)
  }

  const handleDeleteSession = async (id) => {
    if (!businessId) return
    try {
      await deleteSession(businessId, id)
      if (id === sessionId) {
        resetSession()
        setMessages([welcome])
      }
      await refreshSessions({ showSpinner: false })
    } catch (err) {
      setError(err.message || 'Could not delete conversation')
    }
  }

  return (
    <Box
      sx={{
        py: demoMode ? 0 : { xs: 2.5, sm: 3.5 },
        px: { xs: 0, sm: 2 },
        background: demoMode
          ? undefined
          : 'radial-gradient(ellipse 80% 50% at 50% 0%, rgba(20,184,166,0.06), transparent 55%)',
      }}
    >
      {!demoMode && (
        <Container maxWidth="lg" sx={{ mb: 2.5 }}>
          <Typography
            variant="overline"
            sx={{ color: 'primary.main', fontWeight: 700, letterSpacing: '0.08em' }}
          >
            Live preview
          </Typography>
          <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 0.75, flexWrap: 'wrap' }}>
            <Typography variant="h4">
              Try as customer
            </Typography>
            <Chip label="Preview" color="primary" size="small" />
            <Chip label="Multilingual" size="small" variant="outlined" />
          </Stack>
          <Typography color="text.secondary" variant="body2" sx={{ maxWidth: 560 }}>
            Reopen past chats from the history panel. Ask in Spanish, French, and more — the bot replies in your language.
          </Typography>
        </Container>
      )}

      <Container
        maxWidth="lg"
        disableGutters
        sx={{
          height: { xs: demoMode ? '100vh' : '78vh', sm: '78vh' },
          maxHeight: 820,
          display: 'flex',
          flexDirection: { xs: 'column', sm: 'row' },
          bgcolor: 'background.paper',
          borderRadius: { xs: 0, sm: 3 },
          overflow: 'hidden',
          border: { xs: 'none', sm: '1px solid' },
          borderColor: 'divider',
          boxShadow: { xs: 'none', sm: 5 },
        }}
      >
        {!demoMode && (
          <SessionHistorySidebar
            sessions={sessions}
            activeSessionId={sessionId}
            loading={historyLoading}
            onSelect={handleSelectSession}
            onNew={handleNewChat}
            onDelete={handleDeleteSession}
          />
        )}

        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', minWidth: 0 }}>
          <ChatHeader
            onClear={handleNewChat}
            clearLabel="New chat"
            title={`${companyName} Support`}
            subtitle="Customer support assistant"
            headerColor={chatColors?.header}
          />
          {ollamaStatus && !ollamaStatus.ollama_available && (
            <Alert severity="warning" sx={{ borderRadius: 0 }}>
              Ollama is not running. Start with: ollama serve
            </Alert>
          )}
          <ChatWindow messages={messages} isTyping={isTyping} colors={chatColors} />
          <Box
            sx={{
              p: { xs: 1.5, sm: 2 },
              borderTop: '1px solid',
              borderColor: 'divider',
              bgcolor: 'rgba(7, 21, 37, 0.02)',
            }}
          >
            <ChatInput onSend={handleSend} disabled={isBusy} primaryColor={chatColors?.primary} />
          </Box>
        </Box>
      </Container>

      <Snackbar open={!!error} autoHideDuration={6000} onClose={() => setError(null)} anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}>
        <Alert severity="error" onClose={() => setError(null)}>{error}</Alert>
      </Snackbar>
    </Box>
  )
}
