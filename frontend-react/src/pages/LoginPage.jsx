import { useState } from 'react'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import { Alert, Box, Button, Container, TextField, Typography, Link, Stack } from '@mui/material'
import { useAuth } from '../context/AuthContext'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const onSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(email, password)
      navigate('/dashboard')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Box
      sx={{
        minHeight: 'calc(100vh - 64px)',
        display: 'flex',
        alignItems: 'center',
        py: { xs: 5, md: 8 },
        background:
          'radial-gradient(ellipse 70% 50% at 0% 0%, rgba(20,184,166,0.1), transparent 50%), radial-gradient(ellipse 50% 40% at 100% 100%, rgba(11,31,51,0.06), transparent)',
      }}
    >
      <Container maxWidth="sm">
        <Box
          sx={{
            p: { xs: 3, sm: 4.5 },
            bgcolor: 'background.paper',
            borderRadius: 3,
            border: '1px solid',
            borderColor: 'divider',
            boxShadow: 4,
            animation: 'sf-fade-up 0.5s ease both',
          }}
        >
          <Typography
            variant="overline"
            sx={{ color: 'primary.main', fontWeight: 700, letterSpacing: '0.08em', mb: 0.5, display: 'block' }}
          >
            SupportFlow
          </Typography>
          <Typography variant="h4" sx={{ mb: 1 }}>
            Welcome back
          </Typography>
          <Typography color="text.secondary" sx={{ mb: 3.5 }}>
            Demo: demo@supportflow.local / demo1234
          </Typography>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          <Box component="form" onSubmit={onSubmit}>
            <Stack spacing={2.25}>
              <TextField label="Email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
              <TextField label="Password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} />
              <Button type="submit" variant="contained" size="large" disabled={loading} sx={{ mt: 0.5 }}>
                {loading ? 'Signing in…' : 'Sign in'}
              </Button>
            </Stack>
          </Box>
          <Typography sx={{ mt: 3 }} color="text.secondary">
            No account?{' '}
            <Link component={RouterLink} to="/signup" fontWeight={600} underline="hover">
              Sign up
            </Link>
          </Typography>
        </Box>
      </Container>
    </Box>
  )
}
