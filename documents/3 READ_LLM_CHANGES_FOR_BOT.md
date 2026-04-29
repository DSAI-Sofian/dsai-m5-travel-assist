# 🔄 Adapting the Travel Assist Bot to Another LLM Provider

- [🔄 Adapting the Travel Assist Bot to Another LLM Provider](#-adapting-the-travel-assist-bot-to-another-llm-provider)
  - [Purpose](#purpose)
- [🧠 Current Architecture](#-current-architecture)
- [📁 Files That Must Be Modified](#-files-that-must-be-modified)
  - [1. Create `app/llm/client.py` (Recommended Future Abstraction Layer)](#1-create-appllmclientpy-recommended-future-abstraction-layer)
    - [Purpose](#purpose-1)
    - [Current Responsibility](#current-responsibility)
    - [Typical Current Logic](#typical-current-logic)
    - [What To Change](#what-to-change)
- [🔧 Example Provider Changes](#-example-provider-changes)
  - [Anthropic Claude](#anthropic-claude)
  - [Google Gemini](#google-gemini)
  - [Ollama Local Models](#ollama-local-models)
  - [Groq](#groq)
- [📁 2. Create `app/settings.py` or Environment Config File](#-2-create-appsettingspy-or-environment-config-file)
    - [Purpose](#purpose-2)
    - [Current Environment Variables](#current-environment-variables)
    - [Example Replacement](#example-replacement)
- [📁 3. `requirements.txt`](#-3-requirementstxt)
    - [Purpose](#purpose-3)
    - [Current Example](#current-example)
    - [Replace With](#replace-with)
- [📁 4. Agent Files (Usually Minimal Changes)](#-4-agent-files-usually-minimal-changes)
    - [Usually No Major Changes Needed](#usually-no-major-changes-needed)
- [📁 5. `app/orchestrator/workflow.py`](#-5-apporchestratorworkflowpy)
    - [Usually No Changes Needed](#usually-no-changes-needed)
- [📁 6. `app/api.py`](#-6-appapipy)
    - [Usually No Changes Needed](#usually-no-changes-needed-1)
- [📁 7. `.env`](#-7-env)
    - [Must Be Updated](#must-be-updated)
- [🔁 Recommended Abstraction Strategy](#-recommended-abstraction-strategy)
- [🧩 Example Future Architecture](#-example-future-architecture)
- [⚠️ Important Compatibility Notes](#️-important-compatibility-notes)
  - [1. JSON Reliability](#1-json-reliability)
- [⚠️ 2. Token Limits](#️-2-token-limits)
- [⚠️ 3. Cost vs Quality](#️-3-cost-vs-quality)
- [🏠 Local Model Deployment Notes](#-local-model-deployment-notes)
- [🔐 Security Reminder](#-security-reminder)
- [✅ Minimum Files Usually Required](#-minimum-files-usually-required)
- [🎯 Recommended Simplest Migration Path](#-recommended-simplest-migration-path)
  - [Replace Only](#replace-only)
  - [Alternatively](#alternatively)


## Purpose

This section explains which files must be modified if another developer wishes to use a different Large Language Model (LLM) provider instead of OpenAI.

Examples:
- Anthropic Claude
- Google Gemini
- Groq
- Ollama (local models)
- LM Studio
- Azure OpenAI
- Hugging Face Inference API
- Mistral API

The Travel Assist Bot architecture already separates:
- orchestration logic
- prompt generation
- execution flow
- LLM API calls

Therefore, only a small number of files require modification.

---

# 🧠 Current Architecture

Current flow:

```text
Telegram
   ↓
FastAPI Backend
   ↓
Workflow Orchestrator
   ↓
Planner / Reviewer / Executor Agents
   ↓
OpenAI Client
```

Only the final layer is provider-specific.

---

# 📁 Files That Must Be Modified

## 1. Create `app/llm/client.py` (Recommended Future Abstraction Layer)

**Note:**

This file does not currently exist in the project repository.

It is recommended as a future architecture improvement if another developer wishes to support multiple LLM providers cleanly.

### Purpose

Centralized LLM API client wrapper.

### Current Responsibility

Usually contains:

* OpenAI client initialization
* API key handling
* model selection
* chat completion calls

### Typical Current Logic

Example:

```python
from openai import OpenAI

client = OpenAI(api_key=OPENAI_API_KEY)

response = client.chat.completions.create(...)
```

### What To Change

Replace:

* OpenAI SDK
* OpenAI request format
* OpenAI response parsing

with:

* Claude SDK
* Gemini SDK
* Ollama HTTP calls
* Groq client
* etc.

---

# 🔧 Example Provider Changes

## Anthropic Claude

Replace:

```python
from openai import OpenAI
```

with:

```python
from anthropic import Anthropic
```

---

## Google Gemini

Replace with:

```python
import google.generativeai as genai
```

---

## Ollama Local Models

Replace with HTTP request:

```python
http://localhost:11434/api/generate
```

---

## Groq

Replace with:

```python
from groq import Groq
```

---

# 📁 2. Create `app/settings.py` or Environment Config File

### Purpose

Stores:

* API keys
* model names
* provider settings

### Current Environment Variables

```env
OPENAI_API_KEY=
OPENAI_MODEL=
```

### Example Replacement

For Claude:

```env
ANTHROPIC_API_KEY=
CLAUDE_MODEL=claude-3-sonnet
```

For Gemini:

```env
GEMINI_API_KEY=
GEMINI_MODEL=gemini-1.5-pro
```

For Ollama:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

---

# 📁 3. `requirements.txt`

### Purpose

Dependency management.

### Current Example

```text
openai
```

### Replace With

| Provider     | Dependency                    |
| ------------ | ----------------------------- |
| Claude       | `anthropic`                   |
| Gemini       | `google-generativeai`         |
| Groq         | `groq`                        |
| Ollama       | usually only `httpx` required |
| Azure OpenAI | still uses `openai`           |

---

# 📁 4. Agent Files (Usually Minimal Changes)

Possible files:

```text
app/agents/planner.py
app/agents/reviewer.py
app/agents/executor.py
```

### Usually No Major Changes Needed

Because these files typically:

* build prompts
* call shared client wrapper

If architecture is clean, only:

* model names
* token limits
* response extraction

may require adjustment.

---

# 📁 5. `app/orchestrator/workflow.py`

### Usually No Changes Needed

Workflow orchestration is provider-independent.

This file handles:

* routing
* continuity
* ranking
* state management
* trace logging

and should remain unchanged.

---

# 📁 6. `app/api.py`

### Usually No Changes Needed

FastAPI endpoints are provider-independent.

Only modify if:

* adding provider selection endpoint
* exposing model choice to API caller

---

# 📁 7. `.env`

### Must Be Updated

Remove:

```env
OPENAI_API_KEY=
```

and replace with provider-specific variables.

---

# 🔁 Recommended Abstraction Strategy

Best practice:

Create:

```text
app/llm/
```

with:

```text
base.py
openai_client.py
claude_client.py
gemini_client.py
ollama_client.py
factory.py
```

Then use:

```python
get_llm_client()
```

This allows:

* easy provider switching
* benchmarking
* failover models
* hybrid routing

without changing agent logic.

---

# 🧩 Example Future Architecture

```text
Telegram
   ↓
Workflow
   ↓
LLM Factory
   ├── OpenAI
   ├── Claude
   ├── Gemini
   ├── Groq
   └── Ollama
```

---

# ⚠️ Important Compatibility Notes

## 1. JSON Reliability

Some models are weaker at:

* structured JSON
* strict schema compliance

Reviewer and ranking agents rely heavily on structured outputs.

Recommended:

* GPT-4.x
* Claude Sonnet
* Gemini Pro
* Groq Llama 3.1 70B

Avoid very small models for reviewer/ranking stages.

---

# ⚠️ 2. Token Limits

Long itinerary generation requires:

* sufficient context window
* adequate output token limit

Small local models may:

* truncate itineraries
* produce malformed JSON
* hallucinate structure

---

# ⚠️ 3. Cost vs Quality

| Provider       | Typical Strength               |
| -------------- | ------------------------------ |
| OpenAI GPT-4.x | strongest structured reasoning |
| Claude Sonnet  | excellent natural language     |
| Gemini Pro     | strong multimodal ecosystem    |
| Groq           | extremely fast inference       |
| Ollama local   | privacy + offline use          |
| Mistral local  | lightweight local deployment   |

---

# 🏠 Local Model Deployment Notes

For Ollama:

Install:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Run model:

```bash
ollama run llama3
```

Test:

```bash
curl http://localhost:11434/api/tags
```

---

# 🔐 Security Reminder

Never commit API keys into GitHub.

Use:

* `.env`
* Render environment variables
* Docker secrets
* cloud secret managers

---

# ✅ Minimum Files Usually Required

For most provider migrations:

| File                | Required?  |
| ------------------- | ---------- |
| `app/llm/client.py` | YES        |
| `.env`              | YES        |
| `requirements.txt`  | YES        |
| agent files         | MAYBE      |
| workflow.py         | usually NO |
| api.py              | usually NO |

---

# 🎯 Recommended Simplest Migration Path

If another developer wants the easiest migration:

## Replace Only

```text
1. app/llm/client.py
2. requirements.txt
3. .env
```

and keep the rest of the architecture unchanged.

That is usually sufficient if the project already uses:

* centralized client wrapper
* provider-independent orchestration
* clean agent abstraction

## Alternatively

For experienced developers,

Run:

```
grep -R "OpenAI" .
```

or:

```
grep -R "chat.completions" .
```

Then modify whichever files currently contain:

* OpenAI imports
* API calls
* model names