import { useState } from 'react'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import { Alert, Box, Button, Container, TextField, Typography, Link, Stack } from '@mui/material'
import { useAuth } from '../context/AuthContext'

export default function SignupPage() {
  const { register } = useAuth()
  const navigate = useNavigate()
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    business_name: '',
    website: '',
    description: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const set = (k) => (e) => setForm((f) => ({ ...f, [k]: e.target.value }))

  const onSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await register(form)
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
        py: { xs: 5, md: 7 },
        background:
          'radial-gradient(ellipse 70% 50% at 100% 0%, rgba(20,184,166,0.1), transparent 50%), radial-gradient(ellipse 50% 40% at 0% 100%, rgba(11,31,51,0.06), transparent)',
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
            Create your account
          </Typography>
          <Typography color="text.secondary" sx={{ mb: 3.5 }}>
            Register your business and start configuring your support bot.
          </Typography>
          {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
          <Box component="form" onSubmit={onSubmit}>
            <Stack spacing={2}>
              <TextField label="Your name" required value={form.name} onChange={set('name')} />
              <TextField label="Email" type="email" required value={form.email} onChange={set('email')} />
              <TextField
                label="Password"
                type="password"
                required
                helperText="Min 10 characters, include a letter and a number"
                value={form.password}
                onChange={set('password')}
                inputProps={{ minLength: 10 }}
              />
              <TextField label="Business name" required value={form.business_name} onChange={set('business_name')} />
              <TextField label="Website" value={form.website} onChange={set('website')} placeholder="https://mugs.example.com" />
              <TextField label="Short description" multiline minRows={2} value={form.description} onChange={set('description')} />
              <Button type="submit" variant="contained" size="large" disabled={loading} sx={{ mt: 0.5 }}>
                {loading ? 'Creating…' : 'Create account'}
              </Button>
            </Stack>
          </Box>
          <Typography sx={{ mt: 3 }} color="text.secondary">
            Already have an account?{' '}
            <Link component={RouterLink} to="/login" fontWeight={600} underline="hover">
              Log in
            </Link>
          </Typography>
        </Box>
      </Container>
    </Box>
  )
}
