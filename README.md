# TimeBase Agent Plugins

TimeBase plugins for Cursor, VSCode, Claude Code, and any tool supporting the Open Plugin standard.

If you only need skills, jump to [Skills](#skills).

## Quickstart

### 1. Install uv

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if `uvx` is not available.

Check that `uvx` is available in your shell:

```bash
uvx -V
```

### 2. Install plugin in your tool

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
> claude mcp add timebase-mcp --transport stdio --env TIMEBASE_URL='dxtick://localhost:8011' -- uvx --from 'timebase-mcp[all]==0.2.0' timebase-mcp
> ```

</details>

<details>
<summary>Other tools</summary>

This repository follows the [Open Plugin](https://open-plugins.com/) standard, so it can be used in any compatible tool.

</details>

> [!NOTE]
> If you encounter issues with the MCP server, check out the [troubleshooting guide](https://github.com/epam/TimeBase-MCP#troubleshooting).

### Updating an existing plugin installation

Updating the plugin updates the pinned TimeBase MCP version. You do not need to update TimeBase MCP separately.

<details>
<summary>Cursor</summary>

If you cloned the plugin locally, pull the latest changes:

macOS/Linux:

```bash
git -C ~/.cursor/plugins/local/timebase pull
```

Windows:

```bash
git -C %USERPROFILE%\.cursor\plugins\local\timebase pull
```

</details>

<details>
<summary>VSCode</summary>

VS Code updates plugins automatically every 24 hours by default. To trigger an update manually, open command palette (CMD+Shift+P / Ctrl+Shift+P) and run `Extensions: Check for Extension Updates`.

</details>

<details>
<summary>Claude Code</summary>

Inside Claude Code session run:

```bash
/plugin
```

Navigate to the installed plugin and click `Update` button.

</details>

<details>
<summary>Other tools</summary>

Refer to your tool's documentation for updating plugins installed from a repository source.

</details>

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

2. Copy the desired `/skills/<skill-name>` directory into your tool's skills installation folder.

### Usage

No special actions are required. Just ask your agent something about QQL.

### Updating

To update skills you already installed from this repository:

```bash
npx skills update
```

To install a newly added skill from this repository, run the installation command again or copy the new skill directory manually.

### Uninstallation

```bash
npx skills remove
```
