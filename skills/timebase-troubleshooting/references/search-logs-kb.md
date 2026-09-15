# Search logs KB

Use `search_logs_kb` for likely-match retrieval against the bundled TimeBase troubleshooting knowledge base.

`search_logs_kb` requires TimeBase MCP 0.2.5 or later. It searches a bundled knowledge base without connecting to TimeBase, so it can help even when the TimeBase server cannot start. If the tool is unavailable, say so clearly before falling back to manual triage or docs search.

## Good query shapes

Best first choice:

- first exception line
- first stack frame

Good fallback when there is no stack trace:

- the main error line
- one or two adjacent lines that explain the context

Good container-log cleanup:

- keep the error text
- drop repeated container prefixes, timestamps, and boilerplate when they add no signal

Avoid:

- a single generic exception name with no context
- very long log dumps when a 2 to 6 line excerpt captures the same failure
- mixing several unrelated errors into one query

## How to read the tool response

The tool returns:

- `query`: what was sent
- `normalized_query`: the shorter, cleaned query actually searched
- `advice`: hints when the query is too broad
- `matches`: best-first candidate matches

`matches[0]` is the best current candidate, not a guaranteed diagnosis.

## Broad-query behavior

If the tool says the query is broad, do not keep guessing from that result set.

Ask for one of these:

- the first stack frame
- the error line immediately before `Caused by`
- 20 to 30 lines around the failure

Then rerun the search.

## Weak-match signals

Treat the result as weak when:

- it only shares a generic exception class such as `IOException` or `IllegalStateException`
- the returned `symptom_summary` describes a different subsystem than the user's log
- the returned `symptom_signature` includes a frame or class that is absent from the user's evidence
- the match looks like a client-side issue while the user's evidence points to a server-side failure, or the other way around

In that case, say the KB found only loose matches and continue with manual troubleshooting.

## Upgrade guidance

Only recommend an upgrade when both are true:

- `fix_version` is present
- `fix_confidence` is `confirmed` or `likely`

Even then, phrase it carefully. Say the issue was fixed or likely fixed in that version, not that the upgrade is guaranteed to solve every similar report.


## Safe answer pattern

A solid reply usually sounds like this:

- the closest KB match is X, or the KB has no strong match
- it fits because Y
- the confidence is limited because Z
- the next thing to check is N

That keeps the answer useful without pretending the KB proved more than it did.
