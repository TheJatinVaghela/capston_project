import { useState } from 'react'
import {
  Alert,
  Box,
  Button,
  Container,
  TextField,
  Typography,
} from '@mui/material'
import { useAuth } from '../context/AuthContext'
import { API_URL, rotateWidgetKey } from '../api/client'

export default function EmbedPage() {
  const { activeBusiness, upsertBusiness } = useAuth()
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)

  if (!activeBusiness) {
    return (
      <Container sx={{ py: 4 }}>
        <Alert severity="info">Select a business first.</Alert>
      </Container>
    )
  }

  const status = activeBusiness.subscription_status || 'free'
  const allowed = status === 'active' || status === 'trialing'
  const snippet = `<script src="${API_URL}/widget.js" data-key="${activeBusiness.widget_key}"></script>`

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(snippet)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      setError('Could not copy — select the text manually.')
    }
  }

  const rotate = async () => {
    setError('')
    try {
      const data = await rotateWidgetKey(activeBusiness.id)
      upsertBusiness(data.business)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <Container maxWidth="md" sx={{ py: { xs: 3.5, md: 5 } }}>
      <Box sx={{ mb: 3.5 }}>
        <Typography
          variant="overline"
          sx={{ color: 'primary.main', fontWeight: 700, letterSpacing: '0.08em' }}
        >
          Integration
        </Typography>
        <Typography variant="h4" sx={{ mb: 1 }}>
          Embed on your website
        </Typography>
        <Typography color="text.secondary" sx={{ maxWidth: 520 }}>
          Paste this script before <code>&lt;/body&gt;</code> on {activeBusiness.name}&apos;s site.
        </Typography>
      </Box>

      {!allowed && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          An active subscription is required to use the embed widget. Go to Billing to subscribe.
          (Demo TechFlow account is already active.)
        </Alert>
      )}
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
      {copied && <Alert severity="success" sx={{ mb: 2 }}>Copied to clipboard.</Alert>}

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
        <Typography variant="subtitle2" sx={{ mb: 1.25, fontWeight: 650 }}>
          Embed snippet
        </Typography>
        <TextField
          fullWidth
          multiline
          value={snippet}
          InputProps={{ readOnly: true }}
          sx={{
            mb: 2,
            '& textarea': {
              fontFamily: 'ui-monospace, "Cascadia Code", monospace',
              fontSize: 13,
              lineHeight: 1.55,
            },
          }}
        />
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Button variant="contained" onClick={copy} disabled={!allowed}>Copy snippet</Button>
          <Button variant="outlined" onClick={rotate} disabled={!allowed}>Rotate widget key</Button>
        </Box>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2.5 }}>
          Widget key: <Box component="code" sx={{ fontSize: '0.85em' }}>{activeBusiness.widget_key}</Box>
        </Typography>
      </Box>

      <Box
        sx={{
          p: { xs: 2.5, sm: 3.5 },
          mt: 3,
          bgcolor: 'background.paper',
          borderRadius: 3,
          border: '1px solid',
          borderColor: 'divider',
          boxShadow: 2,
        }}
      >
        <Typography variant="h6" sx={{ mb: 1 }}>Test page</Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5 }}>
          Save this as <code>test.html</code>, open it in a browser (with the API running), and click the chat bubble:
        </Typography>
        <TextField
          fullWidth
          multiline
          minRows={8}
          value={`<!DOCTYPE html>
<html>
<body>
  <h1>${activeBusiness.name}</h1>
  <p>Sample storefront page.</p>
  ${snippet}
</body>
</html>`}
          InputProps={{ readOnly: true }}
          sx={{
            '& textarea': {
              fontFamily: 'ui-monospace, "Cascadia Code", monospace',
              fontSize: 12,
              lineHeight: 1.5,
            },
          }}
        />
      </Box>
    </Container>
  )
}
