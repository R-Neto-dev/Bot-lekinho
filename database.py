import sqlite3

def criar_tabela():
    conexao = sqlite3.connect("usuarios.db")
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            discord_id INTEGER PRIMARY KEY,
            github_username TEXT NOT NULL
        )
    """)

    conexao.commit()
    conexao.close()

def registrar_usuario(discord_id, github_username):
    conexao = sqlite3.connect("usuarios.db")
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO usuarios (discord_id, github_username)
        VALUES (?, ?)
    """, (discord_id, github_username))

    conexao.commit()
    conexao.close()

def buscar_usuario(discord_id):
    conexao = sqlite3.connect("usuarios.db")
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT github_username FROM usuarios WHERE discord_id = ?
    """, (discord_id,))

    resultado = cursor.fetchone()
    conexao.close()

    return resultado[0] if resultado else None