"""
LLM API Interface for Translation
Supports OpenAPI format compatible and Gemini format LLM interface calls
"""

import os
import json
import requests
from typing import Optional, Dict, List, Any, Union
from dataclasses import dataclass
from enum import Enum


class APIProvider(Enum):
    """API provider enumeration"""
    OPENAI = "openai"
    GEMINI = "gemini"
    CLAUDE = "claude"
    CUSTOM = "custom"


@dataclass
class APIConfig:
    """API configuration class"""
    provider: APIProvider
    api_key: str
    base_url: str
    model: str
    temperature: float = 0.7
    max_tokens: int = 2048
    timeout: int = 30


class LLMAPIClient:
    """LLM API client, supports multiple API formats"""
    
    def __init__(self, config: Optional[APIConfig] = None):
        """
        Initialize API client
        
        Args:
            config: API configuration, if None load from environment variables
        """
        if config is None:
            config = self._load_config_from_env()
        self.config = config
        
    def _load_config_from_env(self) -> APIConfig:
        """Load configuration from environment variables"""
        provider_str = os.getenv('LLM_PROVIDER', 'openai').lower()
        provider = APIProvider(provider_str)
        
        api_key = os.getenv('LLM_API_KEY')
        if not api_key:
            raise ValueError("LLM_API_KEY environment variable is required")
            
        base_url = os.getenv('LLM_BASE_URL', self._get_default_base_url(provider))
        model = os.getenv('LLM_MODEL', self._get_default_model(provider))
        temperature = float(os.getenv('LLM_TEMPERATURE', '0.7'))
        max_tokens = int(os.getenv('LLM_MAX_TOKENS', '2048'))
        timeout = int(os.getenv('LLM_TIMEOUT', '30'))
        
        return APIConfig(
            provider=provider,
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout
        )
    
    def _get_default_base_url(self, provider: APIProvider) -> str:
        """Get default base URL"""
        defaults = {
            APIProvider.OPENAI: "https://api.openai.com/v1",
            APIProvider.GEMINI: "https://generativelanguage.googleapis.com/v1",
            APIProvider.CLAUDE: "https://api.anthropic.com",
            APIProvider.CUSTOM: "http://localhost:8000"
        }
        return defaults.get(provider, "https://api.openai.com/v1")
    
    def _get_default_model(self, provider: APIProvider) -> str:
        """Get default model name"""
        defaults = {
            APIProvider.OPENAI: "gpt-3.5-turbo",
            APIProvider.GEMINI: "gemini-pro",
            APIProvider.CLAUDE: "claude-3-sonnet-20240229",
            APIProvider.CUSTOM: "default"
        }
        return defaults.get(provider, "gpt-3.5-turbo")
    
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send chat completion request
        
        Args:
            messages: Message list, format: [{"role": "user", "content": "..."}]
            temperature: Temperature parameter
            max_tokens: Maximum token count
            **kwargs: Other parameters
            
        Returns:
            API response result
        """
        if self.config.provider == APIProvider.OPENAI:
            return self._openai_chat_completion(messages, temperature, max_tokens, **kwargs)
        elif self.config.provider == APIProvider.GEMINI:
            return self._gemini_chat_completion(messages, temperature, max_tokens, **kwargs)
        elif self.config.provider == APIProvider.CLAUDE:
            return self._claude_chat_completion(messages, temperature, max_tokens, **kwargs)
        else:
            return self._custom_chat_completion(messages, temperature, max_tokens, **kwargs)
    
    def _openai_chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """OpenAI format chat completion request"""
        url = f"{self.config.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.config.model,
            "messages": messages,
            "temperature": temperature or self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
            **kwargs
        }
        
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=self.config.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def _gemini_chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Gemini format chat completion request"""
        url = f"{self.config.base_url}/models/{self.config.model}:generateContent"
        
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.config.api_key
        }
        
        # Convert message format to Gemini format
        gemini_messages = self._convert_to_gemini_format(messages)
        
        payload = {
            "contents": gemini_messages,
            "generationConfig": {
                "temperature": temperature or self.config.temperature,
                "maxOutputTokens": max_tokens or self.config.max_tokens,
                **kwargs
            }
        }
        
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=self.config.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def _claude_chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Claude format chat completion request"""
        url = f"{self.config.base_url}/v1/messages"
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        # Extract system message
        system_message = None
        user_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append(msg)
        
        payload = {
            "model": self.config.model,
            "messages": user_messages,
            "temperature": temperature or self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
            **kwargs
        }
        
        if system_message:
            payload["system"] = system_message
        
        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=self.config.timeout
        )
        response.raise_for_status()
        return response.json()
    
    def _custom_chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Custom format chat completion request (OpenAI compatible)"""
        return self._openai_chat_completion(messages, temperature, max_tokens, **kwargs)
    
    def _convert_to_gemini_format(self, messages: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Convert OpenAI format messages to Gemini format"""
        gemini_contents = []
        
        for message in messages:
            role = message["role"]
            content = message["content"]
            
            if role == "system":
                # Gemini merges system messages into user messages
                gemini_contents.append({
                    "role": "user",
                    "parts": [{"text": f"System: {content}"}]
                })
            elif role == "user":
                gemini_contents.append({
                    "role": "user",
                    "parts": [{"text": content}]
                })
            elif role == "assistant":
                gemini_contents.append({
                    "role": "model",
                    "parts": [{"text": content}]
                })
        
        return gemini_contents
    
    def extract_response_content(self, response: Dict[str, Any]) -> str:
        """Extract text content from API response"""
        if self.config.provider == APIProvider.OPENAI or self.config.provider == APIProvider.CUSTOM:
            return response["choices"][0]["message"]["content"]
        elif self.config.provider == APIProvider.GEMINI:
            return response["candidates"][0]["content"]["parts"][0]["text"]
        elif self.config.provider == APIProvider.CLAUDE:
            return response["content"][0]["text"]
        else:
            raise ValueError(f"Unsupported provider: {self.config.provider}")


def translate_text(
    text: str,
    target_language: str = "zh-CN",
    source_language: str = "auto",
    api_key: Optional[str] = None,
    provider: str = "openai",
    model: Optional[str] = None,
    **kwargs
) -> str:
    """
    Convenience function for translating text
    
    Args:
        text: Text to translate
        target_language: Target language
        source_language: Source language
        api_key: API key, if None read from environment variables
        provider: API provider
        model: Model name
        **kwargs: Other parameters
        
    Returns:
        Translated text
    """
    # Build configuration
    if api_key:
        config = APIConfig(
            provider=APIProvider(provider.lower()),
            api_key=api_key,
            base_url=kwargs.get('base_url', ''),
            model=model or '',
            temperature=kwargs.get('temperature', 0.3),
            max_tokens=kwargs.get('max_tokens', 2048)
        )
        if not config.base_url:
            config.base_url = LLMAPIClient(config)._get_default_base_url(config.provider)
        if not config.model:
            config.model = LLMAPIClient(config)._get_default_model(config.provider)
        
        client = LLMAPIClient(config)
    else:
        client = LLMAPIClient()
    
    # Build translation prompt
    if source_language == "auto":
        prompt = f"""Please translate the following text to {target_language}:

{text}

Please return only the translation result without additional explanations."""
    else:
        prompt = f"""Please translate the following {source_language} text to {target_language}:

{text}

Please return only the translation result without additional explanations."""
    
    messages = [
        {"role": "system", "content": "You are a professional translation assistant capable of accurately translating various languages."},
        {"role": "user", "content": prompt}
    ]
    
    # Send request
    response = client.chat_completion(messages, **kwargs)
    
    # Extract translation result
    return client.extract_response_content(response).strip()


def batch_translate(
    texts: List[str],
    target_language: str = "zh-CN",
    source_language: str = "auto",
    **kwargs
) -> List[str]:
    """
    Batch translate texts
    
    Args:
        texts: List of texts to translate
        target_language: Target language
        source_language: Source language
        **kwargs: Other parameters
        
    Returns:
        List of translated texts
    """
    results = []
    
    for text in texts:
        try:
            translated = translate_text(
                text,
                target_language=target_language,
                source_language=source_language,
                **kwargs
            )
            results.append(translated)
        except Exception as e:
            print(f"Translation failed for '{text}': {e}")
            results.append(text)  # Keep original text when translation fails
    
    return results


# Environment variable configuration example:
# export LLM_PROVIDER=openai          # or gemini, claude, custom
# export LLM_API_KEY=your_api_key
# export LLM_BASE_URL=https://api.openai.com/v1
# export LLM_MODEL=gpt-3.5-turbo
# export LLM_TEMPERATURE=0.7
# export LLM_MAX_TOKENS=2048
# export LLM_TIMEOUT=30


if __name__ == "__main__":
    # Usage examples
    
    # 1. Using environment variable configuration
    try:
        result = translate_text("Hello, world!", "zh-CN")
        print(f"Translation result: {result}")
    except Exception as e:
        print(f"Translation failed: {e}")
    
    # 2. Using function parameter configuration
    try:
        result = translate_text(
            "Hello, world!",
            "zh-CN",
            api_key="your_api_key",
            provider="openai",
            model="gpt-3.5-turbo"
        )
        print(f"Translation result: {result}")
    except Exception as e:
        print(f"Translation failed: {e}")
    
    # 3. Batch translation
    texts = ["Hello", "World", "Python"]
    try:
        results = batch_translate(texts, "zh-CN")
        for original, translated in zip(texts, results):
            print(f"{original} -> {translated}")
    except Exception as e:
        print(f"Batch translation failed: {e}")