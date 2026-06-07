import { useState } from 'react'
import { Box, TextField, IconButton, Paper } from '@mui/material'
import SendIcon from '@mui/icons-material/Send'

export default function ChatInput({ onSend, disabled }) {
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

  return (
    <Paper
      elevation={3}
      sx={{
        p: 1.5,
        display: 'flex',
        gap: 1,
        alignItems: 'flex-end',
        borderRadius: 2,
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
        sx={{ '& .MuiOutlinedInput-root': { borderRadius: 2 } }}
      />
      <IconButton
        color="primary"
        onClick={handleSend}
        disabled={disabled || !text.trim()}
        sx={{ bgcolor: 'primary.main', color: 'white', '&:hover': { bgcolor: 'primary.dark' }, '&.Mui-disabled': { bgcolor: 'action.disabledBackground' } }}
      >
        <SendIcon />
      </IconButton>
    </Paper>
  )
}
