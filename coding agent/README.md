# CLI Coding Agent

A simple CLI-based coding agent that uses raw LLM API calls via `litellm`.
It supports basic tool calling to read, write, and list files in the workspace.

## Features
- CLI chat loop with tool execution
- Tool schemas defined in JSON format
- Safe, workspace-scoped file tools
- Minimal dependencies

## Architecture
```
coding-agent/
├── cli_agent/                  # CLI agent package
│   ├── __init__.py              # package marker
│   ├── __main__.py              # module entrypoint
│   ├── main.py                  # CLI loop + model calls
│   └── tools.py                 # tool schemas + execution
├── demo_agents.ipynb            # notebook experiments
├── itinerary_planner.py         # itinerary generator
├── README.md                    # docs
└── requirements.txt             # dependencies
```

## Installation
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Python version: 3.10+ recommended (tested with 3.12).

## Configuration
Set credentials for your chosen LLM provider. Examples:

Gemini (Google AI Studio):
```bash
export GEMINI_API_KEY=your_key
```

OpenAI:
```bash
export OPENAI_API_KEY=your_key
```

Anthropic:
```bash
export ANTHROPIC_API_KEY=your_key
```

## Usage
```bash
python -m cli_agent --model gemini/gemini-3-flash-preview
```

Optional flags:
- `--max-steps 8` maximum tool steps per turn
- `--system "..."` override system prompt
- `--verbose` show tool calls and results

Example prompt:
```
agent> list the files in the current directory
```

## Prompt to Generate `itinerary_planner.py`
Run the agent, then paste this single prompt:
```
Create a simple Python CLI program called itinerary_planner.py. It should accept --city and --days, then generate a Markdown itinerary with Day 1..Day N and 3–5 suggested spots per day. If you can browse the web, pick popular attractions for that city; if not, use general knowledge and clearly mark suggestions as “example”. Output Markdown only. Then modify itinerary_planner.py so it only takes --city and --days. It should call an online places API (use OpenTripMap or another free API) to fetch popular attractions for the city, then distribute them across days and output Markdown. If no API key is set, fall back to a small hardcoded list.
```

## Verify Output
After the agent generates the script, verify it runs:
```bash
python itinerary_planner.py --city "Paris" --days 2
```

## Run `itinerary_planner.py`
Basic usage:
```bash
python itinerary_planner.py --city "Tokyo" --days 2
```

If your script supports an API key (e.g., OpenTripMap), set it first:
```bash
export OPENTRIPMAP_API_KEY=your_key
python itinerary_planner.py --city "Tokyo" --days 2
```

Example output (with API key):
```
# Itinerary for Tokyo

**Duration:** 2 days

## Day 1
- Chueigekijo Theater
- Grant Heights Theater
- Meigaza Theater

## Day 2
- Shingekijo Theater
- Tōkaidō
- Tokyo Metropolitan Government Office - South Observatory Deck
```

Example output (without API key):
```
# Trip Itinerary: London

**Duration:** 3 Days
*Note: Using example suggestions (API unavailable or city not found).*

## Day 1
- Historical Landmark (Example)
- Local Museum (Example)
- Central Park (Example)

## Day 2
- Shopping District (Example)
- Scenic Viewpoint (Example)
- Local Eatery (Example)

## Day 3
- Art Gallery (Example)
- Old Town Square (Example)
- Botanical Garden (Example)
```

## Tools
The agent supports:
- `list_files`
- `read_file`
- `write_file`
- `make_dir`

All file tools are restricted to the current workspace directory.

## Example Projects Built by the Agent
- `examples/itinerary_planner`: itinerary planner that takes city, days, and outputs Markdown.

## Notes
- This project intentionally avoids agent frameworks (LangChain, CrewAI, etc.).
- The CLI uses raw `litellm` calls with function tools.
