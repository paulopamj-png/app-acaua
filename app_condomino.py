import flet as ft
import banco_dados
import os
import platform
import subprocess
import datetime

DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(DIRETORIO_ATUAL, "assets")
DIR_CONTAS = os.path.join(ASSETS_DIR, "Prestacao_Contas")
DIR_RELATORIOS = os.path.join(DIRETORIO_ATUAL, "Relatorios_Gerados")


def main(page: ft.Page):
    page.title = "App do Condómino - Acauã"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.window.width = 400
    page.window.height = 750
    page.bgcolor = "#F4F7FC"
    page.padding = 0

    unidade_logada = ""
    nome_logado = ""

    # ==========================================
    # ROTAS E NAVEGAÇÃO MOBILE
    # ==========================================
    def esconder_tudo():
        tela_login.visible = False
        tela_dashboard.visible = False
        tela_ouvidoria.visible = False
        tela_lista_assembleias.visible = False
        tela_pautas_assembleia.visible = False
        tela_obras.visible = False
        tela_documentos.visible = False
        tela_reservas.visible = False
        tela_estatuto.visible = False

    def ir_para_login(e=None):
        page.appbar.visible = False
        esconder_tudo()
        tela_login.visible = True
        page.update()

    def ir_para_dashboard(e=None):
        saudacao_nome.value = f"Olá, {nome_logado.split()[0]}"
        saudacao_unidade.value = f"Unidade: {unidade_logada}"
        letra_avatar.value = nome_logado[0].upper()
        page.appbar.visible = False
        esconder_tudo()
        tela_dashboard.visible = True
        page.update()

    def criar_appbar_interna(titulo):
        page.appbar.title = ft.Text(titulo, weight="bold", color="white")
        page.appbar.leading = ft.IconButton(
            ft.Icons.ARROW_BACK, icon_color="white", on_click=ir_para_dashboard
        )
        page.appbar.visible = True

    def ir_para_ouvidoria(e=None):
        criar_appbar_interna("Ouvidoria")
        esconder_tudo()
        tela_ouvidoria.visible = True
        carregar_historico_premium()
        page.update()

    def ir_para_assembleias(e=None):
        criar_appbar_interna("Assembleias")
        esconder_tudo()
        tela_lista_assembleias.visible = True
        carregar_lista_assembleias()
        page.update()

    def ir_para_obras(e=None):
        criar_appbar_interna("Necessidades")
        esconder_tudo()
        tela_obras.visible = True
        carregar_obras_morador()
        page.update()

    def ir_para_documentos(e=None):
        criar_appbar_interna("Meus Documentos")
        esconder_tudo()
        tela_documentos.visible = True
        carregar_documentos_morador()
        page.update()

    def ir_para_reservas(e=None):
        criar_appbar_interna("Reservas")
        esconder_tudo()
        tela_reservas.visible = True
        carregar_reservas_morador()
        page.update()

    def ir_para_estatuto(e=None):
        criar_appbar_interna("Manual de Regras")
        esconder_tudo()
        tela_estatuto.visible = True
        carregar_estatuto_morador()
        page.update()

    page.appbar = ft.AppBar(bgcolor=ft.Colors.TEAL_700, elevation=0, visible=False)

    # ==========================================
    # 1. LOGIN E DASHBOARD FINTECH
    # ==========================================
    def formatar_cpf(e):
        v = "".join(filter(str.isdigit, e.control.value))[:11]
        r = ""
        [
            r := r + ("." if i in [3, 6] else "-" if i == 9 else "") + c
            for i, c in enumerate(v)
        ]
        e.control.value = r
        e.control.update()

    campo_cpf = ft.TextField(
        label="CPF do Morador",
        hint_text="000.000.000-00",
        width=300,
        border_color=ft.Colors.TEAL_600,
        on_change=formatar_cpf,
        max_length=14,
        counter_text=" ",
    )
    campo_unidade = ft.Dropdown(
        label="Sua Unidade",
        options=[
            ft.dropdown.Option("Apt 101"),
            ft.dropdown.Option("Apt 102"),
            ft.dropdown.Option("Apt 201"),
            ft.dropdown.Option("Apt 202"),
        ],
        width=300,
        border_color=ft.Colors.TEAL_600,
    )

    def tentar_login(e):
        nonlocal unidade_logada, nome_logado
        if not campo_cpf.value or not campo_unidade.value:
            page.snack_bar = ft.SnackBar(ft.Text("Preencha todos os dados!"))
            page.snack_bar.open = True
            page.update()
            return
        nome = banco_dados.validar_login_morador(
            "".join(filter(str.isdigit, campo_cpf.value)), campo_unidade.value
        )
        if nome:
            nome_logado = nome
            unidade_logada = campo_unidade.value
            ir_para_dashboard()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Credenciais inválidas.", color="red"))
            page.snack_bar.open = True
        page.update()

    tela_login = ft.Container(
        content=ft.Column(
            [
                ft.Icon(ft.Icons.SECURITY, size=80, color=ft.Colors.TEAL_700),
                ft.Text(
                    "Portal do Morador",
                    size=26,
                    weight="bold",
                    color=ft.Colors.TEAL_900,
                ),
                ft.Container(height=20),
                campo_cpf,
                campo_unidade,
                ft.ElevatedButton(
                    "Entrar no Sistema",
                    icon=ft.Icons.LOGIN,
                    on_click=tentar_login,
                    bgcolor=ft.Colors.TEAL_700,
                    color="white",
                    width=300,
                    height=50,
                ),
            ],
            alignment="center",
            horizontal_alignment="center",
        ),
        alignment=ft.alignment.center,
        expand=True,
    )

    saudacao_nome = ft.Text("", size=22, weight="bold", color="white")
    saudacao_unidade = ft.Text("", size=14, color=ft.Colors.TEAL_100)
    letra_avatar = ft.Text("", size=24, weight="bold", color=ft.Colors.TEAL_900)
    header_dashboard = ft.Container(
        padding=ft.padding.only(top=50, left=30, right=30, bottom=30),
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[ft.Colors.TEAL_700, ft.Colors.TEAL_900],
        ),
        border_radius=ft.border_radius.only(bottom_left=30, bottom_right=30),
        content=ft.Row(
            [
                ft.CircleAvatar(content=letra_avatar, bgcolor="white", radius=30),
                ft.Container(width=10),
                ft.Column([saudacao_nome, saudacao_unidade], spacing=2, expand=True),
                ft.IconButton(
                    ft.Icons.LOGOUT, icon_color="white", on_click=ir_para_login
                ),
            ],
            vertical_alignment="center",
        ),
    )

    def criar_cartao_premium(titulo, icone, cor_icone, rota):
        return ft.Container(
            on_click=rota,
            bgcolor="white",
            border_radius=20,
            padding=20,
            shadow=ft.BoxShadow(
                blur_radius=10, color=ft.Colors.BLACK12, offset=ft.Offset(0, 4)
            ),
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Icon(icone, size=35, color=cor_icone),
                        padding=12,
                        bgcolor=ft.Colors.with_opacity(0.1, cor_icone),
                        border_radius=50,
                    ),
                    ft.Container(height=5),
                    ft.Text(
                        titulo,
                        weight="bold",
                        size=12,
                        color=ft.Colors.BLUE_GREY_900,
                        text_align="center",
                    ),
                ],
                horizontal_alignment="center",
                alignment="center",
            ),
            col={"xs": 4},
        )  # Reduzi xs para 4 para caberem 3 por linha

    grid_dashboard = ft.ResponsiveRow(
        controls=[
            criar_cartao_premium(
                "Assembleias",
                ft.Icons.HOW_TO_VOTE,
                ft.Colors.TEAL_600,
                ir_para_assembleias,
            ),
            criar_cartao_premium(
                "Ouvidoria", ft.Icons.FORUM, ft.Colors.PURPLE_600, ir_para_ouvidoria
            ),
            criar_cartao_premium(
                "Documentos",
                ft.Icons.FOLDER_SPECIAL,
                ft.Colors.RED_600,
                ir_para_documentos,
            ),
            criar_cartao_premium(
                "Priorizar", ft.Icons.LOW_PRIORITY, ft.Colors.ORANGE_600, ir_para_obras
            ),
            criar_cartao_premium(
                "Reservas",
                ft.Icons.EVENT_AVAILABLE,
                ft.Colors.CYAN_600,
                ir_para_reservas,
            ),  # NOVO
            criar_cartao_premium(
                "Regras", ft.Icons.MENU_BOOK, ft.Colors.INDIGO_600, ir_para_estatuto
            ),  # NOVO
        ],
        spacing=15,
        run_spacing=15,
    )

    tela_dashboard = ft.Container(
        content=ft.Column(
            [
                header_dashboard,
                ft.Container(
                    content=ft.Column(
                        [
                            ft.Text(
                                "Acesso Rápido",
                                size=18,
                                weight="bold",
                                color=ft.Colors.BLUE_GREY_800,
                            ),
                            grid_dashboard,
                        ]
                    ),
                    padding=25,
                ),
            ]
        ),
        expand=True,
        visible=False,
    )

    # ==========================================
    # 6. MÓDULO: RESERVAS PREMIUM E AGENDA 📅
    # ==========================================
    # --- Estilo Premium para os Campos ---
    # ==========================================
    # 6. MÓDULO: RESERVAS PREMIUM E AGENDA 📅
    # ==========================================
    # --- Estilo Premium para os Campos ---
    estilo_campo = {
        "border_radius": 12,
        "border_color": ft.Colors.CYAN_400,
        "focused_border_color": ft.Colors.CYAN_700,
        "bgcolor": ft.Colors.CYAN_50,
        "content_padding": 15,
        "text_size": 14,
        "label_style": ft.TextStyle(color=ft.Colors.CYAN_900, weight="bold"),
    }

    # CORREÇÃO FLET ATUALIZADO: Usando prefix=ft.Icon() e já colocando a cor Azul-Ciano neles!
    campo_espaco = ft.Dropdown(
        label="1. Escolha o Espaço",
        prefix=ft.Icon(ft.Icons.HOME_WORK, color=ft.Colors.CYAN_700),
        options=[
            ft.dropdown.Option("Salão de Festas"),
            ft.dropdown.Option("Churrasqueira"),
            ft.dropdown.Option("Quadra Poliesportiva"),
        ],
        **estilo_campo,
    )

    campo_data_reserva = ft.TextField(
        label="2. Defina a Data",
        hint_text="Clique no calendário 👉",
        prefix=ft.Icon(ft.Icons.DATE_RANGE, color=ft.Colors.CYAN_700),
        read_only=True,
        expand=True,
        **estilo_campo,
    )

    campo_horario = ft.Dropdown(
        label="3. Selecione o Turno",
        prefix=ft.Icon(ft.Icons.ACCESS_TIME, color=ft.Colors.CYAN_700),
        options=[],
        **estilo_campo,
    )

    def verificar_turnos_disponiveis(e=None):
        if not campo_espaco.value or not campo_data_reserva.value:
            return
        turnos_ocupados = banco_dados.verificar_disponibilidade_turnos(
            campo_espaco.value, campo_data_reserva.value
        )
        opcoes_padrao = ["Manhã (08h - 12h)", "Tarde (13h - 17h)", "Noite (18h - 22h)"]
        novas_opcoes = []
        for turno in opcoes_padrao:
            if turno in turnos_ocupados:
                novas_opcoes.append(
                    ft.dropdown.Option(
                        key=turno, text=f"🔴 Ocupado: {turno}", disabled=True
                    )
                )
            else:
                novas_opcoes.append(
                    ft.dropdown.Option(key=turno, text=f"✅ Livre: {turno}")
                )
        campo_horario.options = novas_opcoes
        campo_horario.value = None
        page.update()

    campo_espaco.on_change = verificar_turnos_disponiveis

    cal_reserva = ft.DatePicker(first_date=datetime.datetime.now())

    def atualizar_data_reserva(e):
        if cal_reserva.value:
            campo_data_reserva.value = cal_reserva.value.strftime("%d/%m/%Y")
            verificar_turnos_disponiveis()
        page.update()

    cal_reserva.on_change = atualizar_data_reserva
    page.overlay.append(cal_reserva)

    lista_minhas_reservas = ft.Column(
        spacing=10, scroll=ft.ScrollMode.AUTO, expand=True
    )
    lista_agenda_publica = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

    def solicitar_reserva(e):
        if (
            not campo_espaco.value
            or not campo_data_reserva.value
            or not campo_horario.value
        ):
            page.snack_bar = ft.SnackBar(
                ft.Text("Preencha todos os passos!"), bgcolor="red"
            )
            page.snack_bar.open = True
            page.update()
            return

        sucesso = banco_dados.adicionar_reserva(
            campo_espaco.value,
            campo_data_reserva.value,
            campo_horario.value,
            unidade_logada,
        )
        if sucesso:
            page.snack_bar = ft.SnackBar(
                ft.Text("Solicitação enviada ao Síndico!"), bgcolor="green"
            )
            campo_espaco.value = None
            campo_data_reserva.value = ""
            campo_horario.value = None
            carregar_reservas_morador()
        else:
            page.snack_bar = ft.SnackBar(
                ft.Text("Opa! Alguém foi mais rápido e já reservou!"), bgcolor="red"
            )
        page.snack_bar.open = True
        page.update()

    def cancelar_reserva_ui(id_res):
        banco_dados.cancelar_reserva_morador(id_res, unidade_logada)
        page.snack_bar = ft.SnackBar(
            ft.Text("Reserva cancelada e data libertada!"), bgcolor=ft.Colors.ORANGE_700
        )
        page.snack_bar.open = True
        carregar_reservas_morador()

    def carregar_reservas_morador():
        # 1. Carrega as reservas do próprio morador
        lista_minhas_reservas.controls.clear()
        reservas = banco_dados.listar_reservas(unidade_filtro=unidade_logada)
        if not reservas:
            lista_minhas_reservas.controls.append(
                ft.Container(
                    padding=20,
                    content=ft.Text(
                        "Você não tem agendamentos.", italic=True, color="grey"
                    ),
                )
            )
        for res in reservas:
            id_r, espaco, data_r, hor, uni, stat = res
            cor_st = (
                ft.Colors.AMBER_600
                if stat == "Pendente"
                else (ft.Colors.GREEN_600 if stat == "Aprovada" else ft.Colors.RED_600)
            )
            icone_st = (
                ft.Icons.SCHEDULE
                if stat == "Pendente"
                else (ft.Icons.CHECK_CIRCLE if stat == "Aprovada" else ft.Icons.CANCEL)
            )

            # Botão de cancelar (Aparece se estiver pendente ou aprovada)
            btn_cancelar = (
                ft.IconButton(
                    ft.Icons.DELETE_OUTLINE,
                    icon_color="red",
                    tooltip="Cancelar Reserva",
                    on_click=lambda e, i=id_r: cancelar_reserva_ui(i),
                )
                if stat != "Rejeitada"
                else ft.Container()
            )

            card = ft.Container(
                bgcolor="white",
                padding=15,
                border_radius=12,
                border=ft.border.only(left=ft.border.BorderSide(6, cor_st)),
                shadow=ft.BoxShadow(
                    blur_radius=5, color=ft.Colors.BLACK12, offset=ft.Offset(0, 2)
                ),
                content=ft.Row(
                    [
                        ft.Column(
                            [
                                ft.Text(
                                    espaco,
                                    weight="bold",
                                    size=15,
                                    color=ft.Colors.BLUE_GREY_900,
                                ),
                                ft.Text(
                                    f"{data_r} | {hor}",
                                    size=12,
                                    color=ft.Colors.BLUE_GREY_600,
                                ),
                                ft.Row(
                                    [
                                        ft.Icon(icone_st, color=cor_st, size=14),
                                        ft.Text(
                                            stat.upper(),
                                            color=cor_st,
                                            weight="bold",
                                            size=11,
                                        ),
                                    ]
                                ),
                            ],
                            expand=True,
                        ),
                        btn_cancelar,
                    ]
                ),
            )
            lista_minhas_reservas.controls.append(card)

        # 2. Carrega a Agenda Pública (Eventos Aprovados de todos)
        lista_agenda_publica.controls.clear()
        agenda_todos = banco_dados.listar_agenda_publica()

        # Tentativa de ordenar por data via Python para exibir bonito no app
        try:
            agenda_todos.sort(
                key=lambda x: datetime.datetime.strptime(x[1], "%d/%m/%Y")
            )
        except:
            pass

        if not agenda_todos:
            lista_agenda_publica.controls.append(
                ft.Container(
                    padding=40,
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        [
                            ft.Icon(
                                ft.Icons.EVENT_BUSY, size=50, color=ft.Colors.GREY_300
                            ),
                            ft.Text(
                                "Nenhum evento agendado no condomínio.",
                                italic=True,
                                color=ft.Colors.GREY_500,
                            ),
                        ],
                        horizontal_alignment="center",
                    ),
                )
            )

        for ag in agenda_todos:
            espaco_ag, data_ag, hor_ag, uni_ag = ag
            card_ag = ft.Card(
                elevation=2,
                content=ft.Container(
                    padding=15,
                    border_radius=8,
                    border=ft.border.all(1, ft.Colors.CYAN_100),
                    bgcolor=ft.Colors.CYAN_50,
                    content=ft.Row(
                        [
                            ft.Icon(
                                ft.Icons.CELEBRATION, color=ft.Colors.CYAN_700, size=30
                            ),
                            ft.Container(width=10),
                            ft.Column(
                                [
                                    ft.Text(
                                        f"{espaco_ag}",
                                        weight="bold",
                                        size=15,
                                        color=ft.Colors.CYAN_900,
                                    ),
                                    ft.Text(
                                        f"{data_ag} • {hor_ag}",
                                        size=13,
                                        color=ft.Colors.BLUE_GREY_700,
                                    ),
                                    ft.Text(
                                        f"Reservado por: {uni_ag}",
                                        size=11,
                                        color=ft.Colors.GREY_600,
                                        italic=True,
                                    ),
                                ]
                            ),
                        ]
                    ),
                ),
            )
            lista_agenda_publica.controls.append(card_ag)

        page.update()

    cartao_nova_reserva = ft.Container(
        bgcolor="white",
        padding=25,
        border_radius=15,
        shadow=ft.BoxShadow(
            blur_radius=15, color=ft.Colors.BLACK12, offset=ft.Offset(0, 5)
        ),
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(
                                ft.Icons.EVENT_AVAILABLE,
                                color=ft.Colors.CYAN_700,
                                size=24,
                            ),
                            padding=10,
                            bgcolor=ft.Colors.CYAN_50,
                            border_radius=50,
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    "Agendar Espaço",
                                    size=18,
                                    weight="bold",
                                    color=ft.Colors.BLUE_GREY_900,
                                ),
                                ft.Text(
                                    "Confira a agenda e faça sua reserva.",
                                    color=ft.Colors.BLUE_GREY_500,
                                    size=12,
                                ),
                            ]
                        ),
                    ]
                ),
                ft.Divider(height=25, color=ft.Colors.GREY_200),
                campo_espaco,
                ft.Row(
                    [
                        campo_data_reserva,
                        ft.IconButton(
                            icon=ft.Icons.CALENDAR_MONTH,
                            icon_size=35,
                            icon_color=ft.Colors.CYAN_700,
                            on_click=lambda e: page.open(cal_reserva),
                        ),
                    ]
                ),
                campo_horario,
                ft.Container(height=5),
                ft.ElevatedButton(
                    "Enviar Solicitação",
                    icon=ft.Icons.SEND,
                    bgcolor=ft.Colors.CYAN_700,
                    color="white",
                    on_click=solicitar_reserva,
                    height=45,
                    width=400,
                ),
            ]
        ),
    )

    aba_minhas = ft.Container(
        padding=ft.padding.only(top=15),
        content=ft.Column(
            [
                cartao_nova_reserva,
                ft.Text("Meus Pedidos", weight="bold", size=16),
                lista_minhas_reservas,
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
    )
    aba_agenda = ft.Container(
        padding=ft.padding.only(top=15),
        content=ft.Column(
            [
                ft.Text(
                    "Agenda Oficial do Condomínio",
                    weight="bold",
                    size=18,
                    color=ft.Colors.CYAN_900,
                ),
                ft.Text(
                    "Fique por dentro de quais áreas comuns estarão ocupadas nos próximos dias.",
                    color="grey",
                    size=13,
                ),
                ft.Divider(),
                lista_agenda_publica,
            ],
            scroll=ft.ScrollMode.AUTO,
        ),
    )

    tela_reservas = ft.Container(
        content=ft.Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                ft.Tab(
                    text="Fazer Reserva", icon=ft.Icons.ADD_ALARM, content=aba_minhas
                ),
                ft.Tab(
                    text="Agenda Pública",
                    icon=ft.Icons.CALENDAR_TODAY,
                    content=aba_agenda,
                ),
            ],
            expand=True,
        ),
        padding=10,
        expand=True,
        visible=False,
    )

    # ==========================================
    # NOVO MÓDULO: ESTATUTO / MANUAL 📖
    # ==========================================
    lista_regras_ui = ft.ListView(expand=True, spacing=10)

    def carregar_estatuto_morador():
        lista_regras_ui.controls.clear()
        regras = banco_dados.listar_estatuto()
        if not regras:
            lista_regras_ui.controls.append(
                ft.Text("Nenhuma regra cadastrada pelo síndico.", italic=True)
            )
        for r in regras:
            lista_regras_ui.controls.append(
                ft.ExpansionTile(
                    title=ft.Text(r[1], weight="bold", color=ft.Colors.INDIGO_900),
                    leading=ft.Icon(ft.Icons.GAVEL, color=ft.Colors.INDIGO_600),
                    controls=[
                        ft.Container(
                            padding=15,
                            bgcolor=ft.Colors.INDIGO_50,
                            content=ft.Text(r[2], size=14),
                        )
                    ],
                )
            )
        page.update()

    tela_estatuto = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Manual do Condomínio",
                    size=22,
                    weight="bold",
                    color=ft.Colors.INDIGO_900,
                ),
                ft.Text(
                    "Conheça as regras e normas do nosso condomínio atualizadas pela gestão.",
                    color="grey",
                ),
                ft.Divider(),
                lista_regras_ui,
            ]
        ),
        padding=15,
        expand=True,
        visible=False,
    )

    # ==========================================
    # (TODOS OS MÓDULOS ANTERIORES MANTIDOS INTATOS)
    # ==========================================

    # --- DOCUMENTOS ---
    coluna_pastas = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
    tela_documentos = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Central de Transparência",
                    size=22,
                    weight="bold",
                    color=ft.Colors.RED_900,
                ),
                ft.Text(
                    "Selecione a categoria para visualizar os PDFs oficiais.",
                    color="grey",
                ),
                ft.Divider(),
                coluna_pastas,
            ]
        ),
        padding=20,
        expand=True,
        visible=False,
    )

    def abrir_pdf_local(caminho):
        try:
            os.startfile(
                caminho
            ) if platform.system() == "Windows" else subprocess.call(
                ("open" if platform.system() == "Darwin" else "xdg-open", caminho)
            )
        except Exception as err:
            page.snack_bar = ft.SnackBar(ft.Text(f"Erro ao abrir arquivo."))
            page.snack_bar.open = True
            page.update()

    def carregar_documentos_morador():
        coluna_pastas.controls.clear()
        docs = banco_dados.listar_documentos()
        docs_mensais = ft.Column(spacing=5)
        docs_anuais = ft.Column(spacing=5)
        for d in docs:
            id_d, cat, per, tit, arq = d
            caminho = os.path.join(DIR_CONTAS, arq)
            lista_item = ft.ListTile(
                leading=ft.Icon(ft.Icons.PICTURE_AS_PDF, color="green"),
                title=ft.Text(f"{per} - {tit}", weight="bold"),
                subtitle=ft.Text("Toque para abrir"),
                on_click=lambda e, c=caminho: abrir_pdf_local(c),
            )
            if cat == "Prestação de Contas Mensal":
                docs_mensais.controls.append(lista_item)
            elif cat == "Prestação de Contas Anual":
                docs_anuais.controls.append(lista_item)
        arquivos_auto = [f for f in os.listdir(DIR_RELATORIOS) if f.endswith(".pdf")]
        assembleias_db = {str(a[0]): a[1] for a in banco_dados.listar_assembleias()}
        docs_atas = ft.Column(spacing=5)
        docs_obras = ft.Column(spacing=5)
        for arq in arquivos_auto:
            cam = os.path.join(DIR_RELATORIOS, arq)
            if arq.startswith("Ata_Assembleia_"):
                docs_atas.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.GAVEL, color="red"),
                        title=ft.Text(
                            assembleias_db.get(
                                arq.replace("Ata_Assembleia_", "").replace(".pdf", ""),
                                "Ata",
                            ),
                            weight="bold",
                        ),
                        on_click=lambda e, c=cam: abrir_pdf_local(c),
                    )
                )
            elif arq.startswith("Ranking_Prioridades_"):
                docs_obras.controls.append(
                    ft.ListTile(
                        leading=ft.Icon(ft.Icons.INSERT_CHART, color="orange"),
                        title=ft.Text("Relatório de Ranking", weight="bold"),
                        on_click=lambda e, c=cam: abrir_pdf_local(c),
                    )
                )
        coluna_pastas.controls.extend(
            [
                ft.ExpansionTile(
                    title=ft.Text("Prestação de Contas Mensais", weight="bold"),
                    leading=ft.Icon(ft.Icons.FOLDER_OPEN, color="green"),
                    controls=[
                        ft.Container(
                            padding=ft.padding.only(left=20),
                            content=docs_mensais
                            if docs_mensais.controls
                            else ft.Text("Vazia", italic=True),
                        )
                    ],
                ),
                ft.ExpansionTile(
                    title=ft.Text("Prestação de Contas Anuais", weight="bold"),
                    leading=ft.Icon(ft.Icons.FOLDER_SPECIAL, color="blue"),
                    controls=[
                        ft.Container(
                            padding=ft.padding.only(left=20),
                            content=docs_anuais
                            if docs_anuais.controls
                            else ft.Text("Vazia", italic=True),
                        )
                    ],
                ),
                ft.ExpansionTile(
                    title=ft.Text("Atas de Assembleia (Resultados)", weight="bold"),
                    leading=ft.Icon(ft.Icons.LIBRARY_BOOKS, color="red"),
                    controls=[
                        ft.Container(
                            padding=ft.padding.only(left=20),
                            content=docs_atas
                            if docs_atas.controls
                            else ft.Text("Vazia", italic=True),
                        )
                    ],
                ),
                ft.ExpansionTile(
                    title=ft.Text("Relatórios de Prioridades", weight="bold"),
                    leading=ft.Icon(ft.Icons.CONSTRUCTION, color="orange"),
                    controls=[
                        ft.Container(
                            padding=ft.padding.only(left=20),
                            content=docs_obras
                            if docs_obras.controls
                            else ft.Text("Vazia", italic=True),
                        )
                    ],
                ),
            ]
        )
        page.update()

    # --- OUVIDORIA ---
    cat_input = ft.Dropdown(
        label="Assunto",
        border_radius=8,
        options=[
            ft.dropdown.Option("Reclamação"),
            ft.dropdown.Option("Manutenção"),
            ft.dropdown.Option("Sugestão"),
            ft.dropdown.Option("Elogio"),
        ],
        expand=True,
    )
    texto_input = ft.TextField(
        label="Descreva a situação detalhadamente...",
        multiline=True,
        min_lines=3,
        border_radius=8,
    )

    def abrir_novo_chamado_premium(e):
        if not cat_input.value or not texto_input.value:
            page.snack_bar = ft.SnackBar(ft.Text("Preencha tudo!"), bgcolor="red")
            page.snack_bar.open = True
            page.update()
            return
        banco_dados.criar_novo_chamado(
            cat_input.value, texto_input.value, unidade_logada
        )
        cat_input.value = None
        texto_input.value = ""
        page.snack_bar = ft.SnackBar(ft.Text("Chamado enviado!"), bgcolor="green")
        page.snack_bar.open = True
        carregar_historico_premium()

    lista_chamados_ui = ft.Column(spacing=20, scroll=ft.ScrollMode.AUTO)

    def carregar_historico_premium():
        lista_chamados_ui.controls.clear()
        chamados = banco_dados.listar_chamados(unidade_filtro=unidade_logada)
        if not chamados:
            lista_chamados_ui.controls.append(
                ft.Container(
                    padding=40,
                    alignment=ft.alignment.center,
                    content=ft.Column(
                        [
                            ft.Icon(ft.Icons.INBOX, size=50, color=ft.Colors.GREY_300),
                            ft.Text(
                                "Nenhum chamado no momento.",
                                italic=True,
                                color=ft.Colors.GREY_500,
                            ),
                        ],
                        horizontal_alignment="center",
                    ),
                )
            )
        for ch in chamados:
            id_ch, uni, stat, data, cat, txt, resp = ch
            c_cat = ft.Colors.GREY_600
            is_pendente = stat == "Pendente"
            c_stat = (
                ft.Colors.RED_600
                if is_pendente
                else (
                    ft.Colors.GREEN_600 if stat == "Resolvido" else ft.Colors.BLUE_600
                )
            )
            badge_status = ft.Container(
                padding=ft.padding.only(left=10, right=10, top=4, bottom=4),
                border_radius=15,
                bgcolor=ft.Colors.RED_50 if is_pendente else ft.Colors.GREEN_50,
                border=ft.border.all(1, c_stat),
                content=ft.Row(
                    [
                        ft.Icon(ft.Icons.CIRCLE, size=8, color=c_stat),
                        ft.Text(stat.upper(), size=11, weight="bold", color=c_stat),
                    ]
                ),
            )
            caixa_resposta = (
                ft.Container(
                    margin=ft.margin.only(top=15),
                    padding=15,
                    border_radius=10,
                    border=ft.border.all(1, ft.Colors.PURPLE_100),
                    bgcolor=ft.Colors.PURPLE_50,
                    content=ft.Row(
                        [
                            ft.CircleAvatar(
                                content=ft.Icon(
                                    ft.Icons.SUPPORT_AGENT, color="white", size=16
                                ),
                                bgcolor=ft.Colors.PURPLE_400,
                                radius=16,
                            ),
                            ft.Column(
                                [
                                    ft.Text(
                                        "RESPOSTA DO SÍNDICO",
                                        weight="bold",
                                        color=ft.Colors.PURPLE_900,
                                        size=10,
                                    ),
                                    ft.Text(
                                        resp, size=13, color=ft.Colors.BLUE_GREY_900
                                    ),
                                ],
                                expand=True,
                            ),
                        ],
                        vertical_alignment="start",
                    ),
                )
                if resp
                else ft.Container()
            )
            cartao = ft.Container(
                bgcolor="white",
                padding=20,
                border_radius=12,
                border=ft.border.only(left=ft.border.BorderSide(6, c_cat)),
                shadow=ft.BoxShadow(
                    blur_radius=10, color=ft.Colors.BLACK12, offset=ft.Offset(0, 4)
                ),
                content=ft.Column(
                    [
                        ft.Row(
                            [
                                ft.Text(
                                    f"#{id_ch} • {data[:10]}",
                                    color=ft.Colors.GREY_400,
                                    size=11,
                                    weight="bold",
                                )
                            ]
                        ),
                        ft.Container(height=5),
                        ft.Row(
                            [
                                ft.Text(
                                    uni,
                                    weight="bold",
                                    color=ft.Colors.BLUE_GREY_900,
                                    size=16,
                                ),
                                ft.Container(expand=True),
                                badge_status,
                            ]
                        ),
                        ft.Container(
                            padding=ft.padding.only(left=5),
                            content=ft.Text(
                                txt, size=14, color=ft.Colors.BLUE_GREY_800
                            ),
                        ),
                        caixa_resposta,
                    ]
                ),
            )
            lista_chamados_ui.controls.append(cartao)
        page.update()

    cartao_abrir_chamado = ft.Container(
        bgcolor="white",
        padding=25,
        border_radius=15,
        shadow=ft.BoxShadow(
            blur_radius=15, color=ft.Colors.BLACK12, offset=ft.Offset(0, 5)
        ),
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.Container(
                            content=ft.Icon(
                                ft.Icons.HEADSET_MIC,
                                color=ft.Colors.PURPLE_700,
                                size=24,
                            ),
                            padding=10,
                            bgcolor=ft.Colors.PURPLE_50,
                            border_radius=50,
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    "Fale com o Síndico",
                                    size=18,
                                    weight="bold",
                                    color=ft.Colors.BLUE_GREY_900,
                                )
                            ]
                        ),
                    ]
                ),
                ft.Divider(height=25, color=ft.Colors.GREY_200),
                ft.Row([cat_input]),
                texto_input,
                ft.Container(height=5),
                ft.Row(
                    [
                        ft.ElevatedButton(
                            "Enviar Mensagem",
                            icon=ft.Icons.SEND,
                            bgcolor=ft.Colors.PURPLE_700,
                            color="white",
                            on_click=abrir_novo_chamado_premium,
                            height=45,
                        )
                    ],
                    alignment="end",
                ),
            ]
        ),
    )
    tela_ouvidoria = ft.Container(
        content=ft.Column(
            [
                cartao_abrir_chamado,
                ft.Text(
                    "Seus Chamados",
                    size=18,
                    weight="bold",
                    color=ft.Colors.BLUE_GREY_900,
                ),
                lista_chamados_ui,
            ]
        ),
        padding=15,
        expand=True,
        visible=False,
    )

    # --- ASSEMBLEIAS ---
    lista_ass_ui = ft.ListView(expand=True, spacing=10)
    tela_lista_assembleias = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Selecione a Assembleia",
                    weight="bold",
                    size=18,
                    color=ft.Colors.BLUE_GREY_900,
                ),
                lista_ass_ui,
            ]
        ),
        padding=15,
        expand=True,
        visible=False,
    )
    lista_pautas_ui = ft.ListView(expand=True, spacing=15)
    tela_pautas_assembleia = ft.Container(
        content=ft.Column(
            [
                ft.Row(
                    [
                        ft.IconButton(
                            ft.Icons.ARROW_BACK,
                            icon_color=ft.Colors.BLUE_900,
                            on_click=lambda e: (
                                page.appbar.title._set_value("Assembleias"),
                                esconder_tudo(),
                                setattr(tela_lista_assembleias, "visible", True),
                                page.update(),
                            ),
                        ),
                        ft.Text(
                            "Pautas em Deliberação",
                            weight="bold",
                            size=18,
                            color=ft.Colors.BLUE_900,
                        ),
                    ]
                ),
                lista_pautas_ui,
            ]
        ),
        padding=10,
        expand=True,
        visible=False,
    )

    def carregar_lista_assembleias():
        lista_ass_ui.controls.clear()
        assembleias = banco_dados.listar_assembleias()
        if not assembleias:
            lista_ass_ui.controls.append(
                ft.Text("Nenhuma assembleia convocada.", text_align="center")
            )
        for ass in assembleias:
            lista_ass_ui.controls.append(
                ft.Card(
                    elevation=3,
                    content=ft.Container(
                        padding=15,
                        on_click=lambda e, i=ass[0], t=ass[1], s=ass[3]: (
                            abrir_pautas_da_assembleia(i, t, s)
                        ),
                        ink=True,
                        content=ft.Column(
                            [
                                ft.Row(
                                    [
                                        ft.Icon(
                                            ft.Icons.ACCOUNT_BALANCE,
                                            color=ft.Colors.TEAL_700,
                                        ),
                                        ft.Text(
                                            ass[3].upper(),
                                            color=ft.Colors.GREEN_700
                                            if ass[3] == "Aberta"
                                            else ft.Colors.RED_700,
                                            weight="bold",
                                            size=12,
                                        ),
                                    ],
                                    alignment="spaceBetween",
                                ),
                                ft.Text(ass[1], weight="bold", size=16),
                                ft.Text(f"Prazo: {ass[2]}", size=12, color="grey"),
                            ]
                        ),
                    ),
                )
            )
            page.update()

    def abrir_pautas_da_assembleia(id_ass, titulo_ass, status_ass):
        page.appbar.title.value = "Pautas"
        lista_pautas_ui.controls.clear()
        pautas = banco_dados.listar_pautas_da_assembleia(id_ass)
        for p in pautas:
            meu_voto = banco_dados.verificar_voto(p[0], unidade_logada)
            area_votacao = ft.Column()
            if status_ass != "Aberta":
                area_votacao.controls.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.LOCK, color="red"),
                                ft.Text(
                                    "VOTAÇÃO ENCERRADA", weight="bold", color="red"
                                ),
                            ]
                        ),
                        bgcolor=ft.Colors.RED_50,
                        padding=10,
                        border_radius=5,
                        alignment=ft.alignment.center,
                    )
                )
            elif meu_voto:
                area_votacao.controls.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "VOTO REGISTRADO:",
                                    size=12,
                                    weight="bold",
                                    color=ft.Colors.GREEN_900,
                                ),
                                ft.Row(
                                    [
                                        ft.Icon(ft.Icons.CHECK_CIRCLE, color="green"),
                                        ft.Text(
                                            f'"{meu_voto.upper()}"',
                                            color=ft.Colors.GREEN_700,
                                            weight="bold",
                                            size=18,
                                        ),
                                    ],
                                    alignment="center",
                                ),
                            ],
                            horizontal_alignment="center",
                        ),
                        bgcolor=ft.Colors.GREEN_50,
                        padding=15,
                        border_radius=8,
                    )
                )
            else:
                area_votacao.controls.append(
                    ft.Container(
                        padding=15,
                        bgcolor=ft.Colors.BLUE_GREY_50,
                        border_radius=8,
                        content=ft.Column(
                            [
                                ft.Text(
                                    "CÉDULA DE VOTAÇÃO",
                                    weight="bold",
                                    color=ft.Colors.BLUE_GREY_800,
                                    text_align="center",
                                ),
                                ft.Column(
                                    [
                                        ft.ElevatedButton(
                                            "APROVAR (SIM)",
                                            icon=ft.Icons.THUMB_UP,
                                            bgcolor=ft.Colors.GREEN_700,
                                            color="white",
                                            on_click=lambda e, i=p[0]: (
                                                banco_dados.registrar_voto(
                                                    i, unidade_logada, "Sim"
                                                ),
                                                abrir_pautas_da_assembleia(
                                                    id_ass, titulo_ass, status_ass
                                                ),
                                            ),
                                            width=300,
                                        ),
                                        ft.ElevatedButton(
                                            "REJEITAR (NÃO)",
                                            icon=ft.Icons.THUMB_DOWN,
                                            bgcolor=ft.Colors.RED_700,
                                            color="white",
                                            on_click=lambda e, i=p[0]: (
                                                banco_dados.registrar_voto(
                                                    i, unidade_logada, "Não"
                                                ),
                                                abrir_pautas_da_assembleia(
                                                    id_ass, titulo_ass, status_ass
                                                ),
                                            ),
                                            width=300,
                                        ),
                                    ],
                                    horizontal_alignment="center",
                                ),
                            ],
                            horizontal_alignment="center",
                        ),
                    )
                )
            lista_pautas_ui.controls.append(
                ft.Card(
                    elevation=4,
                    content=ft.Container(
                        padding=20,
                        border_radius=10,
                        content=ft.Column(
                            [
                                ft.Text(
                                    f"#{p[0]} - {p[1]}",
                                    weight="bold",
                                    size=18,
                                    color=ft.Colors.TEAL_900,
                                ),
                                ft.Text(p[2], size=14, color=ft.Colors.BLACK87),
                                ft.Container(height=10),
                                ft.Image(
                                    src=p[3], border_radius=8, fit=ft.ImageFit.COVER
                                )
                                if p[3]
                                else ft.Container(),
                                area_votacao,
                            ]
                        ),
                    ),
                )
            )
        esconder_tudo()
        tela_pautas_assembleia.visible = True
        page.update()

    # --- OBRAS ---
    lista_obras_ui = ft.ListView(expand=True, spacing=15)
    tela_obras = ft.Container(
        content=ft.Column(
            [
                ft.Text(
                    "Vote nas prioridades",
                    size=22,
                    weight="bold",
                    color=ft.Colors.ORANGE_900,
                ),
                ft.Text(
                    "Avalie de 1 a 5 estrelas o que você considera mais urgente.",
                    size=13,
                    color=ft.Colors.BLUE_GREY_600,
                ),
                ft.Divider(color=ft.Colors.ORANGE_200),
                lista_obras_ui,
            ]
        ),
        padding=15,
        expand=True,
        visible=False,
    )

    def carregar_obras_morador():
        lista_obras_ui.controls.clear()
        obras = banco_dados.listar_obras()
        if not obras:
            lista_obras_ui.controls.append(
                ft.Text(
                    "Nenhuma necessidade cadastrada.", text_align="center", italic=True
                )
            )
        for ob in obras:
            minha_nota = banco_dados.verificar_minha_nota(ob[0], unidade_logada)
            botoes = [
                ft.IconButton(
                    icon=ft.Icons.STAR if i <= minha_nota else ft.Icons.STAR_BORDER,
                    icon_color=ft.Colors.AMBER_500
                    if i <= minha_nota
                    else ft.Colors.GREY_400,
                    icon_size=32,
                    padding=0,
                    on_click=lambda e, i_ob=ob[0], n=i: (
                        banco_dados.registrar_avaliacao_obra(i_ob, unidade_logada, n),
                        carregar_obras_morador(),
                    ),
                )
                for i in range(1, 6)
            ]
            lista_obras_ui.controls.append(
                ft.Card(
                    elevation=4,
                    content=ft.Container(
                        padding=20,
                        border_radius=10,
                        border=ft.border.all(1, ft.Colors.ORANGE_200),
                        bgcolor=ft.Colors.ORANGE_50,
                        content=ft.Column(
                            [
                                ft.Text(
                                    ob[1],
                                    weight="bold",
                                    size=18,
                                    color=ft.Colors.ORANGE_900,
                                ),
                                ft.Text(
                                    f"Custo: {ob[3] or 'N/A'}",
                                    size=12,
                                    color=ft.Colors.GREY_700,
                                ),
                                ft.Divider(),
                                ft.Text(ob[2], size=14, color=ft.Colors.BLUE_GREY_800),
                                ft.Container(
                                    padding=10,
                                    border_radius=8,
                                    bgcolor="white",
                                    content=ft.Column(
                                        [
                                            ft.Text(
                                                "Qual a urgência disto?",
                                                size=12,
                                                weight="bold",
                                                color=ft.Colors.BLUE_GREY_500,
                                            ),
                                            ft.Row(
                                                botoes, alignment="center", spacing=0
                                            ),
                                        ],
                                        horizontal_alignment="center",
                                    ),
                                ),
                            ]
                        ),
                    ),
                )
            )
        page.update()

    page.add(
        tela_login,
        tela_dashboard,
        tela_documentos,
        tela_ouvidoria,
        tela_lista_assembleias,
        tela_pautas_assembleia,
        tela_obras,
        tela_reservas,
        tela_estatuto,
    )


porta = int(os.environ.get("PORT", 8080))
ft.app(target=main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=porta, assets_dir=ASSETS_DIR)
