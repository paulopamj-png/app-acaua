import psycopg2
import datetime

# ==========================================
# CONEXÃO COM A NUVEM (SUPABASE / POSTGRESQL)
# ==========================================
# ⚠️ SUBSTITUA 'SUA_SENHA_AQUI' PELA SUA SENHA REAL DO SUPABASE!
URL_BANCO = "postgresql://postgres.zzqgqaotepitoevfxbns:h8ERjbMi4Uu70jTY@aws-1-sa-east-1.pooler.supabase.com:6543/postgres"


def conectar():
    """Cria a conexão com o banco na nuvem"""
    return psycopg2.connect(URL_BANCO)


def inicializar_banco_nuvem():
    """Cria todas as tabelas no servidor da internet caso não existam"""
    conexao = conectar()
    cursor = conexao.cursor()

    # Ouvidoria
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS chamados (id SERIAL PRIMARY KEY, unidade TEXT, status TEXT, data TEXT, categoria TEXT, texto TEXT, resposta TEXT)"
    )

    # Usuários
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS usuarios (nome TEXT, unidade TEXT, contato TEXT, cpf TEXT UNIQUE)"
    )

    # Assembleias e Pautas
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS assembleias (id SERIAL PRIMARY KEY, titulo TEXT, data_limite TEXT, status TEXT)"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS pautas (id SERIAL PRIMARY KEY, id_assembleia INTEGER, titulo TEXT, descricao TEXT, anexo TEXT)"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS votos (id_pauta INTEGER, unidade TEXT, voto TEXT, UNIQUE(id_pauta, unidade))"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS comentarios_pauta (id SERIAL PRIMARY KEY, id_pauta INTEGER, autor TEXT, texto TEXT)"
    )

    # Necessidades/Obras
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS obras (id SERIAL PRIMARY KEY, titulo TEXT, descricao TEXT, custo TEXT, status TEXT)"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS avaliacoes_obras (id_obra INTEGER, unidade TEXT, nota INTEGER, UNIQUE(id_obra, unidade))"
    )

    # Configurações do Sistema
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS configuracoes (chave TEXT PRIMARY KEY, valor TEXT)"
    )
    cursor.execute(
        "INSERT INTO configuracoes (chave, valor) VALUES ('nome_condominio', 'Condomínio Acauã') ON CONFLICT (chave) DO NOTHING"
    )
    cursor.execute(
        "INSERT INTO configuracoes (chave, valor) VALUES ('cnpj_condominio', '00.000.000/0001-00') ON CONFLICT (chave) DO NOTHING"
    )
    cursor.execute(
        "INSERT INTO configuracoes (chave, valor) VALUES ('voto_secreto', 'Não') ON CONFLICT (chave) DO NOTHING"
    )

    # Síndicos
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS sindicos (id SERIAL PRIMARY KEY, nome TEXT, cpf TEXT UNIQUE, contato TEXT)"
    )
    cursor.execute("SELECT COUNT(*) FROM sindicos")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO sindicos (nome, cpf, contato) VALUES ('Administrador Padrão', '000.000.000-00', '(00) 00000-0000')"
        )

    # Documentos Oficiais (Prestação de Contas etc)
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS documentos_oficiais (id SERIAL PRIMARY KEY, categoria TEXT, periodo TEXT, titulo TEXT, arquivo TEXT)"
    )

    # Reservas e Estatuto
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS reservas (id SERIAL PRIMARY KEY, espaco TEXT, data_reserva TEXT, horario TEXT, unidade TEXT, status TEXT DEFAULT 'Pendente')"
    )
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS estatuto (id SERIAL PRIMARY KEY, titulo TEXT, conteudo TEXT)"
    )
    cursor.execute("SELECT COUNT(*) FROM estatuto")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO estatuto (titulo, conteudo) VALUES ('Horário de Silêncio', 'O horário de silêncio rigoroso é das 22h às 08h.')"
        )

    conexao.commit()
    conexao.close()


# Executa a criação das tabelas ao importar o módulo
inicializar_banco_nuvem()


# ==========================================
# 1. FUNÇÕES DE USUÁRIOS E LOGIN
# ==========================================
def adicionar_usuario(nome, cpf, unidade, contato):
    conexao = conectar()
    try:
        conexao.cursor().execute(
            "INSERT INTO usuarios (nome, cpf, unidade, contato) VALUES (%s, %s, %s, %s)",
            (nome, cpf, unidade, contato),
        )
        conexao.commit()
    except:
        pass  # Ignora erro de CPF duplicado
    finally:
        conexao.close()


