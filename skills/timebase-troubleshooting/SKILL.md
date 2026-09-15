---
name: timebase-troubleshooting
description: Use when the user is diagnosing a TimeBase failure from logs, stack traces, startup problems, runtime errors, or live operational symptoms such as stuck cursors, loaders, connections, or locks. Use this when the user pasted evidence and wants to know what it means or what to check next. Do not use it when the main deliverable is client code or QQL.
---

# TimeBase troubleshooting

## Mission

Turn raw TimeBase evidence into a grounded triage read. Start with the strongest evidence you have: logs when logs are available, runtime inspection when the issue is live and operational. Prefer `search_logs_kb` when a useful log excerpt is available and TimeBase MCP is configured. Treat matches as candidates, not proof.

## When to use this skill

Use this skill when the user is dealing with:

- TimeBase startup or runtime failures
- pasted logs, container logs, stack traces, or error excerpts
- questions like "what does this log mean?", "why won't TimeBase start?", or "what should I check next?"
- a suspected known issue where a fix version may matter
- live operational problems where MCP runtime state may help, such as stuck cursors, loaders, connections, or locks

This skill can help with both server-side and client-side TimeBase issues when the user starts from logs or runtime symptoms. The logs KB was built from historical TimeBase issue evidence, so some matches may describe client-side failures rather than server bugs.

Do not use this skill for:

- writing or repairing TimeBase client code in Java, Python, C#, or C++ when the main deliverable is code
- pure QQL authoring or repair
- generic infrastructure debugging with no meaningful TimeBase evidence

If the issue is clearly a coding task after triage, switch to the relevant client skill instead of staying here.

## Workflow

1. Confirm the evidence source.
   - If the user has not shared logs yet, ask for a short excerpt.
   - If they only shared a screenshot or archive, ask for the relevant text lines.
   - If the evidence is not obviously from TimeBase, first confirm whether the failure is in the TimeBase server, a TimeBase client, or surrounding infrastructure.
2. Pick the first branch deliberately.
   - If you have a useful log excerpt and TimeBase MCP is configured, start with `search_logs_kb`.
   - If logs are absent or too weak, and the problem is clearly live and operational, go straight to runtime MCP tools.
3. If you start with `search_logs_kb`:
   - Remember that `search_logs_kb` is an MCP tool, not a built-in skill feature.
   - Build a tight query from the strongest lines, not the whole dump.
   - Start with the default limit.
   - If the tool says the query is broad, ask for the first stack frame or a slightly wider excerpt, then retry.
4. Judge the KB matches before you answer.
   - Compare the returned signature and summary to the actual evidence.
   - Do not assume the match is server-side. Some KB entries describe client-side failures.
   - If no result clearly fits, say that the KB did not find a strong match.
5. If the KB is unavailable or weak, branch deliberately.
   - Use runtime MCP tools when live server state is likely to help.
   - Use docs search when the next question is really about product behavior, configuration, or feature semantics.
6. Give a triage answer.
   - Say what the evidence most likely points to.
   - Explain why.
   - Give the next diagnostic or workaround step.
   - Mention an upgrade only when `fix_version` is non-null and `fix_confidence` is `confirmed` or `likely`.

## Answering rules

- Be explicit about uncertainty.
- Do not turn a likely match into a definite root cause.
- Do not claim that upgrading will fix the issue unless the returned entry supports that claim.
- `fix_confidence` tells you how reliable the `fix_version` is. It does not tell you how certain the match itself is.
- If the KB says `unclear from available evidence`, keep that uncertainty in your answer.
- If the log looks too broad or too short, ask for better evidence instead of guessing.
- If MCP is unavailable, say that clearly and continue with the best manual triage you can.
- If runtime monitoring tools are unsupported on the user's TimeBase server version, say that plainly and switch to other evidence.
- If you use `get_server_configuration`, do not overread it. It tells you what MCP is configured to target, not that the server is reachable or healthy.
- If the evidence points to client code using TimeBase rather than the server itself, say so and hand off to the relevant client skill when code work starts.

## If the KB has no strong match

Say that directly, then continue with normal troubleshooting.

Ask for whichever missing evidence would tighten the diagnosis most:

- the first stack frame
- 20 to 30 lines around the error
- whether this happens at startup, runtime, or only from a client application
- the TimeBase version
- whether the issue started after an upgrade, config change, cert change, or storage move
- whether there is a specific stream, loader, cursor, or connection involved

## Response shape

Keep the reply practical. A good default is:

1. `What this most likely is`
2. `Why`
3. `What to check next`
4. `Upgrade note`, only when justified by the KB entry
5. `If MCP is unavailable`, only when that changed the depth of the answer

## Tool notes

Read these references only when you need them:

- [`references/search-logs-kb.md`](references/search-logs-kb.md) for query shaping, weak-match handling, and upgrade rules
- [`references/runtime-triage.md`](references/runtime-triage.md) for live MCP inspection of activity, streams, server state, and tool-support caveats
- [`references/docs-search.md`](references/docs-search.md) for concept and configuration lookup when the next question is really about how a TimeBase feature works
