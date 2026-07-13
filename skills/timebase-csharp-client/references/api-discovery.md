# API Discovery

Use this reference when exact method names, overloads, or APIs must be confirmed.

## Safe discovery order

1. Start with bundled references and examples in this skill.
2. If MCP is available, ground stream/schema facts first.
3. Inspect the target project's `.csproj` and `dotnet list package`.
4. Check installed NuGet package metadata, XML docs, or decompiled API surface for the exact API shape before writing code.
5. Use a small compile probe when examples and package docs are insufficient.
6. Ask for missing version or environment details rather than inventing APIs.

## Project inspection

```bash
dotnet list package
```

Read `PackageReference` entries for `Deltix.Timebase.Api` and `Deltix.Timebase.Client` versions.

## What to confirm

- Whether advanced APIs (live cursor watcher, space selection, multiplexed cursors, etc.) exist in the installed client.
- Target framework compatibility with the chosen package version.

## Guardrails

- Do not invent interfaces, properties, or overloads when package docs, bundled references, or compile checks can confirm them.
- Prefer bundled examples, installed package docs, and confirmed local project metadata over speculative APIs.
- Prefer a compile probe over API archaeology when the question is whether a specific overload or member exists.
- If the client packages are missing, load `project-setup-and-nuget.md` first.
