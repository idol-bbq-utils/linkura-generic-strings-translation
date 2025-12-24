"""
Deprecated: This module is kept for backward compatibility.
Please use src.translate.translator module instead.
"""
import anthropic
from typing import Optional
import warnings


def setup_client(api_key: str, base_url: Optional[str] = None, *args, **kwargs) -> anthropic.Anthropic:
    """
    Deprecated: Use create_translator('claude', api_key, base_url) instead.
    
    Setup Claude API client
    
    Args:
        api_key: API key for Claude
        base_url: Optional base URL for the API
        *args, **kwargs: Additional arguments for the client
        
    Returns:
        Configured Anthropic client
    """
    warnings.warn(
        "claude.setup_client is deprecated. Use create_translator('claude', api_key, base_url) instead.",
        DeprecationWarning,
        stacklevel=2
    )
    
    client_kwargs = {"api_key": api_key, **(kwargs or {})}
    if base_url:
        client_kwargs["base_url"] = base_url
    
    return anthropic.Anthropic(**client_kwargs)

