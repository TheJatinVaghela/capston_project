# Host SupportFlow from your laptop

Share a public link so friends can sign up, sign in, and use the app while **your laptop** runs the database, Flask API, and Ollama AI. Stripe stays in **test mode**.

## How it works

```
Friend's browser  →  public tunnel URL  →  your laptop :5000
                                         ├─ React UI (built files)
                                         ├─ SQLite database
                                         └─ Ollama (local AI)
```

Your laptop must stay awake with Flask + Ollama running. When you close the lid or kill the tunnel, the link dies.

## One-time setup

### 1. Build the frontend

```powershell
cd d:\customer-service-chatbot\frontend-react
npm install
npm run build
```

This creates `frontend-react/dist/`. Flask serves that folder on the same port as the API.

### 2. Start Ollama

```powershell
ollama serve
```

In another terminal, confirm a model is available (e.g. `ollama pull mistral`).

### 3. Point Flask at the public URL

After you start the tunnel (step 5), copy the `https://…` URL and put it in `backend/.env`:

```env
HOST=0.0.0.0
PORT=5000
FRONTEND_URL=https://YOUR-TUNNEL-URL
PUBLIC_BASE_URL=https://YOUR-TUNNEL-URL
ALLOW_TUNNEL_ORIGINS=true
```

Keep your existing Stripe **test** keys. `FRONTEND_URL` is used for Stripe Checkout success/cancel redirects, so it must be the tunnel URL (not `localhost:5173`).

### 4. Start the backend

```powershell
cd d:\customer-service-chatbot\backend
python app.py
```

You should see `SPA build: ready` and `Server: http://0.0.0.0:5000`.

### 5. Open a tunnel to port 5000

Pick one:

**Cloudflare (no account required for a quick try)**

```powershell
# Install once: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
cloudflared tunnel --url http://127.0.0.1:5000
```

**ngrok**

```powershell
ngrok http 5000
```

Copy the printed `https://…` URL → update `.env` → **restart** `python app.py`.

### 6. Share the link

Send people: `https://YOUR-TUNNEL-URL`

They can open the landing page, sign up, log in, manage businesses, and use Stripe **test** cards (e.g. `4242 4242 4242 4242`).

You do **not** need `npm run dev` while sharing — the built UI is served by Flask.

## Stripe test + webhooks

- Use Stripe **test** keys only.
- After checkout, the app can confirm via `/billing/confirm`. For live webhook events while tunneling:

```powershell
stripe listen --forward-to localhost:5000/billing/webhook
```

Paste the `whsec_…` into `STRIPE_WEBHOOK_SECRET` in `.env`.

## Local development (no sharing)

Keep using:

- `HOST=127.0.0.1`
- `FRONTEND_URL=http://localhost:5173`
- `python app.py` + `npm run dev` as before

## Checklist before you share

| Check | Why |
|-------|-----|
| Laptop plugged in / sleep disabled | Tunnel + AI die if the machine sleeps |
| `npm run build` after UI changes | Tunnel serves the built files, not Vite |
| `FRONTEND_URL` = tunnel URL | Stripe redirects and CORS |
| `ollama serve` running | Chat replies need local AI |
| Only share with people you trust | Anyone with the link can hit your laptop |

## Limits (honest)

This is great for demos and classmates — not a permanent public SaaS. For a real launch you would move the API + DB to a cloud host and keep Ollama (or another model) somewhere that stays online 24/7.
