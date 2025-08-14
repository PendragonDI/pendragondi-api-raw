# pendragondi-api-raw

Pendragondi API Raw is a minimal, local-first library for instrumenting your Python code and surfacing hidden inefficiencies in your API usage.  Drop a decorator on your HTTP calls, run your application as normal and generate a report – no agents, no proxies and no telemetry required.

This repository is the **raw** layer of the Pendragondi ecosystem.  It focuses on capturing factual API call information with zero interpretation or opinion.  A higher‑level `pendragondi-api-pro` package builds on top of this to provide analysis, best‑practice advice and automated recommendations.

## Installation

```bash
pip install git+https://github.com/PendragonDI/pendragondi-api-raw.git
```

## Quickstart

Decorate your API call function:

```python
from pendragondi_api_raw import log_api_call
import requests

@log_api_call(service="openai", cacheable=True)
def call_openai():
    return requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": "Bearer sk-xxxxx"},
        json={"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": "Hello"}]}
    )

# call your function as normal
for _ in range(3):
    call_openai()
```

Generate a report:

```bash
python -m pendragondi_api_raw.cli --output report.md
```

This writes a Markdown file summarising total calls, redundant calls, cache misses and other metrics.  See the `examples/` directory for more usage patterns.

## License

This project is licensed under the MIT License.  See the `LICENSE` file for details.