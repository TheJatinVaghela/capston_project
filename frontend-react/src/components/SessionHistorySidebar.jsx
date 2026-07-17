import {
  Box,
  Button,
  IconButton,
  List,
  ListItemButton,
  ListItemText,
  Typography,
  CircularProgress,
} from '@mui/material'
import AddIcon from '@mui/icons-material/Add'
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline'
import HistoryIcon from '@mui/icons-material/History'

function formatWhen(iso) {
  if (!iso) return ''
  try {
    const d = new Date(iso)
    return d.toLocaleString([], {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  } catch {
    return ''
  }
}

export default function SessionHistorySidebar({
  sessions,
  activeSessionId,
  loading,
  onSelect,
  onNew,
  onDelete,
}) {
  return (
    <Box
      sx={{
        width: { xs: '100%', sm: 260 },
        minWidth: { sm: 220 },
        maxWidth: { sm: 280 },
        borderRight: { sm: '1px solid' },
        borderBottom: { xs: '1px solid', sm: 'none' },
        borderColor: 'divider',
        bgcolor: 'rgba(7, 21, 37, 0.025)',
        display: 'flex',
        flexDirection: 'column',
        maxHeight: { xs: 200, sm: '100%' },
      }}
    >
      <Box sx={{ p: 1.75, display: 'flex', alignItems: 'center', gap: 1 }}>
        <HistoryIcon fontSize="small" sx={{ color: 'text.secondary' }} />
        <Typography variant="subtitle2" sx={{ flex: 1, fontWeight: 700 }}>
          Chat history
        </Typography>
        <Button
          size="small"
          startIcon={<AddIcon />}
          onClick={onNew}
          variant="contained"
          sx={{ borderRadius: 2, px: 1.25 }}
        >
          New
        </Button>
      </Box>

      <Box sx={{ flex: 1, overflowY: 'auto', px: 1, pb: 1.5 }}>
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 3 }}>
            <CircularProgress size={22} />
          </Box>
        )}
        {!loading && sessions.length === 0 && (
          <Typography variant="caption" color="text.secondary" sx={{ px: 1, display: 'block', lineHeight: 1.5 }}>
            Past chats with this business will show here.
          </Typography>
        )}
        <List dense disablePadding>
          {sessions.map((s) => (
            <ListItemButton
              key={s.session_id}
              selected={s.session_id === activeSessionId}
              onClick={() => onSelect(s.session_id)}
              sx={{
                borderRadius: 2,
                mb: 0.35,
                alignItems: 'flex-start',
                '&.Mui-selected': {
                  bgcolor: 'rgba(15, 118, 110, 0.1)',
                  '&:hover': { bgcolor: 'rgba(15, 118, 110, 0.14)' },
                },
              }}
            >
              <ListItemText
                primary={s.preview || 'Conversation'}
                secondary={`${s.message_count || 0} msgs · ${formatWhen(s.last_activity || s.created_at)}`}
                primaryTypographyProps={{
                  variant: 'body2',
                  noWrap: true,
                  title: s.preview,
                  fontWeight: 550,
                }}
                secondaryTypographyProps={{ variant: 'caption' }}
              />
              <IconButton
                size="small"
                edge="end"
                aria-label="Delete conversation"
                onClick={(e) => {
                  e.stopPropagation()
                  onDelete(s.session_id)
                }}
                sx={{ opacity: 0.55, '&:hover': { opacity: 1, color: 'error.main' } }}
              >
                <DeleteOutlineIcon fontSize="small" />
              </IconButton>
            </ListItemButton>
          ))}
        </List>
      </Box>
    </Box>
  )
}
