# cogs/eventos.py

from datetime import time

import discord
from discord.ext import commands, tasks

from cogs.setup_servidor import PEDIR_CARGO_CHANNEL_NAME


class Eventos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Inicia a task aqui, dentro do Cog
        self.enviar_messagem.start()

    # --- SEU EVENTO on_member_join ---
    @commands.Cog.listener()
    async def on_member_join(self, membro: discord.Member):
        cargo_base = discord.utils.get(membro.guild.roles, name="Membro")
        if cargo_base and cargo_base < membro.guild.me.top_role:
            try:
                await membro.add_roles(cargo_base, reason="Cargo base de entrada no servidor")
            except discord.Forbidden:
                pass

        avatar_url = membro.display_avatar.url
        nome_usuario = membro.name

        categoria_inicio = discord.utils.get(
            membro.guild.categories,
            name="📌 INÍCIO",
        )
        canal = (
            discord.utils.get(categoria_inicio.text_channels, name="boas-vindas")
            if categoria_inicio
            else None
        )
        if not isinstance(canal, discord.abc.Messageable):
            return

        embed = discord.Embed(
            title="✦ BEM-VINDO(A) À TROPA ✦",
            description=(
                f"É um prazer receber você, {membro.mention}!\n\n"
                "Aqui você encontra duas comunidades em um só lugar:\n"
                "💻 **Programação** • dev, GitHub e calls de criação.\n"
                "🎮 **Games** • partidas, clips e calls para jogar.\n\n"
                "Escolha seu caminho no canal `#pedir-cargo` e desbloqueie seu acesso."
            ),
            color=discord.Color.from_rgb(255, 184, 77),
        )
        embed.set_author(name=f"Novo membro • {nome_usuario}", icon_url=avatar_url)
        embed.set_thumbnail(url=avatar_url)
        embed.add_field(
            name="🚀 Seu próximo passo",
            value="Selecione **Programador**, **Gamer** ou **os dois** em `#pedir-cargo`.",
            inline=False,
        )
        embed.set_footer(text="Tropa dos Magnatas • conecte-se, aprenda e divirta-se")
        await canal.send(
            "👇 Escolha seus cargos no canal "
            f"`#{PEDIR_CARGO_CHANNEL_NAME}` para liberar suas áreas.",
            embed=embed,
        )

    # --- SUA TAREFA AGENDADA (Loop) ---
    @tasks.loop(time=time(10, 30))
    async def enviar_messagem(self):
        canal = self.bot.get_channel(1445248056860610674)
        if isinstance(canal, discord.abc.Messageable):
            await canal.send("Bora acordar")
            
    # Para garantir que o loop só comece quando o bot estiver pronto
    @enviar_messagem.before_loop
    async def before_enviar_messagem(self):
        await self.bot.wait_until_ready()

async def setup(bot):
    await bot.add_cog(Eventos(bot))