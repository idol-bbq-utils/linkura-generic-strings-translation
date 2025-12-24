"""
LLM Translator base class and implementations
"""
from abc import ABC, abstractmethod
from typing import List, Optional
import anthropic
import requests


class LLMTranslator(ABC):
    """Base class for LLM-based translators"""
    
    def __init__(self, api_key: str, base_url: Optional[str] = None, model_id: Optional[str] = None):
        """
        Initialize LLM translator
        
        Args:
            api_key: API key for the LLM service
            base_url: Base URL for the API endpoint (optional)
            model_id: Model identifier to use (optional, uses default if not provided)
        """
        self.api_key = api_key
        self.base_url = base_url
        self.model_id = model_id or self.get_default_model()
        self.client = self._setup_client()
    
    @abstractmethod
    def _setup_client(self):
        """
        Setup and return the API client
        
        Returns:
            Configured API client
        """
        pass
    
    @abstractmethod
    def get_default_model(self) -> str:
        """
        Get the default model ID for this translator
        
        Returns:
            Default model identifier
        """
        pass
    
    @abstractmethod
    def translate(self, prompt: str, max_tokens: int = 4000, target_lang: str = 'zh-CN') -> str:
        """
        Translate using the LLM API
        
        Args:
            prompt: The full prompt including texts to translate
            max_tokens: Maximum tokens for the response
            
        Returns:
            Translated text response from the API
        """
        pass


class ClaudeTranslator(LLMTranslator):
    """Claude API implementation of LLM translator"""
    
    def get_default_model(self) -> str:
        """Get default Claude model"""
        return "claude-sonnet-4-5-20250929"
    
    def _setup_client(self) -> anthropic.Anthropic:
        """Setup Claude API client"""
        kwargs = {"api_key": self.api_key}
        if self.base_url:
            kwargs["base_url"] = self.base_url
        return anthropic.Anthropic(**kwargs)
    
    def translate(self, prompt: str, max_tokens: int = 4000, target_lang: str = 'zh-CN') -> str:
        """
        Translate using Claude API
        
        Args:
            prompt: The full prompt including texts to translate
            max_tokens: Maximum tokens for the response
            
        Returns:
            Translated text response from Claude
        """
        message = self.client.messages.create(
            model=self.model_id,
            max_tokens=max_tokens,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return message.content[0].text
    
class DeepseekTranslator(LLMTranslator):
    """Deepseek API implementation of LLM translator"""

    def get_default_model(self) -> str:
        """Get default Deepseek model"""
        return "deepseek-chat"

    def _setup_client(self):
        """Setup Deepseek API client"""
        pass
    
    def translate(self, prompt: str, max_tokens: int = 4000, target_lang: str = 'zh-CN') -> str:
        """
        Translate using Claude API
        
        Args:
            prompt: The full prompt including texts to translate
            max_tokens: Maximum tokens for the response
            
        Returns:
            Translated text response from Claude
        """
        res = requests.post(
            url=self.base_url or "https://api.deepseek.com/chat/completions",
            json={
                "model": self.model_id,
                "temperature": 1.3,
                "messages": [
                    {"role": "user", "content": prompt}
                ]
            },
            headers={
                "Authorization": f"Bearer {self.api_key}"
            }
        )
        if not (res.status_code >= 200 and res.status_code < 300):
            raise ValueError(f"API error: {res.status_code} {res.text}")
        return res.json()["choices"][0]["message"]["content"]

class QWenTranslator(LLMTranslator):
    """Qwen API implementation of LLM translator"""

    def get_default_model(self) -> str:
        """Get default Qwen model"""
        return "qwen-mt-turbo"

    def _setup_client(self):
        """Setup Qwen API client"""
        pass

    def translate(self, prompt: str, max_tokens: int = 4000, target_lang: str = 'zh-CN') -> str:
        """
        Translate using Qwen API
        
        Args:
            prompt: The full prompt including texts to translate
            max_tokens: Maximum tokens for the response
            
        Returns:
            Translated text response from Qwen
        """
        res = requests.post(
            url=self.base_url or "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
            json={
                "model": self.model_id,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "extra_body": {
                    "translation_options": {
                        "source_lang": "ja",
                        "target_lang": target_lang[:2].lower() # zh
                    }
                }
            },
            headers={
                "Authorization": f"Bearer {self.api_key}"
            }
        )
        if not (res.status_code >= 200 and res.status_code < 300):
            raise ValueError(f"API error: {res.status_code} {res.text}")
        return res.json()["choices"][0]["message"]["content"]

def create_translator(
    provider: str,
    api_key: str,
    base_url: Optional[str] = None,
    model_id: Optional[str] = None
) -> LLMTranslator:
    """
    Factory function to create a translator instance
    
    Args:
        provider: Provider name ('claude', etc.)
        api_key: API key for the service
        base_url: Base URL for the API endpoint (optional)
        model_id: Model identifier to use (optional)
        
    Returns:
        Configured translator instance
        
    Raises:
        ValueError: If provider is not supported
    """
    provider = provider.lower()
    
    if provider == "claude":
        return ClaudeTranslator(api_key=api_key, base_url=base_url, model_id=model_id)
    elif provider == "deepseek":
        return DeepseekTranslator(api_key=api_key, base_url=base_url, model_id=model_id)
    elif provider == "qwen":
        return QWenTranslator(api_key=api_key, base_url=base_url, model_id=model_id)
    else:
        raise ValueError(f"Unsupported provider: {provider}. Currently only 'claude', 'deepseek', and 'qwen' are supported.")