def listar_usuarios():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT nome, unidade, contato, cpf FROM usuarios ORDER BY unidade")
    res = cursor.fetchall()
    conexao.close()
    return res


def excluir_usuario(cpf):
    conexao = conectar()
    conexao.cursor().execute("DELETE FROM usuarios WHERE cpf = %s", (cpf,))
    conexao.commit()
    conexao.close()


def atualizar_usuario(cpf_antigo, nome, novo_cpf, unidade, contato):
    conexao = conectar()
    conexao.cursor().execute(
        "UPDATE usuarios SET nome = %s, cpf = %s, unidade = %s, contato = %s WHERE cpf = %s",
        (nome, novo_cpf, unidade, contato, cpf_antigo),
    )
    conexao.commit()
    conexao.close()


def validar_login_morador(cpf, unidade):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT nome FROM usuarios WHERE cpf = %s AND unidade = %s", (cpf, unidade)
    )
    usuario = cursor.fetchone()
    conexao.close()
    return usuario[0] if usuario else None


# ==========================================
# 2. FUNÇÕES DE OUVIDORIA
# ==========================================
def criar_novo_chamado(categoria, texto, unidade):
    data_atual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    conexao = conectar()
    conexao.cursor().execute(
        "INSERT INTO chamados (unidade, status, data, categoria, texto) VALUES (%s, 'Pendente', %s, %s, %s)",
        (unidade, data_atual, categoria, texto),
    )
    conexao.commit()
    conexao.close()


def listar_chamados(unidade_filtro=None):
    conexao = conectar()
    cursor = conexao.cursor()
    if unidade_filtro:
        cursor.execute(
            "SELECT id, unidade, status, data, categoria, texto, resposta FROM chamados WHERE unidade = %s ORDER BY id DESC",
            (unidade_filtro,),
        )
    else:
        cursor.execute(
            "SELECT id, unidade, status, data, categoria, texto, resposta FROM chamados ORDER BY id DESC"
        )
    res = cursor.fetchall()
    conexao.close()
    return res


def atualizar_status_chamado(id_chamado, novo_status):
    conexao = conectar()
    conexao.cursor().execute(
        "UPDATE chamados SET status = %s WHERE id = %s", (novo_status, id_chamado)
    )
    conexao.commit()
    conexao.close()


def salvar_mensagem(
    id_chamado, autor, texto, unidade="Administração", status="Em Andamento"
):
    conexao = conectar()
    conexao.cursor().execute(
        "UPDATE chamados SET resposta = %s, status = %s WHERE id = %s",
        (texto, status, id_chamado),
    )
    conexao.commit()
    conexao.close()


# ==========================================
# 3. FUNÇÕES DE ASSEMBLEIAS
# ==========================================
def criar_assembleia(titulo, data_limite):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "INSERT INTO assembleias (titulo, data_limite, status) VALUES (%s, %s, 'Aberta') RETURNING id",
        (titulo, data_limite),
    )
    id_ass = cursor.fetchone()[0]
    conexao.commit()
    conexao.close()
    return id_ass


def listar_assembleias():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT id, titulo, data_limite, status FROM assembleias ORDER BY id DESC"
    )
    res = cursor.fetchall()
    conexao.close()
    return res


def encerrar_assembleia(id_assembleia):
    conexao = conectar()
    conexao.cursor().execute(
        "UPDATE assembleias SET status = 'Encerrada' WHERE id = %s", (id_assembleia,)
    )
    conexao.commit()
    conexao.close()


def criar_pauta(id_assembleia, titulo, descricao, anexo=None):
    conexao = conectar()
    conexao.cursor().execute(
        "INSERT INTO pautas (id_assembleia, titulo, descricao, anexo) VALUES (%s, %s, %s, %s)",
        (id_assembleia, titulo, descricao, anexo),
    )
    conexao.commit()
    conexao.close()


def listar_pautas_da_assembleia(id_assembleia):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT id, titulo, descricao, anexo FROM pautas WHERE id_assembleia = %s",
        (id_assembleia,),
    )
    res = cursor.fetchall()
    conexao.close()
    return res


def excluir_pauta(id_pauta):
    conexao = conectar()
    conexao.cursor().execute("DELETE FROM pautas WHERE id = %s", (id_pauta,))
    conexao.commit()
    conexao.close()


def registrar_voto(id_pauta, unidade, voto):
    conexao = conectar()
    try:
        conexao.cursor().execute(
            "INSERT INTO votos (id_pauta, unidade, voto) VALUES (%s, %s, %s) ON CONFLICT (id_pauta, unidade) DO UPDATE SET voto = EXCLUDED.voto",
            (id_pauta, unidade, voto),
        )
        conexao.commit()
        return True
    except Exception as e:
        print(e)
        return False
    finally:
        conexao.close()


