# TimeBase Agent Plugins

TimeBase plugins for Cursor, VSCode, Claude Code, and any tool supporting the Open Plugin standard.

If you only need skills, jump to [Skills](#skills).

## Quickstart

### 1. Install TimeBase MCP

Community edition:

```bash
uv tool install -p 3.14 --from "timebase-mcp[community]" timebase-mcp
```

Enterprise edition:

> [!IMPORTANT]
> Make sure to replace `<user>` and `<password>` with your Nexus credentials.

```bash
uv tool install -p 3.14 --index "https://<user>:<password>@nexus.deltixhub.com/repository/epm-rtc-public-python/simple" --from "timebase-mcp[enterprise]" timebase-mcp
```

If you prefer `pip`/`pipx` or another method, see the [TimeBase MCP installation docs](https://github.com/epam/TimeBase-MCP#installation).

### 2. Verify MCP installation from a new terminal

```bash
timebase-mcp -v
```

> [!NOTE]
> The MCP client launches the server automatically, but `timebase-mcp` must be discoverable in `PATH`.

### 3. Install plugin in your tool

<details>
<summary>Cursor</summary>

Clone this repository as a local plugin.

macOS/Linux:
```bash
git clone https://github.com/epam/TimeBase-Agent-Plugins.git ~/.cursor/plugins/local/timebase
```

Windows:
```bash
git clone https://github.com/epam/TimeBase-Agent-Plugins.git %USERPROFILE%\.cursor\plugins\local\timebase
```

Open `Cursor Settings > Plugins > TimeBase Plugin > TimeBase MCP` to edit configuration.  
Available options: [MCP configuration](https://github.com/epam/TimeBase-MCP#advanced-configuration).

</details>

<details>
<summary>VSCode</summary>

Open command palette (CMD+Shift+P / Ctrl+Shift+P), run `Chat: Install Plugin from Source`, then paste:

```text
https://github.com/epam/TimeBase-Agent-Plugins.git
```

In chat panel, click `Configure Tools`, hover `timebase-mcp`, then click `Configure TimeBase`.
Available options: [MCP configuration](https://github.com/epam/TimeBase-MCP#advanced-configuration).

</details>

<details>
<summary>Claude Code</summary>

Open Claude Code and run the following commands:

```bash
/plugin marketplace add https://github.com/epam/TimeBase-Agent-Plugins.git
/plugin install timebase@timebase-plugins
/reload-plugins
```

You will be prompted to configure MCP during installation.  
Available options: [MCP configuration](https://github.com/epam/TimeBase-MCP#advanced-configuration).

> [!WARNING]
> On macOS there's an [upstream issue](https://github.com/anthropics/claude-code/issues/11927) with plugin configuration sometimes not being passed to the MCP. 
> As a workaround, you can disable the plugin-managed MCP server from the `/plugin` menu and manually add it using the following command:
> 
> ```bash
> claude mcp add timebase-mcp --transport stdio --env TIMEBASE_URL='dxtick://localhost:8011' -- timebase-mcp
> ```

</details>

<details>
<summary>Other tools</summary>

This repository follows the [Open Plugin](https://open-plugins.com/) standard, so it can be used in any compatible tool.

</details>

> [!NOTE]
> If you encounter issues with the MCP server, check out the [troubleshooting guide](https://github.com/epam/TimeBase-MCP#troubleshooting).

## Skills

> [!WARNING]
> The **qql-generator** skill is built around grounding from **TimeBase MCP**. For task-correct, schema-backed QQL, run the agent with [TimeBase MCP](https://github.com/epam/TimeBase-MCP) configured.
> Usage **without** MCP is **not recommended**, you are likely to get materially worse results.

### Prerequisites

- **Node.js** installed (for `npx`).

### Installation

#### npx skills (recommended)

Works for Claude Code, Cursor, VSCode and any other tool supporting the [Agent Skills](https://agentskills.io/home) open standard.

```bash
npx skills add https://github.com/epam/TimeBase-Agent-Plugins.git
```

#### Manual installation

1. Clone this repository:

```bash
git clone https://github.com/epam/TimeBase-Agent-Plugins.git
```

2. Copy the `/skills/qql-generator` directory into your tool's skills installation folder.

### Usage

No special actions are required. Just ask your agent something about QQL.

### Uninstallation

```bash
npx skills remove
```
