# API Discovery

Use this reference when exact method names, overloads, or APIs must be confirmed.

## Safe discovery order

1. Start with bundled references and examples in this skill.
2. If MCP is available, ground stream/schema facts first.
3. Inspect the target project's `pom.xml`/`build.gradle` and resolved dependency versions.
4. Check the dependency's sources/javadoc jar or IDE-resolved API surface for the exact API shape before writing code.
5. Use a small compile probe when examples and dependency docs are insufficient.
6. Ask for missing version or environment details rather than inventing APIs.

## Project inspection

```bash
./gradlew dependencies
```

or

```bash
mvn dependency:tree
```

Confirm the resolved versions of `deltix-timebase-client` and `deltix-timebase-api-messages`.

## What to confirm

- Whether advanced APIs (live cursor watchers, stream spaces, topics, schema evolution) exist in the resolved client version.
- Java version compatibility with the chosen client version.

## Guardrails

- Do not invent interfaces, properties, or overloads when dependency docs, bundled references, or compile checks can confirm them.
- Prefer bundled examples, resolved dependency docs, and confirmed local project metadata over speculative APIs.
- Prefer a compile probe over API archaeology when the question is whether a specific overload or member exists.
- If the client dependencies are missing, load `project-setup-and-maven-gradle.md` first.
