import { useEffect, useMemo, useState } from 'react'
import {
  Alert,
  Box,
  Button,
  Container,
  LinearProgress,
  TextField,
  Typography,
  Stack,
} from '@mui/material'
import { Link as RouterLink } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { getBusiness, updateKnowledge } from '../api/client'

function countWords(text) {
  return (text || '').trim() ? (text.trim().match(/\S+/g) || []).length : 0
}

export default function KnowledgePage() {
  const { activeBusiness, upsertBusiness } = useAuth()
  const [text, setText] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [warnings, setWarnings] = useState([])
  const [loading, setLoading] = useState(false)
  const [maxWords, setMaxWords] = useState(200)

  useEffect(() => {
    if (!activeBusiness) return
    getBusiness(activeBusiness.id)
      .then((data) => {
        const biz = data.business
        setText(biz.knowledge_text || biz.knowledge?.text || '')
        setMaxWords(biz.plan_limits?.max_knowledge_words || 200)
      })
      .catch((err) => setError(err.message))
  }, [activeBusiness])

  const wordCount = useMemo(() => countWords(text), [text])
  const overLimit = wordCount > maxWords
  const progress = Math.min(100, Math.round((wordCount / Math.max(maxWords, 1)) * 100))

  if (!activeBusiness) {
    return (
      <Container sx={{ py: 4 }}>
        <Alert severity="info">Select or create a business first.</Alert>
      </Container>
    )
  }

  const onSave = async () => {
    setError('')
    setSuccess('')
    setWarnings([])
    setLoading(true)
    try {
      const data = await updateKnowledge(activeBusiness.id, text)
      upsertBusiness(data.business)
      setWarnings(data.warnings || [])
      if (data.max_knowledge_words) setMaxWords(data.max_knowledge_words)
      setSuccess('Knowledge saved. The chatbot will use this text as reference data only.')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const planName = (activeBusiness.effective_plan || activeBusiness.plan || 'free').replace(
    /^\w/,
    (c) => c.toUpperCase()
  )

  return (
    <Container maxWidth="md" sx={{ py: { xs: 3.5, md: 5 } }}>
      <Box sx={{ mb: 3 }}>
        <Typography
          variant="overline"
          sx={{ color: 'primary.main', fontWeight: 700, letterSpacing: '0.08em' }}
        >
          Knowledge base
        </Typography>
        <Typography variant="h4" sx={{ mb: 1 }}>
          Knowledge
        </Typography>
        <Typography color="text.secondary" sx={{ maxWidth: 580 }}>
          Paste facts about {activeBusiness.name} — products, policies, FAQs, hours, shipping.
          This is treated as reference data only (not instructions). Do not paste API keys or
          prompts trying to override the assistant.
        </Typography>
      </Box>

      <Box
        sx={{
          p: { xs: 2.5, sm: 3 },
          bgcolor: 'background.paper',
          borderRadius: 3,
          border: '1px solid',
          borderColor: 'divider',
          boxShadow: 2,
        }}
      >
        <Stack spacing={1} sx={{ mb: 2.5 }}>
          <Stack direction="row" justifyContent="space-between" alignItems="center">
            <Typography variant="body2" color={overLimit ? 'error' : 'text.secondary'} fontWeight={500}>
              {wordCount.toLocaleString()} / {maxWords.toLocaleString()} words ({planName} plan)
            </Typography>
            {overLimit && (
              <Button component={RouterLink} to="/billing" size="small">
                Upgrade for more
              </Button>
            )}
          </Stack>
          <LinearProgress
            variant="determinate"
            value={progress}
            color={overLimit ? 'error' : progress > 85 ? 'warning' : 'primary'}
          />
        </Stack>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}
        {warnings.map((w) => (
          <Alert key={w} severity="warning" sx={{ mb: 1 }}>{w}</Alert>
        ))}

        <TextField
          fullWidth
          multiline
          minRows={18}
          value={text}
          onChange={(e) => setText(e.target.value)}
          error={overLimit}
          placeholder={`Example:\nWe sell handmade ceramic mugs.\nShipping: 3-5 days in Canada, $5 flat.\nReturns: 14 days unused.\nSupport email: hello@mugs.example\nFAQ: Do you do custom colors? Yes, +$8.`}
          sx={{
            mb: 2.5,
            '& .MuiOutlinedInput-root': {
              fontFamily: 'ui-monospace, "Cascadia Code", monospace',
              fontSize: '0.875rem',
              lineHeight: 1.65,
            },
          }}
        />

        <Button
          variant="contained"
          size="large"
          onClick={onSave}
          disabled={loading || overLimit}
        >
          {loading ? 'Saving…' : 'Save knowledge'}
        </Button>
      </Box>
    </Container>
  )
}
