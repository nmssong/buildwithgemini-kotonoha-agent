# Kotonoha (言の葉) - Self-Hosted & Personal Antigravity Setup Guide

This guide explains how to set up, run, and continue developing your Kotonoha Translation Agent on your personal device and Google Cloud / Antigravity account, as well as how to maintain session continuity.

---

## 1. Prerequisites
- **Git** & **Python 3.11+**
- **uv** (recommended for ADK dependency management): `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **Google Cloud SDK (`gcloud`)**: https://cloud.google.com/sdk/docs/install
- **Google Antigravity IDE / CLI (`agy`)**

---

## 2. Clone Your Repository
```bash
git clone https://github.com/nmssong/buildwithgemini-kotonoha-agent.git
cd buildwithgemini-kotonoha-agent
```
Open this folder as your workspace in Antigravity.

---

## 3. Google Cloud Setup & Authentication
Authenticate with your personal Google Cloud account:
```bash
# 1. Login with your personal account
gcloud auth login
gcloud auth application-default login

# 2. Select or create your personal GCP Project
gcloud config set project YOUR_PERSONAL_GCP_PROJECT_ID

# 3. Enable required Google Cloud APIs
gcloud services enable \
  aiplatform.googleapis.com \
  firestore.googleapis.com \
  storage.googleapis.com
```

---

## 4. Cloud Infrastructure Configuration

### A. Create Cloud Storage Bucket
Create a public bucket for exported chapters and images:
```bash
# Create bucket (pick a unique name)
gcloud storage buckets create gs://kotonoha-novels-YOUR_PROJECT_ID --location=us-central1

# Make bucket objects readable publicly
gcloud storage buckets add-iam-policy-binding gs://kotonoha-novels-YOUR_PROJECT_ID \
  --member=allUsers \
  --role=roles/storage.objectViewer
```

### B. Create Firestore Database
If you don't already have Firestore in (Native mode):
```bash
gcloud firestore databases create --location=nam5 --type=firestore-native
```

### C. Update Hardcoded Project Variables
In `test-agent/app/agent.py` and `test-agent/seed_glossary.py`:
- Replace `"qwiklabs-gcp-04-f382b3dbe525"` with `"YOUR_PERSONAL_GCP_PROJECT_ID"`.
- Replace `"kotonoha-novels-qwiklabs-gcp-04-f382b3dbe525"` with `"kotonoha-novels-YOUR_PROJECT_ID"`.

Seed initial glossary terms into Firestore:
```bash
cd test-agent
python3 seed_glossary.py
```

---

## 5. Running Kotonoha Locally

### Option 1: ADK Web Playground
```bash
cd test-agent
uv run adk web . --port 8080 --reload_agents
```
Then open `http://localhost:8080` in your browser.

### Option 2: Custom FastAPI Dialogue Frontend
```bash
cd test-agent/frontend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 main.py
```
Then open `http://localhost:8080` (or the port specified by `$PORT`).

---

## 6. Deploying to Agent Platform (Agent Runtime)
When you are ready to deploy your agent into your personal Vertex AI Agent Platform:
```bash
cd test-agent
agents-cli deploy -d agent_runtime --project YOUR_PERSONAL_GCP_PROJECT_ID --region us-central1
```
Grant your deployed agent's service account permissions:
```bash
# Get service account from deployment output, e.g.: service-<NUM>@gcp-sa-aiplatform-re.iam.gserviceaccount.com
gcloud projects add-iam-policy-binding YOUR_PERSONAL_GCP_PROJECT_ID \
  --member="serviceAccount:YOUR_AGENT_SERVICE_ACCOUNT" \
  --role="roles/datastore.user"

gcloud storage buckets add-iam-policy-binding gs://kotonoha-novels-YOUR_PROJECT_ID \
  --member="serviceAccount:YOUR_AGENT_SERVICE_ACCOUNT" \
  --role="roles/storage.objectAdmin"
```

---

## 7. Session Continuity in Antigravity

To ensure full continuity when starting a new session on your personal device:

1. **Automatic Context**: Antigravity automatically indexes `project_brief.md`, `README.md`, and all code under `test-agent/`.
2. **First Prompt**: In your new Antigravity session, simply prompt:
   > *"I am continuing development on Kotonoha from my previous session. Please inspect `project_brief.md`, `CONTINUITY_INSTRUCTIONS.md`, and `test-agent/app/agent.py` to familiarize yourself with the tools, Firestore glossary, and frontend before we begin."*
3. **Persisting Rules**: Use Antigravity's `/learn` slash command to store any personal development guidelines or styling rules directly into your user config.
