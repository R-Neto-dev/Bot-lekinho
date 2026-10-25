"""Configuração automatizada e painel persistente de cargos do servidor."""

from __future__ import annotations

import discord
from discord.ext import commands


BASE_ROLE_NAME = "Membro"
PROGRAMADOR_ROLE_NAME = "Programador"
GAMER_ROLE_NAME = "Gamer"
ADM_ROLE_NAME = "ADM"

START_CATEGORY_NAME = "📌 INÍCIO"
DEV_CATEGORY_NAME = "💻 PROGRAMAÇÃO"
GAMES_CATEGORY_NAME = "🎮 GAMES"
PEDIR_CARGO_CHANNEL_NAME = "pedir-cargo"
GITHUB_CHANNEL_NAME = "github"
COMMANDS_CHANNEL_NAME = "comandos"
DEV_VOICE_CHANNELS = ("💻 Call Dev 1", "💻 Call Dev 2")
GAMES_VOICE_CHANNELS = ("🎮 Call Game 1", "🎮 Call Game 2")


class RoleSelect(discord.ui.Select):
    """Menu persistente que atribui os cargos escolhidos pelo membro."""

    def __init__(self) -> None:
        options = [
            discord.SelectOption(
                label="Quero programar",
                value="programador",
                emoji="💻",
                description="Libera os canais e calls de programação.",
            ),
            discord.SelectOption(
                label="Quero apenas jogar",
                value="gamer",
                emoji="🎮",
                description="Libera os canais e calls de games.",
            ),
            discord.SelectOption(
                label="Quero os dois!",
                value="ambos",
                emoji="🚀",
                description="Libera programação e games.",
            ),
        ]
        super().__init__(
            placeholder="Escolha seus interesses...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="setup_servidor:selecao_cargo",
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        if interaction.guild is None or not isinstance(interaction.user, discord.Member):
            await interaction.response.send_message(
                "Este menu só pode ser usado dentro de um servidor.",
                ephemeral=True,
            )
            return

        guild = interaction.guild
        membro = interaction.user
        programador = discord.utils.get(guild.roles, name=PROGRAMADOR_ROLE_NAME)
        gamer = discord.utils.get(guild.roles, name=GAMER_ROLE_NAME)
        base = discord.utils.get(guild.roles, name=BASE_ROLE_NAME)
        if not programador or not gamer or not base:
            await interaction.response.send_message(
                "Os cargos ainda não foram configurados. Peça a um administrador para usar `!setup`.",
                ephemeral=True,
            )
            return

        escolhida = self.values[0]
        cargos_adicionar: list[discord.Role] = [base]
        cargos_remover: list[discord.Role] = []
        if escolhida == "programador":
            cargos_adicionar.append(programador)
            cargos_remover.append(gamer)
            mensagem = "Programador"
        elif escolhida == "gamer":
            cargos_adicionar.append(gamer)
            cargos_remover.append(programador)
            mensagem = "Gamer"
        else:
            cargos_adicionar.extend((programador, gamer))
            mensagem = "Programador e Gamer"

        try:
            if cargos_remover:
                await membro.remove_roles(*cargos_remover, reason="Seleção no painel de cargos")
            await membro.add_roles(*cargos_adicionar, reason="Seleção no painel de cargos")
        except discord.Forbidden:
            await interaction.response.send_message(
                "Não consegui alterar seus cargos. Verifique se meu cargo está acima de "
                "`Membro`, `Programador` e `Gamer` na hierarquia.",
                ephemeral=True,
            )
            return

        await interaction.response.send_message(
            f"✅ Cargos atualizados: **{mensagem}**.",
            ephemeral=True,
        )


class RolePanel(discord.ui.View):
    """View persistente: não expira e é registrada após cada reinicialização."""

    def __init__(self) -> None:
        super().__init__(timeout=None)
        self.add_item(RoleSelect())


class SetupServidor(commands.Cog):
    """Cria a estrutura inicial de um servidor de programação e games."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        # O custom_id fixo e timeout=None permitem o funcionamento após restart.
        bot.add_view(RolePanel())

    @commands.hybrid_command(
        name="setup",
        description="Cria cargos, categorias, canais e o painel de seleção.",
    )
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    @commands.bot_has_permissions(
        manage_roles=True,
        manage_channels=True,
        manage_guild=True,
        send_messages=True,
    )
    async def setup(self, ctx: commands.Context) -> None:
        """Executa o setup de forma idempotente, sem duplicar recursos."""
        if ctx.guild is None:
            raise commands.NoPrivateMessage()

        guild = ctx.guild
        roles = await self._ensure_roles(guild)
        await self._ensure_public_area(guild)
        await self._ensure_private_area(
            guild,
            DEV_CATEGORY_NAME,
            roles[PROGRAMADOR_ROLE_NAME],
            ["geral-dev", "duvidas", GITHUB_CHANNEL_NAME],
            list(DEV_VOICE_CHANNELS),
            [roles[ADM_ROLE_NAME]],
        )
        await self._ensure_private_area(
            guild,
            GAMES_CATEGORY_NAME,
            roles[GAMER_ROLE_NAME],
            ["geral-games", "clips"],
            list(GAMES_VOICE_CHANNELS),
            [roles[ADM_ROLE_NAME]],
        )
        await self._remove_unmanaged_channels(guild)
        await self._remove_empty_legacy_categories(guild)
        await self._ensure_roles_panel(guild)
        await ctx.reply(
            "✅ Setup concluído! Cargos, categorias, canais e painel foram configurados.",
            mention_author=False,
        )

    async def _ensure_roles(self, guild: discord.Guild) -> dict[str, discord.Role]:
        roles: dict[str, discord.Role] = {}
        for name, color in (
            (BASE_ROLE_NAME, discord.Color.light_grey()),
            (PROGRAMADOR_ROLE_NAME, discord.Color.blue()),
            (GAMER_ROLE_NAME, discord.Color.green()),
            (ADM_ROLE_NAME, discord.Color.red()),
        ):
            matches = [item for item in guild.roles if item.name == name]
            role = matches[0] if matches else None
            if role is None:
                permissions = discord.Permissions.none()
                if name == ADM_ROLE_NAME:
                    permissions = discord.Permissions(
                        manage_channels=True,
                        manage_roles=True,
                        manage_messages=True,
                        moderate_members=True,
                        move_members=True,
                        mute_members=True,
                        deafen_members=True,
                        view_channel=True,
                        connect=True,
                        speak=True,
                    )
                role = await guild.create_role(
                    name=name,
                    color=color,
                    permissions=permissions,
                    reason="Setup automático",
                )
            elif name == ADM_ROLE_NAME:
                await role.edit(
                    permissions=discord.Permissions(
                        manage_channels=True,
                        manage_roles=True,
                        manage_messages=True,
                        moderate_members=True,
                        move_members=True,
                        mute_members=True,
                        deafen_members=True,
                        view_channel=True,
                        connect=True,
                        speak=True,
                    ),
                    reason="Atualização do setup automático",
                )
            await self._remove_duplicate_roles(guild, role, matches[1:])
            roles[name] = role
        return roles

    async def _remove_duplicate_roles(
        self,
        guild: discord.Guild,
        role: discord.Role,
        duplicates: list[discord.Role],
    ) -> None:
        """Consolida cargos iguais e só remove cópias que o bot pode gerenciar."""
        bot_member = guild.me
        if bot_member is None:
            return
        for duplicate in duplicates:
            if duplicate >= bot_member.top_role:
                continue
            for member in list(duplicate.members):
                if role < bot_member.top_role:
                    await member.add_roles(role, reason="Consolidação de cargo duplicado")
                await member.remove_roles(
                    duplicate,
                    reason="Consolidação de cargo duplicado",
                )
            await duplicate.delete(reason="Remoção de cargo duplicado")

    async def _ensure_public_area(self, guild: discord.Guild) -> None:
        public_overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
            )
        }
        category = await self._ensure_category(guild, START_CATEGORY_NAME, public_overwrites)
        welcome_channel = None
        for name in (
            "geral",
            "regras",
            "boas-vindas",
            PEDIR_CARGO_CHANNEL_NAME,
            COMMANDS_CHANNEL_NAME,
        ):
            channel = await self._ensure_text_channel(guild, name, category)
            await channel.edit(
                overwrites=public_overwrites,
                reason="Atualização do setup automático",
            )
            if name == "boas-vindas":
                welcome_channel = channel
        if welcome_channel is not None and guild.system_channel != welcome_channel:
            await guild.edit(
                system_channel=welcome_channel,
                reason="Definição do canal oficial de boas-vindas",
            )

    async def _remove_unmanaged_channels(self, guild: discord.Guild) -> None:
        """Remove somente canais extras das categorias mantidas pelo setup."""
        canais_permitidos = {
            START_CATEGORY_NAME: {
                "geral",
                "regras",
                "boas-vindas",
                PEDIR_CARGO_CHANNEL_NAME,
                COMMANDS_CHANNEL_NAME,
            },
            DEV_CATEGORY_NAME: {"geral-dev", "duvidas", GITHUB_CHANNEL_NAME}
            | set(DEV_VOICE_CHANNELS),
            GAMES_CATEGORY_NAME: {"geral-games", "clips"} | set(GAMES_VOICE_CHANNELS),
        }
        for category_name, allowed_names in canais_permitidos.items():
            category = discord.utils.get(guild.categories, name=category_name)
            if category is None:
                continue
            for channel in list(category.channels):
                if channel.name not in allowed_names:
                    await channel.delete(reason="Limpeza da estrutura do setup")

    async def _remove_empty_legacy_categories(self, guild: discord.Guild) -> None:
        """Remove categorias padrão antigas apenas quando estão vazias."""
        legacy_names = {"Canais de Texto", "Canais de Voz", "Text Channels", "Voice Channels"}
        for category in list(guild.categories):
            if category.name in legacy_names and not category.channels:
                await category.delete(reason="Limpeza de categoria padrão vazia")

    async def _ensure_private_area(
        self,
        guild: discord.Guild,
        category_name: str,
        role: discord.Role,
        text_channels: list[str],
        voice_channels: list[str],
        extra_roles: list[discord.Role] | None = None,
    ) -> None:
        extra_roles = extra_roles or []
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            role: discord.PermissionOverwrite(view_channel=True),
        }
        for extra_role in extra_roles:
            overwrites[extra_role] = discord.PermissionOverwrite(view_channel=True)
        category = await self._ensure_category(guild, category_name, overwrites)
        for name in text_channels:
            channel = await self._ensure_text_channel(guild, name, category)
            await channel.edit(overwrites=overwrites, reason="Atualização do setup automático")
        for name in voice_channels:
            channel = discord.utils.get(category.voice_channels, name=name)
            if channel is None:
                channel = await guild.create_voice_channel(
                    name, category=category, reason="Setup automático"
                )
            await channel.edit(overwrites=overwrites, reason="Atualização do setup automático")

    async def _ensure_category(
        self,
        guild: discord.Guild,
        name: str,
        overwrites: dict[discord.Role, discord.PermissionOverwrite] | None = None,
    ) -> discord.CategoryChannel:
        categories = [item for item in guild.categories if item.name == name]
        category = categories[0] if categories else None
        if category is None:
            category = await guild.create_category(
                name,
                overwrites=overwrites or {},
                reason="Setup automático",
            )
        elif overwrites is not None:
            await category.edit(overwrites=overwrites, reason="Atualização do setup automático")
        for duplicate in categories[1:]:
            if not duplicate.channels:
                await duplicate.delete(reason="Remoção de categoria duplicada vazia")
        return category

    async def _ensure_text_channel(
        self, guild: discord.Guild, name: str, category: discord.CategoryChannel
    ) -> discord.TextChannel:
        channels = [item for item in category.text_channels if item.name == name]
        channel = channels[0] if channels else None
        if channel is None:
            channel = await guild.create_text_channel(
                name, category=category, reason="Setup automático"
            )
        for duplicate in channels[1:]:
            await duplicate.delete(reason="Remoção de canal duplicado")
        return channel

    async def _ensure_roles_panel(self, guild: discord.Guild) -> None:
        embed = discord.Embed(
            title="✦ ESCOLHA SEU CAMINHO ✦",
            description=(
                "Entre para a comunidade e desbloqueie as áreas que combinam com você.\n\n"
                "Use o menu abaixo para escolher seu perfil. "
                "A escolha pode ser alterada quando quiser em `#pedir-cargo`."
            ),
            color=discord.Color.from_rgb(91, 77, 255),
        )
        if self.bot.user:
            embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.add_field(
            name="💻 PROGRAMADOR",
            value="Dev, GitHub, dúvidas e calls exclusivas.",
            inline=True,
        )
        embed.add_field(
            name="🎮 GAMER",
            value="Games, clips e calls para jogar com a galera.",
            inline=True,
        )
        embed.add_field(
            name="🚀 DUPLO ACESSO",
            value="Libere as duas áreas de uma vez.",
            inline=False,
        )
        embed.set_footer(text="Tropa dos Magnatas • escolha, conecte-se e evolua")
        for channel_name in (
            PEDIR_CARGO_CHANNEL_NAME,
        ):
            category = discord.utils.get(guild.categories, name=START_CATEGORY_NAME)
            channel = (
                discord.utils.get(category.text_channels, name=channel_name)
                if category
                else None
            )
            if channel is None:
                continue

            painel_existente = None
            async for message in channel.history(limit=50):
                if (
                    message.author == self.bot.user
                    and message.embeds
                    and message.embeds[0].title in {
                        "👋 Escolha seus cargos",
                        "✦ ESCOLHA SEU CAMINHO ✦",
                    }
                ):
                    painel_existente = message
                    break
            if painel_existente is None:
                await channel.send(
                    embed=embed,
                    view=RolePanel(),
                )
            else:
                await painel_existente.edit(
                    embed=embed,
                    view=RolePanel(),
                )

        await self._ensure_commands_panel(guild)

    async def _ensure_commands_panel(self, guild: discord.Guild) -> None:
        category = discord.utils.get(guild.categories, name=START_CATEGORY_NAME)
        channel = (
            discord.utils.get(category.text_channels, name=COMMANDS_CHANNEL_NAME)
            if category
            else None
        )
        if channel is None:
            return

        embed = discord.Embed(
            title="✦ CENTRAL DE COMANDOS ✦",
            description=(
                "Tudo o que você precisa para aproveitar a **Tropa dos Magnatas**.\n"
                "Prefixo: `!` • Slash Commands: `/`"
            ),
            color=discord.Color.from_rgb(91, 77, 255),
        )
        embed.add_field(
            name="🌐 Gerais",
            value="`!help`\n`!ola`\n`!enviar_embed`",
            inline=False,
        )
        embed.add_field(
            name="🎭 Cargos",
            value="`!cargo` ou `/cargo` — use em #pedir-cargo",
            inline=False,
        )
        embed.add_field(
            name="🐙 GitHub",
            value="`!registrar <usuário>`\n`!github`\n`!github @membro`",
            inline=False,
        )
        embed.add_field(
            name="🛡️ Moderação e informações",
            value="`!ping`\n`!userinfo [@membro]`\n`!clear <quantidade>`",
            inline=False,
        )
        embed.add_field(
            name="🚀 Projetos e música",
            value="`!criar_projeto`\n`!play <busca>`\n`!stop`",
            inline=False,
        )
        embed.set_footer(text="Tropa dos Magnatas • use os comandos com responsabilidade")

        async for message in channel.history(limit=50):
            if message.author == self.bot.user and message.embeds:
                if message.embeds[0].title == embed.title:
                    await message.edit(embed=embed)
                    return
        await channel.send(embed=embed)

    async def cog_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ) -> None:
        original = getattr(error, "original", error)
        if isinstance(original, commands.MissingPermissions):
            await ctx.send("❌ Apenas administradores podem usar `!setup`.")
        elif isinstance(original, commands.BotMissingPermissions):
            await ctx.send(
                "❌ Não consigo concluir o setup. Dê ao bot **Gerenciar canais**, "
                "**Gerenciar cargos**, **Gerenciar servidor** e **Enviar mensagens**."
            )
        else:
            raise error

    @commands.hybrid_command(
        name="cargo",
        description="Envia o painel para escolher Programador, Gamer ou os dois.",
    )
    @commands.guild_only()
    async def cargo(self, ctx: commands.Context) -> None:
        categoria_inicio = discord.utils.get(ctx.guild.categories, name=START_CATEGORY_NAME)
        canal_pedir_cargo = (
            discord.utils.get(categoria_inicio.text_channels, name=PEDIR_CARGO_CHANNEL_NAME)
            if categoria_inicio
            else None
        )
        if ctx.channel != canal_pedir_cargo:
            await ctx.reply(
                f"Use este comando no canal #{PEDIR_CARGO_CHANNEL_NAME}.",
                mention_author=False,
            )
            return

        embed = discord.Embed(
            title="Escolha ou troque seus cargos",
            description="Selecione abaixo a área que você deseja acessar.",
            color=discord.Color.blurple(),
        )
        await ctx.send(embed=embed, view=RolePanel())


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SetupServidor(bot))
