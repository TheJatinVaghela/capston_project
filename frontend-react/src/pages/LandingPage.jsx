import { Link as RouterLink } from 'react-router-dom'
import { Box, Button, Container, Typography, Stack } from '@mui/material'

function ChatMock() {
  return (
    <Box
      sx={{
        position: 'relative',
        width: '100%',
        maxWidth: 440,
        mx: 'auto',
        animation: 'sf-float 7s ease-in-out infinite',
      }}
    >
      <Box
        sx={{
          borderRadius: '18px 18px 0 0',
          bgcolor: '#0b1f33',
          px: 2.5,
          py: 1.75,
          border: '1px solid rgba(255,255,255,0.14)',
          borderBottom: 'none',
          boxShadow: '0 24px 60px rgba(0,0,0,0.35)',
        }}
      >
        <Typography sx={{ color: '#fff', fontWeight: 700, fontSize: '0.95rem' }}>
          Acme Ceramics Support
        </Typography>
        <Typography sx={{ color: 'rgba(255,255,255,0.55)', fontSize: '0.75rem' }}>
          Online · replies in your language
        </Typography>
      </Box>
      <Box
        sx={{
          bgcolor: '#f4f6f8',
          border: '1px solid rgba(255,255,255,0.14)',
          borderTop: 'none',
          borderRadius: '0 0 18px 18px',
          p: 2.25,
          display: 'grid',
          gap: 1.35,
          boxShadow: '0 28px 60px rgba(0,0,0,0.28)',
        }}
      >
        <Box
          sx={{
            justifySelf: 'start',
            bgcolor: '#fff',
            border: '1px solid rgba(11,31,51,0.08)',
            px: 1.75,
            py: 1.15,
            borderRadius: '4px 14px 14px 14px',
            maxWidth: '90%',
            fontSize: 13.5,
            color: '#0b1f33',
            lineHeight: 1.5,
          }}
        >
          Hi! I can help with shipping, returns, and our handmade mugs.
        </Box>
        <Box
          sx={{
            justifySelf: 'end',
            bgcolor: '#0f766e',
            color: '#fff',
            px: 1.75,
            py: 1.15,
            borderRadius: '14px 4px 14px 14px',
            maxWidth: '82%',
            fontSize: 13.5,
            lineHeight: 1.5,
          }}
        >
          Do you ship to Canada?
        </Box>
        <Box
          sx={{
            justifySelf: 'start',
            bgcolor: '#fff',
            border: '1px solid rgba(11,31,51,0.08)',
            px: 1.75,
            py: 1.15,
            borderRadius: '4px 14px 14px 14px',
            maxWidth: '92%',
            fontSize: 13.5,
            color: '#0b1f33',
            lineHeight: 1.5,
          }}
        >
          Yes — 3–5 business days, $5 flat rate across Canada.
        </Box>
        <Box
          sx={{
            mt: 0.5,
            display: 'flex',
            gap: 1,
            alignItems: 'center',
            bgcolor: '#fff',
            border: '1px solid rgba(11,31,51,0.1)',
            borderRadius: 2,
            px: 1.5,
            py: 1,
          }}
        >
          <Typography sx={{ flex: 1, color: 'rgba(11,31,51,0.35)', fontSize: 13 }}>
            Ask about products, shipping, returns…
          </Typography>
          <Box
            sx={{
              bgcolor: '#14b8a6',
              color: '#042f2e',
              fontSize: 12,
              fontWeight: 700,
              px: 1.5,
              py: 0.6,
              borderRadius: 1.5,
            }}
          >
            Send
          </Box>
        </Box>
      </Box>
    </Box>
  )
}

const FEATURES = [
  {
    title: 'Your knowledge',
    body: 'Paste FAQs, shipping rules, and product details. The assistant uses them as reference — not free-form invention.',
  },
  {
    title: 'Live on your site',
    body: 'One script tag. Multilingual replies. Preview as a customer before you publish.',
  },
  {
    title: 'Simple plans',
    body: 'Start free, then unlock embed and model controls with a monthly subscription per business.',
  },
]

