import { createTheme, alpha } from '@mui/material/styles'

const ink = '#071525'
const navy = '#0b1f33'
const teal = '#0f766e'
const tealBright = '#14b8a6'
const surface = '#f4f6f8'
const paper = '#ffffff'

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: teal,
      dark: '#0a5c56',
      light: tealBright,
      contrastText: '#ffffff',
    },
    secondary: {
      main: tealBright,
      contrastText: '#042f2e',
    },
    background: {
      default: surface,
      paper,
    },
    text: {
      primary: ink,
      secondary: '#5a6b7d',
    },
    divider: 'rgba(11, 31, 51, 0.09)',
    success: { main: '#0d9488' },
    warning: { main: '#b45309' },
    error: { main: '#b91c1c' },
    info: { main: '#0369a1' },
  },
  typography: {
    fontFamily: '"Plus Jakarta Sans", "Segoe UI", sans-serif',
    h1: {
      fontFamily: '"Fraunces", Georgia, serif',
      fontWeight: 700,
      letterSpacing: '-0.03em',
    },
    h2: {
      fontFamily: '"Fraunces", Georgia, serif',
      fontWeight: 700,
      letterSpacing: '-0.02em',
    },
    h3: {
      fontFamily: '"Fraunces", Georgia, serif',
      fontWeight: 700,
      letterSpacing: '-0.02em',
    },
    h4: {
      fontFamily: '"Fraunces", Georgia, serif',
      fontWeight: 700,
      letterSpacing: '-0.02em',
    },
    h5: {
      fontFamily: '"Fraunces", Georgia, serif',
      fontWeight: 650,
      letterSpacing: '-0.015em',
    },
    h6: {
      fontFamily: '"Plus Jakarta Sans", "Segoe UI", sans-serif',
      fontWeight: 650,
      letterSpacing: '-0.01em',
    },
    subtitle1: { fontWeight: 600 },
    button: {
      fontWeight: 600,
      letterSpacing: '-0.01em',
    },
    body1: {
      lineHeight: 1.65,
    },
    body2: {
      lineHeight: 1.6,
    },
  },
  shape: {
    borderRadius: 12,
  },
  shadows: [
    'none',
    '0 1px 2px rgba(7, 21, 37, 0.04)',
    '0 2px 8px rgba(7, 21, 37, 0.05)',
    '0 4px 16px rgba(7, 21, 37, 0.06)',
    '0 8px 28px rgba(7, 21, 37, 0.07)',
    '0 12px 36px rgba(7, 21, 37, 0.08)',
    '0 16px 48px rgba(7, 21, 37, 0.09)',
    '0 20px 56px rgba(7, 21, 37, 0.1)',
    '0 24px 64px rgba(7, 21, 37, 0.11)',
    ...Array(16).fill('0 24px 64px rgba(7, 21, 37, 0.11)'),
  ],
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          backgroundImage:
            'radial-gradient(ellipse 120% 80% at 100% -20%, rgba(20, 184, 166, 0.07), transparent 50%), radial-gradient(ellipse 80% 50% at -10% 40%, rgba(11, 31, 51, 0.04), transparent 45%)',
          backgroundAttachment: 'fixed',
        },
      },
    },
    MuiButton: {
      defaultProps: {
        disableElevation: true,
      },
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 600,
          borderRadius: 10,
          paddingInline: 18,
        },
        contained: {
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 4px 14px rgba(15, 118, 110, 0.28)',
          },
        },
        sizeLarge: {
          paddingBlock: 12,
          fontSize: '0.95rem',
        },
      },
    },
    MuiPaper: {
      defaultProps: {
        elevation: 0,
      },
      styleOverrides: {
        root: {
          backgroundImage: 'none',
          border: '1px solid rgba(11, 31, 51, 0.08)',
        },
        rounded: {
          borderRadius: 14,
        },
      },
    },
    MuiCard: {
      defaultProps: {
        elevation: 0,
      },
      styleOverrides: {
        root: {
          border: '1px solid rgba(11, 31, 51, 0.08)',
          borderRadius: 14,
          transition: 'border-color 0.2s ease, box-shadow 0.2s ease',
          '&:hover': {
            borderColor: alpha(teal, 0.35),
            boxShadow: '0 8px 28px rgba(7, 21, 37, 0.06)',
          },
        },
      },
    },
    MuiTextField: {
      defaultProps: {
        variant: 'outlined',
      },
    },
    MuiOutlinedInput: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          backgroundColor: paper,
          '&:hover .MuiOutlinedInput-notchedOutline': {
            borderColor: alpha(navy, 0.28),
          },
          '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
            borderWidth: 1.5,
          },
        },
        notchedOutline: {
          borderColor: 'rgba(11, 31, 51, 0.14)',
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontSize: '0.72rem',
          fontWeight: 600,
          borderRadius: 8,
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          border: '1px solid transparent',
        },
        standardInfo: {
          borderColor: alpha('#0369a1', 0.18),
        },
        standardSuccess: {
          borderColor: alpha('#0d9488', 0.2),
        },
        standardWarning: {
          borderColor: alpha('#b45309', 0.2),
        },
        standardError: {
          borderColor: alpha('#b91c1c', 0.18),
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: 99,
          height: 7,
          backgroundColor: alpha(navy, 0.08),
        },
        bar: {
          borderRadius: 99,
        },
      },
    },
    MuiContainer: {
      styleOverrides: {
        root: {
          animation: 'sf-fade-in 0.45s ease both',
        },
      },
    },
  },
})

export default theme
