GitHub Copilot & MCP Servers in VSCode: The Power User's Comprehensive Manual
As of May 24, 2025

Chapter 1: Introduction to Advanced GitHub Copilot Extensibility in VSCode
1.1 Beyond Basic Copilot: The Power User's Path
GitHub Copilot has rapidly established itself as a transformative tool in the software development landscape. Initially recognized for its intelligent code completion and basic chat assistance within Integrated Development Environments (IDEs) like Visual Studio Code 1, it has evolved into a more sophisticated and extensible AI-powered platform. For developers who have mastered these foundational capabilities—leveraging Copilot for autocompletions, generating boilerplate code, and seeking explanations for code snippets—the journey towards becoming a power user involves unlocking deeper integrations and more potent functionalities.

As an experienced user, the quest to move beyond simple prompting and automated fixes naturally leads to exploring mechanisms that can endow GitHub Copilot with new skills. This includes granting it access to broader contextual information beyond the currently open files and enabling it to interact with a multitude of external systems and services. It is this very extensibility that forms the core of advanced Copilot usage, transforming it from a helpful assistant into an integral and proactive member of the development workflow. The key to this transformation lies in understanding and harnessing protocols and features designed to expand Copilot's operational scope and intelligence within the VSCode environment.

1.2 Unveiling the Model Context Protocol (MCP)
Central to the advanced extensibility of GitHub Copilot is the Model Context Protocol (MCP). MCP is an open standard designed to facilitate a standardized way for AI applications, such as Copilot, to connect with and utilize a wide array of external tools, data sources, and services.3 This protocol is pivotal because it allows Copilot, particularly when operating in its more autonomous "Agent Mode" within VSCode, to leverage "tools." These tools are specific functionalities exposed by MCP servers, which empower Copilot to perform actions and retrieve information far exceeding its intrinsic knowledge base, thereby evolving it into a significantly more versatile and powerful AI assistant.3

The introduction and integration of MCP represent a significant evolution in how AI-assisted development can be approached. While traditional GitHub Copilot primarily offers inline code suggestions and chat-based interactions focused on the immediate context of the code editor 1, MCP provides a structured and standardized pathway for Copilot to autonomously discover and interact with diverse external systems.3 These systems can range from databases 13 and version control platforms 4 to cloud services 2, web content repositories 7, and more. This capability fundamentally shifts Copilot's role from a passive suggestion provider to an active participant—an agent—that can be delegated complex, multi-step tasks.5 It can orchestrate workflows and integrate external data into its reasoning and generation processes. For example, the ability for Copilot to use a tool like create_issue provided by a GitHub MCP server 4 or to query a PostgreSQL database through a Neon MCP server 13 illustrates a profound expansion of its operational domain. Consequently, MCP is not merely an add-on feature; it marks a change in the paradigm of AI assistance in software development. GitHub Copilot, augmented by MCP, becomes an extensible platform, moving beyond the "AI pair programmer" concept towards an "AI-powered development team member" that can be customized, extended, and tailored to meet the specific needs and complex workflows of power users and their projects. This evolution is crucial for those seeking to maximize automation and leverage the full potential of AI in their development practices.

Chapter 2: Deep Dive into the Model Context Protocol (MCP)
2.1 MCP Architecture: Connecting Copilot to a World of Tools
The Model Context Protocol (MCP) is architected around a client-server model. In the specific context of this manual, GitHub Copilot, particularly its agentic functionalities within Visual Studio Code, functions as the MCP client. External services, local processes, or even other AI systems that expose their capabilities in conformance with the MCP standard operate as MCP servers.8

The fundamental purpose of MCP is to standardize the way AI applications discover the tools available to them, understand the parameters required to use these tools, invoke them, and then process the results. This standardization is critical because it obviates the need for custom, one-off integrations for each pairing of an AI model and an external tool. Instead, it fosters a more interoperable and scalable ecosystem.4 As highlighted in multiple sources, MCP aims to convert what would traditionally be an M×N integration complexity (M AI clients needing to integrate with N tools) into a more manageable M+N problem, where tool creators build N MCP servers and application developers build M MCP clients.8 Communication within this architecture typically relies on JSON-RPC 2.0 messages, ensuring a structured, well-defined, and widely understood format for the exchange of information between clients and servers.8

The architectural design of MCP, with its clear demarcation between AI applications (Hosts/Clients like Copilot) and tool providers (Servers) 8, is a cornerstone of its flexibility and power. This separation allows for the independent development, deployment, and versioning of both the AI agents and the tools they consume. An AI client, such as GitHub Copilot in VSCode, is not limited to a single MCP server; it can connect to multiple servers simultaneously. This allows it to draw upon a diverse array of capabilities from different sources, as exemplified by the suggestion to use Neon Postgres MCP alongside Azure MCP for a comprehensive cloud-native development experience.13 Conversely, a single MCP server can be designed to serve multiple MCP-compatible clients, extending its utility beyond just GitHub Copilot to other AI tools like Claude Desktop or Cursor.8

Furthermore, the MCP architecture supports composability, where MCP servers can themselves act as clients to other MCP servers.22 This enables the creation of sophisticated, chained AI workflows, where tools can build upon the functionalities provided by other tools, leading to highly specialized and powerful sequences of operations. This "many-to-many" integration potential 22 is fundamental to MCP's vision of fostering a dynamic ecosystem. In such an ecosystem, specialized tools can be developed by various parties and readily integrated into diverse AI applications, leading to highly customizable, powerful, and composable AI-assisted development environments. This represents a significant advancement from monolithic AI tools that come with a fixed set of functionalities, offering power users unprecedented control over their AI-augmented workflows.

2.2 Core MCP Concepts: Servers, Clients, and "Tools"
To fully grasp MCP, understanding its core components is essential:

MCP Servers: These are software programs or services designed to act as intermediaries or wrappers. They take existing functionalities—whether from an API, a database, local scripts, or other systems—and expose these capabilities in a manner that is compliant with the MCP specification.8 A key aspect is their language independence; MCP servers can be implemented in a variety of programming languages, as long as they adhere to the protocol's communication standards.8
MCP Clients: In the context of this manual, the MCP client is the component embedded within the host application, which is GitHub Copilot running inside Visual Studio Code. The client's responsibilities include managing connections to one or more MCP servers, discovering the capabilities (primarily "tools") offered by these servers, forwarding requests from the AI model (Copilot) to the appropriate server tool, and then handling the responses received from the server.8
"Tools" in MCP: This is the most critical concept for the power user aiming to extend Copilot's capabilities.
Tools are the primary mechanism through which MCP servers provide functionalities to an AI agent. They represent specific, callable functions or discrete actions that the AI model (Copilot) can invoke to perform tasks or retrieve information.3
Each tool is meticulously defined by the server, including a unique name (for invocation), a human-readable description (vital for the AI to understand its purpose and relevance to a user's prompt), a schema detailing its input parameters (including their types and optionality), and a schema for its expected output or return value.8
It is important for users to understand that while the broader MCP specification also defines other types of server-provided capabilities such as "Resources" (for data access) and "Prompts" (pre-configured interactions) 6, the current integration of GitHub Copilot, especially its coding agent and its usage within VSCode, primarily focuses on the consumption of "Tools" from MCP servers.2
2.3 MCP Transport Mechanisms
MCP is designed to be flexible in how clients and servers communicate, supporting several transport mechanisms to cater to different deployment scenarios and technical requirements:

Standard Input/Output (stdio): This is a common method for local communication, employed when the MCP client (e.g., Copilot within VSCode) and the MCP server process are running on the same machine. In this setup, the client typically launches the server as a child process and then communicates with it by writing to its standard input and reading from its standard output.6 This transport is characterized by its simplicity and efficiency for local tools that might need to access the local file system, execute local command-line utilities, or interact directly with the local development environment. Visual Studio Code has robust support for configuring MCP servers to use the stdio transport.27
HTTP with Server-Sent Events (SSE): This transport mechanism is designed for scenarios where the MCP server is hosted remotely, i.e., not on the same machine as the client. The client establishes an HTTP connection to the server. After the initial handshake, the server can push messages or events to the client over this persistent connection using the SSE standard. This is particularly well-suited for web-based services or tools that are centrally hosted and accessed over a network.6 VSCode also supports sse for MCP server configurations.11
Streamable HTTP: This is a more recent addition to the MCP specification, also utilizing HTTP for communication. It aims to provide a potentially simpler, single-endpoint communication model compared to the often dual-endpoint (one for SSE, one for client messages) approach sometimes used with the traditional HTTP+SSE method.20 VSCode documentation indicates support for a generic http transport type for MCP servers, which likely encompasses this newer streamable HTTP approach.27
The availability of these diverse transport mechanisms is a key factor in MCP's broad applicability and adoption. The stdio transport 6 provides a low-overhead, direct integration path for local tools. This is essential for many developer-centric utilities that need to interact closely with the user's immediate environment, such as file system tools or local build and test scripts. The current restriction of the GitHub Copilot Coding Agent to local MCP servers 2 likely leverages stdio for reasons of security and simplicity in managing autonomous actions within a known environment.

On the other hand, HTTP+SSE 6 and Streamable HTTP 20 are indispensable for enabling connections to remote servers. This capability unlocks the integration of a vast array of services that cannot, or should not, run locally on every developer's machine. Examples include third-party APIs, cloud-hosted platforms (like the Neon Serverless Postgres MCP server, which uses a remote hosted model 13), and centralized enterprise tools.

By supporting these different transport protocols, MCP empowers developers and tool builders to select the most appropriate integration strategy. The choice will depend on the specific tool's architecture, its security requirements, its deployment model (local utility vs. scalable web service), and the nature of the data it handles. This inherent flexibility significantly expands the range of tools and services that can be seamlessly brought into the GitHub Copilot ecosystem, catering to the needs of individual developers working with local utilities as well as large organizations integrating complex, shared services.

Chapter 3: MCP Servers: Your Gateway to Enhanced Copilot Capabilities
3.1 Understanding MCP Servers and the "Tools" They Offer
The primary function of an MCP server, from the perspective of GitHub Copilot and its user, is to expose a collection of "tools".3 These tools are not to be confused with VSCode extensions themselves; rather, they are discrete functionalities or actions provided by the MCP server process that Copilot can invoke. Think of an MCP server as a specialized worker that Copilot can delegate specific tasks to.

Each tool represents a well-defined capability. For instance, a tool might allow Copilot to "create a new GitHub issue," "execute a specific SQL query against a database," or "fetch the content of a webpage." When a user makes a request to Copilot (typically in Agent Mode), Copilot's underlying AI model analyzes the request, identifies the most suitable tool(s) from the available MCP servers, and then invokes those tools to fulfill the request.20

Concrete examples abound:

The official GitHub MCP server offers a suite of tools for interacting with the GitHub platform, such as create_issue, list_pull_requests, search_code, get_file_content, and merge_pull_request.4
Database-oriented MCP servers, like the Neon Postgres server, provide tools for schema introspection (e.g., "list tables," "describe table schema") and SQL query execution.13
Utility servers might offer tools like fetch_url (from a Fetch MCP server) 7 or browse_webpage (from a Playwright MCP server).2
3.2 Local vs. Remote MCP Servers: Setup and Use Cases
MCP servers can be broadly categorized into local and remote, each with distinct setup procedures, use cases, and implications:

Local MCP Servers:
Setup: These servers execute directly on the user's local machine. VSCode typically initiates these server processes based on a command (e.g., a script, an executable, or a Docker command) specified in the user's MCP configuration files (.vscode/mcp.json or settings.json).2
Communication: Communication between Copilot (the client) and the local server usually occurs via the stdio (standard input/output) transport mechanism.6
Use Cases: Local MCP servers are ideal for tools that require access to the local file system, need to execute local command-line utilities, or interact with aspects of the local development environment. For example, a local MCP server could provide tools to run project-specific build scripts, interact with a locally running database instance, or perform static analysis using locally installed linters. A significant point is that the GitHub Copilot Coding Agent, in its current iteration, only supports local MCP servers.2 This design choice likely prioritizes security and control for autonomous actions performed by the agent within the context of a developer's repository and local environment.
Remote MCP Servers:
Setup: These servers are hosted on a network-accessible machine, which could be a cloud server, an on-premises server, or a third-party service provider's infrastructure. They are distinct from the user's local VSCode instance.
Communication: Remote servers are accessed over the network, typically using HTTP with Server-Sent Events (SSE) or the newer Streamable HTTP transport.6
Use Cases: Remote MCP servers are essential for integrating Copilot with cloud-based services (e.g., Azure services via the Azure MCP server 2), third-party APIs (such as interacting with a Sanity CMS through its dedicated MCP server 23), shared databases (like the Neon Serverless Postgres which offers a remote hosted MCP server 13), or centralized enterprise-specific internal tools that are not deployed on individual developer machines. VSCode provides full support for configuring and utilizing remote MCP servers.18
The distinction between local and remote MCP servers is fundamental, as it reflects different trust boundaries, deployment models, and the scope of capabilities they can offer. Local servers 2 operate within the developer's direct control and environment, implying a higher degree of implicit trust. This makes them suitable for tasks needing privileged access to local resources. The Copilot Coding Agent's current restriction to local servers 3 underscores a cautious approach, likely prioritizing security for autonomous operations by keeping execution within a more contained and user-monitored boundary.

Remote servers 13, conversely, are designed for broader accessibility and can be scaled and managed independently of individual developer setups. They are the natural choice for integrating services that are inherently network-based or are shared among multiple users or development teams. While local servers excel at leveraging the developer's immediate environment and local toolchains, remote servers are key to connecting Copilot to the vast world of external, often shared, data and services.

The configuration and authentication mechanisms also differ. Local servers often involve straightforward command execution, with credentials (like a GitHub Personal Access Token for the GitHub MCP server 4) potentially passed via environment variables or prompted inputs. Remote servers, on the other hand, may necessitate more complex authentication schemes, such as OAuth 2.1, to securely manage access.13 A power user must grasp these differences to select or develop the appropriate server type for their specific needs, configure them correctly within VSCode, and remain cognizant of the distinct security implications each model presents.

3.3 Tool Definition, Discovery, and Manifests: How Copilot Learns About Tools
For GitHub Copilot to effectively utilize an MCP server, it needs to understand what tools the server offers and how to use them. This involves a process of tool definition by the server, discovery by the client (Copilot), and adherence to a manifest structure.

Tool Definition by MCP Servers:
The onus of defining tools lies with the MCP server. Each tool must be described with sufficient detail for an AI agent to comprehend its purpose and usage. Key components of a tool definition typically include 3:
Name: A unique identifier for the tool (e.g., github.issues.create, database.executeQuery).
Description: A natural language explanation of what the tool does, its purpose, and when it might be useful. This is a critical piece of information for the Language Model (LLM) within Copilot to determine the tool's relevance to a user's prompt.
Input Schema: A formal definition of the parameters the tool accepts, including their names, data types, whether they are required or optional, and any validation rules. JSON Schema is often used for this purpose.
Output Schema: A definition of the structure and data types of the information the tool is expected to return upon successful execution. The Simplescraper blog provides an excellent conceptual breakdown, highlighting the name, parameter schema, description, and the crucial handler function that bridges the MCP tool definition to the actual underlying API call or logic.20 The fastmcp Python library demonstrates a programmatic approach using decorators like @mcp.tool() to define tools, where the function signature and docstring contribute to the schema and description respectively.8
Tool Discovery by Copilot (MCP Client):
When VSCode, acting as the MCP client for Copilot, connects to a configured MCP server, it initiates a discovery process to learn about the tools that server provides.7 This discovery typically occurs when the MCP server is started. For servers configured via .vscode/mcp.json, clicking the "Start" button in the VSCode editor for this file triggers the server launch and subsequent tool discovery. The discovered tools are then cached by VSCode for use in later sessions.7 The MCP specification itself outlines an initialization handshake during which the client and server exchange their capabilities, including the list of tools the server offers.19 The server responds to a discovery request with a manifest or list of its available tools.8
MCP Tool Manifest:
The MCP Tool Manifest is a machine-readable registry, commonly formatted in JSON, that enumerates and defines the external tools an AI agent like Copilot can invoke.25 It serves as a formal contract between the MCP server (tool provider) and the MCP client (tool consumer). This manifest is crucial for enabling dynamic discovery, understanding, and safe execution of external functions.
The manifest typically includes for each tool:
Identity (name)
Capabilities (description)
Invocation details (how to call it)
Parameters (input schema, types, optionality, validation rules)
Operational constraints
Scopes and permissions (security constraints specifying what the tool can access or modify).25 While a universally mandated JSON schema for the discovery response message itself is not explicitly detailed in many user-facing documents, the official MCP specification refers to its schema.ts file as the authoritative source for protocol requirements, which would define these structures.33 The MCP server exposes its list of tools through the protocol.22 For the GitHub Copilot Coding Agent, the tools array specified in its JSON MCP configuration 2 acts as a client-side filter or an explicit request list, determining which of the server's discovered tools are made available to the agent. The Java SDK for MCP also shows server capabilities being built, including a flag for tool support (ServerCapabilities.builder().tools(true)).28
Tool Selection by Copilot Agent Mode:
Once tools are discovered and their manifests are understood, GitHub Copilot's Agent Mode can select the most appropriate tool(s) based on the user's natural language prompt. The agent matches the user's intent against the descriptions and names of the available tools.20 For more direct control, users can bypass this autonomous selection by explicitly invoking a tool using the #tool_name syntax within the Copilot Chat prompt in VSCode.18
The effectiveness of Copilot's agentic capabilities hinges on the quality and clarity of these tool manifests and their descriptions. For Copilot to autonomously and accurately select and utilize an external tool in response to a user's request, it must first understand the tool's purpose, its required inputs, and the nature of its output. This understanding is derived directly from the metadata provided in the tool's definition within the MCP server's manifest.8 The natural language description of a tool is particularly vital, as it forms the primary basis upon which the LLM maps the user's intent to a specific tool's functionality.20 A poorly worded, ambiguous, or misleading description will inevitably lead to incorrect tool selection, failed invocations, or irrelevant results. Similarly, a well-defined parameter schema is essential to ensure that Copilot provides the tool with valid and correctly structured inputs, which is a prerequisite for successful execution.20 Without these rich, machine-readable self-descriptions from MCP servers, Copilot's capacity to function as an effective agent would be severely diminished. It would be largely confined to using only those tools explicitly invoked by the user or relying on overly simplistic and error-prone heuristics. The "invisible" integration and autonomous tool utilization, which are hallmarks of advanced MCP usage 3, are entirely dependent on this comprehensive metadata exchange.

The following table summarizes the key elements typically found in an MCP tool definition:

Table: Key Elements of an MCP Tool Definition

Element

Purpose

Example (Conceptual for a GitHub Issue Creation Tool)

Name

Unique identifier for the tool, used for invocation.

github.issues.create

Description

Natural language explanation of what the tool does, its purpose, and when it might be useful.

"Creates a new issue in a specified GitHub repository."

Parameter Schema (Input)

Defines the arguments the tool accepts, their types, optionality, and validation rules (e.g., JSON Schema).

{"owner": "string", "repo": "string", "title": "string", "body": "string (optional)"}

Handler Function / Invocation Details

The actual logic or API call the server executes when the tool is invoked. This is internal to the server but represented by the tool definition.

Server-side code that calls the GitHub API endpoint for creating issues.

Return Value Schema (Output)

Defines the structure and data types of the information the tool returns upon successful execution.

{"issue_url": "string", "issue_number": "integer"}

This structured approach to tool definition ensures that AI agents like Copilot can reliably and effectively extend their capabilities by leveraging external functionalities.

Chapter 4: Mastering MCP Server Configuration in VSCode
Effectively utilizing MCP servers with GitHub Copilot in Visual Studio Code requires a solid understanding of the prerequisites and the intricacies of configuration. Power users must be adept at setting up both local and remote servers, managing credentials securely, and understanding how VSCode discovers and activates these external tools.

4.1 Prerequisites for Running MCP Servers
Before diving into MCP server configuration, ensure the following prerequisites are met:

Visual Studio Code Version: Support for MCP in Copilot's Agent Mode is available in VSCode version 1.99 and later. It's crucial to run an up-to-date version of VSCode to access these features.27
GitHub Copilot Extensions: The GitHub Copilot and GitHub Copilot Chat extensions must be installed and enabled in VSCode. These extensions provide the client-side functionality for interacting with MCP servers.4
Relevant Runtimes: Depending on how a specific MCP server is packaged and executed, you may need corresponding runtimes installed on your system and available in your system's PATH. Common requirements include:
Node.js (often with npx) for servers distributed as NPX packages.4
Python for servers distributed as PIP packages.4
Docker if the MCP server is designed to run as a Docker container.4
Other language-specific runtimes if the server is a compiled executable or script.
MCP Enabled in VSCode Settings: The primary setting to ensure MCP support is active is chat.mcp.enabled. By default, this setting is usually true, but it's worth verifying in your VSCode settings (JSON or UI).18 An older, potentially deprecated setting github.copilot.advanced.mcp.enabled has been mentioned in some community discussions 37, but chat.mcp.enabled appears to be the current official setting referenced in VSCode documentation.27
4.2 Configuration Deep Dive: .vscode/mcp.json and settings.json
VSCode offers two primary locations for configuring MCP servers, allowing for flexibility in scope and sharing:

Workspace-Specific Configuration (.vscode/mcp.json):
Creating a file named mcp.json inside the .vscode directory at the root of your project workspace allows you to define MCP servers that are specific to that project.
This configuration is ideal for tools that are relevant only to the current project or for sharing a common set of MCP server configurations with team members who clone the repository (assuming .vscode/mcp.json is committed to version control).7
When you open a .vscode/mcp.json file in the VSCode editor, helper commands often appear at the top of the file, allowing you to easily start, stop, or restart the configured servers directly from the editor interface.27
User-Specific (Global) Configuration (settings.json):
You can configure MCP servers globally for your personal VSCode instance by adding the configuration to your user settings.json file. These servers will then be available across all your workspaces.
This approach is suitable for general-purpose MCP servers that you use frequently, regardless of the specific project you are working on.7
It is generally recommended to configure a given MCP server in only one location (either workspace or user settings) to prevent potential conflicts or unexpected behavior that might arise from duplicate definitions.7
While the primary focus for VSCode is these two locations, it's worth noting that other MCP-compatible environments like Visual Studio or Cursor might use other conventional file paths (e.g., %USERPROFILE%\.mcp.json, <SOLUTIONDIR>\.mcp.json).31 This guide, however, will concentrate on the VSCode-specific methods.

JSON Structure for MCP Server Configuration:

The configuration for MCP servers in VSCode follows a specific JSON structure.

If configuring in user settings.json, the MCP server definitions will be nested under a top-level "mcp" key, which then contains a "servers" object.
If configuring in .vscode/mcp.json, the root of the JSON file is typically the "servers" object itself (or sometimes just the server definitions directly, though nesting under "servers" is common for consistency with settings.json structure if it also contains an inputs array).
The "servers" object contains key-value pairs:

Key: A unique, descriptive name for the MCP server. Conventions suggest using camelCase (e.g., "githubMcp", "neonDB") and avoiding special characters or whitespace. This name is used by VSCode to identify and manage the server.2
Value: An object containing the specific configuration details for that server.
The server configuration object itself can contain the following fields:

Parameter

Data Type

Req/Opt

Description

Scope (Primary)

Example Value/Snippet

Snippet Refs

command

string

Required (for stdio/local)

The command to execute to start the MCP server (e.g., "npx", "docker", "python"). Must be on system PATH or a full path. For Docker, do not use detach options.

User/Workspace

"npx", "docker"

3

args

string

Optional

An array of arguments to pass to the command.

User/Workspace

["-y", "@modelcontextprotocol/server-github"]

3

env

object

Optional

Key-value pairs of environment variables to set for the server process. Values can be strings or reference VSCode input variables (e.g., ${input:apiKey}).

User/Workspace/Coding Agent

{"API_KEY": "${input:myApiKey}"}

3

envFile

string

Optional

Path to a .env file from which to load additional environment variables. Supports VSCode variables like ${workspaceFolder}.

User/Workspace

"${workspaceFolder}/.env.local"

27

type

string

Optional

Specifies the server connection type. For VSCode: "stdio", "sse", "http". For Copilot Coding Agent (GitHub repo settings): only "local" is currently accepted.

User/Workspace/Coding Agent

"stdio", "sse"

3

url

string

Required (for sse/http)

The endpoint URL for remote MCP servers using sse or http transport.

User/Workspace

"<https://mcp.neon.tech/sse>"

27

tools

string

Optional (Primarily Coding Agent)

An allowlist of tool names from the MCP server to enable. "*" enables all tools. VSCode Agent Mode allows UI-based tool toggling.

Coding Agent

["get_issue_details", "get_issue_summary"], ["*"]

2

inputs

array

Optional (VSCode specific)

Defines input variables that VSCode will prompt the user for, often used for securely obtaining secrets like API keys. Each object in the array defines an input.

User/Workspace

See structure below

7

inputs.id

string

Required (if inputs used)

Unique identifier for the input variable, referenced as ${input:id}.

User/Workspace

"githubPat"

27

inputs.type

string

Required (if inputs used)

Type of input. Commonly "promptString".

User/Workspace

"promptString"

27

inputs.description

string

Optional

Description shown to the user when prompted for the input.

User/Workspace

"GitHub Personal Access Token"

27

inputs.password

boolean

Optional

If true, the input will be masked (e.g., for passwords/tokens). Defaults to false.

User/Workspace

true

27

Example: Neon Postgres MCP Server (Remote SSE in settings.json) 13

This server uses a remote hosted option, simplifying setup as it doesn't require local installation of the server itself, only the mcp-remote bridge tool via npx.

JSON

{
"mcp": {
"servers": {
"NeonPostgres": { // Descriptive server name
"command": "npx",
"args":
// No 'inputs' needed here as OAuth is handled by the browser via mcp-remote
}
}
}
}

Upon starting this server, VSCode will likely trigger mcp-remote, which will open a browser window for OAuth authentication with Neon.

Example: GitHub MCP Server (Local Docker via stdio in .vscode/mcp.json) 4

This example demonstrates running the official GitHub MCP server as a Docker container locally. It uses the inputs array to securely prompt for the GitHub Personal Access Token.

JSON

{
"inputs":,
"servers": {
"GitHubMCP": { // Server name
"type": "stdio", // Communication via standard input/output
"command": "docker",
"args":
// 'env' could also be used here if preferred over -e in args:
// "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${input:githubPat}" }
}
}
}

When this server is started, VSCode will first prompt the user for the "githubPat" value, mask it, and then substitute it into the Docker command.

Example: Fetch MCP Server (Local stdio in .vscode/mcp.json) 7

This server allows Copilot to fetch content from URLs. The uvx command suggests it might be a utility or package runner.

JSON

{
// The 'inputs' array might be minimal or absent if the fetch server
// doesn't require specific API keys for basic operation.
// If it did (e.g., for authenticated fetches), an input would be defined here.
"inputs":,
"servers": {
"WebFetch": { // Server name
"type": "stdio",
"command": "uvx", // Placeholder for actual command/package manager
"args": ["mcp-server-fetch"] // Arguments to start the fetch server
// If 'fetchApiKey' input was defined:
// "env": { "FETCH_API_KEY": "${input:fetchApiKey}" }
}
}
}

Automatic Discovery from Claude Desktop Configuration:

For users who also use Claude Desktop and have MCP servers configured there, VSCode offers a convenience feature. If the chat.mcp.discovery.enabled setting is true (which is often the default), VSCode can automatically find and use your existing Claude Desktop MCP configurations.7 This streamlines setup if you're already invested in the MCP ecosystem through other tools.

4.3 Secure Credential Management: PATs, Environment Variables, and Secrets
MCP servers frequently require credentials (API keys, Personal Access Tokens (PATs), etc.) to interact with the services they expose. Managing these credentials securely is paramount. Hardcoding secrets directly into mcp.json or settings.json files is strongly discouraged, especially if these files are shared, committed to version control, or if the machine is used by multiple users.27

VSCode and the MCP configuration schema provide several mechanisms for more secure credential handling:

Using VSCode Input Variables (${input:variableId}):
This is a VSCode-specific mechanism. You define an inputs array in your mcp.json or settings.json (if using the mcp top-level key). Each object in this array describes an input VSCode should prompt the user for (e.g., an API key or PAT).27
The id field gives the input a name (e.g., "githubPat").
The type is typically "promptString".
A description tells the user what to enter.
Setting password: true ensures the input is masked in the VSCode prompt, preventing shoulder-surfing.31
Once the user provides the value, VSCode securely stores it (scoped to the workspace or user settings where defined) and substitutes it wherever ${input:id} is used in the args or env fields of the server configuration.4 This is the recommended way to handle secrets for MCP servers configured directly within VSCode. Source 39 mentions that VSCode stores these prompted values securely.
Using Environment Files (envFile):
The envFile property in a server configuration object allows you to specify the path to a standard .env file.27 The MCP server process will then be started with the environment variables defined in this file.
This method is suitable for non-sensitive configuration parameters or for development-specific overrides that you don't want in the main JSON configuration.
Crucial Security Note: If a .env file contains sensitive secrets, it must not be committed to version control. Ensure it is listed in your project's .gitignore file.
Direct Environment Variables (env object):
The env object in a server configuration allows you to directly set environment variables that will be available to the MCP server process.2
While you can place string literals here, it is highly recommended to use this in conjunction with ${input:variableId} for sensitive values to avoid hardcoding. For example: "env": { "API_TOKEN": "${input:myToken}" }.
GitHub Personal Access Tokens (PATs) for the GitHub MCP Server:
The @modelcontextprotocol/server-github (or its ghcr.io Docker image equivalent) requires a GitHub PAT to authenticate its API calls to GitHub.4
Security Best Practice - Principle of Least Privilege: It is critical to create a fine-grained PAT with the minimum necessary scopes for the actions Copilot will perform via this server.2
The documentation for @modelcontextprotocol/server-github 17 often suggests the broad repo scope ("Full control of private repositories") or public_repo (for public repositories only). While this ensures functionality for all its tools, power users should critically assess which tools they will actually use.
For example, if you only need to read issues and repository content, more granular scopes like repo:read (or specific read permissions under fine-grained PATs) and issues:read would be more secure than full repo control. If you need to create issues, issues:write would be required. For creating pull requests, pull_requests:write is necessary. The GitHub MCP server exposes tools like create_issue, create_pull_request, merge_pull_request, get_issue, list_pull_requests etc..17 The necessary PAT scopes will depend on which of these tools are enabled in your MCP server configuration (if you use the tools allowlist) and which ones you intend Copilot to use.
A user in a GitHub discussion 42 highlighted the strategy of using separate MCP servers for different GitHub functionalities (e.g., one for GHAS) to apply more granular PAT scopes to each, which is an advanced security consideration.
PAT Security Hygiene: Always treat PATs as highly sensitive credentials. They should be kept secret, never shared publicly, and absolutely not committed to version control repositories.4 Use expiration dates for PATs.
Secrets for Copilot Coding Agent's MCP Servers (Repository Settings):
When configuring MCP servers for the GitHub Copilot Coding Agent (which is done via the repository settings on GitHub.com, not directly in VSCode's JSON files), secrets are managed using GitHub Actions environment secrets.2
These secrets must be created within a dedicated GitHub environment named copilot for that repository.
Crucially, the names of these secrets must be prefixed with COPILOT_MCP_ (e.g., COPILOT_MCP_SENTRY_AUTH_TOKEN, COPILOT_MCP_NOTION_API_KEY).2 Only secrets following this naming convention will be available to the MCP server configuration.
A special secret name, COPILOT_MCP_GITHUB_PERSONAL_ACCESS_TOKEN, is used to provide a PAT if the built-in GitHub MCP server used by the Coding Agent needs to access data outside the current repository or requires permissions beyond the default GITHUB_TOKEN.2 For this specific PAT, GitHub documentation recommends using a fine-grained PAT with read-only permissions on specific repositories, unless broader write access is demonstrably essential.2
The robust and secure handling of credentials is not merely a recommendation but a necessity when integrating MCP servers. These servers, by design, often require privileged access to valuable data and powerful APIs.3 Hardcoding sensitive information like PATs or API keys directly into configuration files that might be shared or version-controlled 27 introduces a significant and unacceptable security vulnerability. VSCode's inputs mechanism for prompting 27, and GitHub's environment secrets system for the Copilot Coding Agent 2, offer far more secure alternatives by either prompting the user at runtime or leveraging secure secret storage facilities. Adherence to the principle of least privilege when defining PAT scopes 2 is another critical layer of defense, minimizing the potential impact should a credential be inadvertently exposed. Power users must be acutely aware of the permissions they grant to any MCP server and diligently employ these secure credential management practices.

4.4 Activating and Managing MCP Servers within VSCode
Once MCP servers are defined in your VSCode configuration, you need to start them to make their tools available to GitHub Copilot.

Starting Servers:
If you have configured servers in a .vscode/mcp.json file, VSCode often provides a "Start" button directly within the editor when this file is open. This button typically appears at the top of the list of defined servers. Clicking it will initiate the startup process for all servers defined in that file. This process may also trigger any input dialogs for secrets defined in the inputs array and will initiate the tool discovery phase.7
VSCode may also display individual commands (like start, stop, restart) for each server defined in .vscode/mcp.json directly in the editor's title bar or context menu when the file is active, offering more granular control.27
For MCP servers configured in the user settings.json file, they might be started automatically when VSCode launches, or when GitHub Copilot Chat initializes, though the exact behavior can vary.
Viewing Server Status and Available Tools:
To get an overview of your configured MCP servers and their current status (e.g., running, stopped), you can use the MCP: List Servers command from the VSCode Command Palette (Ctrl+Shift+P or Cmd+Shift+P).18
This view typically allows you to see the configuration of each server and, importantly, access its logs, which is invaluable for troubleshooting.40
Within GitHub Copilot Chat, when Agent Mode is active, clicking the "tools" 🔧 icon (usually located near the chat input area) will display a list of all currently available MCP servers and the specific tools each server has successfully exposed to Copilot.4 This is the primary way to confirm that your MCP servers are running and that Copilot is aware of their capabilities.
Chapter 5: Unleashing MCP Tools with Copilot Agent Mode in VSCode
The true power of MCP servers is realized when they are used in conjunction with GitHub Copilot's Agent Mode in Visual Studio Code. This mode transforms Copilot from a suggestion-based assistant into a more autonomous entity capable of orchestrating complex tasks.

5.1 Copilot Agent Mode: The Engine for MCP Tool Interaction
Copilot Agent Mode is a significant evolution of Copilot's capabilities within VSCode. It enables Copilot to autonomously plan and execute multi-step tasks based on high-level natural language prompts from the user. This goes far beyond simple code completion or single-shot chat responses.5

In Agent Mode, Copilot can:

Analyze the existing codebase to understand context.
Propose and apply edits across multiple files.
Execute terminal commands (e.g., for building, testing, or installing dependencies).
Monitor for errors (compile errors, lint errors, test failures) and attempt to self-correct by iterating on its actions.5
MCP servers and their tools are the primary mechanism by which Agent Mode extends its actions beyond built-in capabilities to interact with external systems and data.27 Agent Mode is available in VSCode version 1.99 and newer and must be explicitly enabled via the chat.agent.enabled setting in VSCode.27

The combination of Agent Mode's autonomous task execution capabilities 5 with MCP's standardized interface for external tool interaction 3 represents a significant leap towards more autonomous development assistance. Agent Mode provides the "brain" for planning and iteration, while MCP provides the "senses" and "hands" for that brain to interact with the broader digital environment. This synergy allows Copilot to not only reason about code but also to actively perform actions like fetching web content 7, querying databases 13, or managing GitHub issues and pull requests 4 as integral parts of its autonomous task completion process. This is the "supercharged" Copilot experience that power users seek, where Copilot functions less like a passive assistant and more like a proactive junior developer or an intelligent agent that can be delegated complex tasks.

5.2 Discovering and Selecting Available MCP Tools in Agent Mode
Once your MCP servers are correctly configured in VSCode and successfully started, the tools they provide become discoverable and available for use within Copilot's Agent Mode.

To view the tools that Copilot Agent Mode is aware of:

Ensure you are in the GitHub Copilot Chat view within VSCode.
Switch the chat mode to "Agent" (usually via a dropdown near the chat input field).
Click on the "Tools" 🔧 icon. This icon is typically located in the Copilot Chat panel, often near the input box or in a toolbar section of the chat interface.4
This action will open a list or panel displaying all the MCP tools that have been successfully discovered from your active MCP servers. From this list, you can often select or deselect specific tools, giving you granular control over which capabilities Copilot Agent Mode can utilize for a particular request or session.27 Some interfaces may also provide a search box to quickly find tools by name if the list is extensive.27

5.3 Invoking Tools: Natural Language and Explicit Commands (#tool_name)
There are two primary ways to instruct Copilot Agent Mode to use the tools provided by MCP servers:

Natural Language Invocation:
This is the more "agentic" way of interacting. You describe the task you want Copilot to perform in natural language. Copilot Agent Mode then analyzes your prompt, and based on the descriptions of the available tools (as defined in their manifests by the MCP servers), it autonomously determines which tool(s) are most relevant and how to invoke them to achieve your goal.4 For example, prompting "Create a bug report for the login issue we discussed" might lead Copilot to select a create_issue tool from a configured GitHub MCP server.
Explicit Invocation (#tool_name):
For more direct control, or when you know exactly which tool you want to use, you can explicitly invoke an MCP tool within your chat prompt. This is done by typing the # symbol followed by the specific name of the tool (e.g., #github.issues.createIssue, #web.fetchUrl).18
This explicit invocation method is powerful because it bypasses Copilot's tool selection logic and directly targets a known capability.
According to VSCode documentation, this #tool_name syntax is generally available in all Copilot chat modes (ask, edit, and agent mode), not just limited to Agent Mode.27
When a tool is about to be invoked (either autonomously or explicitly), VSCode often provides an interface where you can review and even edit the input parameters that Copilot is about to send to the tool. This is typically accessed by clicking a chevron or expansion icon next to the tool name in the chat UI before confirming the execution.27
5.4 The Tool Approval Workflow: Ensuring Control and Security
A critical aspect of using MCP tools with Copilot Agent Mode is the tool approval workflow. Because MCP tools can potentially run arbitrary code, modify files, make external API calls, or execute terminal commands, there's an inherent security consideration.

Default Behavior: User Confirmation Required:
By default, when Copilot Agent Mode decides to invoke an MCP tool (especially a non-built-in tool or one that performs actions with side effects), it will first request explicit confirmation from the user before proceeding.21
This confirmation prompt usually displays the name of the tool Copilot intends to use and the input parameters it has prepared for that tool.21 This transparency allows you to verify what action is about to be taken.
Scoped Approval Options:
When presented with a tool invocation confirmation, VSCode typically offers several options for approval, allowing you to tailor the level of trust for specific tools 27:
Allow Once: Approve the tool invocation for the current instance only.
Allow for Session: Approve the tool for all invocations during the current VSCode session.
Allow for Workspace/Solution: Approve the tool for all invocations within the current workspace. This approval is typically remembered for future sessions in that workspace.
Allow Always (Auto-Approve Specific Tool): Permanently approve this specific tool for all future invocations across all workspaces. These scoped approval options provide a balance between security (requiring confirmation for new or potentially risky tools) and convenience (reducing repetitive prompts for frequently used, trusted tools).
Managing Approvals:
Tool approval selections can usually be managed or reset. For example, in Visual Studio, this is done via Tools > Options > GitHub > Copilot > Tools.31 Similar settings or commands likely exist in VSCode for managing these remembered approvals.
Experimental Auto-Approval (Use with Extreme Caution):
There may be experimental settings like chat.tools.autoApprove that can bypass the confirmation step for all tools.14 However, enabling such a setting significantly increases risk, as it removes the user's ability to vet potentially harmful or unintended actions before they are executed. It should only be considered in highly controlled and trusted environments.
The tool approval workflow is a deliberate design choice that balances the power of AI automation with the need for user control and security. MCP tools can perform potent actions, including file modifications, API interactions, and command executions.3 Allowing an AI to autonomously carry out such operations without any oversight would present a substantial security risk. The confirmation step 21 ensures that the user remains in the loop, is aware of Copilot's intended actions, and has the opportunity to prevent unintended or malicious consequences. The provision of scoped approval options (current session, workspace, always for a specific tool) 27 offers a flexible approach, enabling users to streamline their workflow by reducing repetitive confirmations for tools they frequently use and trust, while maintaining a necessary level of caution for new, unfamiliar, or particularly powerful tools. This reflects a user-centric security model that acknowledges both the benefits of automation and the imperative of maintaining control.

5.5 Practical Power Plays: Example MCP Servers and Their Tools
To illustrate the practical power of MCP servers, let's explore some common examples and how their tools can be leveraged within VSCode Copilot Chat's Agent Mode.

5.5.1 The GitHub MCP Server (@modelcontextprotocol/server-github or ghcr.io/github/github-mcp-server)

This is arguably one of the most valuable MCP servers for developers using GitHub. It allows Copilot to interact directly with the GitHub API, automating many common repository management and development tasks.4 Configuration typically involves providing a GitHub Personal Access Token (PAT) with appropriate scopes (see Chapter 4.3 and Chapter 7.1 for security details).

Key Tools & Example Use Cases (derived from 4):
create_issue:
Natural Language: "Copilot, create a bug report in the my-awesome-app repository for the parser.js file, titled 'Parsing error with large JSON inputs' and describe the issue as 'The parser hangs when processing JSON files over 10MB'."
Explicit: #github.create_issue {"owner": "my-org", "repo": "my-awesome-app", "title": "Parsing error with large inputs", "body": "The parser hangs..."}
list_issues:
Natural Language: "@github Can you list all open issues assigned to me in the my-project/backend repository that are labeled 'bug'?"
Explicit: #github.list_issues {"owner": "my-project", "repo": "backend", "assignee": "@me", "labels": ["bug"], "state": "open"} 31
get_pull_request / list_pull_requests:
Natural Language: "What's the status of pull request #123 in my-org/my-repo? Summarize the changes."
Explicit: #github.get_pull_request {"owner": "my-org", "repo": "my-repo", "pull_number": 123}
create_pull_request:
Natural Language: "Create a pull request for the current branch feature/new-auth to merge into the develop branch. Title it 'Implement OAuth2 Authentication' and add a description about the new endpoints."
Explicit: #github.create_pull_request {"owner": "my-org", "repo": "my-app", "head": "feature/new-auth", "base": "develop", "title": "Implement OAuth2 Authentication", "body": "Adds new /auth/oauth2 endpoints..."} 17
add_issue_comment / create_review_on_pull_request:
Natural Language: "Add a comment to issue #45 in another-org/another-repo asking for clarification on the acceptance criteria."
Explicit (comment): #github.add_issue_comment {"owner": "another-org", "repo": "another-repo", "issue_number": 45, "body": "Could you please clarify the expected behavior for invalid inputs?"} 17
merge_pull_request:
Natural Language: "Merge PR #67 in my-org/my-repo using the squash method and add 'Closes #65' to the commit message."
Explicit: #github.merge_pull_request {"owner": "my-org", "repo": "my-repo", "pull_number": 67, "merge_method": "squash", "commit_message": "Closes #65"} 17
Code Search (implied capability via GitHub API access) 4:
Natural Language: "Search public GitHub repositories for Python examples of using the asyncio.gather function with error handling."
File Reading (implied capability) 4:
Natural Language: "Read the CONTRIBUTING.md file from the expressjs/express repository and tell me about their PR guidelines." The GitHub MCP server is also a core component for the GitHub Copilot Coding Agent, which operates on GitHub.com, leveraging these tools for autonomous task completion.2
5.5.2 Database MCP Servers (e.g., Neon Postgres MCP Server)

These servers empower Copilot with the ability to understand database schemas, generate SQL queries, and sometimes even interact with database data or metadata.13 The Neon Postgres MCP server is a notable example, offering a remote hosted option that simplifies setup by requiring only an npx command for its bridge tool and OAuth authentication.13

Key Tools & Example Use Cases (based on 13):
Schema Introspection:
Natural Language: "What are the columns in the customers table in my Neon database? Include their data types."
Explicit (conceptual): #neonDB.get_table_schema {"table_name": "customers"}
SQL Query Generation & Execution:
Natural Language: "Generate a SQL query for my Neon Postgres DB to find all users from 'Canada' who registered in the last 30 days and have made at least one purchase. Then, can you run it and show me the results?"
Explicit (conceptual for generation): #neonDB.generate_sql {"prompt": "Find Canadian users registered last 30 days with purchases"}
API Data Model Generation:
Natural Language: "Based on the products table schema in Neon, help me generate a Python Pydantic model for an API response."
Connection String Management / Environment Variable Updates:
Natural Language: "Fetch the connection string for my 'staging' Neon database and set it as the DATABASE_URL environment variable in my Azure Function App settings."
Database/Table Creation & Modification (with caution and appropriate permissions):
Natural Language: "Create a sample product_reviews table in my Neon database with columns for review_id, product_id, user_id, rating, comment, and created_at."
Data Population (Mock Data):
Natural Language: "Populate the customers table in Neon with 10 rows of mock data."
5.5.3 Cloud Service MCP Servers (e.g., Azure MCP Server)

These servers bridge Copilot to various cloud platform services, enabling interaction with resources like storage, queues, AI services, and more.13 The Azure MCP server, for example, allows Copilot to understand and potentially manipulate Azure resources. It can be used in conjunction with other MCP servers (like Neon MCP) for a comprehensive cloud development experience.13 The Copilot Coding Agent also has support for the Azure MCP server.2

Key Tools & Example Use Cases (based on 2):
Blob Storage Interaction:
Natural Language: "Upload the file report.pdf from my local Downloads folder to the monthly-reports container in my Azure Blob Storage account."
Explicit (conceptual): #azure.blob_upload {"source_file": "Downloads/report.pdf", "container": "monthly-reports", "blob_name": "report.pdf"}
Queue Interaction:
Natural Language: "What are the current messages in the Azure Queue named image-processing-tasks?"
Service Provisioning (evolving capability):
Natural Language (future): "Spin up a new Azure Function with an HTTP trigger and a Cosmos DB output binding." 13
5.5.4 Utility MCP Servers (e.g., Fetch, Playwright, Pieces)

This category includes servers providing general-purpose utilities that can enhance Copilot's ability to gather information or interact with various systems.

Fetch MCP Server:
Allows Copilot to retrieve the content of a given URL.7
Natural Language: "Fetch the content of the Mozilla Developer Network page for JavaScript Promises and summarize its key points."
Explicit: #fetch {"url": "<https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise"}> (Tool name might vary, e.g., #web.fetchUrl) 7
Playwright MCP Server:
Provides tools for browser automation, enabling Copilot to interact with web pages, extract information, or even perform actions on websites. This is particularly useful for the Copilot Coding Agent to gather context from web documentation or live web applications.2
Natural Language (conceptual): "Analyze the DOM structure of example.com/product-listing and identify all elements with the class product-price."
Pieces MCP Server:
Integrates with Pieces, a tool for saving and reusing code snippets and other development-related materials. The Pieces MCP server allows Copilot to access this "Long-Term Memory" (LTM).29
Tool: ask_pieces_ltm.29
Natural Language: "Search my Pieces LTM for Python snippets related to asynchronous file I/O that I've used in the past."
The following table provides a consolidated view of these example MCP servers and their tools:

Table: Example MCP Servers and Common Tools

MCP Server Category

Example Server Name

Key Tool(s) (Conceptual/Actual)

Example VSCode Chat Invocation (Natural Language & Explicit)

Typical Use Case

Version Control

GitHub MCP Server (@modelcontextprotocol/server-github)

create_issue, list_pull_requests, merge_pull_request, search_code, get_file_content

"Create a P1 bug for 'login fails' in my/repo." <br/> #github.create_issue {"repo": "my/repo",...}

Automating GitHub workflows, repository management, code search.

Databases

Neon Postgres MCP Server

get_table_schema, execute_sql_query, generate_sql_query

"What columns are in the orders table (Neon)?" <br/> #neonDB.get_table_schema {"table_name": "orders"}

Database schema understanding, query generation and execution, data interaction.

Cloud Services

Azure MCP Server

upload_blob, list_queue_messages, (future: provision_service)

"List messages in Azure queue processing_queue." <br/> #azure.list_queue_messages {"queue_name": "processing_queue"}

Interacting with cloud resources (storage, queues, AI services), service provisioning.

Web Utilities

Fetch MCP Server

fetch_url (or similar)

"Fetch contents of example.com/api/docs." <br/> #fetch {"url": "example.com/api/docs"}

Retrieving content from web pages for context or analysis.

Browser Automation

Playwright MCP Server

browse_webpage, extract_element_text

"Summarize the main content of github.blog." <br/> #playwright.summarize_page {"url": "github.blog"}

Web scraping, UI interaction, gathering context from live web pages.

Developer Productivity

Pieces MCP Server

ask_pieces_ltm

"Find my saved Python snippets for JWT authentication." <br/> #pieces.ask_ltm {"query": "python jwt auth"}

Accessing and reusing personal code snippets and development knowledge.

These examples showcase the breadth of capabilities that MCP servers can bring to GitHub Copilot, transforming it into a far more dynamic and powerful assistant for power users.

Chapter 6: MCP in the Copilot Extensibility Ecosystem
The Model Context Protocol and its server-based tools represent a significant pathway for extending GitHub Copilot's capabilities within VSCode. However, it's important for power users to understand how MCP fits into the broader Copilot extensibility landscape, which also includes direct usage of VSCode's Copilot APIs by extensions and the separate concept of GitHub Copilot Extensions (which are GitHub Apps).

6.1 MCP Tools vs. VSCode Native Copilot API Usage by Extensions
A key distinction lies in where the "tool" logic executes and what APIs it can access:

MCP Tools (via MCP Servers):
Execution Environment: MCP server processes run externally to the VSCode extension host. They can be local child processes launched by VSCode (e.g., a Docker container or a Node.js script) or entirely remote services accessed over HTTP/SSE.44
VSCode API Access: Crucially, MCP tools themselves do not have direct access to the rich set of Visual Studio Code extension APIs (e.g., APIs for manipulating editor content directly, accessing VSCode's UI elements, or interacting with other extensions' states).44 Their interaction with VSCode is mediated by Copilot and the MCP protocol.
Activation: MCP tools are typically invoked by Copilot's Agent Mode, either autonomously based on the user's natural language prompt and the tool's description, or explicitly by the user via the #tool_name syntax in Copilot Chat.6
Ideal For: Connecting Copilot to existing external services, databases, command-line utilities, or any functionality that can be wrapped in a standalone server process and doesn't require deep, direct interaction with the VSCode editor's internal state or UI.
VSCode Extensions Using Native Copilot APIs (Language Model API, Chat API, Tool API):
Execution Environment: These are standard VSCode extensions that run within the VSCode extension host environment.44
VSCode API Access: As native VSCode extensions, they have full access to the entire suite of VSCode extension APIs. This allows them to deeply integrate with the editor, manipulate workspace content, contribute UI elements, and interact with other parts of VSCode.44
Copilot Integration Options:
Agent Mode Tool Contribution: Extensions can use the Language Model Tool API to contribute a tool directly to Copilot's Agent Mode. Such tools are invoked automatically by the agent based on the user's prompt and can leverage other VSCode APIs in their execution.44
Chat Participant: Extensions can use the Chat API and Language Model API to create custom chat participants (e.g., @mycorp or @mydomainexpert) for Copilot Chat's "ask mode." These participants can answer domain-specific questions using natural language, leveraging the extension's logic and VSCode context.6
Custom AI-Powered Features: Extensions can directly use Copilot's Language Model API along with other VSCode APIs to build entirely custom AI-powered features that are deeply embedded within the editor experience, enhancing specific interactions or workflows.44 Examples include AI-assisted coding annotations, AI-powered code reviews within the editor, or custom data retrieval actions tied to editor events.
Ideal For: Features that require tight integration with the VSCode editor, direct manipulation of the workspace or editor state, custom UI contributions within VSCode, or leveraging VSCode-specific contextual information that wouldn't be available to an external MCP server.
6.2 MCP Tools (in VSCode) vs. GitHub Copilot Extensions (GitHub Apps)
Another important distinction is between MCP tools used within VSCode and the concept of "GitHub Copilot Extensions," which are built as GitHub Apps:

MCP Tools (via MCP Servers in VSCode):
Primary Scope: Their main purpose is to enhance GitHub Copilot's capabilities specifically within the Visual Studio Code IDE (and potentially other IDEs that adopt MCP client support).7
Configuration: Setup is typically local to the user's VSCode environment (user settings.json) or a specific workspace (.vscode/mcp.json).7
Nature: They extend Copilot's ability to interact with external processes or services from within the IDE.
GitHub Copilot Extensions (built as GitHub Apps):
Implementation: These are implemented as GitHub Apps, which are server-side applications that can interact with the GitHub platform via its APIs. They are augmented with specific capabilities to integrate with GitHub Copilot.6
Cross-Platform Availability: A key characteristic is that GitHub Copilot Extensions are designed to work across all supported Copilot surfaces. This includes not only IDEs (like VSCode, Visual Studio, JetBrains) but also GitHub.com (e.g., in PR summaries, issue discussions) and the GitHub Mobile app.6
VSCode API Access: They generally do not have access to VSCode-specific functionalities or the deep editor context available to native VSCode extensions.44 Their context is more centered around GitHub data and user interactions on the GitHub platform.
Distribution: These extensions can be private to an organization, public and shareable, or listed on the GitHub Marketplace for wider discovery and installation.51
"Copilot Agents" (within GitHub Copilot Extensions): The term "Copilot agent" is also used in the context of GitHub Copilot Extensions. Here, it refers to custom tools or functionalities embedded within these GitHub App-based extensions that integrate with Copilot Chat to provide specialized behaviors.52 These agents often involve a server-side component and can leverage the GitHub API and potentially the Copilot API for their operations.6
6.3 Choosing the Right Extensibility Path
For a power user looking to extend GitHub Copilot in VSCode, understanding these distinctions is crucial for choosing the most appropriate development or integration path:

When to use MCP Servers with VSCode:
To integrate existing external tools, services, or APIs into Copilot's Agent Mode within VSCode.
When the functionality can be encapsulated in a standalone server process (local or remote) and does not require direct, deep access to VSCode's internal APIs or UI.
For relatively quick integration of utilities or data sources that Copilot can then autonomously leverage.
When to build a VSCode Extension using Copilot APIs:
For features that need to be deeply embedded within the VSCode user experience.
When direct access to and manipulation of the editor's content, workspace files, VSCode UI elements, or other VSCode extension states is necessary.
To create custom chat participants for highly domain-specific interactions within Copilot Chat that are tightly coupled with the VSCode environment.
When to build a GitHub Copilot Extension (GitHub App):
If the goal is to provide a service or tool that works consistently across multiple GitHub Copilot surfaces (various IDEs, GitHub.com, GitHub Mobile), not just VSCode.
When the primary interaction context is with GitHub data (repositories, issues, PRs) and the GitHub API, rather than the local IDE environment.
For distributing a Copilot-enhancing tool or service broadly via the GitHub Marketplace.
The Copilot extensibility landscape offers a layered set of integration options, each catering to different requirements and use cases. MCP servers 27 provide a standardized, relatively lightweight method for plugging external tools and data sources into Copilot's agentic capabilities within the IDE, with a focus on the tool's intrinsic functionality rather than deep IDE interaction. Native VSCode extensions that utilize the Copilot APIs 44 allow for the creation of deeply integrated AI features that can harness the full power and context of the VSCode environment itself. Finally, GitHub Copilot Extensions, built as GitHub Apps 51, offer a pathway for building cross-platform integrations that are intrinsically tied to the broader GitHub ecosystem and can operate wherever Copilot is present. A power user's ability to navigate this landscape and select the appropriate mechanism for extending Copilot—or for choosing which third-party extensions to adopt—depends on a clear understanding of these architectural differences, their respective strengths, and their limitations.

The following table provides a comparative overview:

Table: Comparison of Copilot Extensibility Mechanisms in VSCode

Mechanism

Implementation Location

VSCode API Access

GitHub API Access (Typical)

Activation Model (Primary)

Primary Use Case in VSCode Context

MCP Tool via Server

External Process (Local/Remote)

No

Via PAT/OAuth by Server

Agent-driven (auto or explicit #tool_name by user)

Integrating external tools/services into Copilot Agent Mode; minimal IDE-specific code.

VSCode Agent Mode Tool (Native Ext)

VSCode Extension Host

Yes (Full)

Via Extension (if needed)

Agent-driven (auto by Copilot based on prompt)

AI features needing deep editor integration, workspace access, custom UI within VSCode.

VSCode Chat Participant (Native Ext)

VSCode Extension Host

Yes (Full)

Via Extension (if needed)

User-invoked (@participant) in Copilot Chat (Ask mode)

Domain-specific Q&A, leveraging VSCode context and APIs.

GitHub Copilot Extension (GitHub App)

GitHub App / External Service

No (Limited to non-VSCode specific context if any)

Yes (Via GitHub App permissions)

User-invoked (@participant) or event-driven (GitHub platform)

Cross-platform tools (IDEs, GitHub.com) focused on GitHub ecosystem integration.

This comparison should aid power users in deciding whether to configure an existing MCP server, build a new one, develop a native VSCode extension with AI capabilities, or look for a GitHub Copilot Extension, depending on their specific goals for enhancing their Copilot experience in VSCode.

Chapter 7: Advanced Strategies, Security, and Troubleshooting
Leveraging MCP servers with GitHub Copilot in VSCode unlocks powerful new workflows, but it also introduces considerations around security, optimal usage, and potential troubleshooting. Power users must be adept at managing these aspects to ensure a safe, efficient, and reliable experience.

7.1 Best Practices for Secure and Efficient MCP Usage
Security is paramount when integrating external tools and services with an AI assistant that can autonomously invoke them.

Personal Access Token (PAT) Scopes: The Principle of Least Privilege:
When configuring the GitHub MCP server (e.g., @modelcontextprotocol/server-github or ghcr.io/github/github-mcp-server), which requires a GitHub PAT for authentication, it is crucial to adhere to the principle of least privilege.2 This means the PAT should only be granted the minimum set of permissions necessary for the tools you intend Copilot to use.
The documentation for @modelcontextprotocol/server-github 17 and related community guides 24 often suggest the broad repo scope ("Full control of private repositories") for simplicity, as this covers all repository-related actions its tools might perform (reading content, creating issues, managing PRs). For public repositories, public_repo might be suggested.17
However, power users should scrutinize this. If you only intend to use tools that read repository content and issues, a PAT with more granular read-only scopes (e.g., contents:read, issues:read, pull_requests:read available under fine-grained PATs) is far more secure than granting full repo control. If issue creation is needed, add issues:write. If PR creation/management is needed, pull_requests:write would be necessary.
The GitHub MCP Server exposes a variety of tools like create_issue, get_issue_comments, create_pull_request, merge_pull_request, get_file_content, etc..17 The specific PAT scopes required will depend directly on which of these tools are enabled (via the tools allowlist in the Copilot Coding Agent configuration or implied by usage in VSCode) and which actions Copilot will be prompted to perform.
Recommendation: Start with the most restrictive PAT scopes possible (e.g., read-only if that's all you need initially). Incrementally add more permissive scopes only when a specific tool or workflow demonstrably requires them. Regularly review the scopes of your PATs and revoke any that are no longer needed or are overly permissive.
For the COPILOT_MCP_GITHUB_PERSONAL_ACCESS_TOKEN used by the GitHub Copilot Coding Agent (configured in repository settings), GitHub's own documentation explicitly recommends using fine-grained PATs with read-only permissions on specific repositories, unless write access is absolutely essential for the agent's tasks.2
Tool Permissions and Read-Only Preference:
When configuring MCP servers for the GitHub Copilot Coding Agent (via GitHub repository settings), it is a strong recommendation to restrict the agent's access to read-only tools from the MCP server, unless write access is indispensable for the tasks it will be assigned.2
The tools array in the JSON configuration for the Coding Agent should be used to explicitly allowlist only known, safe, and necessary tools from an MCP server, rather than enabling all ("*") by default if the server offers many tools.2
Within VSCode, always review tool invocation prompts carefully, especially for tools that can modify files, execute terminal commands, or make external API calls with side effects. Understand what the tool is about to do before granting approval.21
Source Trust and Configuration Review:
Only add and configure MCP servers that come from trusted sources. If you are using a community-provided MCP server, review its source code or documentation to understand its behavior and potential security implications.27
Before starting an MCP server, carefully review its configuration in your .vscode/mcp.json or settings.json, paying close attention to the command being executed, the arguments, and any environment variables being passed, especially those containing secrets.
Secure Credential Handling:
As detailed in Chapter 4.3, never hardcode secrets like PATs or API keys directly into your JSON configuration files if those files are shared or committed to version control.
Utilize VSCode's built-in input prompting mechanism (via the inputs array in mcp.json) for securely providing secrets at runtime.4
For the Copilot Coding Agent, rely on GitHub's encrypted environment secrets, ensuring they are prefixed with COPILOT_MCP_.2
Network Security:
When interacting with remote MCP servers, ensure that the communication is encrypted using HTTPS to protect data in transit.19
Be mindful of firewall configurations that might block VSCode or the MCP server process from accessing necessary network resources or endpoints.
Understanding GitHub Copilot Content Exclusion:
GitHub Copilot offers content exclusion settings at the repository and organization levels (configured on GitHub.com).53 These settings prevent Copilot from using specified files or paths for generating suggestions or as context for chat.
While these settings don't directly control MCP servers, they affect the overall context available to Copilot. If sensitive files are excluded, Copilot (and by extension, any MCP tools it uses that rely on Copilot's context understanding) will not "see" that content. This is an indirect but important layer for data protection.
The following table provides guidance on GitHub PAT scopes for common actions performed by the GitHub MCP server:

Table: Recommended GitHub PAT Scopes for Common GitHub MCP Server Actions

Action / Goal

GitHub MCP Server Tool(s)

Recommended Minimum Fine-Grained PAT Scopes (Illustrative)

Classic PAT Scope Suggestion (Broad)

Read repository files/content

get_file_content, get_repository_tree

contents:read

repo (or public_repo)

Read issues & pull requests (metadata, comments)

get_issue, get_issue_comments, get_pull_request

issues:read, pull_requests:read

repo (or public_repo)

Create/Update/Close issues, Add issue comments

create_issue, update_issue, add_issue_comment

issues:write

repo

Create/Update pull requests, Add PR comments/reviews

create_pull_request, update_pull_request, create_review_on_pull_request

pull_requests:write

repo

Merge pull requests

merge_pull_request

pull_requests:write (merging is a write operation on the repo)

repo

Search code within repositories

search_code_repositories (conceptual)

search:read (if available and sufficient), often contents:read is needed for the search to be useful.

repo (or public_repo)

List repositories

list_repositories

metadata:read (for repository metadata)

repo (or public_repo)

Note: Fine-grained PATs allow selection of specific repositories. Always grant access only to the repositories the MCP server needs to interact with. The "Classic PAT Scope Suggestion" is often overly broad; prefer fine-grained PATs whenever possible.

7.2 Troubleshooting Common MCP Server and Tool Issues in VSCode
Despite careful configuration, issues can arise when working with MCP servers. A systematic approach to troubleshooting is essential.

Common Symptoms and Potential Causes:
Server Fails to Start:
Incorrect command or args in the JSON configuration (e.g., typos, incorrect path to executable).
Required runtime (Node.js, Docker, Python) not installed, not in system PATH, or not running (e.g., Docker daemon stopped).4
Permissions issues preventing VSCode from executing the specified command.
Invalid JSON syntax in mcp.json or settings.json.2
Tools Not Appearing in Agent Mode / Tool Discovery Failures:
MCP server process crashed or exited prematurely after starting.
The MCP server is not running when VSCode/Copilot attempts discovery.37
Network issues preventing VSCode from reaching a remote MCP server.
SSL certificate problems with remote HTTPS servers.55
The server is not correctly implementing the MCP discovery protocol (e.g., not responding with a valid tool manifest).
Incompatibility between MCP protocol versions used by the client (Copilot) and the server.37
The tools array in the Copilot Coding Agent configuration might be misconfigured, filtering out expected tools.2
Tool Invocation Errors (Copilot attempts to use a tool, but it fails):
Missing dependencies required by the MCP server or the underlying tool it wraps.40
Incorrect or insufficient permissions for the MCP server process (e.g., file system permissions for a local server, or incorrect PAT scopes for the GitHub MCP server leading to GitHub API errors).
The tool's input parameters provided by Copilot (or manually edited by the user) do not match the tool's expected schema.
Bugs within the MCP server's implementation of the tool logic.
Network timeouts or errors when a tool tries to reach an external API.
Rate limiting by the external API the tool is calling.
VSCode Prompts Repeatedly for Secrets:
The mechanism for VSCode to store/retrieve the prompted secret might be failing.
The ${input:variableId} reference in the configuration might be misspelled.
Diagnostic Steps:
Check VSCode Output Channels: This is often the first place to look.
View > Output, then select "GitHub Copilot" or "GitHub Copilot Chat" from the dropdown. Look for error messages related to MCP server startup, connection, or tool invocation.37
Use MCP: List Servers Command:
Open the Command Palette (Ctrl+Shift+P or Cmd+Shift+P) and run MCP: List Servers.
This command should show the status of configured servers. For any problematic server, there's usually an option to "Show Output" or "View Logs," which provides server-specific logs directly within VSCode.18
Inspect VSCode Developer Tools Console:
Go to Help > Toggle Developer Tools. Check the Console tab for any JavaScript errors or more detailed logs from the Copilot extension itself.37
Enable Debug Logging on the MCP Server (if supported):
Some MCP servers might offer a debug mode or higher verbosity logging that can be enabled via command-line arguments or environment variables. Consult the specific server's documentation.37
Validate MCP JSON Configuration:
Carefully check your .vscode/mcp.json or settings.json for syntax errors (e.g., missing commas, incorrect brackets). VSCode's JSON editor usually provides good syntax highlighting and error detection. For the Copilot Coding Agent, GitHub.com validates the syntax upon saving.2
Test Server Command Manually:
Try running the command and args specified in your MCP configuration directly from your system's terminal (outside of VSCode). This can help isolate whether the issue is with the server itself or with how VSCode is trying to launch it.
Network Troubleshooting (for remote servers):
Use tools like ping or curl to check basic network connectivity to the remote MCP server's host and port.
Verify firewall rules or proxy settings that might be interfering.
Restart and Reload:
Sometimes, simply restarting Copilot Chat (via Command Palette: GitHub Copilot: Restart Copilot Chat 37) or reloading the VSCode window (Command Palette: Developer: Reload Window 37) can resolve transient issues or force a fresh discovery of MCP servers and tools.
Known Caveats and Limitations:
Tool Quantity Limit: Some MCP clients might impose a limit on the number of tools they can handle from all connected servers. For instance, the Cursor editor was reported to only send the first 40 discovered tools to its Agent.21 While not explicitly stated for Copilot in VSCode, it's a potential factor if you have many servers with numerous tools.
Remote Development (SSH/Containers): MCP servers configured to run locally on your client machine (the one running the VSCode UI) might not function as expected in remote development scenarios (e.g., when using VSCode Remote - SSH to connect to a server, or developing in a container). If the local MCP server needs access to resources on your client machine that aren't available or mapped to the remote environment, it will fail. The MCP server process itself runs where the VSCode client (or its server-side component for remote dev) is effectively running it.21
Troubleshooting MCP integrations requires a methodical, multi-layered approach because issues can originate from various components: the VSCode client configuration 40, the Copilot extension's handling of MCP, the MCP server process itself (whether local or remote) including its startup and runtime behavior 40, network communication paths 40, the tool discovery mechanism 37, the actual execution of a tool's logic, or authentication and permission problems (e.g., PAT scopes). Effective diagnosis involves checking logs and states at different points in this chain—VSCode's output panels, specific server logs if accessible 40, system process lists—and verifying configurations meticulously. This complexity is inherent in such a distributed and extensible system, contrasting with the more straightforward debugging of a monolithic application.

The following table summarizes common troubleshooting steps:

Table: Troubleshooting Common MCP Issues in VSCode

Symptom

Potential Cause(s)

Diagnostic Steps

Resolution Strategies

MCP Server fails to start / Not listed as active

Incorrect command/args in JSON config; Runtime (Docker, Node) not found/running; Permissions issue; Invalid JSON.

Check VSCode Copilot Output; MCP: List Servers + Show Output; Manually run server command in terminal.

Correct JSON config; Install/start runtime; Adjust permissions; Validate JSON syntax.

Tools not appearing in Agent Mode tool list

Server crashed post-start; Network issue (remote); SSL issue (remote); Server not implementing discovery correctly.

Check server logs (via MCP: List Servers); Ping/curl remote server; Check VSCode Developer Console; GitHub Copilot: Restart Copilot Chat.

Fix server implementation; Resolve network/SSL issues; Ensure server is running before Copilot discovery.

Tool invocation fails (e.g., with API error)

Insufficient PAT scopes (for GitHub MCP); Incorrect tool input parameters; Bug in server tool logic; Network timeout.

Examine error message in Copilot Chat; Check server logs; Verify PAT scopes; Review tool input parameters before confirming invocation.

Grant necessary PAT scopes; Correct input parameters if editable; Report bug to server maintainer; Check network to external API.

VSCode repeatedly prompts for secrets

Input variable ID mismatch; VSCode secure storage issue (rare).

Double-check ${input:id} in config against inputs array id; Restart VSCode.

Correct input variable ID in config.

General unexpected behavior

Protocol version mismatch; Extension conflict; Outdated VSCode/Copilot.

Check VSCode Copilot Output for version warnings; Disable other extensions temporarily; Update VSCode and Copilot extensions.

Consult MCP server documentation for compatibility; Update components.

7.3 Performance Considerations and Optimization
While MCP greatly expands Copilot's capabilities, power users should be mindful of potential performance implications:

Local vs. Remote Server Latency: Local MCP servers communicating via stdio generally have very low latency. Remote servers accessed over HTTP/SSE will inherently introduce network latency, which can affect the responsiveness of tools. Choose local servers for performance-critical, frequently used tools if possible.
Complexity of Tool Execution: Tools that perform complex computations, make multiple downstream API calls, or process large amounts of data will naturally take longer to execute. This is a characteristic of the tool itself, not MCP, but it impacts the overall user experience.
Number and Verbosity of Tools: If many MCP servers are active, each exposing numerous tools with very verbose descriptions, there could be an impact on Copilot's initial tool discovery time and potentially on the LLM's ability to efficiently select the correct tool from a vast search space. While Copilot is designed to handle this, being judicious about enabling only necessary servers and tools can be beneficial.
Copilot Agent Mode Request Consumption: As noted in VSCode documentation 15, a single high-level prompt in Agent Mode can result in multiple underlying requests to the LLM and multiple tool invocations as the agent plans, executes, and iterates. This means Agent Mode operations can be slower and may consume more "premium requests" (if applicable to the model being used) compared to simpler chat interactions or inline completions. For well-defined, single-step tasks, using Copilot's "edit mode" or direct chat might be more efficient. Agent Mode shines for more complex, open-ended tasks where its planning and iteration capabilities are needed.
By understanding these security, troubleshooting, and performance aspects, power users can more effectively and safely integrate MCP servers into their GitHub Copilot workflow in VSCode, maximizing the benefits while mitigating potential downsides.

Chapter 8: The Evolving Landscape of MCP and AI-Assisted Development
The introduction of the Model Context Protocol and features like GitHub Copilot's Agent Mode marks a dynamic phase in the evolution of AI-assisted software development. For power users, understanding this evolving landscape is key to staying ahead and continuously leveraging the most advanced capabilities.

8.1 Current State and Future Trends in MCP
The Model Context Protocol is an open standard that has seen rapid adoption and development since its introduction.4 Its design facilitates a plug-and-play architecture for AI tools, which is a significant departure from bespoke, one-off integrations.

Growing Ecosystem: The number and variety of available MCP servers are continuously expanding. This includes official servers from major players (like the GitHub MCP server 4 and Azure MCP server 13), as well as community-driven and third-party servers for various databases, APIs, and utilities (e.g., Neon Postgres 13, Sanity 23, Pieces 29, Fetch 7). This growing ecosystem means that Copilot's capabilities via MCP will likely continue to broaden.
Protocol Evolution: The MCP specification itself is not static. For instance, the introduction of Streamable HTTP as a transport mechanism 20 shows ongoing efforts to refine and improve the protocol. Users should anticipate further enhancements and potentially new versions of the MCP standard.
Public Preview Status: Many advanced Copilot features related to MCP and agentic behavior, including Agent Mode in VSCode 27, the Copilot Coding Agent on GitHub.com 3, and specific MCP server integrations, are often released in public preview. This status implies that these features are still under active development, may be subject to change, and user feedback is crucial for their refinement.3
8.2 The Rise of AI Agents in Software Development
GitHub Copilot's Agent Mode 5 and the more autonomous Copilot Coding Agent 14 clearly signal a trend towards more sophisticated AI agents in the software development lifecycle. These agents are designed to:

Understand high-level tasks described in natural language.
Plan and execute multi-step solutions.
Interact with the codebase across multiple files.
Utilize external tools (via MCP) to gather information or perform actions.
Iterate and self-correct based on feedback or errors encountered.
MCP plays a crucial role as an enabler for these agents, providing the standardized interface they need to connect to a diverse range of "senses" (data sources) and "hands" (action-performing tools). As AI models become more capable of complex reasoning and planning, the richness of the MCP tool ecosystem will directly influence the scope and effectiveness of these AI development agents.

8.3 Implications for Power Users: Staying Ahead
For power users of GitHub Copilot in VSCode, this evolving landscape presents both opportunities and the need for continuous learning:

Explore New MCP Servers and Tools: Actively seek out and experiment with new MCP servers as they become available. The official MCP servers repository 7 and community channels are good places to discover new integrations.
Engage with the Community: Participate in discussions on platforms like the GitHub Community forums 37 or relevant subreddits.39 These can be valuable sources for troubleshooting tips, discovering new use cases, and sharing knowledge about MCP and advanced Copilot features.
Keep Software Updated: Ensure that your VSCode installation, GitHub Copilot extensions, and any locally managed MCP server packages (like Node.js modules or Docker images) are regularly updated to benefit from the latest features, bug fixes, and security patches.
Develop Prompt Engineering Skills for Agents: Interacting effectively with AI agents like Copilot in Agent Mode requires nuanced prompt engineering. Learning how to phrase high-level goals, provide appropriate context, and guide the agent's iterative process will be crucial for maximizing its utility.
Monitor Protocol and Feature Changes: Given the "public preview" nature of many of these advanced features, stay informed about updates to the MCP specification, changes in Copilot's behavior, and new capabilities introduced in VSCode or by GitHub.
By embracing these practices, power users can not only master the current capabilities of GitHub Copilot with MCP servers but also position themselves to take full advantage of future advancements in AI-assisted software engineering. The journey with AI tools is one of continuous adaptation and learning, and MCP is a foundational piece of this rapidly evolving puzzle.

Chapter 9: Conclusions
The integration of Model Context Protocol (MCP) servers with GitHub Copilot in Visual Studio Code represents a significant leap forward for power users, transforming Copilot from a sophisticated code completion and chat assistant into a versatile, extensible AI agent. This deep research report has aimed to provide a comprehensive manual for understanding, configuring, and effectively utilizing this powerful combination.

The core of this advancement lies in MCP's open standard, which enables Copilot to seamlessly connect with and leverage a diverse array of external tools and data sources. Whether these are local utilities interacting with a developer's file system, remote databases providing schema and query capabilities, cloud services offering platform interactions, or the GitHub API itself, MCP provides the crucial bridge. The architectural flexibility of MCP, supporting both local (stdio) and remote (HTTP/SSE, Streamable HTTP) servers, caters to a wide spectrum of use cases, from personal developer productivity enhancements to enterprise-grade service integrations.

For the power user, mastering MCP server configuration within VSCode—via .vscode/mcp.json for workspace-specific setups or user settings.json for global access—is key. This includes understanding the JSON structure, managing server commands and arguments, and, critically, handling credentials like Personal Access Tokens securely using VSCode's input prompting mechanisms or environment variables, always adhering to the principle of least privilege.

The true potential of MCP is unlocked through GitHub Copilot's Agent Mode. In this mode, Copilot can autonomously analyze user prompts, select appropriate tools from configured MCP servers, and orchestrate multi-step tasks, including code modification, terminal command execution, and error remediation. Users retain control through a vital tool approval workflow, ensuring a balance between automation and security. The ability to invoke tools both through natural language and explicit #tool_name commands offers flexibility in guiding the agent.

The landscape of Copilot extensibility is layered. MCP servers provide a standardized way to plug in external functionalities. Native VSCode extensions using Copilot APIs allow for deeply integrated AI features within the editor. GitHub Copilot Extensions (as GitHub Apps) offer cross-platform integration tied to the GitHub ecosystem. Understanding these distinctions allows power users to choose the right approach for their needs.

Security remains a paramount consideration. The use of PATs with minimal necessary scopes, careful vetting of MCP server sources, adherence to read-only tool preferences where possible, and diligent review of tool invocations are essential practices. Troubleshooting, given the multi-component nature of MCP integrations, requires a systematic approach, leveraging logs from VSCode, the Copilot extension, and the MCP servers themselves.

As of May 2025, the MCP ecosystem and AI agent capabilities are rapidly evolving. Power users are encouraged to stay abreast of new MCP server releases, updates to the MCP specification, and advancements in Copilot's agentic functionalities. Continuous learning, experimentation with new tools, and active participation in developer communities will be vital for harnessing the full potential of this dynamic field.

In essence, the combination of GitHub Copilot and MCP servers empowers developers to customize and significantly amplify their AI-assisted workflows within VSCode, moving towards a future where AI is not just an assistant but a proactive and adaptable partner in the software development lifecycle.

Appendix A: MCP Server Configuration Blueprints
This appendix provides detailed, copy-paste-ready JSON examples for setting up some of the key MCP servers discussed in Chapter 5. These blueprints are intended for use in VSCode, typically within the .vscode/mcp.json file (for workspace-specific configurations) or adapted for the user settings.json file (for global configurations). Remember to replace placeholder values (like <YOUR_GITHUB_PAT>) with your actual credentials, preferably managed via VSCode's input prompting mechanism for security.

1. GitHub MCP Server (Local Docker Container via stdio)

This configuration runs the official GitHub MCP server as a Docker container. It prompts the user for a GitHub Personal Access Token (PAT).

File: .vscode/mcp.json

JSON

{
"inputs":,
"servers": {
"GitHubMCP": {
"type": "stdio", // Communication via standard input/output
"command": "docker",
"args":,
// Optional: Specify which toolsets from the GitHub MCP server to enable
// "env": {
// "GITHUB_TOOLSETS": "issues,pull_requests,repositories" // Example: enable only these toolsets
// }
}
}
}

Notes:
Ensure Docker is installed and running.
The PAT provided (${input:githubPatMcp}) should have the necessary scopes for the GitHub API actions you intend Copilot to perform (e.g., repo for full repository access, or more granular scopes like issues:write, pull_requests:read). Refer to Chapter 7.1 for PAT scope recommendations.
The ghcr.io/modelcontextprotocol/server-github image is commonly referenced. Check the official GitHub MCP server documentation for the latest recommended image tag if issues arise.
2. Neon Serverless Postgres MCP Server (Remote SSE via npx bridge)

This configuration uses the npx command to run the mcp-remote bridge tool, which connects to Neon's remote hosted MCP server. Authentication is handled via OAuth through a browser window opened by mcp-remote.

File: User settings.json (example for global setup)

JSON

{
"mcp": {
"servers": {
"NeonPostgresMCP": {
// "type" is often inferred by VSCode for command-based servers,
// but explicitly it would be a local process managing a remote connection.
"command": "npx",
"args":
// No 'inputs' array needed here as authentication is OAuth-based.
}
}
}
}

Notes:
Requires Node.js and npx to be installed and in your PATH.
When this server is started, mcp-remote will typically open a browser window for you to authenticate with your Neon account.
3. Generic Azure MCP Server (Local npx command via stdio)

This configuration is for the Azure MCP server, which allows Copilot to interact with Azure services. This example assumes it's run locally using npx. Authentication with Azure (e.g., via Azure CLI login, service principal, or OIDC for the Copilot Coding Agent) would need to be handled by the server or its environment.

File: .vscode/mcp.json

JSON

{
// "inputs" might be needed if the Azure MCP server requires specific
// credentials like service principal IDs/secrets passed via environment variables.
// Example:
// "inputs":,
"servers": {
"AzureMCP": {
"type": "stdio",
"command": "npx",
"args":
// Example if using inputs for credentials:
// "env": {
// "AZURE_CLIENT_ID": "${input:azureClientId}",
// "AZURE_TENANT_ID": "${input:azureTenantId}",
// // Other necessary Azure auth environment variables
// }
}
}
}

Notes:
Requires Node.js and npx.
The Azure MCP server might rely on existing Azure CLI sessions or environment variables (like AZURE_CLIENT_ID, AZURE_TENANT_ID, AZURE_CLIENT_SECRET, AZURE_SUBSCRIPTION_ID) for authentication. Consult the Azure MCP server documentation for specific authentication requirements.
For the Copilot Coding Agent, Azure MCP server setup involves OIDC and GitHub Actions workflow modifications.2
4. Fetch MCP Server (Generic local command via stdio)

This example is for a generic "fetch" server that allows Copilot to retrieve content from URLs. The actual command (uvx mcp-server-fetch) is illustrative; you would replace it with the correct command for your chosen fetch MCP server implementation.

File: .vscode/mcp.json

JSON

{
// No inputs typically needed for a basic public URL fetcher,
// unless it supports authenticated fetches with an API key.
"servers": {
"WebFetchMCP": {
"type": "stdio",
"command": "uvx", // Replace with the actual command for your fetch server
"args": ["mcp-server-fetch"] // Replace with actual arguments
}
}
}

Notes:
The uvx mcp-server-fetch is a placeholder from documentation examples.7 You'll need to find or build an actual MCP server that provides URL fetching capabilities and use its specific startup command and arguments.
These blueprints provide a starting point. Always refer to the official documentation for the specific MCP server you intend to use for the most accurate and up-to-date configuration details and security recommendations.

Appendix B: Glossary of Terms
Agent Mode (Copilot in VSCode): An operational mode for GitHub Copilot Chat in VSCode where Copilot can autonomously plan and execute multi-step tasks, including analyzing code, proposing edits across multiple files, running terminal commands, and invoking tools from MCP servers. 5
Copilot Coding Agent (GitHub.com): An autonomous AI agent integrated into GitHub that can be assigned issues or prompted via chat to perform development tasks, resulting in pull requests. It uses local MCP servers configured in repository settings. 2
GitHub Copilot Extensions (GitHub Apps): Integrations built as GitHub Apps that extend Copilot Chat's functionality across multiple surfaces (IDEs, GitHub.com, Mobile). They are distinct from VSCode-specific extensions or MCP server configurations within VSCode. 6
JSON-RPC 2.0: A stateless, light-weight remote procedure call (RPC) protocol. MCP uses JSON-RPC 2.0 messages for communication between clients and servers. 8
MCP Client: The component within a host application (like GitHub Copilot in VSCode) that connects to and interacts with MCP Servers, requesting tool invocations on behalf of the AI model. 8
MCP Server: A program or service that exposes capabilities (primarily "tools") of an external system (API, database, file system, CLI) to MCP clients, according to the Model Context Protocol specification. Can be local or remote. 3
MCP Tool: A specific, callable function or action defined and exposed by an MCP server. Tools have a name, description, and defined input/output schemas, allowing AI agents like Copilot to discover and invoke them. 3
MCP Tool Manifest: A machine-readable (often JSON) registry or description provided by an MCP server that lists and defines the tools it offers, including their capabilities, parameters, and constraints. 25
Model Context Protocol (MCP): An open standard that defines how AI applications (like GitHub Copilot) can connect to and interact with external data sources and tools through a unified interface, enabling them to work together more effectively. 3
Personal Access Token (PAT): A credential used to authenticate to services like GitHub, often used by MCP servers (especially the GitHub MCP server) to access APIs on behalf of the user. Security requires using PATs with appropriate, minimal scopes. 2
Server-Sent Events (SSE): A web technology that allows a server to push data to a client over a single, long-lived HTTP connection. One of the transport mechanisms supported by MCP for remote server communication. 6
Standard Input/Output (stdio): The default communication channels for a command-line program. Used as a transport mechanism by MCP for local server communication. 6
Streamable HTTP: A modern MCP transport protocol using a single HTTP endpoint for bidirectional communication. 20
VSCode Input Variables (${input:id}): A VSCode-specific mechanism allowing configurations (like mcp.json) to define inputs that VSCode will prompt the user for at runtime, useful for securely handling secrets. 27
Appendix C: GitHub Copilot Settings Reference for Power Users (VSCode)
This appendix lists key Visual Studio Code settings relevant for power users working with GitHub Copilot, particularly focusing on Agent Mode, MCP server integration, context customization, and performance. For a full list of all Copilot settings, refer to the official VSCode documentation.38

Table: Key VSCode Settings for Copilot MCP/Agent Power Users

Setting ID

Description

Default Value

Recommended Value/Considerations for Power Users

Snippet Ref(s)

chat.mcp.enabled

Enables or disables Model Context Protocol (MCP) support in VSCode, allowing connection to MCP servers for Agent Mode tools.

true

Keep true to use MCP servers. Ensure this is enabled if MCP servers are not being discovered or used.

18

chat.agent.enabled

Enables or disables Copilot Agent Mode in the Chat view. Requires VSCode 1.99+.

false

Set to true to use Agent Mode and its MCP tool invocation capabilities.

27

chat.agent.maxRequests

Defines the maximum number of requests (LLM calls, tool invocations) Copilot Agent Mode can make for a single user prompt.

15 (paid plans), 5 (Free)

Power users might consider increasing this for very complex tasks if hitting limits, but be mindful of potential performance impact and (if applicable) premium request consumption.

36

github.copilot.chat.agent.autoFix

Allows Agent Mode to automatically diagnose and attempt to fix issues in generated code changes (e.g., based on test failures).

true

Generally beneficial. Power users might disable temporarily for very delicate refactoring if they prefer full manual control over every fix attempt, but true aligns with the agentic paradigm.

36

github.copilot.chat.agent.runTasks

Enables Agent Mode to run workspace tasks defined in tasks.json (e.g., build tasks) as part of its execution plan.

true

Useful for ensuring code validity. Disable if automated task execution is undesirable for specific workflows or projects.

36

chat.mcp.discovery.enabled

Enables or disables automatic discovery of MCP server configurations from other tools like Claude Desktop.

true

Keep true for convenience if you use MCP servers with other compatible tools. Set to false if you prefer explicit configuration in VSCode only or encounter conflicts.

7

github.copilot.chat.codesearch.enabled (Preview)

When using #codebase in a prompt, allows Copilot to automatically discover relevant files for editing.

(Varies)

Enable for better context gathering in Agent Mode, especially for tasks spanning multiple initially unspecified files.

38

chat.tools.autoApprove (Experimental)

If true, automatically approves all tool invocations by Agent Mode, bypassing the user confirmation prompt.

false

Use with extreme caution. Only enable if you fully trust all configured MCP servers and understand the risks of autonomous execution of potentially destructive actions. Generally, keeping this false is safer.

38

github.copilot.chat.codeGeneration.useInstructionFiles

Controls whether code generation instructions from .github/copilot-instructions.md are added to Copilot requests.

true

Essential for tailoring Copilot's behavior at the repository level. Keep true if using such files.

38

chat.promptFilesLocations (Experimental)

Specifies locations for reusable .prompt.md files.

".github/prompts": true

Customize if you prefer a different organizational structure for prompt files within your workspace.

38

chat.instructionsFilesLocations (Experimental)

Specifies locations for .instructions.md files (finer-grained custom instructions).

".github/instructions": true

Customize if organizing instructions into multiple files/locations beyond the main copilot-instructions.md.

38

telemetry.telemetryLevel

Global VSCode setting to control telemetry reporting (options: "all", "error", "crash", "off").

"all"

Set to "off" for maximum privacy regarding VSCode's own telemetry. Note that Copilot has its own data handling policies (see Appendix D).

72

github.copilot.enable

Enable or disable Copilot completions globally or for specified languages.

(Varies)

{"*": true} enables for all. {"plaintext": false, "markdown": false, "*": true} disables for specific non-code files while keeping it for others. Useful for fine-tuning where completions appear.

38

Language Model Selection (via UI or commands)

Settings to choose different LLMs for chat or completions (e.g., Configure Code Completions..., Chat UI model picker).

(Varies)

Power users should experiment with different models (e.g., GPT-4o, Claude variants) for various tasks, as some excel at coding speed, others at reasoning.38 Note that BYO LLM is not for Business/Enterprise yet.56

38

github.copilot.advanced (e.g. authProvider)

Contains advanced, less commonly changed settings. authProvider: "github-enterprise" is used for GHE.com authentication.

(Varies)

Typically only modified for specific enterprise authentication scenarios. Not directly related to MCP functionality itself but can affect overall Copilot connectivity.

75

Content Exclusion:

Content exclusion settings are configured on GitHub.com at the repository or organization level, not directly in VSCode's settings.json.53 However, these settings directly impact Copilot's behavior in VSCode:

Excluded files will not provide context for suggestions or chat.
Completions will be disabled in excluded files.
VSCode indicates exclusion with a diagonal line through the Copilot status bar icon; hovering shows the reason.53
Changes to exclusion settings on GitHub.com may take up to 30 minutes to propagate, or can be forced by reloading the VSCode window (Developer: Reload Window).53
Understanding and appropriately configuring these settings will allow power users to fine-tune their GitHub Copilot experience, especially when working with the advanced capabilities offered by MCP servers and Agent Mode.

Appendix D: Data Handling and Privacy for Advanced Copilot Features
When utilizing advanced GitHub Copilot features like MCP servers, custom instructions, and Bring Your Own LLM (BYO LLM), it's crucial for power users to understand the associated data handling and privacy implications.

1. General Data Handling for Prompts, Suggestions, and Context by GitHub Copilot:

GitHub Copilot processes various data types to provide its services. This includes "User Engagement Data" (interactions with features), "Prompts" (contextual information from your editor, selected code, chat queries), and "Suggestions" (code or text generated by Copilot).57

Transmission and Encryption: Data transmitted to GitHub's Azure tenant for suggestion generation is encrypted in transit (TLS) and at rest (Azure's data encryption, FIPS 140-2 standards).58
Data Retention for Prompts and Suggestions:
For GitHub Copilot in the editor (code completions): Prompts (code context) are generally considered ephemeral and are discarded after a suggestion is returned. They are not retained for training foundational LLMs.57
For GitHub Copilot outside the editor (Copilot Chat in IDEs, CLI, Mobile, GitHub.com): Prompts, suggestions, and responses are typically retained for a period (e.g., 28 days) to maintain conversation history and continuity.57
Training Opt-Out:
For GitHub Copilot Individual subscribers: They can opt-out of allowing GitHub to use their prompts and suggestions from the code editor for product improvements (which can include fine-tuning GitHub's foundational models) via their GitHub account settings.57
For GitHub Copilot Business and Enterprise customers: Prompts and suggestions are not used to train the publicly available models offered by GitHub [58 (implies Business/Enterprise data is handled differently)]. Custom models for Copilot Enterprise are trained on designated repositories, and this data remains private to the organization.61
Content Exclusion: As detailed in Appendix C and Chapter 7.1, users can configure content exclusion on GitHub.com to prevent specified files from being sent to Copilot or used as context.53
2. Data Handling for Custom Instructions (.github/copilot-instructions.md and .instructions.md files):

Custom instruction files (.github/copilot-instructions.md for repository-wide context, and .instructions.md files for more granular or reusable instructions) are a powerful way to tailor Copilot's behavior.38

Storage: These instruction files are stored directly within your GitHub repository (e.g., in the .github/ directory) or your local workspace, just like any other source code or documentation file.62 Their persistence and visibility are governed by the repository's own settings (public or private) and access controls.
Transmission and Usage: When you interact with Copilot Chat in a context where these instruction files apply (e.g., within a repository that has a .github/copilot-instructions.md file, or when an .instructions.md file is explicitly attached or matched via applyTo), their content is transmitted to the GitHub Copilot service as part of the overall prompt context.62 This contextual information is then used by the LLM to generate more tailored and relevant responses. The instructions themselves are not typically displayed in the chat UI but are used by Copilot in the background. Copilot Chat often indicates when custom instructions were used by listing the instruction file in the "references" section of a response.62
Privacy Considerations:
The primary privacy and security considerations for custom instruction files stem from their storage within the repository. If a repository is public or accessible to individuals who should not see certain instructions (e.g., internal coding standards, sensitive project details), then those instructions should not be placed in that repository's custom instruction file.
Once transmitted as part of a prompt, the content of these instruction files is subject to GitHub Copilot's general data handling policies for prompts and suggestions, as outlined above (e.g., retention for chat history, potential use for product improvement if not opted out for Individual accounts).
It is crucial not to embed highly sensitive secrets (like API keys or passwords) directly within custom instruction files. While these files are intended to provide context to Copilot, their storage within a version control system makes them unsuitable for direct secret management.
The content of custom instruction files becomes part of the data GitHub Copilot processes. Their security and privacy are intrinsically linked to the security of the repository where they reside and GitHub's overarching data protection measures for Copilot services. Users should treat these files with the same diligence as any other potentially sensitive project documentation or configuration.

3. Data Flow for "Bring Your Own LLM" (BYO LLM) in VSCode:

VSCode allows users (currently not available for Business or Enterprise plans 56) to use their own API keys for certain third-party LLM providers (like Anthropic, Azure OpenAI, Google Gemini, Ollama, OpenAI, OpenRouter) for the Copilot Chat experience.56

Data Sent to Third-Party LLM: When BYO LLM is active, the core chat conversation (your prompts and the LLM's direct responses) is routed to the selected third-party LLM provider via your API key.56 The data handling and privacy policies of that third-party provider will then apply to this part of the interaction.
Data Still Processed by GitHub Copilot API: Importantly, using BYO LLM does not completely bypass GitHub's Copilot services. Several crucial contextualization and pre-processing steps are still handled by the GitHub Copilot API before the (potentially refined) prompt is sent to your chosen third-party LLM. These include 56:
Embeddings Generation: Creating numerical representations of your code and queries for semantic understanding.
Repository Indexing: Processing your codebase to build an index that Copilot uses for context.
Query Refinement: Improving or clarifying your chat prompts.
Intent Detection: Understanding the underlying goal of your query.
Side Queries: Potentially making additional calls to GitHub services for supplementary context.
Scope of BYO LLM: This feature primarily affects the chat experience. Code completions and other AI-powered features in VSCode (like commit message generation) continue to use Copilot's built-in models.56
Responsible AI Filtering: GitHub notes that when using your own model, there is no guarantee that responsible AI filtering (which GitHub applies to its own models) is applied to the output of the user-provided third-party model.56
The use of BYO LLM introduces a hybrid data flow. While the main inferencing for chat responses is offloaded to a third-party provider under the user's API key, GitHub Copilot's own APIs remain integral for several aspects of context processing, query understanding, and integration with the developer's environment. Users opting for BYO LLM, perhaps for access to specific models or for perceived data control benefits, must be aware that a significant portion of the interaction still involves GitHub's infrastructure and data processing. This means that the data handling policies of both GitHub Copilot and the chosen third-party LLM provider become relevant.

Power users should consult the latest GitHub Copilot Trust Center documentation 57, privacy statements 58, and terms of service for the most current and detailed information on data handling, as these policies can evolve.

Works cited
GitHub Copilot in VS Code, accessed May 24, 2025, <https://code.visualstudio.com/docs/copilot/overview>
Get started with GitHub Copilot in VS Code, accessed May 24, 2025, <https://code.visualstudio.com/docs/copilot/getting-started>
Extending Copilot coding agent with the Model Context Protocol (MCP) - GitHub Docs, accessed May 24, 2025, <https://docs.github.com/en/copilot/customizing-copilot/extending-copilot-coding-agent-with-mcp>
Supercharge VSCode GitHub Copilot using Model Context Protocol (MCP) - Easy Setup Guide - DEV Community, accessed May 24, 2025, <https://dev.to/pwd9000/supercharge-vscode-github-copilot-using-model-context-protocol-mcp-easy-setup-guide-371e>
Agent mode and MCP support for Copilot in JetBrains, Eclipse, and Xcode now in public preview - The GitHub Blog, accessed May 24, 2025, <https://github.blog/changelog/2025-05-19-agent-mode-and-mcp-support-for-copilot-in-jetbrains-eclipse-and-xcode-now-in-public-preview/>
GitHub Copilot Extensions | Tiago Pascoal, accessed May 24, 2025, <https://pascoal.net/2024/10/22/gh-copilot-extensions/>
Extending Copilot Chat with the Model Context Protocol (MCP) - GitHub Docs, accessed May 24, 2025, <https://docs.github.com/en/copilot/customizing-copilot/extending-copilot-chat-with-mcp>
Model Context Protocol (MCP) an overview - Philschmid, accessed May 24, 2025, <https://www.philschmid.de/mcp-introduction>
Enterprise-Grade Security for the Model Context Protocol (MCP): Frameworks and Mitigation Strategies - arXiv, accessed May 24, 2025, <https://arxiv.org/html/2504.08623v2>
What Is the Model Context Protocol (MCP) and How It Works - Descope, accessed May 24, 2025, <https://www.descope.com/learn/post/mcp>
Extend your agent with Model Context Protocol (preview) - Microsoft Copilot Studio, accessed May 24, 2025, <https://learn.microsoft.com/en-us/microsoft-copilot-studio/agent-extend-action-mcp>
Understanding the Model Context Protocol (MCP) | deepset Blog, accessed May 24, 2025, <https://www.deepset.ai/blog/understanding-the-model-context-protocol-mcp>
How to Use Postgres MCP Server with GitHub Copilot in VS Code ..., accessed May 24, 2025, <https://techcommunity.microsoft.com/blog/azuredevcommunityblog/how-to-use-postgres-mcp-server-with-github-copilot-in-vs-code/4412547>
GitHub Copilot: Meet the new coding agent, accessed May 24, 2025, <https://github.blog/news-insights/product-news/github-copilot-meet-the-new-coding-agent/>
Introducing GitHub Copilot agent mode (preview) - Visual Studio Code, accessed May 24, 2025, <https://code.visualstudio.com/blogs/2025/02/24/introducing-copilot-agent-mode>
Agent mode 101: All about GitHub Copilot's powerful mode - The GitHub Blog, accessed May 24, 2025, <https://github.blog/ai-and-ml/github-copilot/agent-mode-101-all-about-github-copilots-powerful-mode/>
@modelcontextprotocol/server-github - npm, accessed May 24, 2025, <https://www.npmjs.com/package/@modelcontextprotocol/server-github>
Boost VS Code Copilot with MCP Servers: A Detailed Guide - DEV ..., accessed May 24, 2025, <https://dev.to/shrsv/boost-vs-code-copilot-with-mcp-servers-a-detailed-guide-5fh4>
Core architecture - Model Context Protocol, accessed May 24, 2025, <https://modelcontextprotocol.io/docs/concepts/architecture>
How to MCP - The Complete Guide to Understanding Model Context Protocol and Building Remote Servers | Simplescraper Blog, accessed May 24, 2025, <https://simplescraper.io/blog/how-to-mcp>
Model Context Protocol - Cursor, accessed May 24, 2025, <https://docs.cursor.com/context/model-context-protocol>
Everything a Developer Needs to Know About the Model Context Protocol (MCP) - Neo4j, accessed May 24, 2025, <https://neo4j.com/blog/developer/model-context-protocol/>
Introducing the Sanity Model Context Protocol (MCP) server, accessed May 24, 2025, <https://www.sanity.io/blog/introducing-sanity-model-context-protocol-server>
Exploring MCP: GitHub MCP for iOS Dev in VS Code, Cursor & Windsurf - Rudrank Riyam, accessed May 24, 2025, <https://www.rudrank.com/exploring-mcp-github-mcp-ios-dev-vs-code-cursor-windsurf/>
MCP Tool Manifest - Explanation & Examples | Secoda, accessed May 24, 2025, <https://www.secoda.co/glossary/mcp-tool-manifest>
Specification - Model Context Protocol, accessed May 24, 2025, <https://modelcontextprotocol.io/specification/2025-03-26>
Use MCP servers in VS Code (Preview), accessed May 24, 2025, <https://code.visualstudio.com/docs/copilot/chat/mcp-servers>
MCP Server - Model Context Protocol, accessed May 24, 2025, <https://modelcontextprotocol.io/sdk/java/mcp-server>
Integrate Pieces Model Context Protocol (MCP) with GitHub Copilot, accessed May 24, 2025, <https://docs.pieces.app/products/mcp/github-copilot>
ranaroussi/muxi: An extensible AI agents framework - GitHub, accessed May 24, 2025, <https://github.com/ranaroussi/muxi>
Use MCP servers (Preview) - Visual Studio (Windows) - Learn Microsoft, accessed May 24, 2025, <https://learn.microsoft.com/en-us/visualstudio/ide/mcp-servers?view=vs-2022>
GitHub's official MCP Server, accessed May 24, 2025, <https://github.com/github/github-mcp-server>
modelcontextprotocol/modelcontextprotocol: Specification ... - GitHub, accessed May 24, 2025, <https://github.com/modelcontextprotocol/specification>
Model Context Protocol: Introduction, accessed May 24, 2025, <https://modelcontextprotocol.io/docs/specification>
Specification - Model Context Protocol, accessed May 24, 2025, <https://modelcontextprotocol.io/specification/>
Use agent mode in VS Code, accessed May 24, 2025, <https://code.visualstudio.com/docs/copilot/chat/chat-agent-mode>
MCP server prompts not showing up in copilot agent mode #157618 - GitHub, accessed May 24, 2025, <https://github.com/orgs/community/discussions/157618>
GitHub Copilot in VS Code settings reference - Visual Studio Code, accessed May 24, 2025, <https://code.visualstudio.com/docs/copilot/reference/copilot-settings>
MCP GitHub Server for VS Code Copilot : r/vscode - Reddit, accessed May 24, 2025, <https://www.reddit.com/r/vscode/comments/1ku9xpm/mcp_github_server_for_vs_code_copilot/>
How to Use VSCode MCP Server - Apidog, accessed May 24, 2025, <https://apidog.com/blog/vscode-mcp-server/>
GitHub - MCP Server - Magic Slides, accessed May 24, 2025, <https://www.magicslides.app/mcps/modelcontextprotocol-github>
Addition or separation of separate API scopes · Issue #1125 · modelcontextprotocol/servers - GitHub, accessed May 24, 2025, <https://github.com/modelcontextprotocol/servers/issues/1125>
GitHub Copilot Coding Agent Automates Issue-to-PR Workflow with Secure AI Integration, accessed May 24, 2025, <https://wandb.ai/byyoung3/ml-news/reports/GitHub-Copilot-Coding-Agent-Automates-Issue-to-PR-Workflow-with-Secure-AI-Integration--VmlldzoxMjg0ODE2MQ>
GitHub Copilot extensibility in VS Code, accessed May 24, 2025, <https://code.visualstudio.com/docs/copilot/copilot-extensibility-overview>
Use Copilot agent mode in Visual Studio (Preview) - Learn Microsoft, accessed May 24, 2025, <https://learn.microsoft.com/en-us/visualstudio/ide/copilot-agent-mode?view=vs-2022>
Vibe coding with GitHub Copilot: Agent mode and MCP support rolling out to all VS Code users - The GitHub Blog, accessed May 24, 2025, <https://github.blog/news-insights/product-news/github-copilot-agent-mode-activated/>
Mastering GitHub Copilot: When to use AI agent mode, accessed May 24, 2025, <https://github.blog/ai-and-ml/github-copilot/mastering-github-copilot-when-to-use-ai-agent-mode/>
Using Copilot coding agent effectively in your organization - GitHub Enterprise Cloud Docs, accessed May 24, 2025, <https://docs.github.com/en/enterprise-cloud@latest/copilot/rolling-out-github-copilot-at-scale/enabling-developers/using-copilot-coding-agent-in-org>
Copilot chat context - Visual Studio Code, accessed May 24, 2025, <https://code.visualstudio.com/docs/copilot/chat/copilot-chat-context>
GitHub Copilot Extensions are all you need - Visual Studio Code, accessed May 24, 2025, <https://code.visualstudio.com/blogs/2024/06/24/extensions-are-all-you-need>
About building Copilot Extensions - GitHub Docs, accessed May 24, 2025, <https://docs.github.com/en/copilot/building-copilot-extensions/about-building-copilot-extensions>
About Copilot agents - GitHub Docs, accessed May 24, 2025, <https://docs.github.com/en/copilot/building-copilot-extensions/building-a-copilot-agent-for-your-copilot-extension/about-copilot-agents>
Excluding content from GitHub Copilot - GitHub Docs, accessed May 24, 2025, <https://docs.github.com/en/copilot/managing-copilot/configuring-and-auditing-content-exclusion/excluding-content-from-github-copilot>
Configuring content exclusions for GitHub Copilot, accessed May 24, 2025, <https://github.net.cn/zh/copilot/managing-copilot-business/configuring-content-exclusions-for-github-copilot>
Issues · modelcontextprotocol/servers - GitHub, accessed May 24, 2025, <https://github.com/modelcontextprotocol/servers/issues>
AI language models in VS Code - Visual Studio Code, accessed May 24, 2025, <https://code.visualstudio.com/docs/copilot/language-models>
GitHub Copilot Data Pipeline Security, accessed May 24, 2025, <https://resources.github.com/learn/pathways/copilot/essentials/how-github-copilot-handles-data/>
GitHub Copilot Trust Center - trust.page, accessed May 24, 2025, <https://copilot.github.trust.page/faq>
creating-a-custom-model-for-github-copilot.md, accessed May 24, 2025, <https://github.com/github/docs/blob/main/content/copilot/customizing-copilot/creating-a-custom-model-for-github-copilot.md>
Managing Copilot policies as an individual subscriber - GitHub Docs, accessed May 24, 2025, <https://docs.github.com/en/copilot/managing-copilot/managing-copilot-as-an-individual-subscriber/managing-your-copilot-plan/managing-copilot-policies-as-an-individual-subscriber>
Creating a custom model for GitHub Copilot - GitHub Enterprise Cloud Docs, accessed May 24, 2025, <https://docs.github.com/enterprise-cloud@latest/copilot/customizing-copilot/creating-a-custom-model-for-github-copilot>
Adding repository custom instructions for GitHub Copilot, accessed May 24, 2025, <https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot>
Customize chat responses in VS Code - Visual Studio Code, accessed May 24, 2025, <https://code.visualstudio.com/docs/copilot/copilot-customization>
Adding repository custom instructions for GitHub Copilot, accessed May 24, 2025, <https://docs.github.com/en/copilot/customizing-copilot/adding-repository-custom-instructions-for-github-copilot?tool=webui>
About customizing GitHub Copilot Chat responses, accessed May 24, 2025, <https://docs.github.com/en/copilot/customizing-copilot/about-customizing-github-copilot-chat-responses>
Responsible use of GitHub Copilot in GitHub Desktop - GitHub Enterprise Cloud Docs, accessed May 24, 2025, <https://docs.github.com/enterprise-cloud@latest/copilot/responsible-use-of-github-copilot-features/responsible-use-of-github-copilot-in-github-desktop>
Asking GitHub Copilot questions in your IDE - GitHub Enterprise Cloud Docs, accessed May 24, 2025, <https://docs.github.com/en/enterprise-cloud@latest/copilot/using-github-copilot/asking-github-copilot-questions-in-your-ide>
Asking GitHub Copilot questions in your IDE - GitHub Docs, accessed May 24, 2025, <https://docs.github.com/en/copilot/using-github-copilot/copilot-chat/asking-github-copilot-questions-in-your-ide>
GitHub Trust Center, accessed May 24, 2025, <https://github.com/trust-center>
Prompting GitHub Copilot Chat to become your personal AI assistant for accessibility, accessed May 24, 2025, <https://github.blog/developer-skills/github/prompting-github-copilot-chat-to-become-your-personal-ai-assistant-for-accessibility/>
Part 25: AI Tools – What about data protection? - VISCHER, accessed May 24, 2025, <https://www.vischer.com/en/knowledge/blog/part-25-ai-tools-what-about-data-protection/>
Set up GitHub Copilot in VS Code, accessed May 24, 2025, <https://code.visualstudio.com/docs/copilot/setup>
Telemetry - Visual Studio Code, accessed May 24, 2025, <https://code.visualstudio.com/docs/configure/telemetry>
Set up Visual Studio Code with Copilot, accessed May 24, 2025, <https://code.visualstudio.com/docs/copilot/setup-simplified>
Using GitHub Copilot with an account on GHE.com, accessed May 24, 2025, <https://docs.github.com/en/copilot/managing-copilot/configure-personal-settings/using-github-copilot-with-an-account-on-ghecom>
Week 2: Features & Data handling – Copilot Free learning & cert prep #151641 - GitHub, accessed May 24, 2025, <https://github.com/orgs/community/discussions/151641>
