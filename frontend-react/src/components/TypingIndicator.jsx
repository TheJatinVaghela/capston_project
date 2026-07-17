import { Box, Paper } from '@mui/material'
import SmartToyIcon from '@mui/icons-material/SmartToy'

export default function TypingIndicator({ colors }) {
  const accent = colors?.primary || 'primary.main'
  return (
    <Box sx={{ display: 'flex', gap: 1.15, mb: 1.75, alignItems: 'flex-start' }}>
      <Box
        sx={{
          width: 28,
          height: 28,
          borderRadius: 1.5,
          bgcolor: 'rgba(15, 118, 110, 0.1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          mt: 0.35,
          flexShrink: 0,
        }}
      >
        <SmartToyIcon sx={{ color: accent, fontSize: 16 }} />
      </Box>
      <Paper
        elevation={0}
        sx={{
          px: 2,
          py: 1.5,
          bgcolor: 'background.paper',
          border: '1px solid',
          borderColor: 'divider',
          borderRadius: '4px 16px 16px 16px',
          display: 'flex',
          gap: 0.5,
          alignItems: 'center',
        }}
      >
        {[0, 1, 2].map((i) => (
          <Box
            key={i}
            sx={{
              width: 8,
              height: 8,
              borderRadius: '50%',
              bgcolor: accent,
              opacity: 0.6,
              animation: 'bounce 1.2s infinite',
              animationDelay: `${i * 0.2}s`,
              '@keyframes bounce': {
                '0%, 80%, 100%': { transform: 'scale(0.6)', opacity: 0.4 },
                '40%': { transform: 'scale(1)', opacity: 1 },
              },
            }}
          />
        ))}
      </Paper>
    </Box>
  )
}
