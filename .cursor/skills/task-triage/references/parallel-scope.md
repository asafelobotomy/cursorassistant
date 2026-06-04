# Parallel scope ledger (template)

Use before spawning multiple Task subagents.

```text
Goal: <one line>
Agents: <name → allowed paths>
Forbidden: <paths no agent may touch>
Proof: <command that must pass before merge>
Interfaces to re-check: <files touched by 2+ scopes>
```

Stop and narrow scope if two agents need the same file.
