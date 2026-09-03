import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import utils.db as db  # Veritabanı bağlantısı eklendi

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def setup_hook():
    # 1. BOT BAŞLARKEN VERİTABANI TABLOLARINI ZORLA OLUŞTUR
    try:
        await db.init_db()
        print("📁 Veritabanı tabloları başarıyla yüklendi.")
    except Exception as e:
        print(f"❌ Veritabanı başlatılamadı: {e}")

    # 2. Modülleri yükle
    print("Modüller (Cogs) yükleniyor...")
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py') and not filename.startswith('__'):
            try:
                await bot.load_extension(f'cogs.{filename[:-3]}')
                print(f"✅ Yüklendi: {filename}")
            except Exception as e:
                print(f"❌ Yüklenemedi {filename}: {e}")
                
    # 3. Komutları senkronize et
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