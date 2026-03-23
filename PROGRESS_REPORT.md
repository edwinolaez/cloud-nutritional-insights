# Cloud Nutritional Insights — Progress Report
**Date:** March 23, 2026
**Student:** Edwin Olaez — Southern Alberta Institute of Technology (SAIT)
**Project:** Cloud Nutritional Insights Dashboard

---

## Project Overview
A full-stack cloud-connected web application that visualizes nutritional data from a diet dataset, secured with OAuth authentication, and integrated with a live Azure Virtual Machine for cloud resource management.

---

## Tech Stack
| Layer | Technology |
|---|---|
| Backend | Python / Flask |
| Frontend | HTML, Tailwind CSS, Chart.js |
| Data | Pandas (All_Diets.csv) |
| Authentication | Google OAuth 2.0, GitHub OAuth |
| Cloud | Microsoft Azure (Azure for Students) |
| Azure SDK | azure-mgmt-compute, azure-mgmt-resource, azure-identity |
| Environment | python-dotenv (.env) |

---

## Features Completed

### Frontend (frontend/index.html)
- [x] Nutritional Insights Dashboard with Tailwind CSS styling
- [x] **Bar Chart** — Average macronutrients by diet type (Chart.js)
- [x] **Scatter Plot** — Protein vs Carbs relationship (Chart.js)
- [x] **Heatmap** — Nutrient correlations (Chart.js)
- [x] **Pie Chart** — Recipe distribution by diet type (Chart.js)
- [x] **Filters** — Search by diet type + dropdown filter
- [x] **Recipe Table** — Paginated results (20 per page, windowed pagination)
- [x] **API Interaction Buttons** — Get Insights, Get Recipes, Get Clusters
- [x] **Security & Compliance** panel (Encryption, Access Control, GDPR)
- [x] **OAuth Login Panel** — Google + GitHub login buttons
- [x] **2FA Verification Step** — 6-digit code prompt after OAuth
- [x] **Logged-in State** — Shows provider and user name, Logout button
- [x] **Cloud Resource Cleanup** — Real Azure VM status + deallocate with progress bar
- [x] **Toast Notifications** — Success/error popups

### Backend (app.py)
- [x] Flask app serving frontend and REST API
- [x] `/api/insights` — Average macros grouped by diet type
- [x] `/api/recipes` — Full recipe list with optional diet filter
- [x] `/api/auth/status` — Session-based auth check
- [x] `/api/auth/logout` — Session clear
- [x] `/auth/google` + `/auth/google/callback` — Full Google OAuth flow
- [x] `/auth/github` + `/auth/github/callback` — Full GitHub OAuth flow
- [x] `/api/azure/status` — Live Azure VM power state
- [x] `/api/azure/deallocate` — Stops and deallocates Azure VM (stops billing)
- [x] `/api/azure/resources` — Lists all resources in the Azure resource group

### Security
- [x] All secrets stored in `.env` (never committed to git)
- [x] `.gitignore` excludes `.env`
- [x] Google OAuth Client Secret rotated (old one deleted)
- [x] Flask secret key generated with `secrets.token_hex(32)`
- [x] CORS configured with credentials support

### Azure Setup
- [x] Azure for Students account (SAIT tenant)
- [x] Resource Group: `nutritional-insights-rg`
- [x] VM: `nutritional-insights-vm` (Ubuntu Server 24.04 LTS, B1s)
- [x] Azure CLI installed and authenticated locally
- [x] VM successfully deallocated via app (confirmed: 6 resources checked)

### OAuth Setup
- [x] Google OAuth App — Project: `crafty-by-mace` (Google Cloud Console)
  - Redirect URI: `http://127.0.0.1:5000/auth/google/callback`
- [x] GitHub OAuth App — `Nutritional Insights`
  - Redirect URI: `http://127.0.0.1:5000/auth/github/callback`
  - Open to all GitHub users

---

## Environment Variables Required (.env)
```
FLASK_SECRET_KEY=...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GITHUB_CLIENT_ID=...
GITHUB_CLIENT_SECRET=...
AZURE_SUBSCRIPTION_ID=...
AZURE_TENANT_ID=...
AZURE_RESOURCE_GROUP=nutritional-insights-rg
AZURE_VM_NAME=nutritional-insights-vm
```

---

## How to Run
```bash
# 1. Log into Azure CLI (required for VM management)
az login

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the app
python app.py

# 4. Open browser
# http://127.0.0.1:5000
```

---

## What's Left (Future Work)
- [ ] Deploy to a public cloud host (Render, Azure App Service, etc.)
- [ ] Update OAuth redirect URIs to production domain after deployment
- [ ] Add real TOTP-based 2FA (e.g. Authy/Google Authenticator)
- [ ] Add user database to persist login sessions
- [ ] Add VM start button (complement to the deallocate/cleanup)

---

## Demo Checklist
- [ ] Show charts loading from Flask API
- [ ] Filter recipes by diet type
- [ ] Login with GitHub OAuth
- [ ] Login with Google OAuth
- [ ] Show 2FA prompt and verify
- [ ] Click Clean Up Resources — show real Azure VM status
- [ ] Verify VM deallocated in Azure Portal
