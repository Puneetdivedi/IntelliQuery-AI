# Deployment Guide

IntelliQuery AI is designed to be easily deployed on **Streamlit Cloud** (free community tier).

## Prerequisites

1. **GitHub Account** with the repository pushed.
2. **Streamlit Cloud Account** (sign up at streamlit.io).
3. **Groq Cloud API Key**.
4. **Supabase Database** (or any cloud PostgreSQL).

## Step-by-Step Deployment

### 1. Database Setup (Supabase)

1. Create a new project on [Supabase.com](https://supabase.com).
2. Go to **Project Settings > Database** and copy the Connection String (URI).
   - Mode: **Session** (ensure port is 5432).
   - Example: `postgresql://postgres.[ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres`
3. Allows access from all IPs (0.0.0.0/0) or Streamlit Cloud IPs.

### 2. Configure Streamlit Cloud

1. Login to **Streamlit Cloud**.
2. Click **"New app"**.
3. Select your repository, branch (`main`), and main file path (`app.py`).
4. Click **"Advanced Settings"** to add secrets.

### 3. Environment Secrets

Add the following to the Streamlit Secrets TOML area:

```toml
GROQ_API_KEY = "gsk_..."
DATABASE_URL = "postgresql://..."
ENVIRONMENT = "production"
```

### 4. Deploy

Click **"Deploy!"**. Streamlit will install requirements from `requirements.txt` and `runtime.txt`.

### 5. Initialize Database (First Run)

The app is configured to expect an existing schema. You can run the setup scripts locally pointing to the cloud DB, or you can add a temporary button in `app.py` to run `models.Base.metadata.create_all()` if you prefer lazy initialization.

**Recommended:** Run initialization locally:
```bash
# In your local terminal
export DATABASE_URL="postgresql://[your-supabase-url]"
python scripts/setup_database.py
python scripts/generate_sample_data.py
```

## Troubleshooting

- **Connection Errors:** Ensure Supabase is not pausing the project (free tier pauses after inactivity).
- **Missing Dependencies:** Check `requirements.txt`.
