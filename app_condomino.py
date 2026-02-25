import flet as ft
import banco_dados
import os
import datetime

# Ajuste de diretórios para o servidor Render
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(DIRETORIO_ATUAL, "assets")

def main(page: ft.Page):
    page.title = "App do Condômino - Acauã"
    page.theme_mode = ft.ThemeMode.LIGHT
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
        if page.appbar:
            page.appbar.visible = False
        esconder_tudo()
        tela_login.visible = True
        page.update()

    def ir_para_dashboard(e=None):
        saudacao_nome.value = f"Olá, {nome_logado.split()[0]}"
        saudacao_unidade.value = f"Unidade: {unidade_logada}"
        letra_avatar.value = nome_logado[0].upper()
        if page.appbar:
            page.appbar.visible = False
        esconder_tudo()
        tela_dashboard.visible = True
        page.update()

    def criar_appbar_interna(titulo):
        page.appbar.title = ft.Text(titulo, weight="bold", color="white")
        page.appbar.leading = ft.IconButton(
            ft.icons.ARROW_BACK, icon_color="white", on_click=ir_para_dashboard
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

    page.appbar = ft.AppBar(bgcolor=ft.colors.TEAL_700, elevation=0)
    page.appbar.visible = False

    # ==========================================
    # 1. LOGIN E DASHBOARD FINTECH
    # ==========================================
    def formatar_cpf(e):
        v = "".join(filter(str.isdigit, e.control.value))[:11]
        r = ""
        for i, c in enumerate(v):
            if i in [3, 6]: r += "."
            elif i == 9: r += "-"
            r += c
        e.control.value = r
        e.control.update()

    campo_cpf = ft.TextField(
        label="CPF do Morador",
        hint_text="Apenas números (sem pontos)",
        width=300,
        border_color=ft.colors.TEAL_600,
        # O filtro abaixo bloqueia qualquer letra ou ponto, aceitando só números
        input_filter=ft.InputFilter(allow=True, regex_string=r"[0-9]", replacement_string=""),
        keyboard_type=ft.KeyboardType.NUMBER,
        max_length=11, 
        counter_text=" ",
    )
    
    # NOVAS UNIDADES ADICIONADAS
    campo_unidade = ft.Dropdown(
        label="Sua Unidade",
        options=[
            ft.dropdown.Option("Apt 101"),
            ft.dropdown.Option("Apt 102"),
            ft.dropdown.Option("Apt 201"),
            ft.dropdown.Option("Apt 202"),
            ft.dropdown.Option("Apt 301"),
            ft.dropdown.Option("Apt 302"),
        ],
        width=300,
        border_color=ft.colors.TEAL_600,
    )

    def tentar_login(e):
        nonlocal unidade_logada, nome_logado
        if not campo_cpf.value or not campo_unidade.value:
            page.snack_bar = ft.SnackBar(ft.Text("Preencha todos os dados!"))
            page.snack_bar.open = True
            page.update()
            return
        
        cpf_limpo = "".join(filter(str.isdigit, campo_cpf.value))
        nome = banco_dados.validar_login_morador(cpf_limpo, campo_unidade.value)
        
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
                ft.Icon(ft.icons.SECURITY, size=80, color=ft.colors.TEAL_700),
                ft.Text("Portal do Morador", size=26, weight="bold", color=ft.colors.TEAL_900),
                ft.Container(height=20),
                campo_cpf,
                campo_unidade,
                ft.ElevatedButton(
                    "Entrar no Sistema",
                    icon=ft.icons.LOGIN,
                    on_click=tentar_login,
                    bgcolor=ft.colors.TEAL_700,
                    color="white",
                    width=300,
                    height=50,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        ),
        alignment=ft.alignment.center,
        expand=True,
    )

    saudacao_nome = ft.Text("", size=22, weight="bold", color="white")
    saudacao_unidade = ft.Text("", size=14, color=ft.colors.TEAL_100)
    letra_avatar = ft.Text("", size=24, weight="bold", color=ft.colors.TEAL_900)
    header_dashboard = ft.Container(
        padding=ft.padding.only(top=50, left=30, right=30, bottom=30),
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[ft.colors.TEAL_700, ft.colors.TEAL_900],
        ),
        border_radius=ft.border_radius.only(bottom_left=30, bottom_right=30),
        content=ft.Row(
            [
                ft.CircleAvatar(content=letra_avatar, bgcolor="white", radius=30),
                ft.Container(width=10),
                ft.Column([saudacao_nome, saudacao_unidade], spacing=2, expand=True),
                ft.IconButton(ft.icons.LOGOUT, icon_color="white", on_click=ir_para_login),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        ),
    )

    def criar_cartao_premium(titulo, icone, cor_icone, rota):
        return ft.Container(
            on_click=rota,
            bgcolor="white",
            border_radius=20,
            padding=20,
            shadow=ft.BoxShadow(blur_radius=10, color=ft.colors.BLACK12, offset=ft.Offset(0, 4)),
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Icon(icone, size=35, color=cor_icone),
                        padding=12,
                        bgcolor=ft.colors.with_opacity(0.1, cor_icone),
                        border_radius=50,
                    ),
                    ft.Container(height=5),
                    ft.Text(titulo, weight="bold", size=12, color=ft.colors.BLUE_GREY_900, text_align=ft.TextAlign.CENTER),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            col={"xs": 4},
        )

    grid_dashboard = ft.ResponsiveRow(
        controls=[
            criar_cartao_premium("Assembleias", ft.icons.HOW_TO_VOTE, ft.colors.TEAL_600, ir_para_assembleias),
            criar_cartao_premium("Ouvidoria", ft.icons.FORUM, ft.colors.PURPLE_600, ir_para_ouvidoria),
            criar_cartao_premium("Documentos", ft.icons.FOLDER_SPECIAL, ft.colors.RED_600, ir_para_documentos),
            criar_cartao_premium("Priorizar", ft.icons.LOW_PRIORITY, ft.colors.ORANGE_600, ir_para_obras),
            criar_cartao_premium("Reservas", ft.icons.EVENT_AVAILABLE, ft.colors.CYAN_600, ir_para_reservas),
            criar_cartao_premium("Regras", ft.icons.MENU_BOOK, ft.colors.INDIGO_600, ir_para_estatuto),
        ],
        spacing=15,
        run_spacing=15,
    )

    tela_dashboard = ft.Container(
        content=ft.Column(
            [
                header_dashboard,
                ft.Container(
                    content=ft.Column([ft.Text("Acesso Rápido", size=18, weight="bold", color=ft.colors.BLUE_GREY_800), grid_dashboard]),
                    padding=25,
                ),
            ]
        ),
        expand=True,
        visible=False,
    )

    # ==========================================
    # 6. MÓDULO: RESERVAS 
    # ==========================================
    estilo_campo = {
        "border_radius": 12,
        "border_color": ft.colors.CYAN_400,
        "focused_border_color": ft.colors.CYAN_700,
        "bgcolor": ft.colors.CYAN_50,
        "content_padding": 15,
        "text_size": 14,
        "label_style": ft.TextStyle(color=ft.colors.CYAN_900, weight="bold"),
    }

    campo_espaco = ft.Dropdown(
        label="1. Escolha o Espaço",
        prefix=ft.Icon(ft.icons.HOME_WORK, color=ft.colors.CYAN_700),
        options=[ft.dropdown.Option("Salão de Festas"), ft.dropdown.Option("Churrasqueira"), ft.dropdown.Option("Quadra Poliesportiva")],
        **estilo_campo,
    )

    campo_data_reserva = ft.TextField(
        label="2. Defina a Data",
        hint_text="Clique no calendário 👉",
        prefix=ft.Icon(ft.icons.DATE_RANGE, color=ft.colors.CYAN_700),
        read_only=True,
        expand=True,
        **estilo_campo,
    )

    campo_horario = ft.Dropdown(
        label="3. Selecione o Turno",
        prefix=ft.Icon(ft.icons.ACCESS_TIME, color=ft.colors.CYAN_700),
        options=[],
        **estilo_campo,
    )

    def verificar_turnos_disponiveis(e=None):
        if not campo_espaco.value or not campo_data_reserva.value: return
        turnos_ocupados = banco_dados.verificar_disponibilidade_turnos(campo_espaco.value, campo_data_reserva.value)
        opcoes_padrao = ["Manhã (08h - 12h)", "Tarde (13h - 17h)", "Noite (18h - 22h)"]
        campo_horario.options = [
            ft.dropdown.Option(key=t, text=f"🔴 Ocupado: {t}" if t in turnos_ocupados else f"✅ Livre: {t}", disabled=(t in turnos_ocupados))
            for t in opcoes_padrao
        ]
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

    def abrir_calendario(e):
        page.open(cal_reserva)
        page.update()

    lista_minhas_reservas = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)
    lista_agenda_publica = ft.Column(spacing=10, scroll=ft.ScrollMode.AUTO, expand=True)

    def solicitar_reserva(e):
        if not campo_espaco.value or not campo_data_reserva.value or not campo_horario.value:
            page.snack_bar = ft.SnackBar(ft.Text("Preencha todos os passos!"), bgcolor="red")
            page.snack_bar.open = True; page.update(); return

        if banco_dados.adicionar_reserva(campo_espaco.value, campo_data_reserva.value, campo_horario.value, unidade_logada):
            page.snack_bar = ft.SnackBar(ft.Text("Solicitação enviada ao Síndico!"), bgcolor="green")
            campo_espaco.value = None; campo_data_reserva.value = ""; campo_horario.value = None; carregar_reservas_morador()
        else:
            page.snack_bar = ft.SnackBar(ft.Text("Opa! Alguém foi mais rápido!"), bgcolor="red")
        page.snack_bar.open = True; page.update()

    def cancelar_reserva_ui(id_res):
        banco_dados.cancelar_reserva_morador(id_res, unidade_logada)
        page.snack_bar = ft.SnackBar(ft.Text("Reserva cancelada!"), bgcolor=ft.colors.ORANGE_700)
        page.snack_bar.open = True; carregar_reservas_morador()

    def carregar_reservas_morador():
        lista_minhas_reservas.controls.clear()
        reservas = banco_dados.listar_reservas(unidade_filtro=unidade_logada)
        if not reservas:
            lista_minhas_reservas.controls.append(ft.Container(padding=20, content=ft.Text("Você não tem agendamentos.", italic=True, color="grey")))
        for res in reservas:
            id_r, esp, dat, hor, uni, stat = res
            cor_st = ft.colors.AMBER_600 if stat == "Pendente" else (ft.colors.GREEN_600 if stat == "Aprovada" else ft.colors.RED_600)
            icone_st = ft.icons.SCHEDULE if stat == "Pendente" else (ft.icons.CHECK_CIRCLE if stat == "Aprovada" else ft.icons.CANCEL)
            btn_cancelar = ft.IconButton(ft.icons.DELETE_OUTLINE, icon_color="red", on_click=lambda e, i=id_r: cancelar_reserva_ui(i)) if stat != "Rejeitada" else ft.Container()

            lista_minhas_reservas.controls.append(ft.Container(
                bgcolor="white", padding=15, border_radius=12, border=ft.border.only(left=ft.border.BorderSide(6, cor_st)),
                content=ft.Row([
                    ft.Column([ft.Text(esp, weight="bold", size=15), ft.Text(f"{dat} | {hor}", size=12), ft.Row([ft.Icon(icone_st, color=cor_st, size=14), ft.Text(stat.upper(), color=cor_st, weight="bold", size=11)])], expand=True),
                    btn_cancelar
                ])
            ))
        
        lista_agenda_publica.controls.clear()
        for ag in banco_dados.listar_agenda_publica():
            lista_agenda_publica.controls.append(ft.Card(content=ft.Container(padding=15, border_radius=8, bgcolor=ft.colors.CYAN_50, content=ft.Row([
                ft.Icon(ft.icons.CELEBRATION, color=ft.colors.CYAN_700, size=30), ft.Container(width=10),
                ft.Column([ft.Text(ag[0], weight="bold", size=15, color=ft.colors.CYAN_900), ft.Text(f"{ag[1]} • {ag[2]}", size=13), ft.Text(f"Reservado por: {ag[3]}", size=11, italic=True)])
            ]))))
        page.update()

    aba_minhas = ft.Container(padding=ft.padding.only(top=15), content=ft.Column([
        ft.Container(bgcolor="white", padding=25, border_radius=15, content=ft.Column([
            ft.Text("Agendar Espaço", size=18, weight="bold"),
            campo_espaco, ft.Row([campo_data_reserva, ft.IconButton(ft.icons.CALENDAR_MONTH, on_click=abrir_calendario)]),
            campo_horario, ft.ElevatedButton("Enviar Solicitação", bgcolor=ft.colors.CYAN_700, color="white", on_click=solicitar_reserva, width=400)
        ])),
        ft.Text("Meus Pedidos", weight="bold", size=16), lista_minhas_reservas
    ], scroll=ft.ScrollMode.AUTO))

    aba_agenda = ft.Container(padding=15, content=ft.Column([ft.Text("Agenda Oficial", weight="bold", size=18), lista_agenda_publica], scroll=ft.ScrollMode.AUTO))

    tela_reservas = ft.Container(content=ft.Tabs(tabs=[
        ft.Tab(text="Fazer Reserva", icon=ft.icons.ADD_ALARM, content=aba_minhas),
        ft.Tab(text="Agenda Pública", icon=ft.icons.CALENDAR_TODAY, content=aba_agenda),
    ], expand=True), padding=10, expand=True, visible=False)

    # ==========================================
    # MÓDULO: ESTATUTO / MANUAL 📖
    # ==========================================
    lista_regras_ui = ft.ListView(expand=True, spacing=10)
    def carregar_estatuto_morador():
        lista_regras_ui.controls.clear()
        for r in banco_dados.listar_estatuto():
            lista_regras_ui.controls.append(ft.ExpansionTile(title=ft.Text(r[1], weight="bold"), leading=ft.Icon(ft.icons.GAVEL), controls=[ft.Container(padding=15, content=ft.Text(r[2]))]))
        page.update()

    tela_estatuto = ft.Container(content=ft.Column([ft.Text("Manual do Condomínio", size=22, weight="bold"), ft.Divider(), lista_regras_ui]), padding=15, expand=True, visible=False)

    # --- DOCUMENTOS ---
    coluna_pastas = ft.Column(expand=True, scroll=ft.ScrollMode.AUTO)
    tela_documentos = ft.Container(content=ft.Column([ft.Text("Transparência", size=22, weight="bold"), ft.Divider(), coluna_pastas]), padding=20, expand=True, visible=False)

    def abrir_pdf_web(subpasta, nome_arquivo):
        page.launch_url(f"/{subpasta}/{nome_arquivo}")

    def carregar_documentos_morador():
        coluna_pastas.controls.clear()
        docs = banco_dados.listar_documentos()
        docs_mensais = ft.Column(spacing=5); docs_anuais = ft.Column(spacing=5)
        for d in docs:
            item = ft.ListTile(leading=ft.Icon(ft.icons.PICTURE_AS_PDF, color="green"), title=ft.Text(f"{d[2]} - {d[3]}"), on_click=lambda e, a=d[4]: abrir_pdf_web("Prestacao_Contas", a))
            if d[1] == "Prestação de Contas Mensal": docs_mensais.controls.append(item)
            else: docs_anuais.controls.append(item)
        coluna_pastas.controls.extend([
            ft.ExpansionTile(title=ft.Text("Mensais", weight="bold"), leading=ft.Icon(ft.icons.FOLDER_OPEN, color="green"), controls=[ft.Container(padding=10, content=docs_mensais)]),
            ft.ExpansionTile(title=ft.Text("Anuais", weight="bold"), leading=ft.Icon(ft.icons.FOLDER_SPECIAL, color="blue"), controls=[ft.Container(padding=10, content=docs_anuais)])
        ])
        page.update()

    # --- OUVIDORIA ---
    cat_input = ft.Dropdown(label="Assunto", options=[ft.dropdown.Option("Reclamação"), ft.dropdown.Option("Manutenção")], expand=True)
    texto_input = ft.TextField(label="Descrição...", multiline=True, min_lines=3)
    lista_chamados_ui = ft.Column(spacing=20, scroll=ft.ScrollMode.AUTO)

    def abrir_novo_chamado_premium(e):
        if not cat_input.value or not texto_input.value: return
        banco_dados.criar_novo_chamado(cat_input.value, texto_input.value, unidade_logada)
        cat_input.value = None; texto_input.value = ""; carregar_historico_premium()

    def carregar_historico_premium():
        lista_chamados_ui.controls.clear()
        for ch in banco_dados.listar_chamados(unidade_filtro=unidade_logada):
            lista_chamados_ui.controls.append(ft.Container(bgcolor="white", padding=20, border_radius=10, content=ft.Text(f"{ch[4]}: {ch[5]}")))
        page.update()

    tela_ouvidoria = ft.Container(content=ft.Column([ft.Text("Fale com o Síndico", size=18, weight="bold"), cat_input, texto_input, ft.ElevatedButton("Enviar", on_click=abrir_novo_chamado_premium), lista_chamados_ui]), padding=15, expand=True, visible=False)

    # --- ASSEMBLEIAS E DEBATE ---
    lista_ass_ui = ft.ListView(expand=True, spacing=10)
    tela_lista_assembleias = ft.Container(content=ft.Column([ft.Text("Assembleias", size=18, weight="bold"), lista_ass_ui]), padding=15, expand=True, visible=False)
    
    def voltar_assembleias(e):
        page.appbar.title.value = "Assembleias"
        esconder_tudo()
        tela_lista_assembleias.visible = True
        page.update()

    lista_pautas_ui = ft.ListView(expand=True, spacing=15)
    tela_pautas_assembleia = ft.Container(content=ft.Column([ft.Row([ft.IconButton(ft.icons.ARROW_BACK, icon_color=ft.colors.BLUE_900, on_click=voltar_assembleias), ft.Text("Pautas em Deliberação", weight="bold", size=18, color=ft.colors.BLUE_900)]), lista_pautas_ui]), padding=10, expand=True, visible=False)

    def carregar_lista_assembleias():
        lista_ass_ui.controls.clear()
        for ass in banco_dados.listar_assembleias():
            lista_ass_ui.controls.append(ft.Card(content=ft.Container(padding=15, on_click=lambda e, i=ass[0], t=ass[1], s=ass[3]: abrir_pautas_da_assembleia(i, t, s), content=ft.Text(ass[1], weight="bold"))))
        page.update()

    # MÓDULO NOVO DE DEBATE
    def criar_caixa_debate(id_pauta):
        lista_comentarios = ft.Column(spacing=5, height=150, scroll=ft.ScrollMode.AUTO)
        campo_msg = ft.TextField(label="Sua opinião sobre a pauta...", expand=True, height=45, content_padding=10)

        def atualizar_mensagens():
            lista_comentarios.controls.clear()
            try:
                msgs = banco_dados.listar_comentarios_pauta(id_pauta)
                if not msgs:
                    lista_comentarios.controls.append(ft.Text("Nenhum comentário. Seja o primeiro a debater!", italic=True, color="grey", size=12))
                for m in msgs:
                    lista_comentarios.controls.append(
                        ft.Container(
                            bgcolor=ft.colors.GREY_100, padding=10, border_radius=8,
                            content=ft.Column([
                                ft.Text(f"{m[0]} - {m[2]}", weight="bold", size=11, color=ft.colors.BLUE_GREY_700),
                                ft.Text(m[1], size=13)
                            ], spacing=2)
                        )
                    )
            except:
                lista_comentarios.controls.append(ft.Text("Atualize o banco de dados para ver os debates.", color="red", size=12))
            page.update()

        def enviar_msg(e):
            if campo_msg.value:
                banco_dados.adicionar_comentario_pauta(id_pauta, unidade_logada, campo_msg.value)
                campo_msg.value = ""
                atualizar_mensagens()

        atualizar_mensagens()
        return ft.ExpansionTile(
            title=ft.Text("Debate da Pauta", weight="bold", size=14, color=ft.colors.BLUE_900),
            leading=ft.Icon(ft.icons.FORUM, color=ft.colors.BLUE_700),
            controls=[
                ft.Container(
                    padding=15, bgcolor=ft.colors.BLUE_50,
                    content=ft.Column([
                        lista_comentarios,
                        ft.Row([campo_msg, ft.IconButton(ft.icons.SEND, icon_color=ft.colors.BLUE_700, on_click=enviar_msg)])
                    ])
                )
            ]
        )

    def abrir_pautas_da_assembleia(id_ass, titulo, status):
        lista_pautas_ui.controls.clear()
        for p in banco_dados.listar_pautas_da_assembleia(id_ass):
            caixa_debate = criar_caixa_debate(p[0]) # ADICIONA O DEBATE AQUI
            
            meu_voto = banco_dados.verificar_voto(p[0], unidade_logada)
            area_votacao = ft.Column()
            if status != "Aberta": area_votacao.controls.append(ft.Container(content=ft.Row([ft.Icon(ft.icons.LOCK, color="red"), ft.Text("ENCERRADA", color="red")]), bgcolor=ft.colors.RED_50, padding=10))
            elif meu_voto: area_votacao.controls.append(ft.Container(content=ft.Text(f"Votado: {meu_voto.upper()}", color="green", weight="bold"), bgcolor=ft.colors.GREEN_50, padding=15))
            else:
                area_votacao.controls.append(
                    ft.Container(
                        padding=15, bgcolor=ft.colors.BLUE_GREY_50,
                        content=ft.Column([
                            ft.ElevatedButton("APROVAR", icon=ft.icons.THUMB_UP, bgcolor="green", color="white", on_click=lambda e, i=p[0]: (banco_dados.registrar_voto(i, unidade_logada, "Sim"), abrir_pautas_da_assembleia(id_ass, titulo, status))),
                            ft.ElevatedButton("REJEITAR", icon=ft.icons.THUMB_DOWN, bgcolor="red", color="white", on_click=lambda e, i=p[0]: (banco_dados.registrar_voto(i, unidade_logada, "Não"), abrir_pautas_da_assembleia(id_ass, titulo, status))),
                        ])
                    )
                )
            
            lista_pautas_ui.controls.append(ft.Card(content=ft.Container(padding=20, content=ft.Column([ft.Text(p[1], weight="bold"), ft.Text(p[2]), caixa_debate, area_votacao]))))
        esconder_tudo(); tela_pautas_assembleia.visible = True; page.update()

    # --- OBRAS ---
    lista_obras_ui = ft.ListView(expand=True, spacing=15)
    tela_obras = ft.Container(content=ft.Column([ft.Text("Prioridades", size=22, weight="bold"), lista_obras_ui]), padding=15, expand=True, visible=False)

    def carregar_obras_morador():
        lista_obras_ui.controls.clear()
        for ob in banco_dados.listar_obras():
            minha_nota = banco_dados.verificar_minha_nota(ob[0], unidade_logada)
            botoes = [
                ft.IconButton(
                    icon=ft.icons.STAR if i <= minha_nota else ft.icons.STAR_BORDER, icon_color=ft.colors.AMBER_500 if i <= minha_nota else ft.colors.GREY_400, icon_size=32,
                    on_click=lambda e, i_ob=ob[0], n=i: (banco_dados.registrar_avaliacao_obra(i_ob, unidade_logada, n), carregar_obras_morador()),
                ) for i in range(1, 6)
            ]
            lista_obras_ui.controls.append(ft.Card(content=ft.Container(padding=20, content=ft.Column([ft.Text(ob[1], weight="bold", size=18), ft.Row(botoes)]))))
        page.update()

    page.add(tela_login, tela_dashboard, tela_documentos, tela_ouvidoria, tela_lista_assembleias, tela_pautas_assembleia, tela_obras, tela_reservas, tela_estatuto)

# Ponto de Entrada Web
porta = int(os.environ.get("PORT", 8080))
ft.app(target=main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=porta, assets_dir=ASSETS_DIR)

