"""Make.com Automatisierungs-Konnektor für FassadenFix."""
from .mcp_setup import (
    MakeClient,
    generate_manus_mcp_config,
    generate_env_template,
    verify_credentials,
    get_recommended_scenarios,
    MCP_SERVER_CONFIG,
    RECOMMENDED_SCENARIOS,
)

__all__ = [
    "MakeClient",
    "generate_manus_mcp_config",
    "generate_env_template",
    "verify_credentials",
    "get_recommended_scenarios",
    "MCP_SERVER_CONFIG",
    "RECOMMENDED_SCENARIOS",
]
