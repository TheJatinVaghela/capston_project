import { useEffect, useRef } from 'react'
import { Box } from '@mui/material'
import MessageBubble from './MessageBubble'
import TypingIndicator from './TypingIndicator'

export default function ChatWindow({ messages, isTyping }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  return (
    <Box
      sx={{
        flex: 1,
        overflowY: 'auto',
        px: { xs: 1.5, sm: 2.5 },
        py: 2,
        bgcolor: 'background.default',
      }}
    >
      {messages.map((msg, idx) => (
        <MessageBubble key={msg.id || idx} message={msg} />
      ))}
      {isTyping && <TypingIndicator />}
      <div ref={bottomRef} />
    </Box>
  )
}