def verificar_voto(id_pauta, unidade):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT voto FROM votos WHERE id_pauta = %s AND unidade = %s",
        (id_pauta, unidade),
    )
    res = cursor.fetchone()
    conexao.close()
    return res[0] if res else None


def contar_votos(id_pauta):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT voto, COUNT(*) FROM votos WHERE id_pauta = %s GROUP BY voto",
        (id_pauta,),
    )
    votos = dict(cursor.fetchall())
    conexao.close()
    return votos


def listar_votos_detalhados(id_pauta):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT unidade, voto FROM votos WHERE id_pauta = %s ORDER BY unidade",
        (id_pauta,),
    )
    res = cursor.fetchall()
    conexao.close()
    return res


def salvar_comentario(id_pauta, autor, texto):
    conexao = conectar()
    conexao.cursor().execute(
        "INSERT INTO comentarios_pauta (id_pauta, autor, texto) VALUES (%s, %s, %s)",
        (id_pauta, autor, texto),
    )
    conexao.commit()
    conexao.close()


def carregar_comentarios(id_pauta):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT autor, texto FROM comentarios_pauta WHERE id_pauta = %s ORDER BY id ASC",
        (id_pauta,),
    )
    res = [{"autor": c[0], "texto": c[1]} for c in cursor.fetchall()]
    conexao.close()
    return res


# ==========================================
# 4. FUNÇÕES DE NECESSIDADES (OBRAS)
# ==========================================
def adicionar_obra(titulo, descricao, custo):
    conexao = conectar()
    conexao.cursor().execute(
        "INSERT INTO obras (titulo, descricao, custo, status) VALUES (%s, %s, %s, 'Em Avaliação')",
        (titulo, descricao, custo),
    )
    conexao.commit()
    conexao.close()


def listar_obras():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT id, titulo, descricao, custo, status FROM obras")
    res = cursor.fetchall()
    conexao.close()
    return res


def excluir_obra(id_obra):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("DELETE FROM avaliacoes_obras WHERE id_obra = %s", (id_obra,))
    cursor.execute("DELETE FROM obras WHERE id = %s", (id_obra,))
    conexao.commit()
    conexao.close()


def registrar_avaliacao_obra(id_obra, unidade, nota):
    conexao = conectar()
    conexao.cursor().execute(
        "INSERT INTO avaliacoes_obras (id_obra, unidade, nota) VALUES (%s, %s, %s) ON CONFLICT (id_obra, unidade) DO UPDATE SET nota = EXCLUDED.nota",
        (id_obra, unidade, nota),
    )
    conexao.commit()
    conexao.close()


def verificar_minha_nota(id_obra, unidade):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT nota FROM avaliacoes_obras WHERE id_obra = %s AND unidade = %s",
        (id_obra, unidade),
    )
    res = cursor.fetchone()
    conexao.close()
    return res[0] if res else 0


def obter_media_obra(id_obra):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT AVG(nota), COUNT(nota) FROM avaliacoes_obras WHERE id_obra = %s",
        (id_obra,),
    )
    res = cursor.fetchone()
    conexao.close()
    if res and res[0] is not None:
        return round(float(res[0]), 1), res[1]
    return 0.0, 0


# ==========================================
# 5. CONFIGURAÇÕES E SÍNDICOS
# ==========================================
def salvar_config(chave, valor):
    conexao = conectar()
    conexao.cursor().execute(
        "INSERT INTO configuracoes (chave, valor) VALUES (%s, %s) ON CONFLICT (chave) DO UPDATE SET valor = EXCLUDED.valor",
        (chave, valor),
    )
    conexao.commit()
    conexao.close()


def obter_config(chave):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT valor FROM configuracoes WHERE chave = %s", (chave,))
    res = cursor.fetchone()
    conexao.close()
    return res[0] if res else ""


def resetar_votos_atas():
    conexao = conectar()
    cursor = conexao.cursor()
    tabelas = [
        "assembleias",
        "pautas",
        "votos",
        "comentarios_pauta",
        "obras",
        "avaliacoes_obras",
    ]
    for t in tabelas:
        cursor.execute(f"TRUNCATE TABLE {t} RESTART IDENTITY CASCADE")
    conexao.commit()
    conexao.close()


def listar_sindicos():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT id, nome, cpf, contato FROM sindicos")
    res = cursor.fetchall()
    conexao.close()
    return res


