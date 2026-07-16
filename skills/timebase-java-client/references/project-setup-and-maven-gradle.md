# Project Setup And Maven/Gradle

Use this reference when setting up or integrating the TimeBase Java client.

## Detect the target project first

Before generating code, check whether the user has an existing build:

1. Read the target `pom.xml` (Maven) or `build.gradle`/`build.gradle.kts` (Gradle) if present.
2. Preserve the existing Java version/toolchain.
3. Preserve existing dependency-management style (BOM imports, version catalogs, property-based versions).
4. Add TimeBase dependencies to the existing project instead of creating a separate scaffold unless the user asked for a new project.

For projects with no existing preference, target Java 11 (the client's documented supported baseline; later LTS versions generally work too) and label it as adjustable.

## Required dependencies

Gradle:

```gradle
dependencies {
    implementation "deltix.qsrv.timebase:deltix-timebase-client:<version>"
    implementation "deltix.qsrv:deltix-timebase-api-messages:<version>"
}
```

Maven:

```xml
<dependency>
    <groupId>deltix.qsrv.timebase</groupId>
    <artifactId>deltix-timebase-client</artifactId>
    <version>&lt;version&gt;</version>
</dependency>
<dependency>
    <groupId>deltix.qsrv</groupId>
    <artifactId>deltix-timebase-api-messages</artifactId>
    <version>&lt;version&gt;</version>
</dependency>
```

- `deltix-timebase-client` is the main client dependency.
- `deltix-timebase-api-messages` provides built-in message types (`BarMessage`, `TradeMessage`, `BestBidOfferMessage`, etc.); only needed when the user wants bound built-in types instead of custom schema.
- Do not hardcode a specific version from memory. Use whatever version is already pinned in the project, or tell the user to substitute the latest version published to their configured repository.

## Repository

TimeBase Java packages are typically hosted on your organization's configured TimeBase Maven repository rather than Maven Central. You can browse published Java artifacts at `https://nexus.deltixhub.com/#browse/search/maven` to confirm an artifact and version exist, but that browse URL is a search UI, not a resolvable repository endpoint for a build file — the actual `<url>`/`repositories { maven { url ... } }` value must be the organization's configured repository endpoint, and repository access requires credentials from the organization (contact an admin for access if missing). If the build does not already have this configured, add a repository block using a placeholder host, and ask the user to confirm the actual repository URL for their organization:

Gradle:

```gradle
repositories {
    mavenCentral()
    maven {
        url "<your-organization's-timebase-maven-repository>"
        credentials {
            username = System.getenv("TIMEBASE_REPO_USER")
            password = System.getenv("TIMEBASE_REPO_PASSWORD")
        }
    }
}
```

Maven (`settings.xml` or `pom.xml`):

```xml
<repositories>
    <repository>
        <id>timebase-repo</id>
        <url>&lt;your-organization's-timebase-maven-repository&gt;</url>
    </repository>
</repositories>
<servers>
    <server>
        <id>timebase-repo</id>
        <username>${env.TIMEBASE_REPO_USER}</username>
        <password>${env.TIMEBASE_REPO_PASSWORD}</password>
    </server>
</servers>
```

## Credentials guardrails

- Do not hardcode secrets in generated files.
- Do not overwrite existing repository/credential configuration blindly.
- Do not tell users to commit filled-in credentials.
- Prefer environment-backed values, but preserve the naming convention already used by the project or user.
- If dependency resolution fails with 401/403, report that the configured repository credentials are missing or incorrect.
- If the project has no existing convention, use clear placeholder names and tell the user to wire them through their preferred local secret or environment setup.

## Verification

When mode and tools allow:

```bash
./gradlew build
./gradlew dependencies
```

or

```bash
mvn compile
mvn dependency:tree
```

In read-only modes, provide these commands in a verification section and explain expected success.

## New vs existing project

| Situation | Action |
| --- | --- |
| User has existing Maven/Gradle project | Add dependencies, preserve Java version and structure |
| User wants a new app | Scaffold minimal project + build file if needed |
| User only wants a code snippet | Provide fragment labeled with required project context |
