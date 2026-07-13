# Project Setup And NuGet

Use this reference when setting up or integrating the TimeBase .NET client.

## Detect the target project first

Before generating code, check whether the user has an existing solution:

1. Read the target `.csproj` if present.
2. Preserve the existing target framework.
3. Preserve nullable settings, implicit usings, and existing package conventions.
4. Add TimeBase packages to the existing project instead of creating a separate scaffold unless the user asked for a new project.

For projects with no user preference, use a conservative currently supported target framework and label it as adjustable.

## Required packages

```xml
<PackageReference Include="Deltix.Timebase.Api" Version="5.6.14" />
<PackageReference Include="Deltix.Timebase.Client" Version="5.6.14" />
```

## NuGet feed

TimeBase packages are hosted on the Deltix NEXUS NuGet feed. If the solution does not already have feed configuration, add or extend `NuGet.config`:

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <packageSources>
    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
    <add key="Deltix.NET" value="https://nexus.deltixhub.com/repository/epm-rtc-public-net" />
  </packageSources>
  <packageSourceCredentials>
    <Deltix.NET>
      <add key="Username" value="%NEXUS_USER%" />
      <add key="ClearTextPassword" value="%NEXUS_PASS%" />
    </Deltix.NET>
  </packageSourceCredentials>
</configuration>
```

## Credentials guardrails

- Do not hardcode secrets in generated files.
- Do not overwrite existing `packageSourceCredentials` blindly.
- Do not tell users to commit filled-in credentials.
- Prefer placeholders or environment-backed values in `NuGet.config`, but preserve the naming convention already used by the project or user.
- If restore fails with 401/403, report that the configured feed credentials are missing or incorrect.
- If the project has no existing convention, use clear placeholder names and tell the user to wire them through their preferred local secret or environment setup.

## Verification

When mode and tools allow:

```bash
dotnet restore
dotnet build
dotnet list package
```

In read-only modes, provide these commands in a verification section and explain expected success.

## New vs existing project

| Situation | Action |
| --- | --- |
| User has existing `.csproj` | Add package references, preserve TFM and structure |
| User wants new console app | Scaffold minimal project + `NuGet.config` if needed |
| User only wants a code snippet | Provide fragment labeled with required project context |
