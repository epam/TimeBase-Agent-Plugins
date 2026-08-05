# TimeBase Agent Plugins

TimeBase plugins for Cursor, VSCode, Claude Code, OpenAI Codex and any tool supporting the Open Plugin standard.

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
Available options: [MCP configuration](https://github.com/epam/TimeBase-MCP/blob/main/docs/reference/environment-variables.md).

</details>

<details>
<summary>VSCode</summary>

Search for `@agentPlugins timebase` in the Extensions tab to install.

For adjusting the settings open the chat panel, click `Configure Tools`, hover over `timebase-mcp`, then click `Configure TimeBase`.
Available options: [MCP configuration](https://github.com/epam/TimeBase-MCP/blob/main/docs/reference/environment-variables.md).

</details>

<details>
<summary>Claude Code</summary>

Open a terminal and run:

```bash
claude plugin marketplace add epam/TimeBase-Agent-Plugins
claude plugin install timebase@timebase-plugins
```

You will be able to configure MCP by running `/plugins` inside a Claude Code session, selecting the plugin under `Installed` and clicking `Configure options`.  
Available options: [MCP configuration](https://github.com/epam/TimeBase-MCP/blob/main/docs/reference/environment-variables.md).

> [!WARNING]
> On macOS there's an [upstream issue](https://github.com/anthropics/claude-code/issues/11927) with plugin configuration sometimes not being passed to the MCP. 
> As a workaround, you can disable the plugin-managed MCP server from the `/plugin` menu and manually add it using the following command:
> 
> ```bash
> claude mcp add timebase --transport stdio --env TIMEBASE_URL='dxtick://localhost:8011' -- uvx --from 'timebase-mcp[all]==0.2.2' timebase-mcp
> ```

</details>

<details>
<summary>Claude Desktop</summary>

Open `Settings > Plugins > Add > Add Marketplace` and paste:

```
epam/TimeBase-Agent-Plugins
```

Press `Sync` button and wait for the plugin list to appear.

Select `TimeBase` and click the `+` to install.

</details>

<details>
<summary>OpenAI Codex</summary>

From your terminal, run:

```bash
codex plugin marketplace add epam/TimeBase-Agent-Plugins
codex plugin add timebase@timebase-plugins
```

Then start a new Codex instance so the plugin skills and MCP tools are loaded.

The MCP server settings can be configured globally in `~/.codex/config.toml` or per project in `.codex/config.toml`:

```toml
[plugins."timebase@timebase-plugins".mcp_servers.timebase.env]
TIMEBASE_URL = "dxtick://localhost:8011"
```

Check out the available [MCP configuration options](https://github.com/epam/TimeBase-MCP/blob/main/docs/reference/environment-variables.md).

</details>

<details>
<summary>GitHub Copilot CLI</summary>

In your terminal, run:

```bash
copilot plugin install timebase@awesome-copilot
```

Then start a new Copilot CLI session so the plugin is loaded.

Adjust the MCP server settings via `/mcp edit timebase-mcp` command. 
Check out the available [MCP configuration options](https://github.com/epam/TimeBase-MCP/blob/main/docs/reference/environment-variables.md).

</details>

<details>
<summary>GitHub Copilot App</summary>

Use the following button:

[![Install TimeBase plugin](https://img.shields.io/badge/Install-TimeBase_Plugin-blue?logo=github&style=flat-square)](ghapp://plugins/marketplace/add?source=epam%2FTimeBase-Agent-Plugins)

Or go to `Settings > Plugins` and search for `timebase`.

</details>

<details>
<summary>Other tools</summary>

This repository follows the [Open Plugin](https://open-plugins.com/) standard, so it can be used in any compatible tool.

</details>

> [!NOTE]
> If you encounter issues with the MCP server, check out the [troubleshooting guide](https://github.com/epam/TimeBase-MCP/blob/main/docs/troubleshooting.md).

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
<summary>Claude Desktop</summary>

Use the `Settings > Plugins > TimeBase > Update` button.

</details>

<details>
<summary>OpenAI Codex</summary>

Refresh the marketplace snapshot and reinstall the plugin:

```bash
codex plugin marketplace upgrade timebase-plugins
codex plugin add timebase@timebase-plugins
```

Then restart any running Codex instances.

</details>

<details>
<summary>GitHub Copilot CLI</summary>

In your terminal, run:

```bash
copilot plugin update timebase
```

Then restart any running Copilot CLI sessions.

</details>

<details>
<summary>GitHub Copilot App</summary>

Go to `Settings > Plugins`, find `timebase` and click `Update plugin` under the 3-dot menu.

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
