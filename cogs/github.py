import asyncio

import discord
import requests
from discord.ext import commands

from database import registrar_usuario, buscar_usuario


class GitHub(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx: commands.Context) -> bool:
        """Mantém os comandos GitHub concentrados no canal privado de programação."""
        if ctx.guild is not None and ctx.channel.name != "github":
            await ctx.reply("Use os comandos do GitHub no canal #github.", mention_author=False)
            return False
        return True

    @commands.hybrid_command(name="registrar", description="Vincula seu usuário do GitHub.")
    async def registrar(self, ctx: commands.Context, username: str):
        username = username.strip()
        resposta = await asyncio.to_thread(
            requests.get,
            f"https://api.github.com/users/{username}",
            timeout=10,
        )

        if resposta.status_code != 200:
            await ctx.send("❌ Usuário não encontrado no GitHub.")
            return

        dados = resposta.json()

        registrar_usuario(ctx.author.id, username)

        embed = discord.Embed(
            title="Conta GitHub Registrada",
            description=f"GitHub: https://github.com/{username}",
            color=discord.Color.green()
        )

        embed.set_thumbnail(url=dados["avatar_url"])

        await ctx.send(embed=embed)

    @commands.hybrid_command(
        name="github", description="Exibe o perfil GitHub de um membro."
    )
    async def github(self, ctx: commands.Context, membro: discord.Member | None = None):
        membro = membro or ctx.author
        username = buscar_usuario(membro.id)
        if not username:
            await ctx.send(f"{membro.mention} ainda não cadastrou um GitHub.")
            return

        resposta = await asyncio.to_thread(
            requests.get,
            f"https://api.github.com/users/{username}",
            timeout=10,
        )
        if resposta.status_code != 200:
            await ctx.send("Não foi possível consultar este perfil no GitHub agora.")
            return

        dados = resposta.json()
        embed = discord.Embed(
            title=f"Perfil GitHub de {membro.display_name}",
            url=dados["html_url"],
            description=dados.get("bio") or "Sem biografia pública.",
            color=discord.Color.dark_grey(),
        )
        embed.set_thumbnail(url=dados["avatar_url"])
        embed.add_field(name="Repositórios", value=str(dados["public_repos"]))
        embed.add_field(name="Seguidores", value=str(dados["followers"]))
        embed.add_field(name="Seguindo", value=str(dados["following"]))
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(GitHub(bot))