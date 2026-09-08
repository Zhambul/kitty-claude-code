# Copyright (c) 2026 Zhambyl Yermagambet
"""Define Claude Code browser tool values."""

from types import MappingProxyType

CHROME_TOOL_PREFIX = "mcp__claude-in-chrome__"

CHROME_ACTIONS = MappingProxyType({
    "browser_batch": "Run browser actions",
    "file_upload": "Upload file in browser",
    "form_input": "Fill browser form",
    "get_page_text": "Read page text",
    "gif_creator": "Record browser GIF",
    "javascript_tool": "Run JavaScript in browser",
    "list_connected_browsers": "List connected browsers",
    "read_console_messages": "Read browser console",
    "read_network_requests": "Read browser network requests",
    "read_page": "Read page",
    "resize_window": "Resize browser window",
    "select_browser": "Select browser",
    "shortcuts_execute": "Run browser shortcut",
    "shortcuts_list": "List browser shortcuts",
    "switch_browser": "Switch browser",
    "tabs_close_mcp": "Close browser tab",
    "tabs_context_mcp": "Read browser tabs",
    "tabs_create_mcp": "Create browser tab",
    "upload_image": "Upload image in browser",
})
