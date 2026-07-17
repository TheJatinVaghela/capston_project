import { useEffect, useState } from 'react'
import { Link as RouterLink } from 'react-router-dom'
import {
  Alert,
  Box,
  Button,
  Card,
  CardActions,
  CardContent,
  Chip,
  Container,
  LinearProgress,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import { useAuth } from '../context/AuthContext'
import { createBusiness, getStats, listBusinesses } from '../api/client'

export default function DashboardPage() {
  const { user, businesses, activeBusiness, selectBusiness, upsertBusiness, refresh } = useAuth()
  const [showCreate, setShowCreate] = useState(false)
  const [name, setName] = useState('')
  const [website, setWebsite] = useState('')
  const [description, setDescription] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [stats, setStats] = useState(null)
  const [bizMeta, setBizMeta] = useState(null)

  useEffect(() => {
    if (!activeBusiness) {
      setStats(null)
      return
    }
    getStats(activeBusiness.id).then(setStats).catch(() => setStats(null))
  }, [activeBusiness])

  useEffect(() => {
    listBusinesses()
      .then((d) => setBizMeta(d))
      .catch(() => setBizMeta(null))
  }, [businesses.length])

  const maxBusinesses = bizMeta?.max_businesses ?? 1
  const canCreate = bizMeta?.can_create_business ?? businesses.length < 1
  const accountPlan = (bizMeta?.account_plan || 'free').replace(/^\w/, (c) => c.toUpperCase())

  const onCreate = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const data = await createBusiness({ name, website, description })
      upsertBusiness(data.business)
      selectBusiness(data.business.id)
      setShowCreate(false)
      setName('')
      await refresh()
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const statusColor = (s) => {
    if (s === 'active' || s === 'trialing') return 'success'
    if (s === 'past_due') return 'warning'
    return 'default'
  }

  const intents = stats?.intent_distribution
    ? Object.entries(stats.intent_distribution).sort((a, b) => b[1] - a[1])
    : []
  const totalIntents = intents.reduce((s, [, n]) => s + n, 0) || 1

  return (
    <Container maxWidth="md" sx={{ py: { xs: 3.5, md: 5 } }}>
      <Box sx={{ mb: 4 }}>
        <Typography
          variant="overline"
          sx={{ color: 'primary.main', fontWeight: 700, letterSpacing: '0.08em' }}
        >
          Overview
        </Typography>
        <Typography variant="h4" sx={{ mb: 1 }}>
          Welcome{user ? `, ${user.name}` : ''}
        </Typography>
        <Typography color="text.secondary" sx={{ mb: 1, maxWidth: 560 }}>
          Each business needs its own monthly plan for embed + AI model settings. Free preview works per business until you subscribe that business.
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Account plan: <Box component="strong" sx={{ color: 'text.primary' }}>{accountPlan}</Box>
          {' '}— {businesses.length} / {maxBusinesses} businesses
          {!canCreate && (
            <>
              {' '}
              (<Button component={RouterLink} to="/billing" size="small" sx={{ p: 0, minWidth: 0, verticalAlign: 'baseline' }}>
                Upgrade to add more
              </Button>)
            </>
          )}
        </Typography>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
        <Typography variant="h6">Your businesses</Typography>
        <Button
          variant="contained"
          onClick={() => setShowCreate((v) => !v)}
          disabled={!showCreate && !canCreate}
        >
          {showCreate ? 'Cancel' : 'Add business'}
        </Button>
      </Stack>

      {!canCreate && !showCreate && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Your {accountPlan} plan allows {maxBusinesses} business{maxBusinesses === 1 ? '' : 'es'}.
          Upgrade on Billing to create more.
        </Alert>
      )}

      {showCreate && (
        <Box
          component="form"
          onSubmit={onCreate}
          sx={{
            display: 'grid',
            gap: 2,
            mb: 3,
            p: 3,
            bgcolor: 'background.paper',
            borderRadius: 3,
            border: '1px solid',
            borderColor: 'divider',
            boxShadow: 2,
          }}
        >
          <Alert severity="info">
            New businesses start on Free. Subscribe this business under Billing to unlock embed and model settings.
          </Alert>
          <TextField label="Business name" required value={name} onChange={(e) => setName(e.target.value)} />
          <TextField label="Website" value={website} onChange={(e) => setWebsite(e.target.value)} />
          <TextField label="Description" multiline minRows={2} value={description} onChange={(e) => setDescription(e.target.value)} />
          <Button type="submit" variant="contained" disabled={loading}>{loading ? 'Creating…' : 'Create'}</Button>
        </Box>
      )}

      <Stack spacing={2} sx={{ mb: 4 }}>
        {businesses.map((b) => {
          const selected = activeBusiness?.id === b.id
          return (
            <Card
              key={b.id}
              variant="outlined"
              sx={{
                borderColor: selected ? 'primary.main' : 'divider',
                borderWidth: selected ? 1.5 : 1,
                bgcolor: selected ? 'rgba(15, 118, 110, 0.03)' : 'background.paper',
                boxShadow: selected ? 2 : 0,
              }}
            >
              <CardContent sx={{ pb: 1 }}>
                <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1.25, flexWrap: 'wrap' }}>
                  <Typography variant="h6" sx={{ mr: 0.5 }}>{b.name}</Typography>
                  <Chip size="small" label={b.subscription_status || 'free'} color={statusColor(b.subscription_status)} />
                  <Chip size="small" variant="outlined" label={(b.effective_plan || b.plan || 'free')} />
                  <Chip size="small" variant="outlined" label={`AI: ${b.ai_model || 'mistral'}`} />
                </Stack>
                <Typography color="text.secondary" variant="body2">{b.website || 'No website'}</Typography>
                <Typography variant="body2" sx={{ mt: 1, color: 'text.secondary' }}>{b.description || 'No description yet'}</Typography>
              </CardContent>
              <CardActions sx={{ px: 2, pb: 2, gap: 0.5 }}>
                <Button size="small" onClick={() => selectBusiness(b.id)} variant={selected ? 'contained' : 'text'}>
                  {selected ? 'Selected' : 'Select'}
                </Button>
                <Button size="small" component={RouterLink} to="/knowledge" onClick={() => selectBusiness(b.id)}>Knowledge</Button>
                <Button size="small" component={RouterLink} to="/preview" onClick={() => selectBusiness(b.id)}>Try chat</Button>
                <Button size="small" component={RouterLink} to="/billing" onClick={() => selectBusiness(b.id)}>Billing</Button>
              </CardActions>
            </Card>
          )
        })}
        {businesses.length === 0 && (
          <Alert severity="info">Create a business to get started.</Alert>
        )}
      </Stack>

      {activeBusiness && (
        <Box
          sx={{
            p: { xs: 2.5, sm: 3.5 },
            bgcolor: 'background.paper',
            borderRadius: 3,
            border: '1px solid',
            borderColor: 'divider',
            boxShadow: 2,
          }}
        >
          <Typography variant="h6" sx={{ mb: 0.5 }}>
            Analytics — {activeBusiness.name}
          </Typography>
          {!stats ? (
            <Typography color="text.secondary">No stats yet.</Typography>
          ) : (
            <>
              <Box
                sx={{
                  display: 'grid',
                  gridTemplateColumns: { xs: '1fr 1fr', sm: 'repeat(4, 1fr)' },
                  gap: 1.5,
                  my: 2.5,
                }}
              >
                {[
                  { label: 'Messages', value: stats.total_messages || 0 },
                  { label: 'Sessions', value: stats.total_sessions || 0 },
                  { label: 'Avg confidence', value: `${Math.round((stats.average_confidence || 0) * 100)}%` },
                  { label: 'Fallback rate', value: `${Math.round((stats.fallback_rate || 0) * 100)}%` },
                ].map((m) => (
                  <Box
                    key={m.label}
                    sx={{
                      p: 2,
                      borderRadius: 2,
                      bgcolor: 'rgba(7, 21, 37, 0.03)',
                      border: '1px solid',
                      borderColor: 'divider',
                    }}
                  >
                    <Typography variant="caption" color="text.secondary" fontWeight={600} display="block">
                      {m.label}
                    </Typography>
                    <Typography variant="h5" sx={{ mt: 0.5, fontFamily: '"Fraunces", Georgia, serif' }}>
                      {m.value}
                    </Typography>
                  </Box>
                ))}
              </Box>
              <Typography variant="subtitle2" sx={{ mb: 1.5 }}>Top intents</Typography>
              <Stack spacing={1.25}>
                {intents.slice(0, 8).map(([intent, count]) => (
                  <Box key={intent}>
                    <Stack direction="row" justifyContent="space-between" sx={{ mb: 0.4 }}>
                      <Typography variant="body2" fontWeight={500}>{intent}</Typography>
                      <Typography variant="caption" color="text.secondary">{count}</Typography>
                    </Stack>
                    <LinearProgress
                      variant="determinate"
                      value={(count / totalIntents) * 100}
                    />
                  </Box>
                ))}
                {intents.length === 0 && (
                  <Typography variant="body2" color="text.secondary">No conversations logged yet.</Typography>
                )}
              </Stack>
              {stats.model_usage && Object.keys(stats.model_usage).length > 0 && (
                <>
                  <Typography variant="subtitle2" sx={{ mt: 2.5, mb: 1 }}>Model usage</Typography>
                  <Typography variant="body2" color="text.secondary">
                    {Object.entries(stats.model_usage).map(([m, n]) => `${m}: ${n}`).join(' · ')}
                  </Typography>
                </>
              )}
            </>
          )}
        </Box>
      )}
    </Container>
  )
}
