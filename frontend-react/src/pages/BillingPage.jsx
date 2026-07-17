import { useEffect, useState } from 'react'
import { useSearchParams } from 'react-router-dom'
import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Container,
  Stack,
  Typography,
} from '@mui/material'
import { useAuth } from '../context/AuthContext'
import {
  createCheckout,
  getBillingConfig,
  openBillingPortal,
  confirmCheckout,
  syncSubscription,
} from '../api/client'

const FALLBACK_PLANS = [
  {
    id: 'basic',
    name: 'Basic',
    price_cad: 5,
    description: 'Embed widget + AI model settings for one business.',
    features: ['1 business', '500-word knowledge base', 'Website embed widget', 'Choose AI model'],
    available: true,
  },
  {
    id: 'professional',
    name: 'Professional',
    price_cad: 10,
    description: 'For growing support volume on your store.',
    features: ['Up to 5 businesses', '2,000-word knowledge base', 'Everything in Basic'],
    available: true,
  },
  {
    id: 'premium',
    name: 'Premium',
    price_cad: 20,
    description: 'Highest tier for busy customer-support teams.',
    features: ['Up to 10 businesses', '5,000-word knowledge base', 'Custom chatbot colors', 'Everything in Professional'],
    available: true,
  },
]

export default function BillingPage() {
  const { activeBusiness, upsertBusiness, selectBusiness, refresh } = useAuth()
  const [params, setParams] = useSearchParams()
  const [config, setConfig] = useState(null)
  const [error, setError] = useState('')
  const [loadingPlan, setLoadingPlan] = useState('')
  const [activating, setActivating] = useState(false)
  const [activated, setActivated] = useState(false)

  useEffect(() => {
    getBillingConfig().then(setConfig).catch(() => setConfig({ stripe_configured: false }))
  }, [])

  // After Stripe redirect: verify session and unlock immediately
  useEffect(() => {
    const success = params.get('success')
    const sessionId = params.get('session_id')
    const businessId = params.get('business_id') || activeBusiness?.id
    if (!success || !businessId) return

    let cancelled = false
    const run = async () => {
      setActivating(true)
      setError('')
      try {
        if (sessionId) {
          const data = await confirmCheckout(businessId, sessionId)
          if (cancelled) return
          upsertBusiness(data.business)
          selectBusiness(data.business.id)
          setActivated(true)
        } else {
          await refresh()
        }
        setParams({}, { replace: true })
      } catch (err) {
        if (!cancelled) setError(err.message || 'Could not activate subscription')
      } finally {
        if (!cancelled) setActivating(false)
      }
    }
    run()
    return () => {
      cancelled = true
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps -- run once on return from Stripe

  if (!activeBusiness) {
    return (
      <Container sx={{ py: 4 }}>
        <Alert severity="info">Select a business first.</Alert>
      </Container>
    )
  }

  const status = activeBusiness.subscription_status || 'free'
  const currentPlan = (activeBusiness.plan || 'free').toLowerCase()
  const subscribed = status === 'active' || status === 'trialing'
  const plans = config?.plans?.length ? config.plans : FALLBACK_PLANS

  const subscribe = async (planId) => {
    setError('')
    setLoadingPlan(planId)
    try {
      const data = await createCheckout(activeBusiness.id, planId)
      window.location.href = data.checkout_url
    } catch (err) {
      setError(err.message)
      setLoadingPlan('')
    }
  }

  const manage = async () => {
    setError('')
    setLoadingPlan('portal')
    try {
      const data = await openBillingPortal(activeBusiness.id)
      window.location.href = data.portal_url
    } catch (err) {
      setError(err.message)
      setLoadingPlan('')
    }
  }

  const syncFromStripe = async () => {
    setError('')
    setActivating(true)
    try {
      const data = await syncSubscription(activeBusiness.id)
      if (data.business) upsertBusiness(data.business)
      if (data.found && (data.business.subscription_status === 'active' || data.business.subscription_status === 'trialing')) {
        setActivated(true)
        setError('')
      } else if (!data.found) {
        setError('No active Stripe subscription found for this business yet. Complete Checkout first.')
      }
    } catch (err) {
      setError(err.message || 'Could not refresh billing status')
    } finally {
      setActivating(false)
    }
  }

  const planLabel = (id) => {
    const found = plans.find((p) => p.id === id)
    return found?.name || (id === 'free' ? 'Free' : id)
  }

  return (
    <Container maxWidth="md" sx={{ py: { xs: 3.5, md: 5 } }}>
      <Box sx={{ mb: 3.5 }}>
        <Typography
          variant="overline"
          sx={{ color: 'primary.main', fontWeight: 700, letterSpacing: '0.08em' }}
        >
          Plans
        </Typography>
        <Typography variant="h4" sx={{ mb: 1 }}>
          Billing
        </Typography>
        <Typography color="text.secondary" sx={{ maxWidth: 560 }}>
          Choose a monthly plan for {activeBusiness.name}. Paid plans unlock the embeddable widget
          and AI model settings. Each business needs its own subscription.
        </Typography>
      </Box>

      {activating && (
        <Alert severity="info" icon={<CircularProgress size={18} />} sx={{ mb: 2 }}>
          Confirming your payment and unlocking access…
        </Alert>
      )}
      {activated && !activating && (
        <Alert severity="success" sx={{ mb: 2 }}>
          Subscription active — you can embed the widget now.
        </Alert>
      )}
      {params.get('canceled') && (
        <Alert severity="info" sx={{ mb: 2 }}>Checkout canceled.</Alert>
      )}
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Box
        sx={{
          p: { xs: 2.5, sm: 3 },
          mb: 3,
          bgcolor: 'background.paper',
          borderRadius: 3,
          border: '1px solid',
          borderColor: 'divider',
          boxShadow: 2,
        }}
      >
        <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1.25, flexWrap: 'wrap' }}>
          <Typography variant="h6">Current plan</Typography>
          <Chip label={planLabel(currentPlan)} color={subscribed ? 'success' : 'default'} />
          <Chip label={status} size="small" variant="outlined" />
        </Stack>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          Free: edit knowledge + preview chat (limit {config?.free_preview_limit ?? 100} messages).
          Paid: unlimited preview + website embed widget.
        </Typography>
        <Typography variant="body2" sx={{ mb: 2.5 }}>
          Preview chats used: {activeBusiness.preview_chat_count || 0}
        </Typography>

        {!config?.stripe_configured && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            Stripe is not configured yet. Add keys to <code>backend/.env</code> (see .env.example), then restart the API.
          </Alert>
        )}

        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          {subscribed && (
            <Button
              variant="outlined"
              onClick={manage}
              disabled={!!loadingPlan || !config?.stripe_configured}
            >
              {loadingPlan === 'portal' ? 'Redirecting…' : 'Manage / change plan'}
            </Button>
          )}
          <Button
            variant="text"
            onClick={syncFromStripe}
            disabled={activating || !config?.stripe_configured}
          >
            Refresh status from Stripe
          </Button>
        </Box>
      </Box>

      <Box
        sx={{
          display: 'grid',
          gap: 2,
          gridTemplateColumns: { xs: '1fr', sm: 'repeat(3, 1fr)' },
        }}
      >
        {plans.map((plan) => {
          const isCurrent = subscribed && currentPlan === plan.id
          const busy = loadingPlan === plan.id
          const featured = plan.id === 'professional'
          return (
            <Box
              key={plan.id}
              sx={{
                p: 2.75,
                display: 'flex',
                flexDirection: 'column',
                bgcolor: 'background.paper',
                borderRadius: 3,
                border: featured || isCurrent ? '2px solid' : '1px solid',
                borderColor: isCurrent ? 'primary.main' : featured ? 'primary.light' : 'divider',
                boxShadow: featured ? 3 : 1,
                position: 'relative',
                transition: 'transform 0.2s ease, box-shadow 0.2s ease',
                '&:hover': {
                  transform: 'translateY(-2px)',
                  boxShadow: 4,
                },
              }}
            >
              {featured && !isCurrent && (
                <Typography
                  variant="caption"
                  sx={{
                    position: 'absolute',
                    top: 12,
                    right: 12,
                    color: 'primary.main',
                    fontWeight: 700,
                    letterSpacing: '0.04em',
                    textTransform: 'uppercase',
                    fontSize: '0.65rem',
                  }}
                >
                  Popular
                </Typography>
              )}
              <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                <Typography variant="h6">{plan.name}</Typography>
                {isCurrent && <Chip size="small" color="success" label="Current" />}
              </Stack>
              <Typography variant="h4" sx={{ mb: 0.5 }}>
                ${plan.price_cad}
                <Typography component="span" variant="body2" color="text.secondary">
                  {' '}/ mo CAD
                </Typography>
              </Typography>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2, minHeight: 44 }}>
                {plan.description}
              </Typography>
              <Box component="ul" sx={{ m: 0, pl: 2.2, mb: 2.5, flexGrow: 1 }}>
                {(plan.features || []).map((f) => (
                  <Typography key={f} component="li" variant="body2" sx={{ mb: 0.65, color: 'text.secondary' }}>
                    {f}
                  </Typography>
                ))}
              </Box>
              <Button
                variant={featured ? 'contained' : 'outlined'}
                fullWidth
                disabled={
                  busy ||
                  activating ||
                  !config?.stripe_configured ||
                  !plan.available ||
                  isCurrent
                }
                onClick={() => (subscribed ? manage() : subscribe(plan.id))}
              >
                {busy || loadingPlan === 'portal'
                  ? 'Redirecting…'
                  : isCurrent
                    ? 'Active'
                    : subscribed
                      ? `Change to ${plan.name}`
                      : `Choose ${plan.name}`}
              </Button>
            </Box>
          )
        })}
      </Box>

      {subscribed && (
        <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mt: 2.5 }}>
          Already subscribed? Use Change plan / Manage subscription to upgrade, downgrade, or cancel
          in the Stripe customer portal.
        </Typography>
      )}
    </Container>
  )
}
