"""Google Ads Konnektor für FassadenFix (MCP + Python Fallback)."""
from .mcp_setup import (
    GoogleAdsClient,
    generate_manus_mcp_config,
    generate_env_template,
    verify_credentials,
    install_mcp_server,
    MCP_SERVER_CONFIG,
)

__all__ = [
    "GoogleAdsClient",
    "generate_manus_mcp_config",
    "generate_env_template",
    "verify_credentials",
    "install_mcp_server",
    "MCP_SERVER_CONFIG",
]
