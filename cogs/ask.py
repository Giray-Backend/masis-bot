import discord
from discord.ext import commands
from discord import app_commands
from utils.ai_clients import AIClientManager
import utils.db as db 

class AskCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ai_manager = AIClientManager()

    @app_commands.command(name="ask", description="Ask anything to the AI model")
    async def ask(self, interaction: discord.Interaction, prompt: str):
        # Botun yanıt süresi (15 sn) kazanması için defer() çağırıyoruz
        await interaction.response.defer()
        
        try:
            # 1. Hedef ID'yi belirle (Sunucudaysa guild_id, DM'deyse user_id)
            target_id = interaction.guild_id if interaction.guild else interaction.user.id
            
            # 2. utils/db.py içindeki get_guild fonksiyonunu çağır
            data = await db.get_guild(target_id)
            
            # 3. Verileri aiosqlite.Row formatından çek
            provider = data["provider"] if data["provider"] else "gemini"
            encrypted_key = data["encrypted_api_key"]

            if not encrypted_key:
                await interaction.followup.send("❌ API anahtarı bulunamadı. Lütfen `/ai-api` komutu ile ayarlayın.", ephemeral=True)
                return

            # 4. AI Manager üzerinden şifreyi çöz ve yanıtı al
            response_text = await self.ai_manager.get_response(
                provider=provider,
                encrypted_api_key=encrypted_key,
                prompt=prompt
            )
            
            # 5. Discord 2000 Karakter Sınırı Yönetimi (Uzun yanıtları bölerek gönderme)
            if len(response_text) <= 2000:
                await interaction.followup.send(response_text)
            else:
                chunks = [response_text[i:i+1990] for i in range(0, len(response_text), 1990)]
                await interaction.followup.send(chunks[0])
                for chunk in chunks[1:]:
                    await interaction.channel.send(chunk)
            
        except Exception as e:
            await interaction.followup.send(f"⚠️ İşlem sırasında bir hata oluştu: {str(e)}", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AskCog(bot))