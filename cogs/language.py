import discord
from discord.ext import commands
from discord import app_commands
from utils.db import update_guild_language
from utils.i18n import get_text

class Language(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="language", description="Change the bot language for this server")
    @app_commands.choices(lang=[
        app_commands.Choice(name="Türkçe", value="tr"),
        app_commands.Choice(name="English", value="en"),
        app_commands.Choice(name="Deutsch", value="de"),
        app_commands.Choice(name="Polski", value="pl"),
        app_commands.Choice(name="Русский", value="ru"),
        app_commands.Choice(name="中文", value="zh"),
        app_commands.Choice(name="日本語", value="ja")
    ])
    @app_commands.default_permissions(administrator=True)
    async def language(self, interaction: discord.Interaction, lang: app_commands.Choice[str]):
        if not interaction.guild:
            await interaction.response.send_message(
                get_text("en", "server_only"), 
                ephemeral=True
            )
            return

        await update_guild_language(interaction.guild.id, lang.value)
        
        msg = get_text(lang.value, "lang_updated", lang=lang.name)
        await interaction.response.send_message(msg, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Language(bot))