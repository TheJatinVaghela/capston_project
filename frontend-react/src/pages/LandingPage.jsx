import { Link as RouterLink } from 'react-router-dom'
import { Box, Button, Container, Typography, Stack } from '@mui/material'

function ChatMock() {
  return (
    <Box
      sx={{
        height: '100%',
        minHeight: { xs: 280, md: 420 },
        display: 'flex',
        flexDirection: 'column',
        background:
          'linear-gradient(165deg, rgba(15,118,110,0.22) 0%, rgba(7,21,37,0.4) 40%, rgba(11,31,51,0.55) 100%)',
        borderTop: '1px solid rgba(255,255,255,0.1)',
        position: 'relative',
        overflow: 'hidden',
        animation: 'sf-float 7s ease-in-out infinite',
        '&::before': {
          content: '""',
          position: 'absolute',
          inset: 0,
          backgroundImage:
            'radial-gradient(circle at 20% 30%, rgba(20,184,166,0.15), transparent 40%), radial-gradient(circle at 80% 70%, rgba(255,255,255,0.04), transparent 35%)',
          pointerEvents: 'none',
        },
      }}
    >
      <Box
        sx={{
          position: 'relative',
          zIndex: 1,
          maxWidth: 420,
          width: '100%',
          mx: 'auto',
          mt: { xs: 3, md: 5 },
          px: { xs: 2, md: 0 },
        }}
      >
        <Box
          sx={{
            borderRadius: '16px 16px 0 0',
            bgcolor: '#0b1f33',
            px: 2.5,
            py: 1.75,
            border: '1px solid rgba(255,255,255,0.12)',
            borderBottom: 'none',
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
            bgcolor: 'rgba(244,246,248,0.97)',
            border: '1px solid rgba(255,255,255,0.12)',
            borderTop: 'none',
            borderRadius: '0 0 16px 16px',
            p: 2,
            display: 'grid',
            gap: 1.25,
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
              maxWidth: '88%',
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
              maxWidth: '80%',
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
              maxWidth: '90%',
              fontSize: 13.5,
              color: '#0b1f33',
              lineHeight: 1.5,
            }}
          >
            Yes — 3–5 business days, $5 flat rate across Canada.
          </Box>
        </Box>
      </Box>
    </Box>
  )
}

export default function LandingPage() {
  return (
    <Box sx={{ bgcolor: '#071525', color: '#e8eef5', overflow: 'hidden' }}>
      {/* Hero — first viewport: brand, headline, support, CTAs, product visual */}
      <Box
        sx={{
          minHeight: { xs: 'auto', md: 'calc(100vh - 64px)' },
          display: 'flex',
          flexDirection: 'column',
          position: 'relative',
          background:
            'radial-gradient(ellipse 90% 70% at 15% 0%, rgba(20,184,166,0.28), transparent 55%), radial-gradient(ellipse 60% 50% at 90% 20%, rgba(15,118,110,0.18), transparent 50%), linear-gradient(175deg, #071525 0%, #0b1f33 55%, #0a1a2a 100%)',
        }}
      >
        <Container
          maxWidth="lg"
          sx={{
            pt: { xs: 6, md: 9 },
            pb: { xs: 4, md: 5 },
            flex: 1,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
          }}
        >
          <Box
            sx={{
              maxWidth: 640,
              animation: 'sf-fade-up 0.7s ease both',
            }}
          >
            <Typography
              component="h1"
              sx={{
                fontFamily: '"Fraunces", Georgia, serif',
                fontWeight: 700,
                fontSize: { xs: '3rem', sm: '3.75rem', md: '4.75rem' },
                letterSpacing: '-0.035em',
                lineHeight: 0.98,
                mb: 2.5,
                background: 'linear-gradient(135deg, #ffffff 40%, #99f6e4 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text',
              }}
            >
              SupportFlow
            </Typography>
            <Typography
              sx={{
                fontSize: { xs: '1.15rem', md: '1.35rem' },
                maxWidth: 480,
                color: 'rgba(232,238,245,0.78)',
                mb: 4,
                lineHeight: 1.55,
                fontWeight: 450,
                animation: 'sf-fade-up 0.7s ease 0.1s both',
              }}
            >
              Train a support chatbot on your FAQs and policies, then embed it on your site.
            </Typography>
            <Stack
              direction={{ xs: 'column', sm: 'row' }}
              spacing={1.75}
              sx={{ animation: 'sf-fade-up 0.7s ease 0.18s both' }}
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
                  borderColor: 'rgba(255,255,255,0.28)',
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
        </Container>

        <Box
          sx={{
            width: '100%',
            animation: 'sf-fade-up 0.85s ease 0.28s both',
          }}
        >
          <ChatMock />
        </Box>
      </Box>

      {/* Below fold — one purpose section */}
      <Box
        sx={{
          borderTop: '1px solid rgba(255,255,255,0.08)',
          py: { xs: 8, md: 11 },
          background: 'linear-gradient(180deg, #0a1a2a 0%, #071525 100%)',
        }}
      >
        <Container maxWidth="md">
          <Typography
            variant="h3"
            sx={{
              fontFamily: '"Fraunces", Georgia, serif',
              fontWeight: 700,
              fontSize: { xs: '1.75rem', md: '2.25rem' },
              mb: 1.5,
              letterSpacing: '-0.02em',
            }}
          >
            Built for real support teams
          </Typography>
          <Typography
            sx={{
              color: 'rgba(232,238,245,0.7)',
              fontSize: { xs: '1.05rem', md: '1.15rem' },
              maxWidth: 520,
              mb: 5,
              lineHeight: 1.65,
            }}
          >
            Upload company knowledge once. Customers get accurate answers — the bot stays on-topic.
          </Typography>
          <Stack
            direction={{ xs: 'column', md: 'row' }}
            spacing={{ xs: 4, md: 6 }}
            divider={
              <Box
                sx={{
                  display: { xs: 'none', md: 'block' },
                  width: 1,
                  bgcolor: 'rgba(255,255,255,0.1)',
                  alignSelf: 'stretch',
                }}
              />
            }
          >
            {[
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
            ].map((item) => (
              <Box key={item.title} sx={{ flex: 1 }}>
                <Typography
                  sx={{
                    fontWeight: 700,
                    fontSize: '1.05rem',
                    mb: 1,
                    color: '#99f6e4',
                  }}
                >
                  {item.title}
                </Typography>
                <Typography sx={{ color: 'rgba(232,238,245,0.65)', lineHeight: 1.65, fontSize: '0.95rem' }}>
                  {item.body}
                </Typography>
              </Box>
            ))}
          </Stack>
        </Container>
      </Box>
    </Box>
  )
}
