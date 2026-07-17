import { useState } from 'react'
import { Box, TextField, IconButton } from '@mui/material'
import SendIcon from '@mui/icons-material/Send'

export default function ChatInput({ onSend, disabled, primaryColor }) {
  const [text, setText] = useState('')

  const handleSend = () => {
    const trimmed = text.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setText('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const btnBg = primaryColor || undefined

  return (
    <Box
      sx={{
        p: 0.75,
        display: 'flex',
        gap: 1,
        alignItems: 'flex-end',
        borderRadius: 3,
        bgcolor: 'background.paper',
        border: '1px solid',
        borderColor: 'divider',
        boxShadow: 2,
      }}
    >
      <TextField
        fullWidth
        multiline
        maxRows={3}
        placeholder="Ask about products, shipping, returns..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        size="small"
        variant="outlined"
        sx={{
          '& .MuiOutlinedInput-root': {
            borderRadius: 2.5,
            bgcolor: 'transparent',
            '& fieldset': { border: 'none' },
          },
        }}
      />
      <IconButton
        color="primary"
        onClick={handleSend}
        disabled={disabled || !text.trim()}
        sx={{
          bgcolor: btnBg || 'primary.main',
          color: 'white',
          width: 42,
          height: 42,
          borderRadius: 2.5,
          mb: 0.25,
          mr: 0.25,
          '&:hover': { bgcolor: btnBg || 'primary.dark', filter: btnBg ? 'brightness(0.92)' : undefined },
          '&.Mui-disabled': { bgcolor: 'action.disabledBackground' },
        }}
      >
        <SendIcon fontSize="small" />
      </IconButton>
    </Box>
  )
}
