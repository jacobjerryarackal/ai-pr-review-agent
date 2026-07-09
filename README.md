# AI Pull Request Review Agent

An autonomous, multi-agent orchestrator designed to review pull requests, identify security vulnerabilities, evaluate code quality, audit test coverage, and update documentation before code changes are merged. Complete with a real-time Next.js monitoring dashboard, Human-in-the-Loop (HITL) approval controls, and granular budget/cost-control gates.

---

## Table of Contents
1. [Introduction & Purpose](#1-introduction--purpose)
2. [Key Features](#2-key-features)
3. [Project Directory Structure](#3-project-directory-structure)
4. [Getting Started & Setup](#4-getting-started--setup)
5. [Running the Application](#5-running-the-application)
6. [Testing & Verification](#6-testing--verification)
7. [Future Scope & Roadmap](#7-future-scope--roadmap)

---

## 1. Introduction & Purpose

Code review is one of the most critical stages in the software development lifecycle, yet it is often a bottleneck. Manual reviews are slow, and developers can miss subtle security bugs or style regressions under pressure. 

The **AI Pull Request Review Agent** addresses these pain points by deploying specialized, isolated LLM agents configured to run reviews concurrently. Using a structured **LangGraph orchestration engine**, the agent aggregates findings, evaluates overall confidence, and enforces cost policies.

### Why This Architecture?
* **Modular Agent Separation**: Instead of a single LLM trying to inspect everything, separate agents focus strictly on their domains (Security, Quality, Testing, Docs) to reduce hallucination and improve accuracy.
* **Human-in-the-Loop (HITL)**: If the agent's confidence score drops below the threshold, reviews are held in a pending queue, allowing a human operator to approve, request changes, or edit findings before they are posted to GitHub.
* **Cost Controls**: Enforces daily caps on LLM spends (via `BudgetGuard`), preventing runaway billing if a repository experiences a burst of PR commits.

---

## 2. Key Features

* **Multi-Agent Evaluation**:
  * 🔒 **Security Agent**: Scans for OWASP Top 10, credential leakage, and injection points (uses reasoning-heavy models).
  * ⚙️ **Quality Agent**: Inspects code complexity, structure, patterns, and style guidelines.
  * 🧪 **Test Coverage Agent**: Assesses whether added/changed lines have corresponding test cases.
  * 📝 **Docs Agent**: Checks if docstrings, comments, and README structures are kept up-to-date.
* **LangGraph Orchestrator**: Manages state transitions, aggregates individual agent verdicts, and computes overall confidence.
* **HITL Decision Panel**: Provides a clean UI for operators to audit escalated PRs, resolve disputes, and submit final reviews.
* **Token & Cost Attribution**: Displays daily and monthly spend figures broken down by model type and agent type.

---

## 3. Project Directory Structure

The project is structured clean-architecture style, separating delivery adapters (API endpoints, Webhooks) from internal use cases and entity models:

```
ai-pr-review-agent/
├── backend/                    # Python FastAPI application
│   ├── agents/                 # Specialized agent classes (Security, Quality, etc.)
│   ├── api/                    # Versioned REST routers (reviews, hitl, economics)
│   ├── auth/                   # API key gating and middleware
│   ├── config/                 # Pydantic Settings management
│   ├── core/                   # Orchestrator core and exceptions
│   ├── database/               # Structured database mappings (Postgres ORM & repos)
│   ├── economics/              # Spend rollups and BudgetGuard limits
│   ├── integrations/           # GitHub REST clients and connectors
│   ├── job_queue/              # ARQ background task workers
│   ├── memory/                 # Ephemeral state caches (Redis) and Vector indexes (Qdrant)
│   ├── models/                 # Pure domain entity schemas
│   ├── observability/          # Structured JSON logging, alerts, and tracing
│   ├── orchestrator/           # LangGraph nodes and execution graph
│   └── main.py                 # FastAPI application entry point
├── frontend/                   # Next.js 16 (Turbopack) Dashboard app
│   ├── src/
│   │   ├── app/                # Page routes (Dashboard, reviews, hitl, economics)
│   │   ├── components/         # Premium design system modules (cards, forms, chips)
│   │   └── lib/                # Shared types, SWR providers, and API clients
│   └── package.json            # Frontend dependencies
├── scripts/                    # Database seeding and demo scripts
└── pyproject.toml              # Python environment & Hatchling build definition
```

---

## 4. Getting Started & Setup

### Prerequisites
* **Python**: `3.11` or higher (virtual environments managed via `uv`)
* **Node.js**: `18.x` or higher
* **Infrastructure**: Access to a PostgreSQL instance, Redis server, and optionally Qdrant (local or cloud).

### A. Environment Configuration

1. **Backend Environment**: Copy `.env.example` in the root directory to `.env` and fill in the values:
   ```ini
   GITHUB_TOKEN=your_github_token
   GITHUB_WEBHOOK_SECRET=your_webhook_secret
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   DATABASE_URL=postgresql+asyncpg://user:pass@host:port/dbname?ssl=require
   REDIS_URL=redis://localhost:6379/0
   QDRANT_URL=http://localhost:6333
   ```

2. **Frontend Environment**: Create `frontend/.env.local` and add:
   ```ini
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   NEXT_PUBLIC_API_KEY=dev-secret-api-key
   ```

---

## 5. Running the Application

### Running the Backend
1. Initialize the Python virtual environment and install packages:
   ```bash
   uv sync
   ```
2. Launch the FastAPI server:
   ```bash
   # Set environment variables for required parameters
   $env:GITHUB_TOKEN="dummy"
   $env:OPENAI_API_KEY="dummy"
   $env:ANTHROPIC_API_KEY="dummy"
   $env:GITHUB_WEBHOOK_SECRET="dummy"
   uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Running the Frontend
1. Navigate to the `frontend` folder and install dependencies:
   ```bash
   cd frontend
   npm install --legacy-peer-deps
   ```
2. Start the Turbopack Next.js development server:
   ```bash
   npm run dev
   ```
3. Open `http://localhost:3000` in your browser.

---

## 6. Testing & Verification

### Independent Backend Verification
* **Check Liveness**:
  ```bash
  curl http://localhost:8000/health/live
  ```
* **Verify Infrastructure Status**:
  ```bash
  curl http://localhost:8000/health
  ```
* **Seeding Database**: To run database table migration and inject mock PR records:
  ```bash
  $env:GITHUB_TOKEN="dummy" ; $env:OPENAI_API_KEY="dummy" ; $env:ANTHROPIC_API_KEY="dummy" ; $env:GITHUB_WEBHOOK_SECRET="dummy" ; uv run python scripts/seed_demo_review.py
  ```

---

## 7. Future Scope & Roadmap

1. **Alembic Database Migrations**: Replace the startup `create_all_tables()` hook with versioned, reversible Alembic database migrations for production schema changes.
2. **GitLab & Bitbucket Integration**: Extend the `integrations/` delivery layer to support other Git platforms natively, standardizing pull request comment posting.
3. **Granular RAG Context Retrieval**: Implement deeper codebase context retrieval using semantic code-chunk indexing in Qdrant, feeding agents relevant implementation files beyond raw diffs.
4. **JWT & Role-Based Access Control (RBAC)**: Upgrade backend auth from simple API key headers to secure JWT authentication, mapping actions to user roles (Admin, Reviewer, Operator).
5. **LLM Fine-tuning**: Fine-tune domain-specific models on historic pull-request reviews to replace general-purpose LLMs, reducing latencies and cost.
