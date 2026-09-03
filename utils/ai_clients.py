import os
import asyncio
from cryptography.fernet import Fernet

import openai
from google import genai
import anthropic

class AIClientManager:
    def __init__(self, fernet_key: str = None):
        key = fernet_key or os.getenv("FERNET_KEY")
        if not key:
            raise ValueError("FERNET_KEY ortam değişkeni veya parametresi bulunamadı!")
        self.fernet = Fernet(key.encode() if isinstance(key, str) else key)

    def decrypt_key(self, encrypted_api_key: str) -> str:
        try:
            return self.fernet.decrypt(encrypted_api_key.encode()).decode()
        except Exception as e:
            raise ValueError(f"API anahtarı şifresi çözülemedi: {str(e)}")

    async def generate_openai_response(self, api_key: str, prompt: str, model: str = "gpt-4o-mini") -> str:
        try:
            client = openai.AsyncOpenAI(api_key=api_key)
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            return response.choices[0].message.content.strip()
        except openai.AuthenticationError:
            return "❌ **OpenAI Hatası:** Geçersiz API anahtarı."
        except Exception as e:
            return f"❌ **OpenAI Hatası:** {str(e)}"

    async def generate_gemini_response(self, api_key: str, prompt: str, model: str = "gemini-3.6-flash") -> str:
        """Google'ın genai SDK'sını güncel 3.6 modeliyle çalıştırır."""
        try:
            client = genai.Client(
                api_key=api_key,
                http_options={'api_version': 'v1'}
            )
            
            response = await client.aio.models.generate_content(
                model=model, 
                contents=prompt
            )
            return response.text.strip()
            
        except Exception as e:
            return f"❌ **Gemini Hatası:** {str(e)}"

    async def generate_claude_response(self, api_key: str, prompt: str, model: str = "claude-3-5-sonnet-20240620") -> str:
        try:
            client = anthropic.AsyncAnthropic(api_key=api_key)
            response = await client.messages.create(
                model=model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.content[0].text.strip()
        except anthropic.AuthenticationError:
            return "❌ **Claude Hatası:** Geçersiz API anahtarı."
        except Exception as e:
            return f"❌ **Claude Hatası:** {str(e)}"

    async def get_response(self, provider: str, encrypted_api_key: str, prompt: str, model: str = None) -> str:
        try:
            raw_api_key = self.decrypt_key(encrypted_api_key)
        except Exception as err:
            return f"🔒 **Güvenlik Hatası:** {str(err)}"

        provider = provider.lower().strip()

        if provider in ["openai", "gpt"]:
            selected_model = model or "gpt-4o-mini"
            return await self.generate_openai_response(raw_api_key, prompt, model=selected_model)

        elif provider in ["gemini", "google"]:
            # Varsayılan model 3.6 sürümüne güncellendi
            selected_model = model or "gemini-3.6-flash"
            return await self.generate_gemini_response(raw_api_key, prompt, model=selected_model)

        elif provider in ["claude", "anthropic"]:
            selected_model = model or "claude-3-5-sonnet-20240620"
            return await self.generate_claude_response(raw_api_key, prompt, model=selected_model)

        else:
            return f"❓ Desteklenmeyen AI sağlayıcısı: `{provider}`"