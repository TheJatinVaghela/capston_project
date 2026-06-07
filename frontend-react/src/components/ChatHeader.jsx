import {
  Box,
  Typography,
  Select,
  MenuItem,
  FormControl,
  Button,
  Switch,
  FormControlLabel,
  useMediaQuery,
  useTheme,
} from '@mui/material'
import DeleteOutlineIcon from '@mui/icons-material/DeleteOutline'
import SmartToyIcon from '@mui/icons-material/SmartToy'

export default function ChatHeader({
  model,
  onModelChange,
  aiModeEnabled,
  onAiModeChange,
  onClear,
}) {
  const theme = useTheme()
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'))

  return (
    <Box
      sx={{
        bgcolor: 'primary.main',
        color: 'primary.contrastText',
        px: { xs: 2, sm: 3 },
        py: 2,
        display: 'flex',
        flexDirection: { xs: 'column', sm: 'row' },
        alignItems: { xs: 'stretch', sm: 'center' },
        justifyContent: 'space-between',
        gap: 1.5,
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <SmartToyIcon />
        <Box>
          <Typography variant={isMobile ? 'subtitle1' : 'h6'} fontWeight={700}>
            TechFlow Electronics Support
          </Typography>
          <Typography variant="caption" sx={{ opacity: 0.85 }}>
            AI-Powered with Ollama
          </Typography>
        </Box>
      </Box>

      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          gap: 1.5,
          flexWrap: 'wrap',
          justifyContent: { xs: 'center', sm: 'flex-end' },
        }}
      >
        <FormControl size="small" sx={{ minWidth: 140 }}>
          <Select
            value={model}
            onChange={(e) => onModelChange(e.target.value)}
            sx={{
              bgcolor: 'rgba(255,255,255,0.15)',
              color: 'white',
              '.MuiOutlinedInput-notchedOutline': { border: 'none' },
              '.MuiSvgIcon-root': { color: 'white' },
            }}
          >
            <MenuItem value="mistral">Mistral (Fast)</MenuItem>
            <MenuItem value="llama2">Llama2 (Accurate)</MenuItem>
            <MenuItem value="neural-chat">Neural-Chat</MenuItem>
          </Select>
        </FormControl>

        <FormControlLabel
          control={
            <Switch
              checked={aiModeEnabled}
              onChange={(e) => onAiModeChange(e.target.checked)}
              size="small"
              sx={{
                '& .MuiSwitch-switchBase.Mui-checked': { color: 'secondary.main' },
                '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': { bgcolor: 'secondary.main' },
              }}
            />
          }
          label={
            <Typography variant="caption" sx={{ color: 'white' }}>
              {aiModeEnabled ? 'Auto (FAQ+AI)' : 'FAQ Only'}
            </Typography>
          }
        />

        <Button
          size="small"
          variant="outlined"
          startIcon={<DeleteOutlineIcon />}
          onClick={onClear}
          sx={{
            color: 'white',
            borderColor: 'rgba(255,255,255,0.5)',
            '&:hover': { borderColor: 'white', bgcolor: 'rgba(255,255,255,0.1)' },
          }}
        >
          Clear
        </Button>
      </Box>
    </Box>
  )
}
