# Pendragondi.API Raw

> **Find out how much you're wasting on redundant API calls — with one decorator and one command.**

This is our first public release! Feedback and bug reports are very welcome—if you run into anything unexpected, please open an issue. We'll be shipping improvements quickly.

Pendragondi.API Raw is a local utility that tracks API usage patterns in your Python applications and surfaces hidden inefficiencies like:
- Repeated identical API calls
- Missed caching opportunities
- Wasteful use of expensive services
- Undetected rate-limit collisions

It runs entirely inside your application. No proxies. No agents. No cloud services. Just insight.

---

## 🔍 Why It Exists

Most teams don't track how they're using APIs — they just assume they're used efficiently. But they're not:

- 💸 Many orgs waste **$1000s/month** on duplicate API calls
- 🧱 These inefficiencies compound silently across teams and services
- 🤖 Observability tools are often too heavy, too late, or too expensive

Pendragondi.API Raw gives you a simple, local way to see your API usage like an engineer *and* a finance lead — in minutes.

---

## ✅ Features

- 🧠 Detects redundant API calls (same endpoint + args)
- ❄️ Flags missed caching opportunities
- 🚦 Surfaces rate-limited behavior (HTTP 429)
- 💵 Estimates monthly savings potential
- 📝 Outputs clean, shareable Markdown or JSON reports
- 🔒 Fully local — no external tracking or data storage

---

## 🛠️ Installation

```bash
pip install git+https://github.com/PendragonDI/pendragondi-api-raw.git
```

Or clone and install locally:

```bash
git clone https://github.com/PendragonDI/pendragondi-api-raw.git
cd pendragondi-api-raw
pip install -e .
```

---

## 🚀 Quickstart

### 1. Decorate your API functions:

```python
from pendragondi_api_raw import log_api_call
import requests

@log_api_call(service="openai", cacheable=True)
def call_openai():
    return requests.post("https://api.openai.com/v1/chat/completions", json={"prompt": "Hello"})
```

### 2. Run your app as normal.

### 3. Generate a report:

```bash
python -m pendragondi_api_raw.cli --output report.md
```

### 4. View the results:

```markdown
# Pendragondi.API Raw — Optimization Report

Total API Calls: 53
Redundant Calls: 50
Missed Cache Opportunities: 50
Rate Limit Warnings: 0
Estimated Monthly Savings: $0.75
```

---

## 🧪 Examples

See `/examples` for usage samples for:
- OpenAI / GPT
- Stripe
- REST APIs via `requests`

---

## 🧰 Configuration (optional)

You can control behavior via environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `PENDRAGONDI_DB_PATH` | Path to SQLite log file | `~/.pendragondi_api_log.db` |
| `PENDRAGONDI_SAMPLE_RATE` | Percent of calls to log (0–1.0) | `1.0` |
| `PENDRAGONDI_MASK_FIELDS` | Comma-separated keys to hide from payload hash | `Authorization,api_key` |

---

## 📜 License

[MIT License](LICENSE)

---

## 🧭 Why PendragonDI?

Pendragondi.API Raw was built to solve a problem no other tool addressed:  
How do I find out how my system is *quietly wasting money*—before it hits the billing dashboard?

This tool was written by someone who noticed the pattern, proved it, and compressed it into something that can run anywhere.

**No agents. No overhead. Just signal.**

---

## 🤝 Contributing

Contributions are welcome! If you have suggestions for improvements or find a bug, please open an issue or submit a pull request.

When contributing:
- Fork the repository and create your branch from `main`.
- Ensure any new code has appropriate type hints and docstrings.
- Run the test suite and add tests for new functionality.
- Submit a descriptive pull request so changes can be reviewed efficiently.
- Support/Contact: pendragondi@pendragondi.dev
---

## 💖 Support the Project
Pendragondi.API Raw is open-source and free to use.  
If you’ve found it useful and would like to support ongoing development, you can sponsor us on GitHub:  
[![Sponsor on GitHub](https://img.shields.io/badge/Sponsor-💖-pink?style=flat)](https://github.com/sponsors/jinpendragon)
