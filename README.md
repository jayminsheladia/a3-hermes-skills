# Hermes skills: deadline-radar

A [Hermes Agent](https://github.com/NousResearch/hermes-agent) skill tap with one skill.

**deadline-radar** flags deadlines at risk by comparing how soon each one is due with how recently a public GitHub repository had a commit. It uses only the Python standard library and needs no API keys.

## Install

```bash
hermes skills tap add jayminsheladia/a3-hermes-skills
hermes skills install jayminsheladia/a3-hermes-skills/deadline-radar
```

## Try it

Ask Hermes: "Use deadline-radar in demo mode with the repo NousResearch/hermes-agent."

Or run the script directly:

```bash
python3 skills/deadline-radar/scripts/deadline_radar.py --demo --repo NousResearch/hermes-agent
```

## What it accesses

- A deadlines JSON file that you choose.
- `api.github.com`, with one unauthenticated read of the repository you name.

It stores nothing and uses no credentials, so only public repositories work.

Created for CSCI 599 (Agentic AI), Fall 2026, with AI assistance.