export default function LandingPage() {
  return (
    <Box sx={{ bgcolor: '#071525', color: '#e8eef5', overflow: 'hidden' }}>
      {/* Hero */}
      <Box
        sx={{
          position: 'relative',
          minHeight: { xs: 'auto', md: 'calc(100vh - 64px)' },
          display: 'flex',
          alignItems: 'center',
          background:
            'radial-gradient(ellipse 80% 60% at 10% -10%, rgba(20,184,166,0.32), transparent 55%), radial-gradient(ellipse 50% 40% at 95% 30%, rgba(15,118,110,0.2), transparent 50%), linear-gradient(165deg, #071525 0%, #0b1f33 50%, #081828 100%)',
          '&::after': {
            content: '""',
            position: 'absolute',
            inset: 0,
            backgroundImage:
              'linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)',
            backgroundSize: '48px 48px',
            maskImage: 'radial-gradient(ellipse 70% 60% at 50% 40%, black, transparent)',
            pointerEvents: 'none',
            opacity: 0.5,
          },
        }}
      >
        <Container
          maxWidth="lg"
          sx={{
            position: 'relative',
            zIndex: 1,
            py: { xs: 6, md: 8 },
            display: 'grid',
            gridTemplateColumns: { xs: '1fr', md: '1.05fr 0.95fr' },
            gap: { xs: 5, md: 6 },
            alignItems: 'center',
          }}
        >
          <Box sx={{ animation: 'sf-fade-up 0.7s ease both' }}>
            <Typography
              component="h1"
              sx={{
                fontFamily: '"Fraunces", Georgia, serif',
                fontWeight: 700,
                fontSize: { xs: '3.1rem', sm: '4rem', md: '4.6rem' },
                letterSpacing: '-0.04em',
                lineHeight: 0.96,
                mb: 2.5,
                color: '#fff',
              }}
            >
              SupportFlow
            </Typography>
            <Typography
              sx={{
                fontSize: { xs: '1.12rem', md: '1.3rem' },
                maxWidth: 460,
                color: 'rgba(232,238,245,0.78)',
                mb: 4,
                lineHeight: 1.55,
                animation: 'sf-fade-up 0.7s ease 0.08s both',
              }}
            >
              Train a support chatbot on your FAQs and policies, then embed it on your site.
            </Typography>
            <Stack
              direction={{ xs: 'column', sm: 'row' }}
              spacing={1.75}
              sx={{ animation: 'sf-fade-up 0.7s ease 0.16s both' }}
            >
              <Button
                component={RouterLink}
                to="/signup"
                size="large"
                variant="contained"
                sx={{
                  bgcolor: '#14b8a6',
                  color: '#042f2e',
                  px: 3.5,
                  py: 1.5,
                  fontSize: '1rem',
                  fontWeight: 700,
                  '&:hover': { bgcolor: '#2dd4bf' },
                }}
              >
                Start free
              </Button>
              <Button
                component={RouterLink}
                to="/demo"
                size="large"
                variant="outlined"
                sx={{
                  borderColor: 'rgba(255,255,255,0.3)',
                  color: '#fff',
                  px: 3.5,
                  py: 1.5,
                  '&:hover': {
                    borderColor: 'rgba(255,255,255,0.55)',
                    bgcolor: 'rgba(255,255,255,0.06)',
                  },
                }}
              >
                Try TechFlow demo
              </Button>
            </Stack>
          </Box>

          <Box sx={{ animation: 'sf-fade-up 0.85s ease 0.2s both', px: { xs: 0, sm: 2 } }}>
            <ChatMock />
          </Box>
        </Container>
      </Box>

      {/* Features */}
      <Box
        sx={{
          borderTop: '1px solid rgba(255,255,255,0.08)',
          py: { xs: 8, md: 11 },
          background: 'linear-gradient(180deg, #0a1a2a 0%, #071525 100%)',
        }}
      >
        <Container maxWidth="lg">
          <Box sx={{ maxWidth: 560, mb: { xs: 5, md: 7 } }}>
            <Typography
              component="h2"
              sx={{
                fontFamily: '"Fraunces", Georgia, serif',
                fontWeight: 700,
                fontSize: { xs: '1.85rem', md: '2.4rem' },
                mb: 1.5,
                letterSpacing: '-0.025em',
                color: '#fff',
              }}
            >
              Built for real support teams
            </Typography>
            <Typography
              sx={{
                color: 'rgba(232,238,245,0.68)',
                fontSize: { xs: '1.05rem', md: '1.12rem' },
                lineHeight: 1.65,
              }}
            >
              Upload company knowledge once. Customers get accurate answers — the bot stays on-topic.
            </Typography>
          </Box>

          <Box
            sx={{
              display: 'grid',
              gridTemplateColumns: { xs: '1fr', md: 'repeat(3, 1fr)' },
              gap: { xs: 4, md: 5 },
            }}
          >
            {FEATURES.map((item, i) => (
              <Box
                key={item.title}
                sx={{
                  animation: `sf-fade-up 0.6s ease ${0.08 * i}s both`,
                  pr: { md: 2 },
                  borderTop: '2px solid rgba(20,184,166,0.45)',
                  pt: 2.5,
                }}
              >
                <Typography
                  sx={{
                    fontWeight: 700,
                    fontSize: '1.1rem',
                    mb: 1.25,
                    color: '#99f6e4',
                    letterSpacing: '-0.01em',
                  }}
                >
                  {item.title}
                </Typography>
                <Typography
                  sx={{
                    color: 'rgba(232,238,245,0.68)',
                    lineHeight: 1.7,
                    fontSize: '0.98rem',
                  }}
                >
                  {item.body}
                </Typography>
              </Box>
            ))}
          </Box>
        </Container>
      </Box>

      {/* Closing CTA */}
      <Box
        sx={{
          borderTop: '1px solid rgba(255,255,255,0.08)',
          py: { xs: 7, md: 9 },
          background:
            'radial-gradient(ellipse 70% 80% at 50% 100%, rgba(20,184,166,0.18), transparent 60%), #071525',
        }}
      >
        <Container maxWidth="sm" sx={{ textAlign: 'center' }}>
          <Typography
            component="h2"
            sx={{
              fontFamily: '"Fraunces", Georgia, serif',
              fontWeight: 700,
              fontSize: { xs: '1.75rem', md: '2.15rem' },
              letterSpacing: '-0.02em',
              mb: 1.5,
              color: '#fff',
            }}
          >
            Ready to support your customers?
          </Typography>
          <Typography
            sx={{
              color: 'rgba(232,238,245,0.65)',
              mb: 3.5,
              lineHeight: 1.65,
              fontSize: '1.05rem',
            }}
          >
            Create an account, add your knowledge, and preview the chat in minutes.
          </Typography>
          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={1.75} justifyContent="center">
            <Button
              component={RouterLink}
              to="/signup"
              size="large"
              variant="contained"
              sx={{
                bgcolor: '#14b8a6',
                color: '#042f2e',
                px: 3.5,
                py: 1.4,
                fontWeight: 700,
                '&:hover': { bgcolor: '#2dd4bf' },
              }}
            >
              Create your account
            </Button>
            <Button
              component={RouterLink}
              to="/login"
              size="large"
              variant="outlined"
              sx={{
                borderColor: 'rgba(255,255,255,0.28)',
                color: '#fff',
                px: 3.5,
                py: 1.4,
                '&:hover': {
                  borderColor: 'rgba(255,255,255,0.5)',
                  bgcolor: 'rgba(255,255,255,0.05)',
                },
              }}
            >
              Log in
            </Button>
          </Stack>
        </Container>
      </Box>

      <Box
        component="footer"
        sx={{
          borderTop: '1px solid rgba(255,255,255,0.06)',
          py: 3,
          textAlign: 'center',
        }}
      >
        <Typography sx={{ color: 'rgba(232,238,245,0.4)', fontSize: '0.85rem' }}>
          SupportFlow · Customer support chatbot for your business
        </Typography>
      </Box>
    </Box>
  )
}
