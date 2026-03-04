# AI / Software Engineer Intern position at Dongzhou Technology

This is a interview task for Dongzhou Technology Internship.

## Install 


Insatall the repo:

```
git clone https://github.com/AslauAlexandru/Dongzhou-Tech-Internship

cd Dongzhou-Tech-Internship 
```

Install uv (if you don't have already installed):

```curl -LsSf https://astral.sh/uv/install.sh | sh```


Install using uv for project:

```
uv init
```

Optional: If is needed:
```
uv add package_name 
```

Optional: For uv lock file ```uv.lock``` (if you have the file after you clone the repo, you don't need to do ```uv lock ```):

```
uv lock 
```

For installation the existing packeges in ```pyproject.toml``` (after cloning the repo):

```
uv sync
```

## Ollama LLMs:

Ollama LLMs, Next- Get More Models
To use local LLM responses instead of fallbacks:

```
ollama pull mistral      # 4.7GB - Great quality
ollama pull neural-chat  # Better for instructions  
ollama pull orca2        # Larger but slower

```

Then update ```.env```:

```
OLLAMA_MODEL=mistral
```

Running It:

```

# Terminal 1: Start Ollama server
ollama serve

# Terminal 2: Run campaign
uv run main.py Stripe "ML Platform" #uv run python main.py Stripe "ML Platform"

# With custom model
OLLAMA_MODEL=mistral uv run main.py Google "Search" # OLLAMA_MODEL=mistral uv run python main.py Google "Search"

```


## LinkedIn Outreach Automation System

**Architecture & Workflow**:

INITIALIZE -> FIND_DECISION_MAKER -> SEND_CONNECTION -> WAIT_ACCEPTANCE

        | 
        to
        |  

FOLLOWUP -> WAIT_REPLY -> CREATE_TEAMS -> COMPLETED


**Core Design Decisions**:

Core Design Decisions
Deterministic FSM: Uses transitions library for explicit state management

Controlled LLM Usage: Structured prompts with few-shot examples, cached responses

Mocked External APIs: Realistic LinkedIn/Teams simulation with pluggable real implementations

Robust Error Handling: Retry logic, timeouts, state persistence

Configurable: All sensitive data externalized to .env


**What’s Mocked vs Real**:

| Component           | Status   | Reason                                                        |
| ------------------- | -------- | ------------------------------------------------------------- |
| Company lookup      | Mocked   | Uses static dataset (easily replaceable with Apollo/Clearbit) |
| LinkedIn profile    | Mocked   | Simulates profile data + connection acceptance                |
| Connection message  | Real LLM | Ollama/OpenAI/Anthropic for personalization                          |
| Follow-up message   | Real LLM | Same as above                                                 |
| Teams meeting       | Mocked   | Generates realistic teams.microsoft.com links                 |
| Email notifications | Mocked   | Console output (easily swap for SendGrid/Mailgun)             |

## The runnable demo (CLI or simple web UI is fine)  

This is CLI output demo:

```

@AslauAlexandru ➜ /workspaces/Dongzhou-Tech-Internship (main) $ uv run main.py Stripe 'ML Platform'
🚀 OLLAMA Outreach: Stripe (ML Platform)
💻 100% FREE / OFFLINE

✅ Ollama ready: 1 models
   Using: mistral
📂 Resuming: campaign_stripe.json
🔍 Searching Director at Stripe (ML Platform)
✅ Found: Sarah Chen
accept my connection
📝 LinkedIn message (60 chars):
   Hi Sarah Chen, impressed by your ML Platform work at Stripe....
🚀 [MOCK] Sending via LinkedIn API...
✅ Connection sent!
⏳ [MOCK] Waiting for acceptance (2h 15m)...
✓ Accepted!
a📨 Follow-up (60 chars):
   Hi Sarah Chen, impressed by your ML Platform work at Stripe....
🚀 [MOCK] Sending follow-up...
✅ Follow-up sent!
⏳ [MOCK] Waiting for reply...
✓ Reply: 'Yes, happy to chat next week!'
🔗 Teams meeting: https://teams.microsoft.com/l/meetup-20260307T0108/Stripe_MLPlatform
🎉 Outreach COMPLETED!

🎉 SUCCESS - Zero cost!

```