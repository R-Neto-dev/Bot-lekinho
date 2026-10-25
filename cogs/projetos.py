import discord
from discord.ext import commands
from database import buscar_usuario

class Projetos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def criar_projeto(self, ctx):
        github_user = buscar_usuario(ctx.author.id)

        if not github_user:
            await ctx.send("❌ Você precisa registrar seu GitHub primeiro usando !registrar.")
            return

        guild = ctx.guild
        author = ctx.author

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            author: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                manage_channels=True
            )
        }

        canal = await guild.create_text_channel(
            name=f"projeto-{author.name}",
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="Projeto Criado",
            description=f"Criado por {author.mention}\nGitHub: https://github.com/{github_user}",
            color=discord.Color.blue()
        )

        await canal.send(embed=embed)
        await ctx.send(f"Canal criado: {canal.mention}")

async def setup(bot):
    await bot.add_cog(Projetos(bot))