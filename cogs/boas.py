from discord.ext import commands

# 1. Crie a Classe (O Cog)
class MeuCogDeComandos(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 2. Adicione seus comandos aqui
    @commands.command()
    async def meucomando(self, ctx):
        await ctx.send("Este comando está no Cog!")

# 3. A Função ESSENCIAL: Carrega o Cog no Bot
# É esta função que é chamada pelo 'main.py'
async def setup(bot):
    await bot.add_cog(MeuCogDeComandos(bot))
    
    
    
    
