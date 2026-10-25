from pathlib import Path

import discord
from discord.ext import commands

class ComandosGerais(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- SEU COMANDO !ola ---
    @commands.hybrid_command(name="ola", description="Cumprimenta o usuário.")
    async def ola(self, ctx: commands.Context):
        nome = ctx.author.name
        await ctx.reply(f"Olá, {nome}! Tudo bem?")

    @commands.hybrid_command(
        name="enviar_embed", description="Envia um cartão de boas-vindas."
    )
    async def enviar_embed(self, ctx: commands.Context):
        nome = ctx.author.display_name
        logo_path = Path(__file__).resolve().parent.parent / "imagens" / "logo-discord.jpg"

        try:
            imagem = discord.File(logo_path, filename="logo-discord.jpg")
            embed = discord.Embed(
                title="✦ BEM-VINDO(A) À TROPA ✦",
                description=(
                    f"É um prazer ter você por aqui, **{nome}**!\n\n"
                    "A **Tropa dos Magnatas** é o ponto de encontro para "
                    "quem curte programação, tecnologia e games."
                ),
                color=discord.Color.from_rgb(255, 184, 77),
            )
            embed.set_author(
                name=f"Novo membro • {nome}",
                icon_url=ctx.author.display_avatar.url,
            )
            embed.set_thumbnail(url=ctx.author.display_avatar.url)
            embed.add_field(
                name="💻 PROGRAMAÇÃO",
                value="Projetos, GitHub, dúvidas e calls de desenvolvimento.",
                inline=True,
            )
            embed.add_field(
                name="🎮 GAMES",
                value="Partidas, clips e calls para jogar com a galera.",
                inline=True,
            )
            embed.add_field(
                name="🚀 COMECE AGORA",
                value="Escolha seus cargos em `#pedir-cargo` e desbloqueie suas áreas.",
                inline=False,
            )
            embed.set_image(url="attachment://logo-discord.jpg")
            embed.set_footer(
                text="Tropa dos Magnatas • conecte-se, aprenda e divirta-se"
            )

            await ctx.reply(embed=embed, file=imagem)
        except FileNotFoundError:
            await ctx.reply(
                "Erro: a imagem `imagens/logo-discord.jpg` não foi encontrada."
            )

    @commands.hybrid_command(name="ola_lekinho", description="Diz olá de volta!")
    async def ola_slash(self, ctx: commands.Context):
        # Hybrid Command funciona para barra e prefixo
        await ctx.reply("Olá como vai?")

async def setup(bot):
    await bot.add_cog(ComandosGerais(bot))