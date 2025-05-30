# Overview
This repo currently implements a simple MCP server with a weather tool that provides the forecast for a given city & state. 

## Local service usage

### Neo4j
There is a docker-compose file in the root of the repository that spins up a local Neo4j knowledge graph database.
```shell
make build
make run
```
> **This is an interesting tool that is quite flexible for agent memory. Try asking Claude to look at a website with sub-pages or artifacts and ask it to generate a knowledge graph. You can then follow-up with questions about that content and Claude will use the relationships it made in the knowledge graph to answer.**

## MCP Client Configuration
This is an example of the Claude Desktop config that sets up the Neo4j knowledge graph tool & the custom MCP server from this repo:

```json
{
  "mcpServers": {
    "neo4j": {
      "command": "uvx",
      "args": [ "mcp-neo4j-memory@0.1.4" ],
      "env": {
        "NEO4J_URL": "bolt://localhost:7687",
        "NEO4J_USERNAME": "neo4j",
        "NEO4J_PASSWORD": "password"
      }
    },
    "weather": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "http://localhost:8000/mcp"
      ]
    }
  }
}
```

*Additional information on setting up Claude Desktop with MCP can be found [here](https://modelcontextprotocol.io/quickstart/user)*
> *Note: You must restart the Claude Desktop client to reload MCP configuration!*