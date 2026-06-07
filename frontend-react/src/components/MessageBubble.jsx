import { Box, Paper, Typography, Chip, Stack } from '@mui/material'
import SmartToyIcon from '@mui/icons-material/SmartToy'
import PersonIcon from '@mui/icons-material/Person'

function formatTime(timestamp) {
  if (!timestamp) return ''
  try {
    return new Date(timestamp).toLocaleTimeString([], {
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return ''
  }
}

function getModelLabel(modelUsed) {
  if (!modelUsed) return null
  if (modelUsed === 'faq_database') return { label: 'FAQ', color: 'success' }
  if (modelUsed.includes('ollama')) return { label: 'Ollama AI', color: 'secondary' }
  if (modelUsed === 'pattern_matching') return { label: 'Pattern', color: 'primary' }
  if (modelUsed.includes('faq_database_adjusted')) return { label: 'FAQ+AI', color: 'info' }
  return { label: modelUsed, color: 'default' }
}

export default function MessageBubble({ message }) {
  const isBot = message.role === 'bot'
  const modelInfo = isBot ? getModelLabel(message.model_used) : null

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: isBot ? 'flex-start' : 'flex-end',
        mb: 1.5,
        gap: 1,
      }}
    >
      {isBot && (
        <SmartToyIcon sx={{ color: 'primary.main', mt: 0.5, fontSize: 20 }} />
      )}
      <Box sx={{ maxWidth: { xs: '85%', sm: '70%' } }}>
        <Paper
          elevation={0}
          sx={{
            px: 2,
            py: 1.5,
            bgcolor: isBot ? 'background.paper' : 'primary.main',
            color: isBot ? 'text.primary' : 'primary.contrastText',
            border: isBot ? '1px solid' : 'none',
            borderColor: 'divider',
            borderRadius: isBot ? '4px 16px 16px 16px' : '16px 4px 16px 16px',
          }}
        >
          <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap', lineHeight: 1.6 }}>
            {message.content}
          </Typography>
        </Paper>

        <Stack
          direction="row"
          spacing={0.5}
          alignItems="center"
          sx={{ mt: 0.5, flexWrap: 'wrap', gap: 0.5 }}
        >
          {message.timestamp && (
            <Typography variant="caption" color="text.secondary">
              {formatTime(message.timestamp)}
            </Typography>
          )}
          {isBot && message.intent && message.intent !== 'fallback' && (
            <Chip label={message.intent} size="small" variant="outlined" />
          )}
          {isBot && message.confidence > 0 && (
            <Chip
              label={`${Math.round(message.confidence * 100)}%`}
              size="small"
              color="default"
            />
          )}
          {modelInfo && (
            <Chip label={modelInfo.label} size="small" color={modelInfo.color} />
          )}
        </Stack>
      </Box>
      {!isBot && (
        <PersonIcon sx={{ color: 'primary.main', mt: 0.5, fontSize: 20 }} />
      )}
    </Box>
  )
}
