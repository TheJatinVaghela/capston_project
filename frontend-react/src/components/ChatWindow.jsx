import { useEffect, useRef } from 'react'
import { Box } from '@mui/material'
import MessageBubble from './MessageBubble'
import TypingIndicator from './TypingIndicator'

export default function ChatWindow({ messages, isTyping, colors }) {
  const bottomRef = useRef(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  return (
    <Box
      sx={{
        flex: 1,
        overflowY: 'auto',
        px: { xs: 1.5, sm: 2.75 },
        py: 2.25,
        background:
          'linear-gradient(180deg, rgba(244,246,248,0.95) 0%, rgba(237,241,245,1) 100%)',
      }}
    >
      {messages.map((msg, idx) => (
        <MessageBubble key={msg.id || idx} message={msg} colors={colors} />
      ))}
      {isTyping && <TypingIndicator colors={colors} />}
      <div ref={bottomRef} />
    </Box>
  )
}
