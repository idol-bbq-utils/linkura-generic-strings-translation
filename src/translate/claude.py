import anthropic
import os

def setup_client(api_key: str, base_url: str, *args, **kwargs) -> anthropic.Anthropic:
    return anthropic.Anthropic(api_key=api_key, base_url=base_url, *args, **kwargs)

