import {
  Box,
  Typography,
  Button,
  useMediaQuery,
  useTheme,
} from '@mui/material'
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline'
import SmartToyIcon from '@mui/icons-material/SmartToy'

export default function ChatHeader({
  onClear,
  clearLabel = 'New chat',
  title = 'Support Chat',
  subtitle = 'Customer support',
  headerColor,
}) {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'))

  return (
    <Box
      sx={{
        bgcolor: headerColor || '#0b1f33',
        color: '#fff',
        px: { xs: 2, sm: 2.75 },
        py: 1.85,
        display: 'flex',
        flexDirection: { xs: 'column', sm: 'row' },
        alignItems: { xs: 'stretch', sm: 'center' },
        justifyContent: 'space-between',
        gap: 1.5,
        borderBottom: '1px solid rgba(255,255,255,0.08)',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
        <Box
          sx={{
            width: 40,
            height: 40,
            borderRadius: 2,
            bgcolor: 'rgba(20, 184, 166, 0.2)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
          }}
        >
          <SmartToyIcon sx={{ color: '#5eead4', fontSize: 22 }} />
        </Box>
        <Box>
          <Typography variant={isMobile ? 'subtitle1' : 'h6'} fontWeight={700} sx={{ lineHeight: 1.25 }}>
            {title}
          </Typography>
          <Typography variant="caption" sx={{ opacity: 0.72, letterSpacing: '0.01em' }}>
            {subtitle}
          </Typography>
        </Box>
      </Box>

      {onClear && (
        <Button
          size="small"
          variant="outlined"
          startIcon={<DeleteOutlineIcon />}
          onClick={onClear}
          sx={{
            color: 'white',
            borderColor: 'rgba(255,255,255,0.28)',
            borderRadius: 2,
            '&:hover': { borderColor: 'white', bgcolor: 'rgba(255,255,255,0.08)' },
          }}
        >
          {clearLabel}
        </Button>
      )}
    </Box>
  )
}
