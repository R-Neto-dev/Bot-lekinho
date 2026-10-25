"""Ponto de entrada do bot."""

import logging
import os

import discord
from discord.ext import commands

from database import criar_tabela
from keep_alive import keep_alive

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

intents = discord.Intents.all()


class Ajuda(commands.HelpCommand):
    """Exibe os comandos em um painel organizado ao usar !help."""

    async def send_bot_help(self, mapping):
        embed = discord.Embed(
            title="📚 Comandos disponíveis",
            description="Use `!comando` ou `/comando` quando houver suporte a Slash Command.",
            color=discord.Color.blurple(),
        )
        for cog, commands_list in mapping.items():
            comandos = [
                f"`!{comando.name}` — {comando.short_doc or 'Sem descrição'}"
                for comando in commands_list
                if not comando.hidden
            ]
            if comandos:
                embed.add_field(
                    name=cog.qualified_name if cog else "Geral",
                    value="\n".join(comandos),
                    inline=False,
                )
        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        await self.get_destination().send(
            f"Use `{self.context.prefix}{command.qualified_name}` para executar este comando."
        )


bot = commands.Bot("!", intents=intents, help_command=Ajuda())

COGS = [
    "cogs.eventos",
    "cogs.comandos",
    "cogs.boas",
    "cogs.github",
    "cogs.setup_servidor",
    "cogs.moderacao",
    "cogs.projetos",
    "cogs.musica",
]


async def load_cogs() -> None:
    for cog in COGS:
        await bot.load_extension(cog)
        logger.info("Cog carregado: %s", cog)


@bot.event
async def setup_hook() -> None:
    """Inicializa banco e Cogs uma única vez antes de conectar ao Discord."""
    criar_tabela()
    await load_cogs()
    await bot.tree.sync()
    logger.info("Comandos de barra sincronizados.")


@bot.event
async def on_ready():
    logger.info("Bot conectado como %s (%s)", bot.user, bot.user.id if bot.user else "sem ID")


@bot.event
async def on_message(msg: discord.Message):
    if msg.author.bot:
        return
    await bot.process_commands(msg)


@bot.event
async def on_command_error(ctx: commands.Context, error: commands.CommandError) -> None:
    """Converte erros comuns em mensagens úteis para o usuário."""
    if hasattr(ctx.command, "on_error"):
        return

    original = getattr(error, "original", error)
    if isinstance(original, commands.CommandNotFound):
        return
    if isinstance(original, commands.MissingPermissions):
        await ctx.send("Você não tem permissão para usar este comando.")
    elif isinstance(original, commands.BotMissingPermissions):
        await ctx.send("Eu não tenho as permissões necessárias para executar isso.")
    elif isinstance(original, commands.MissingRequiredArgument):
        await ctx.send(f"Está faltando o argumento: `{original.param.name}`.")
    elif isinstance(original, commands.BadArgument):
        await ctx.send("Não consegui entender um dos argumentos informados.")
    elif isinstance(original, commands.NoPrivateMessage):
        await ctx.send("Este comando só pode ser usado em um servidor.")
    else:
        logger.exception("Erro não tratado no comando %s", ctx.command, exc_info=original)
        await ctx.send("Ocorreu um erro inesperado ao executar o comando.")


token = os.getenv("DISCORD_TOKEN")
if not token:
    raise RuntimeError("Defina a variável de ambiente DISCORD_TOKEN antes de iniciar o bot.")

keep_alive()
bot.run(token)