import sys

from mojentic.llm.tools.ephemeral_task_manager import EphemeralTaskList, AppendTaskTool, PrependTaskTool, \
    InsertTaskAfterTool, StartTaskTool, CompleteTaskTool, ListTasksTool, ClearTasksTool

from mojentic_mcp.mcp_http import HttpMcpServer
from mojentic_mcp.rpc import JsonRpcHandler

sys.stderr.write("Starting STDIO MCP server...\n")
sys.stderr.write("Server ready to receive commands on stdin\n")

task_list = EphemeralTaskList()
rpc_handler = JsonRpcHandler(tools=[
    AppendTaskTool(task_list),
    PrependTaskTool(task_list),
    InsertTaskAfterTool(task_list),
    StartTaskTool(task_list),
    CompleteTaskTool(task_list),
    ListTasksTool(task_list),
    ClearTasksTool(task_list),
])
server = HttpMcpServer(rpc_handler)
server.run()
