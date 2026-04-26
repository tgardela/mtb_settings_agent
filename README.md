# MTB Settings Agent

An AI-powered agent that helps you set up and tune your MTB and E-MTB bikes according to your personal needs. Ask questions about suspension setup, tire pressure, geometry, and more — and get personalized recommendations powered by Claude AI and real-time web search.

**Tech stack:** Python, FastAPI, Anthropic Claude, Tavily, Railway

---

## Table of Contents

1. [Getting API Keys](#1-getting-api-keys)
2. [GitHub Setup](#2-github-setup)
3. [Railway Deployment](#3-railway-deployment)
4. [Automated Development Workflow](#4-automated-development-workflow)
5. [Available Labels](#5-available-labels)

---

## 1. Getting API Keys

You'll need two API keys to run this project: one for the AI (Anthropic) and one for web search (Tavily).

### Anthropic API Key

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up and verify your phone number
3. In the left sidebar, click **API Keys**
4. Click **Create Key**, give it a name, and copy it — it's only shown once
5. Your key starts with `sk-ant-...`

> **Note:** Anthropic provides free starter credits, but a credit card is required after they run out.

### Tavily API Key

1. Go to [tavily.com](https://tavily.com)
2. Sign up for free — no credit card needed
3. Your key will be on the dashboard
4. Your key starts with `tvly-...`

> **Free tier:** 1,000 searches per month

---

## 2. GitHub Setup

### Create a Repository

1. Create a new repository on GitHub (or fork this one)
2. Open **Codespaces** from the repository (click the green **Code** button → **Codespaces** tab)

### Add API Keys as Secrets

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** and add each of the following:
   - `ANTHROPIC_API_KEY` — your Anthropic key (`sk-ant-...`)
   - `TAVILY_API_KEY` — your Tavily key (`tvly-...`)

### Install the Claude GitHub App

1. Go to [github.com/apps/claude](https://github.com/apps/claude)
2. Install the app on your repository

### Enable Workflow Permissions

1. Go to **Settings** → **Actions** → **General**
2. Scroll down to **Workflow permissions**
3. Select **Read and write permissions**
4. Check **Allow GitHub Actions to create and approve pull requests**
5. Click **Save**

---

## 3. Railway Deployment

Railway is used to host the FastAPI server so it's accessible from anywhere.

1. Go to [railway.app](https://railway.app)
2. Sign up with your GitHub account
3. Click **New Project** → **Deploy from GitHub repo**
4. Select your repository
5. Go to the **Variables** tab and add:
   - `ANTHROPIC_API_KEY`
   - `TAVILY_API_KEY`
6. Railway will automatically deploy your app and provide a public URL

### Finding Your Public URL

1. In your Railway project, go to **Settings** → **Networking**
2. Click **Generate Domain**
3. Copy the URL — this is where your agent is accessible

---

## Development Setup

After cloning the repo, install the pre-commit hooks to enable automatic linting and testing before every commit:

```bash
pip install pre-commit
pre-commit install
```

From now on, every `git commit` will automatically:
- Run **ruff** to lint and auto-fix Python files
- Run **pytest** to make sure all tests pass

A commit will be blocked if any test fails.

---

## 4. Automated Development Workflow

This project uses a GitHub Issues → Claude Code → PR → Railway pipeline to automate development.

### How it works

```
Create Issue → Add Label → Claude Makes Changes → Open PR → Merge → Auto-Deploy
```

1. **Create an issue** describing the change or feature you need
2. **Add the `work_in_progress` label** to trigger Claude Code
3. **Claude reads the issue**, makes the required code changes, and opens a Pull Request automatically
4. **Review the PR** — check the changes look correct
5. **Merge the PR** — Railway automatically deploys the updated code

This means you can describe changes in plain English, and the AI handles the implementation.

---

## 5. Available Labels

Use these labels on issues and pull requests to control the workflow:

| Label | Purpose |
|-------|---------|
| `work_in_progress` | Triggers Claude to start working on the issue |
| `ready_for_review` | PR is ready for human review |
| `blocked` | Needs human input before work can continue |
| `needs_clarification` | Claude needs more information to proceed |
| `bug` | Something is broken and needs fixing |
| `feature` | New functionality to be added |
| `improvement` | Improve or enhance existing code |
| `docs` | Documentation changes |
| `chore` | Maintenance and cleanup tasks |
