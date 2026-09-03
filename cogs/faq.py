import discord
from discord.ext import commands
from discord import app_commands
from utils.db import get_guild, get_all_faqs
from utils.i18n import get_text

class FAQ(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="faq", description="Bilgi bankasında arama yapın / Search the knowledge base")
    async def faq(self, interaction: discord.Interaction, query: str):
        guild_data = await get_guild(interaction.guild.id) if interaction.guild else None
        lang = guild_data['language'] if guild_data else 'en'
        
        faqs = await get_all_faqs()
        best_match = None
        
        query_words = query.lower().split()
        for faq in faqs:
            keywords = faq['keywords'].lower().split()
            if any(kw in query_words for kw in keywords):
                best_match = faq['answer_key']
                break
                
        if best_match:
            answer = get_text(lang, best_match)
            await interaction.response.send_message(answer, ephemeral=True)
        else:
            await interaction.response.send_message(get_text(lang, "faq_not_found"), ephemeral=True)

async def setup(bot):
    await bot.add_cog(FAQ(bot))