def adicionar_sindico(nome, cpf, contato):
    conexao = conectar()
    try:
        conexao.cursor().execute(
            "INSERT INTO sindicos (nome, cpf, contato) VALUES (%s, %s, %s)",
            (nome, cpf, contato),
        )
        conexao.commit()
    except:
        pass
    finally:
        conexao.close()


def excluir_sindico(id_sindico):
    conexao = conectar()
    conexao.cursor().execute("DELETE FROM sindicos WHERE id = %s", (id_sindico,))
    conexao.commit()
    conexao.close()


# ==========================================
# 6. DOCUMENTOS, RESERVAS E ESTATUTO
# ==========================================
def adicionar_documento(categoria, periodo, titulo, arquivo):
    conexao = conectar()
    conexao.cursor().execute(
        "INSERT INTO documentos_oficiais (categoria, periodo, titulo, arquivo) VALUES (%s, %s, %s, %s)",
        (categoria, periodo, titulo, arquivo),
    )
    conexao.commit()
    conexao.close()


def listar_documentos():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT id, categoria, periodo, titulo, arquivo FROM documentos_oficiais ORDER BY id DESC"
    )
    res = cursor.fetchall()
    conexao.close()
    return res


def excluir_documento(id_doc):
    conexao = conectar()
    conexao.cursor().execute("DELETE FROM documentos_oficiais WHERE id = %s", (id_doc,))
    conexao.commit()
    conexao.close()


def listar_reservas(unidade_filtro=None):
    conexao = conectar()
    cursor = conexao.cursor()
    if unidade_filtro:
        cursor.execute(
            "SELECT id, espaco, data_reserva, horario, unidade, status FROM reservas WHERE unidade = %s ORDER BY id DESC",
            (unidade_filtro,),
        )
    else:
        cursor.execute(
            "SELECT id, espaco, data_reserva, horario, unidade, status FROM reservas ORDER BY id DESC"
        )
    res = cursor.fetchall()
    conexao.close()
    return res


def adicionar_reserva(espaco, data_reserva, horario, unidade):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT id FROM reservas WHERE espaco = %s AND data_reserva = %s AND horario = %s AND status != 'Rejeitada'",
        (espaco, data_reserva, horario),
    )
    if cursor.fetchone():
        conexao.close()
        return False
    cursor.execute(
        "INSERT INTO reservas (espaco, data_reserva, horario, unidade, status) VALUES (%s, %s, %s, %s, 'Pendente')",
        (espaco, data_reserva, horario, unidade),
    )
    conexao.commit()
    conexao.close()
    return True


def atualizar_status_reserva(id_reserva, novo_status):
    conexao = conectar()
    conexao.cursor().execute(
        "UPDATE reservas SET status = %s WHERE id = %s", (novo_status, id_reserva)
    )
    conexao.commit()
    conexao.close()


def verificar_disponibilidade_turnos(espaco, data_reserva):
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT horario FROM reservas WHERE espaco = %s AND data_reserva = %s AND status != 'Rejeitada'",
        (espaco, data_reserva),
    )
    res = cursor.fetchall()
    conexao.close()
    return [r[0] for r in res]


def cancelar_reserva_morador(id_reserva, unidade):
    conexao = conectar()
    conexao.cursor().execute(
        "DELETE FROM reservas WHERE id = %s AND unidade = %s", (id_reserva, unidade)
    )
    conexao.commit()
    conexao.close()


def listar_agenda_publica():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute(
        "SELECT espaco, data_reserva, horario, unidade FROM reservas WHERE status = 'Aprovada'"
    )
    res = cursor.fetchall()
    conexao.close()
    return res


def listar_estatuto():
    conexao = conectar()
    cursor = conexao.cursor()
    cursor.execute("SELECT id, titulo, conteudo FROM estatuto ORDER BY id ASC")
    res = cursor.fetchall()
    conexao.close()
    return res


def adicionar_regra_estatuto(titulo, conteudo):
    conexao = conectar()
    conexao.cursor().execute(
        "INSERT INTO estatuto (titulo, conteudo) VALUES (%s, %s)", (titulo, conteudo)
    )
    conexao.commit()
    conexao.close()


def atualizar_regra_estatuto(id_regra, titulo, conteudo):
    conexao = conectar()
    conexao.cursor().execute(
        "UPDATE estatuto SET titulo = %s, conteudo = %s WHERE id = %s",
        (titulo, conteudo, id_regra),
    )
    conexao.commit()
    conexao.close()


def excluir_regra_estatuto(id_regra):
    conexao = conectar()
    conexao.cursor().execute("DELETE FROM estatuto WHERE id = %s", (id_regra,))
    conexao.commit()
    conexao.close()


