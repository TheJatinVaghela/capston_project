import { useEffect, useMemo, useState } from 'react'
import {
  Alert,
  Button,
  Container,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  Stack,
  TextField,
  Typography,
  Box,
} from '@mui/material'
import { Link as RouterLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getBusiness, updateBusinessSettings, getModels } from '../api/client'

const MODELS = [
  { value: 'mistral', label: 'Mistral (fast)' },
  { value: 'llama3', label: 'Llama3' },
  { value: 'neural-chat', label: 'Neural-Chat' },
]

const DEFAULT_COLORS = {
  primary: '#0f766e',
  header: '#0b1f33',
  user_bubble: '#0f766e',
  accent: '#14b8a6',
}

export default function SettingsPage() {
  const { activeBusiness, upsertBusiness } = useAuth()
  const [model, setModel] = useState('mistral')
  const [originsText, setOriginsText] = useState('')
  const [colors, setColors] = useState(DEFAULT_COLORS)
  const [available, setAvailable] = useState([])
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  const paid =
    activeBusiness &&
    ['active', 'trialing'].includes(activeBusiness.subscription_status || 'free')
  const isPremium =
    paid && (activeBusiness?.effective_plan || activeBusiness?.plan) === 'premium'
  const canCustomizeColors =
    isPremium || activeBusiness?.plan_limits?.chat_colors === true

  useEffect(() => {
    getModels()
      .then((d) => setAvailable(d.available_models || []))
      .catch(() => setAvailable([]))
  }, [])

  useEffect(() => {
    if (!activeBusiness) return
    getBusiness(activeBusiness.id)
      .then((d) => {
        setModel(d.business.ai_model || 'mistral')
        const origins = d.business.allowed_origins || []
        setOriginsText(Array.isArray(origins) ? origins.join('\n') : '')
        setColors({ ...DEFAULT_COLORS, ...(d.business.chat_colors || {}) })
      })
      .catch((err) => setError(err.message))
  }, [activeBusiness])

  const setColor = (key) => (e) => {
    setColors((c) => ({ ...c, [key]: e.target.value }))
  }

  const previewStyle = useMemo(
    () => ({
      borderRadius: 2.5,
      overflow: 'hidden',
      border: '1px solid',
      borderColor: 'divider',
      maxWidth: 320,
      boxShadow: 2,
    }),
    []
  )

  if (!activeBusiness) {
    return (
      <Container sx={{ py: 4 }}>
        <Alert severity="info">Select a business first.</Alert>
      </Container>
    )
  }

  const onSave = async () => {
    setError('')
    setSuccess('')
    setLoading(true)
    try {
      const allowed_origins = originsText
        .split(/[\n,]+/)
        .map((s) => s.trim())
        .filter(Boolean)
      const payload = { allowed_origins }
      if (paid) payload.ai_model = model
      if (canCustomizeColors) payload.chat_colors = colors
      const data = await updateBusinessSettings(activeBusiness.id, payload)
      upsertBusiness(data.business)
      setSuccess('Settings saved.')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container maxWidth="sm" sx={{ py: { xs: 3.5, md: 5 } }}>
      <Box sx={{ mb: 3 }}>
        <Typography
          variant="overline"
          sx={{ color: 'primary.main', fontWeight: 700, letterSpacing: '0.08em' }}
        >
          Configuration
        </Typography>
        <Typography variant="h4" sx={{ mb: 1 }}>
          Settings
        </Typography>
        <Typography color="text.secondary">
          Configure the AI model, embed origins
          {canCustomizeColors ? ', and chatbot colors' : ''}.
        </Typography>
      </Box>

      <Box
        sx={{
          p: { xs: 2.5, sm: 3.5 },
          bgcolor: 'background.paper',
          borderRadius: 3,
          border: '1px solid',
          borderColor: 'divider',
          boxShadow: 2,
        }}
      >
        {!paid && (
          <Alert severity="warning" sx={{ mb: 2.5 }}>
            AI model selection is a paid feature for this business.{' '}
            <Button component={RouterLink} to="/billing" size="small">Subscribe</Button>
          </Alert>
        )}
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}

        <FormControl fullWidth sx={{ mb: 2 }} disabled={!paid}>
          <InputLabel id="model-label">AI model</InputLabel>
          <Select
            labelId="model-label"
            label="AI model"
            value={model}
            onChange={(e) => setModel(e.target.value)}
          >
            {MODELS.map((m) => (
              <MenuItem key={m.value} value={m.value}>{m.label}</MenuItem>
            ))}
          </Select>
        </FormControl>

        {available.length > 0 && (
          <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 2.5 }}>
            Installed on this machine: {available.join(', ')}
          </Typography>
        )}

        <Typography variant="subtitle1" sx={{ mt: 1, mb: 1, fontWeight: 650 }}>
          Allowed embed origins
        </Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1.25 }}>
          One origin per line (e.g. https://www.yourstore.com). In production, an empty list
          blocks cross-site embeds until you add your domains.
        </Typography>
        <TextField
          fullWidth
          multiline
          minRows={3}
          value={originsText}
          onChange={(e) => setOriginsText(e.target.value)}
          placeholder={"https://www.yourstore.com\nhttps://yourstore.com"}
          sx={{ mb: 3 }}
        />

        <Typography variant="subtitle1" sx={{ mb: 1, fontWeight: 650 }}>
          Chatbot colors
        </Typography>
        {!canCustomizeColors ? (
          <Alert severity="info" sx={{ mb: 2.5 }}>
            Custom chatbot colors are included with the <strong>Premium</strong> plan.{' '}
            <Button component={RouterLink} to="/billing" size="small">Upgrade</Button>
          </Alert>
        ) : (
          <>
            <Stack spacing={2} sx={{ mb: 2 }}>
              {[
                { key: 'header', label: 'Header background' },
                { key: 'primary', label: 'Primary / buttons' },
                { key: 'user_bubble', label: 'Customer message bubble' },
                { key: 'accent', label: 'Accent' },
              ].map((item) => (
                <Stack key={item.key} direction="row" spacing={2} alignItems="center">
                  <Box
                    component="input"
                    type="color"
                    value={colors[item.key] || DEFAULT_COLORS[item.key]}
                    onChange={setColor(item.key)}
                    sx={{
                      width: 48,
                      height: 40,
                      border: '1px solid',
                      borderColor: 'divider',
                      borderRadius: 1.5,
                      bgcolor: 'transparent',
                      cursor: 'pointer',
                      p: 0.25,
                    }}
                  />
                  <TextField
                    size="small"
                    label={item.label}
                    value={colors[item.key] || ''}
                    onChange={setColor(item.key)}
                    sx={{ flex: 1 }}
                  />
                </Stack>
              ))}
            </Stack>
            <Typography variant="caption" color="text.secondary" display="block" sx={{ mb: 1 }}>
              Preview
            </Typography>
            <Box sx={{ ...previewStyle, mb: 3 }}>
              <Box sx={{ bgcolor: colors.header, color: '#fff', px: 2, py: 1.5 }}>
                <Typography variant="subtitle2" fontWeight={700}>
                  {activeBusiness.name}
                </Typography>
                <Typography variant="caption" sx={{ opacity: 0.85 }}>
                  Customer support
                </Typography>
              </Box>
              <Box sx={{ p: 1.5, bgcolor: '#f4f6f8', display: 'grid', gap: 1 }}>
                <Box
                  sx={{
                    justifySelf: 'start',
                    bgcolor: '#fff',
                    border: '1px solid rgba(11,31,51,0.08)',
                    px: 1.5,
                    py: 1,
                    borderRadius: '4px 12px 12px 12px',
                    fontSize: 13,
                  }}
                >
                  Hi! How can I help?
                </Box>
                <Box
                  sx={{
                    justifySelf: 'end',
                    bgcolor: colors.user_bubble,
                    color: '#fff',
                    px: 1.5,
                    py: 1,
                    borderRadius: '12px 4px 12px 12px',
                    fontSize: 13,
                  }}
                >
                  Where is my order?
                </Box>
                <Box
                  sx={{
                    justifySelf: 'stretch',
                    bgcolor: colors.primary,
                    color: '#fff',
                    textAlign: 'center',
                    py: 0.8,
                    borderRadius: 1.5,
                    fontSize: 13,
                    fontWeight: 600,
                  }}
                >
                  Send
                </Box>
              </Box>
            </Box>
          </>
        )}

        <Button variant="contained" onClick={onSave} disabled={loading} size="large">
          {loading ? 'Saving…' : 'Save settings'}
        </Button>
      </Box>
    </Container>
  )
}
