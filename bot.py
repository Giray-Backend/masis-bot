import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

# Ortam değişkenlerini yükle
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Bot ayarları
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Bot başlarken Cogs klasöründeki dosyaları yükle
@bot.event
async def setup_hook():
    print("Modüller (Cogs) yükleniyor...")
    # cogs klasöründeki tüm .py dosyalarını bul
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and not filename.startswith('__'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"✅ Yüklendi: {filename}")
            except Exception as e:
                print(f"❌ Yüklenemedi {filename}: {e}")
                
    # Tüm komutları Discord ile senkronize et
    try:
        synced = await bot.tree.sync()
        print(f"🌐 Toplam {len(synced)} komut senkronize edildi.")
    except Exception as e:
        print(f"Senkronizasyon hatası: {e}")

@bot.event
async def on_ready():
    print(f"🤖 Giriş yapıldı: {bot.user.name}")

if __name__ == "__main__":
    if not TOKEN:
        print("HATA: DISCORD_TOKEN bulunamadı!")
    else:
        bot.run(TOKEN)