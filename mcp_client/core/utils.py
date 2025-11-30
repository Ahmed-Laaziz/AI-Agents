def serialize_tool(tool):
    return {
        "name": tool.metadata.name,
        "description": tool.metadata.description,
        "input_schema": tool.metadata.input_types,
        "output_schema": tool.metadata.output_type,
        "server": getattr(tool, "server_id", "unknown"),
    }
