import { Link as RouterLink, NavLink, useNavigate, useLocation } from 'react-router-dom'
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  Select,
  MenuItem,
  FormControl,
  Container,
} from '@mui/material'
import { useAuth } from '../context/AuthContext'

const NAV = [
  { to: '/dashboard', label: 'Dashboard' },
  { to: '/knowledge', label: 'Knowledge' },
  { to: '/preview', label: 'Try chat' },
  { to: '/settings', label: 'Settings' },
  { to: '/billing', label: 'Billing' },
  { to: '/embed', label: 'Embed' },
]

function NavItem({ to, label }) {
  return (
    <Button
      component={NavLink}
      to={to}
      color="inherit"
      sx={{
        color: 'rgba(255,255,255,0.72)',
        fontWeight: 500,
        fontSize: '0.875rem',
        px: 1.25,
        minWidth: 0,
        borderRadius: 2,
        '&.active': {
          color: '#fff',
          bgcolor: 'rgba(255,255,255,0.1)',
        },
        '&:hover': {
          color: '#fff',
          bgcolor: 'rgba(255,255,255,0.08)',
        },
      }}
    >
      {label}
    </Button>
  )
}

export default function AppShell({ children }) {
  const { user, businesses, activeBusinessId, selectBusiness, logout } = useAuth()
  const navigate = useNavigate()
  const location = useLocation()
  const isLanding = location.pathname === '/' && !user

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: isLanding ? 'transparent' : 'background.default' }}>
      <AppBar
        position="sticky"
        elevation={0}
        sx={{
          bgcolor: isLanding ? 'rgba(7, 21, 37, 0.72)' : '#071525',
          backdropFilter: 'blur(14px)',
          borderBottom: '1px solid rgba(255,255,255,0.08)',
        }}
      >
        <Container maxWidth="lg" disableGutters sx={{ px: { xs: 2, sm: 3 } }}>
          <Toolbar
            disableGutters
            sx={{
              gap: 1,
              flexWrap: 'wrap',
              minHeight: { xs: 60, sm: 64 },
              py: { xs: 0.5, sm: 0 },
            }}
          >
            <Typography
              component={RouterLink}
              to={user ? '/dashboard' : '/'}
              variant="h6"
              sx={{
                color: '#fff',
                textDecoration: 'none',
                fontFamily: '"Fraunces", Georgia, serif',
                fontWeight: 700,
                fontSize: '1.25rem',
                letterSpacing: '-0.02em',
                mr: { sm: 1.5 },
                '&:hover': { color: '#99f6e4' },
              }}
            >
              SupportFlow
            </Typography>

            {user && (
              <>
                <Box
                  sx={{
                    display: 'flex',
                    flexWrap: 'wrap',
                    gap: 0.25,
                    flex: 1,
                    minWidth: 0,
                  }}
                >
                  {NAV.map((item) => (
                    <NavItem key={item.to} {...item} />
                  ))}
                </Box>

                {businesses.length > 0 && (
                  <FormControl size="small" sx={{ minWidth: 150 }}>
                    <Select
                      value={activeBusinessId || ''}
                      onChange={(e) => selectBusiness(e.target.value)}
                      sx={{
                        color: '#fff',
                        fontSize: '0.85rem',
                        borderRadius: 2,
                        '.MuiOutlinedInput-notchedOutline': {
                          borderColor: 'rgba(255,255,255,0.22)',
                        },
                        '&:hover .MuiOutlinedInput-notchedOutline': {
                          borderColor: 'rgba(255,255,255,0.4)',
                        },
                        '.MuiSvgIcon-root': { color: 'rgba(255,255,255,0.7)' },
                      }}
                    >
                      {businesses.map((b) => (
                        <MenuItem key={b.id} value={b.id}>{b.name}</MenuItem>
                      ))}
                    </Select>
                  </FormControl>
                )}

                <Button
                  color="inherit"
                  onClick={() => {
                    logout()
                    navigate('/')
                  }}
                  sx={{
                    color: 'rgba(255,255,255,0.7)',
                    fontWeight: 500,
                    '&:hover': { color: '#fff' },
                  }}
                >
                  Log out
                </Button>
              </>
            )}

            {!user && (
              <Box sx={{ ml: 'auto', display: 'flex', gap: 1, alignItems: 'center' }}>
                <Button
                  color="inherit"
                  component={RouterLink}
                  to="/login"
                  sx={{ color: 'rgba(255,255,255,0.85)', fontWeight: 500 }}
                >
                  Log in
                </Button>
                <Button
                  variant="contained"
                  component={RouterLink}
                  to="/signup"
                  sx={{
                    bgcolor: '#14b8a6',
                    color: '#042f2e',
                    fontWeight: 700,
                    px: 2.25,
                    '&:hover': { bgcolor: '#2dd4bf' },
                  }}
                >
                  Get started
                </Button>
              </Box>
            )}
          </Toolbar>
        </Container>
      </AppBar>
      {children}
    </Box>
  )
}
