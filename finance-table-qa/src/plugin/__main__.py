"""Serve the financial table tools to NanoAgent over standard input/output."""

import anyio
from mcp import types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server
from slimconfig import build_output, output_schema, plain_output

from contract import TOOLS, Tool
from plugin.finance import calculate, describe_table, list_tables, read_cells

server = Server("finance-table-qa")
handlers = {Tool.LIST: list_tables, Tool.DESCRIBE: describe_table, Tool.READ: read_cells, Tool.CALCULATE: calculate}


@server.list_tools()
async def list_tools():
    return [
        types.Tool(name=tool.value, inputSchema=output_schema(given), outputSchema=output_schema(returned))
        for tool, (given, returned) in TOOLS.items()
    ]


@server.call_tool()
async def call_tool(name, arguments):
    tool = Tool(name)
    given, returned = TOOLS[tool]
    result = handlers[tool](build_output(arguments, given))
    if not isinstance(result, returned):
        raise TypeError(f"Unexpected output for {name}")
    return plain_output(result)


async def main():
    async with stdio_server() as (reader, writer):
        await server.run(reader, writer, server.create_initialization_options())


if __name__ == "__main__":
    anyio.run(main)
