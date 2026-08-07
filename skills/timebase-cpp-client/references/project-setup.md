# Project Setup

Use this reference when acquiring or integrating the TimeBase C++ client (dxapi, Enterprise Edition).

Version numbers below are illustrative. Use whatever is already pinned in the target project, or ask the user to confirm the current release.

## Prerequisites

| Platform | Toolset |
| --- | --- |
| Windows | MSVC, `PlatformToolset` v142 (the Visual Studio 2019 toolset, v141 = VS2017, v143 = VS2022) |
| Linux | Clang 10 and GCC libstdc++ |
| macOS | Apple-Clang. arm64 also needs `brew install openssl@1.1` |

dxapi links against OpenSSL 1.1.1, tinyxml2, and Aeron (message transport), bundled into the acquired archive/package, no separate acquisition needed for these.

## Detect the target project first

Look for dxapi already acquired somewhere in the project (an extracted archive on Linux/macOS, or `packages.config` referencing `Deltix.Timebase.Api.Native` on Windows). If found, preserve its version and exact layout, don't move or re-derive it. Only start fresh acquisition when nothing is wired up yet.

## Acquiring dxapi

Prebuilt Nexus archive, credentials via `NEXUS_USER`/`NEXUS_PASS` (see Credentials below), no package manager involved.

### Linux/macOS

```
https://nexus.deltixhub.com/repository/epm-rtc-public/QuantServer/Timebase/Deltix.Timebase.Api.Native.Linux/Deltix.Timebase.Api.Native.Linux-<version>.tar.gz
https://nexus.deltixhub.com/repository/epm-rtc-public/QuantServer/Timebase/Deltix.Timebase.Api.Native.MacOS/Deltix.Timebase.Api.Native.MacOS-<version>.tar.gz
```

Extract, headers under `include/dxapi/*.h`, libs under `lib/`. Wire both into the build manually (`target_include_directories`/`target_link_directories`/`target_link_libraries`), confirm the actual lib file name against what was extracted.

### Windows

Direct download (same Nexus credentials, returns the `.nupkg`, which is a plain zip):

```
https://$NEXUS_USER:$NEXUS_PASS@nexus.deltixhub.com/repository/epm-rtc-public-net/Deltix.Timebase.Api.Native/<version>
```

Or, in Visual Studio, add `https://nexus.deltixhub.com/repository/epm-rtc-public-net/` as a NuGet package source and restore normally via `packages.config`:

```xml
<packages>
  <package id="Deltix.Timebase.Api.Native" version="<version>" targetFramework="native" />
</packages>
```

Restoring this way auto-imports a `.targets` file that adds `include`/`include\dxapi` to the include path and, **only when the project is `Platform=x64` and `PlatformToolset=v142`**, an `x64\Debug`/`x64\Release` lib dir plus `dxapi-x64d.lib`/`dxapi-x64.lib`. Any other platform/toolset gets no wiring from it and needs manual configuration. It doesn't copy a runtime DLL. Real sample projects often use a manually-vendored `dxapi/` folder next to the project instead of, or alongside, this NuGet import, treat that as a normal pattern, not a fallback.

### DFP (Decimal64)

Separate from dxapi. The latest prebuilt DFP (`deltix::dfp::Decimal64`) appears to be distributed via Conan Center rather than Nexus:

```
https://conan.io/center/recipes/dfp
```

If the project already uses Conan for other dependencies, add `dfp/<version>` there. Otherwise check with the user, an older Nexus-hosted DFP archive may exist for older pinned dxapi versions but hasn't been verified this session.

A build failing to find DFP symbols while dxapi itself links fine is a common, easy-to-miss failure mode (see `debugging-and-performance.md`).

## Header layout for API lookups

Headers are laid out `include/dxapi/*.h` inside whatever was acquired, but the root that layout hangs off differs by platform and, on Windows, isn't reliably consistent even across real sample projects. Don't assume a fixed path: find where the project already extracted/restored dxapi (a vendored `dxapi/` folder, a NuGet `packages/Deltix.Timebase.Api.Native.<version>/` folder, or wherever the Nexus tar.gz was unpacked), then search that location for `dxapi.h` to confirm the real root. Once located, use the table below to pick the right header for the API in question, and confirm exact signatures there instead of from memory, this API has no compiler-enforced binding to catch a wrong guess at the call site.

| Header | Covers |
| --- | --- |
| `dxapi.h` | `TickDb`, `TickStream`, `TickCursor`, `TickLoader`, `TopicDB`, core types |
| `data_reader.h` | `DataReader` read methods |
| `data_writer.h` | `DataWriter` write methods |
| `selection_options.h` | `SelectionOptions` fields (live, reverse, time bounds, space) |
| `loading_options.h` | `LoadingOptions` fields (write mode, space) |
| `stream_options.h` | `StreamOptions` for `createStream`, embeds `BufferOptions` |
| `topic_options.h`, `topicdb_options.h` | Topic definition options (mostly unused today, topics are QQL-managed) |
| `publishing_options.h`, `consumer_options.h` | `TopicDB` publish/poll options |
| `schema.h` | `TickDbClassDescriptor`, `FieldInfo`, `DataType`, `FieldTypeDescriptor` |
| `generic-message-decode.h` | Schema-driven generic decode (`GenericCodec::MapMessageDecoderCache`) |
| `schema_change_task.h` | `SchemaChangeTask` for `TickStream::changeSchema` |
| `lock_options.h` | `LockOptions`/`LockType` for `TickStream::lock` |
| `buffer_options.h` | `BufferOptions` (write buffering) |
| `bg_proc_info.h` | `BackgroundProcessInfo`/`ExecutionStatus` |
| `interval.h` | `Interval`/`TimeUnit` for `TickStream::getPeriodicity` |

## Credentials

- Nexus access is credentialed per-organization, issued by an admin.
- Use placeholder env vars (`NEXUS_USER`/`NEXUS_PASS`), preserving whatever naming convention the project already uses.
- Never hardcode credentials in `CMakeLists.txt`, `.vcxproj`, or any committed file.
- A 401/403 means the configured credentials are missing or wrong. Report that rather than retrying blindly.

## Community Edition

Not yet supported by this skill.

## New vs existing project

| Situation | Action |
| --- | --- |
| Existing project with dxapi already wired up | Preserve its version and exact include/lib layout |
| New Linux/macOS project | Extract the Nexus tar.gz, wire include/lib paths manually |
| New Windows project | NuGet restore or direct `.nupkg` download, verify x64/v142 or expect a manually-vendored `dxapi/` folder |
| User only wants a code snippet | Provide the fragment labeled with the required project context |
