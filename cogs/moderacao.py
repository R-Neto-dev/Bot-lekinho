"""Comandos básicos de moderação e consulta do servidor."""

import discord
from discord.ext import commands


class Moderacao(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.hybrid_command(name="clear", description="Apaga mensagens recentes.")
    @commands.has_permissions(manage_messages=True)
    @commands.bot_has_permissions(manage_messages=True)
    async def clear(self, ctx: commands.Context, quantidade: commands.Range[int, 1, 100]):
        if ctx.guild is None or not isinstance(ctx.channel, discord.TextChannel):
            raise commands.NoPrivateMessage()

        apagadas = await ctx.channel.purge(limit=quantidade + 1)
        await ctx.send(f"🧹 {len(apagadas) - 1} mensagem(ns) apagada(s).", delete_after=5)

    @commands.hybrid_command(name="ping", description="Mostra a latência do bot.")
    async def ping(self, ctx: commands.Context):
        await ctx.reply(f"🏓 Pong! `{round(self.bot.latency * 1000)} ms`")

    @commands.hybrid_command(name="userinfo", description="Exibe informações de um membro.")
    async def userinfo(
        self, ctx: commands.Context, membro: discord.Member | None = None
    ):
        membro = membro or ctx.author
        embed = discord.Embed(
            title=f"Informações de {membro.display_name}",
            color=membro.color,
        )
        embed.set_thumbnail(url=membro.display_avatar.url)
        embed.add_field(name="ID", value=str(membro.id))
        embed.add_field(name="Conta criada", value=discord.utils.format_dt(membro.created_at, "D"))
        embed.add_field(
            name="Entrou no servidor",
            value=discord.utils.format_dt(membro.joined_at, "D")
            if membro.joined_at
            else "Desconhecido",
            inline=False,
        )
        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderacao(bot))
