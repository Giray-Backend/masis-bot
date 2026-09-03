import discord
from discord.ext import commands
from discord import app_commands
from utils.db import update_guild_api, get_guild
from utils.encryption import encrypt_api_key
from utils.i18n import get_text

class ApiKeyModal(discord.ui.Modal):
    def __init__(self, guild_id: int, provider: str, lang: str):
        self.lang = lang
        super().__init__(title=get_text(lang, "modal_title"))
        self.guild_id = guild_id
        self.provider = provider
        
        self.api_key = discord.ui.TextInput(
            label=get_text(lang, "modal_label", provider=provider.capitalize()),
            style=discord.TextStyle.short,
            placeholder=get_text(lang, "modal_placeholder"),
            required=True,
            min_length=20  # Temel uzunluk doğrulaması
        )
        self.add_item(self.api_key)

    async def on_submit(self, interaction: discord.Interaction):
        # Ekstra format kontrolü
        key_value = self.api_key.value.strip()
        if len(key_value) < 20:
            embed = discord.Embed(
                description="❌ " + get_text(self.lang, "api_error"),
                color=discord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        encrypted_key = encrypt_api_key(key_value)
        await update_guild_api(self.guild_id, self.provider, encrypted_key)
        
        embed = discord.Embed(
            description="✅ " + get_text(self.lang, "key_saved", provider=self.provider.capitalize()),
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)

class ApiKeyView(discord.ui.View):
    def __init__(self, guild_id: int, provider: str, guild_name: str, lang: str):
        super().__init__(timeout=300)
        self.guild_id = guild_id
        self.provider = provider
        self.lang = lang
        self.enter_key_button.label = get_text(lang, "btn_enter_key")

    @discord.ui.button(style=discord.ButtonStyle.primary)
    async def enter_key_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(ApiKeyModal(self.guild_id, self.provider, self.lang))

class AiApi(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ai-api", description="Set the AI provider and API key for this server")
    @app_commands.choices(provider=[
        app_commands.Choice(name="OpenAI", value="openai"),
        app_commands.Choice(name="Google Gemini", value="gemini"),
        app_commands.Choice(name="Anthropic Claude", value="claude")
    ])
    @app_commands.default_permissions(administrator=True)
    async def ai_api(self, interaction: discord.Interaction, provider: app_commands.Choice[str]):
        if not interaction.guild:
            await interaction.response.send_message(get_text("en", "server_only"), ephemeral=True)
            return

        guild_data = await get_guild(interaction.guild.id)
        lang = guild_data['language']

        view = ApiKeyView(interaction.guild.id, provider.value, interaction.guild.name, lang)
        
        try:
            instruction = get_text(lang, "dm_instruction", provider=provider.name, guild_name=interaction.guild.name)
            dm_embed = discord.Embed(description=instruction, color=discord.Color.blurple())
            await interaction.user.send(embed=dm_embed, view=view)
            
            success_embed = discord.Embed(description="📬 " + get_text(lang, "dm_sent"), color=discord.Color.green())
            await interaction.response.send_message(embed=success_embed, ephemeral=True)
        except discord.Forbidden:
            error_embed = discord.Embed(description="❌ " + get_text(lang, "dm_failed"), color=discord.Color.red())
            await interaction.response.send_message(embed=error_embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(AiApi(bot))