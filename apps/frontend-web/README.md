# Gallery — Frontend Web

The Next.js frontend for Gallery, an AI-powered event photo delivery SaaS platform. Guests scan a QR code, upload a selfie, and instantly receive every photo of themselves from the event — powered by FAISS vector similarity search on the backend.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | [Next.js 15](https://nextjs.org/) (App Router, Turbopack) |
| Language | TypeScript (strict, no `any`) |
| Styling | Tailwind CSS v3 |
| Font | Inter (via `next/font/google`) |
| HTTP Client | Axios (with JWT interceptors) |
| Server State | TanStack React Query v5 |
| Client State | Zustand v5 (persisted to localStorage) |
| Auth | Google OAuth → JWT (access + refresh tokens via cookie/localStorage) |
| Payments | Razorpay (loaded via CDN `<Script>`) |
| File Upload | react-dropzone |
| Toasts | react-hot-toast |
| Icons | lucide-react |
| QR Code | qrcode.react |
| Utilities | clsx |
| Middleware | Next.js Edge Middleware (route protection) |

---

## Project Structure

```
src/
├── app/
│   ├── page.tsx                          # Landing page
│   ├── layout.tsx                        # Root layout (Inter font, providers, Razorpay script)
│   ├── globals.css                       # Global styles & design tokens
│   ├── (auth)/
│   │   └── login/page.tsx               # Google OAuth sign-in page
│   ├── auth/
│   │   └── callback/                    # OAuth redirect callback handler
│   ├── dashboard/
│   │   ├── layout.tsx                   # Sidebar navigation layout
│   │   ├── page.tsx                     # Dashboard overview (stats)
│   │   ├── events/
│   │   │   ├── page.tsx                 # Event list with TanStack Query
│   │   │   ├── new/page.tsx             # Create new event form
│   │   │   └── [eventId]/
│   │   │       ├── page.tsx             # Event detail (stats, actions)
│   │   │       ├── uploads/page.tsx     # Bulk photo upload with react-dropzone
│   │   │       └── qr/page.tsx          # QR code generation (qrcode.react)
│   │   ├── organization/page.tsx        # Org info & team members
│   │   ├── billing/page.tsx             # Razorpay subscription plans
│   │   └── members/                     # RBAC team member management
│   └── g/
│       └── [token]/page.tsx             # Guest QR scan → selfie upload → FAISS search results
├── components/
│   ├── providers.tsx                    # TanStack QueryClient + react-hot-toast
│   └── ui/                              # Reusable primitives (Button, Card, Badge, Input, Spinner)
├── lib/
│   ├── api.ts                           # Axios instance + JWT interceptors + token helpers
│   └── utils.ts                         # cn(), formatBytes(), formatDate(), timeAgo(), storagePercent(), truncate()
├── store/
│   └── auth.ts                          # Zustand auth store (persisted: user, tokens, isAuthenticated)
├── types/
│   └── index.ts                         # All shared TypeScript interfaces (User, Event, Image, QRCode, SearchResult…)
└── middleware.ts                        # Edge middleware: protects /dashboard, redirects authenticated users away from /auth/*
```

---

## Key Architectural Decisions

- **No `process.env` directly**: `NEXT_PUBLIC_API_URL` is consumed via `dotenv-cli` which injects the root `.env` before Next.js starts.
- **Proxy rewrites**: `next.config.ts` rewrites `/api/backend/:path*` → `NEXT_PUBLIC_API_URL/api/v1/:path*` to avoid CORS issues in development.
- **Auth strategy**: Google OAuth is handled server-side by the backend (`/api/v1/auth/google/callback`). The frontend receives a JWT pair and stores them in Zustand (persisted) + localStorage. The middleware checks for `access_token` cookie for SSR-safe route protection.
- **AI/FAISS awareness**: The frontend is aware of `faiss_index_path`, `faiss_pos`, and `index_version` on `Event` and `Image` types — these reflect the backend FAISS vector index state and are displayed in the event detail UI.
- **Guest flow**: The `/g/[token]` route is excluded from middleware auth checks. It resolves the QR token, collects a selfie via react-dropzone, posts to the backend `/search/selfie/:eventId`, and polls for FAISS-matched results.

---

## Setup

### Prerequisites

- Node.js `>=24.0.0` (use `nvm use` — `.nvmrc` is at the monorepo root)

### 1. Environment Variables

This project uses the **root `.env`** as its single source of truth. The `dev`/`build`/`start` scripts load it automatically via `dotenv-cli`. You do not need to manually copy variables.

To override a specific variable locally, add it to `.env.local` in this directory.

Required root `.env` variables for this app:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=...
```

### 2. Install dependencies

```bash
nvm use          # switches to Node 24.14.0 using root .nvmrc
npm install
```

### 3. Run dev server

```bash
npm run dev      # loads ../../.env + .env.local, then starts Next.js with Turbopack
```

### 4. Build

```bash
npm run build
npm run start
```

### 5. Type-check

```bash
npm run type-check
```

---

## Commands

| Command | Description |
|---|---|
| `npm run dev` | Start dev server (Turbopack) with root `.env` injected |
| `npm run build` | Production build with root `.env` injected |
| `npm run start` | Start production server |
| `npm run lint` | Run ESLint |
| `npm run type-check` | TypeScript strict check (no emit) |
