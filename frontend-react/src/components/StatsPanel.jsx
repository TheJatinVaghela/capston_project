import { Box, Paper, Typography, Chip, Stack } from '@mui/material'
import BarChartIcon from '@mui/icons-material/BarChart'

export default function StatsPanel({ stats }) {
  if (!stats) return null

  const topIntents = Object.entries(stats.intent_distribution || {})
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)

  return (
    <Paper
      elevation={0}
      sx={{
        p: 2,
        border: '1px solid',
        borderColor: 'divider',
        borderRadius: 2,
        display: { xs: 'none', md: 'block' },
        width: 220,
        flexShrink: 0,
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1.5 }}>
        <BarChartIcon color="primary" fontSize="small" />
        <Typography variant="subtitle2" fontWeight={600}>
          Session Stats
        </Typography>
      </Box>

      <Typography variant="caption" color="text.secondary" display="block" mb={1}>
        {stats.total_messages} messages | {stats.total_sessions} sessions
      </Typography>

      <Typography variant="caption" color="text.secondary" display="block" mb={1}>
        Avg confidence: {Math.round((stats.average_confidence || 0) * 100)}%
      </Typography>

      <Typography variant="caption" fontWeight={600} display="block" mb={0.5}>
        Top Intents
      </Typography>
      <Stack direction="row" flexWrap="wrap" gap={0.5}>
        {topIntents.map(([intent, count]) => (
          <Chip key={intent} label={`${intent} (${count})`} size="small" variant="outlined" />
        ))}
      </Stack>
    </Paper>
  )
}
