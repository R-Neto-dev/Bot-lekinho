import discord
from discord.ext import commands
import yt_dlp

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def play(self, ctx, *, search):
        if not ctx.author.voice:
            await ctx.send("Você precisa estar em um canal de voz!")
            return

        channel = ctx.author.voice.channel
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)

        if not voice:
            voice = await channel.connect()

        ydl_opts = {
            'format': 'bestaudio',
            'noplaylist': True,
            'quiet': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{search}", download=False)['entries'][0]
            url = info['url']
            title = info['title']

        source = await discord.FFmpegOpusAudio.from_probe(url)

        voice.play(source)

        await ctx.send(f"🎶 Tocando: {title}")

    @commands.command()
    async def stop(self, ctx):
        voice = discord.utils.get(self.bot.voice_clients, guild=ctx.guild)
        if voice:
            await voice.disconnect()
            await ctx.send("⏹ Música parada!")

async def setup(bot):
    await bot.add_cog(Music(bot))