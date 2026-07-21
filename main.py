import flet as ft
import psycopg2
import threading
import time
import os
from datetime import datetime, timedelta, timezone

# ---------------------------------------------------------------------------
# CONEXÃO E CONFIGURAÇÃO DO BANCO
# ---------------------------------------------------------------------------
def conectar_banco():
    url = os.environ.get("DATABASE_URL")
    if url:
        return psycopg2.connect(url, sslmode="require")
    return psycopg2.connect(
        host="aws-1-sa-east-1.pooler.supabase.com",
        port=6543,
        dbname="postgres",
        user="postgres.qvgxlpnicbjqnierhbvi",
        password=os.environ.get("DB_PASSWORD", "supleweb26@"),
        sslmode="require",
    )

def obter_agora_br():
    fuso_br = timezone(timedelta(hours=-3))
    return datetime.now(fuso_br)

# ---------------------------------------------------------------------------
# INICIALIZAÇÃO E DADOS DO PDF
# ---------------------------------------------------------------------------
def inicializar_banco():
    conexao = conectar_banco()
    cursor = conexao.cursor()
    
    # Criação das tabelas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tarefas_vocais (
            id SERIAL PRIMARY KEY,
            fase INTEGER NOT NULL,
            nome TEXT NOT NULL,
            para_que TEXT,
            como_fazer TEXT,
            exercicio TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS checks_vocais (
            tarefa_id INTEGER,
            data TEXT,
            PRIMARY KEY (tarefa_id, data)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS acessos_vocais (
            data TEXT PRIMARY KEY
        )
    ''')
    
    # Verifica se já existem tarefas (se não, popula com o PDF)
    cursor.execute("SELECT COUNT(*) FROM tarefas_vocais")
    if cursor.fetchone()[0] == 0:
        dados_iniciais = [
            # FASE 1
            (1, "A Técnica da Careta", "Acordar a musculatura facial e quebrar a apatia natural do rosto.", "Olhando para o teto, faça as caretas mais exageradas que conseguir, esticando ao máximo os olhos, a boca, as sobrancelhas e o nariz.", "Sustente a careta no limite do estiramento por 10 a 15 segundos."),
            (1, "O Descongestionamento", "Limpar o trato nasal e evitar que a voz saia presa e anasalada.", "Inspire profundamente pelo nariz. Simultaneamente, coloque os dedos nas laterais do nariz e puxe a pele para baixo.", "Repita o movimento de inspirar e puxar a pele 10 vezes."),
            (1, "Soltura de Mandíbula", "Quebrar a rigidez do maxilar que causa a 'fala seca'.", "Apoie as mãos nas laterais do rosto e abra a boca até sentir o seu limite (sem forçar a ponto de estalar a articulação).", "Faça o movimento de abrir e fechar a boca de 5 a 10 vezes, de forma lenta."),
            (1, "O Pêndulo Labial (Bico-Sorriso)", "Fortalecer o músculo orbicular da boca e automatizar a transição rápida.", "Mantenha os dentes levemente encostados. Faça um 'biquinho' projetando os lábios, imediatamente puxe para trás em um sorriso forçado.", "Alterne entre BICO e SORRISO rapidamente, 20 vezes."),
            (1, "O 'X-U' (Acelerador de Articulação)", "Treinar a transição fonética com som, calibrando a dose exata de força para a boca ganhar agilidade.", "Usando a mesma mecânica do pêndulo, vocalize as letras 'X' e 'U' de forma exagerada.", "Fale 'X-U-X-U-X-U' continuamente por 30 segundos, acelerando o ritmo aos poucos."),
            (1, "O Espaguete Retido (A Câmara de Eco)", "Isometria pura para manter a garganta expandida, criando espaço para a voz aveludada.", "Faça um 'biquinho'. Sugue o ar intensamente por 3 seg. Trave o ar por 5 a 10 seg, mantendo o biquinho.", "Solte o ar em um 'S' longo e suave ('Tssssss'). Repita o ciclo 5 vezes."),
            (1, "A Calha do Sulco Sagital", "Hipertrofiar o músculo transverso da língua, criar canal de ar limpo e eliminar o chiado.", "Coloque a língua para fora deixando-a pontiaguda. Tente elevar apenas as bordas laterais (formato de 'U').", "Sustente essa posição de calha por 3 a 8 segundos. Descanse e repita 5 vezes."),
            (1, "Mastigação Sonora e Salto Formântico", "Transferir a vibração para os lábios/nariz e dar um brilho aveludado na voz.", "De lábios fechados, faça o som 'Mmmmmm' contínuo enquanto mastiga exageradamente no ar. Após alguns segundos, abra a boca drasticamente para uma vogal.", "Faça: Mmmmmm... aaaaaa / eeeeee / oooooo. Duração: 3 minutos ininterruptos."),
            (1, "A Sanfona Costal", "Aprender a respirar sem elevar os ombros, usando a expansão lateral do tronco.", "Deitado de barriga para cima, mãos nas costelas flutuantes. Inspire pelo nariz sentindo as costas empurrarem o colchão.", "Faça 5 respirações profundas focando exclusivamente na expansão lateral e nas costas."),
            (1, "A Mão Espalmada", "Regular a pressão subglótica para poder usar um volume alto sem machucar a garganta.", "Assopre o ar contra a palma da mão (pequeno assobio). Faça som contínuo de 'a'. Após alguns seg, tire a mão e projete o som.", "Faça 5 disparos. (Assopra 3 seg -> Tira a mão e fala 'Bá!')."),
            
            # FASE 2
            (2, "O Hack Corporal", "Alterar a bioquímica, reduzir o cortisol e dar energia vital antes de ligar a câmera.", "Em pé, adote a Posição de Poder (Pose da Mulher Maravilha ou Pose de Vitória).", "Fique na posição por 2 a 3 minutos respirando fundo."),
            (2, "O 'Appoggio' de Bancada", "Impedir que as vísceras esmaguem o seu diafragma na postura sentada.", "Sente-se na ponta da cadeira (ísquios). Expanda as costelas laterais.", "Enquanto fala, contraia levemente a região do baixo ventre para manter fluxo de ar forte."),
            (2, "Técnica da Caneta na 'Caixa de Clinton'", "Forçar a musculatura labial para dicção impecável e treinar olhar fixo.", "Coloque caneta entre os dentes. Mantenha as mãos na caixa invisível do umbigo ao peito.", "Leia o texto articulando exageradamente olhando para a lente. Retire e leia novamente: 'A dopamina não é o hormônio do prazer...'"),
            
            # FASE 3
            (3, "Tópico 1: A Âncora do 'S' (Morte ao Chiado)", "O Segredo Mecânico: Ponta da língua colada atrás dos dentes inferiores. Lábios em sorriso leve. Som fino 'Tssssss'.", "Treino Isolado: Dois, Pois, Fiz, Pés, Status. / Meio: Mesmo, Festa, Cesta.", "Frases: 'Os dois clientes aguardam a resposta desde as três.' 'Quais são os custos dessa estratégia para este mês?'"),
            (3, "Tópico 2: A Despalatalização", "O Segredo Mecânico: Para L/N use estritamente a ponta da língua. Para 'Invex', abra bem a boca na vogal 'É'.", "Treino Isolado: Língua, Família, Menino, Invés, Através.", "Frases: 'Podemos marcar na clínica da Avenida Paulista?' 'O Júlio mandou os relatórios da unidade.'"),
            (3, "Tópico 3: Treino de Embelezamento (Adição do 'i')", "O Segredo Mecânico: Adoce as sílabas tônicas terminadas em S ou Z. 'Três' soa 'Trê-is'.", "Treino Isolado: Três->Trêis, Mas->Mais, Paz->Paiz, Voz->Voiz.", "Frases: 'Você faiz o favor de me trazer o orçamento até as trêis?' 'Foi a primeira veiz que a nossa voiz foi ouvida.'"),
            
            # FASE 4
            (4, "Roteiro 1: Remarcando (Tom Empático)", "Simulação de WhatsApp", "Leia aplicando respiração, 'S' ancorado, 'L/N' limpos e o 'i' de embelezamento.", "Oi, Júlio, tudo bem? Aqui é o Pedro. Rapaz, eu esstou te mandando esse áudio pois tivemos um pequeno imprevisto na clínica. Nóis vamos precisar remarcar o nosso encontro de quinta-feira..."),
            (4, "Roteiro 2: Follow-up (Autoridade/Confiança)", "Simulação de WhatsApp", "Leia aplicando respiração, 'S' ancorado, 'L/N' limpos e o 'i' de embelezamento.", "Bom dia, pessoal! Passando para atualizar os status do projeto deste mêis. A nossa equipe fiz uma análise do viés de mercado... Gostaria que todos estudassem os dados hoje..."),
            (4, "Roteiro 3: Networking (Descontraído)", "Simulação de WhatsApp", "Leia aplicando respiração, 'S' ancorado, 'L/N' limpos e o 'i' de embelezamento.", "E aí, meu caro, tudo em paiz? Fiquei sabendo que você está por São Paulo esses dias. O pessoal aqui do escritório vai fazer uma festa pequena, coisa simples, mesmo... Me avisa depois!"),
        ]
        
        cursor.executemany("INSERT INTO tarefas_vocais (fase, nome, para_que, como_fazer, exercicio) VALUES (%s, %s, %s, %s, %s)", dados_iniciais)
        
    conexao.commit()
    conexao.close()

# ---------------------------------------------------------------------------
# APP PRINCIPAL
# ---------------------------------------------------------------------------
def main(page: ft.Page):
    page.title = "Treino Vocal Master"
    page.theme_mode = ft.ThemeMode.DARK
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO
    page.padding = 10

    # Inicializa BD
    inicializar_banco()

    # Registra acesso para o foguinho
    data_hoje = obter_agora_br().strftime("%Y-%m-%d")
    def registrar_acesso():
        con = conectar_banco()
        cur = con.cursor()
        cur.execute("INSERT INTO acessos_vocais (data) VALUES (%s) ON CONFLICT DO NOTHING", (data_hoje,))
        con.commit()
        con.close()
    registrar_acesso()

    # Componentes de Cabeçalho
    txt_ofensiva = ft.Text("🔥 0 dias", size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.ORANGE_500)
    txt_data = ft.Text(obter_agora_br().strftime("%d/%m/%Y"), size=16, color=ft.Colors.GREEN_ACCENT)
    
    cabecalho = ft.Column([
        ft.Text("Treino Vocal Master", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
        ft.Row([txt_ofensiva, txt_data], alignment=ft.MainAxisAlignment.CENTER, spacing=20)
    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    # -----------------------------------------------------------------------
    # ABA 2: METAS E GAMIFICAÇÃO
    # -----------------------------------------------------------------------
    conteudo_metas = ft.Column(visible=False, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
    
    linha_graficos = ft.Row(alignment=ft.MainAxisAlignment.CENTER, spacing=10, wrap=True)

    def criar_card_pizza(titulo, porcentagem):
        valor_anel = porcentagem / 100.0 
        return ft.Container(
            content=ft.Column(
                controls=[
                    ft.Text(titulo, size=15, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Stack([
                        ft.ProgressRing(value=valor_anel, stroke_width=8, color=ft.Colors.GREEN_ACCENT_400, bgcolor=ft.Colors.GREY_800, width=70, height=70),
                        ft.Container(
                            content=ft.Column([ft.Text(f"{int(porcentagem)}%", size=13, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_ACCENT)], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            width=70, height=70
                        )
                    ])
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=6
            ), bgcolor=ft.Colors.GREY_900, padding=12, border_radius=12, width=110, border=ft.Border.all(1, ft.Colors.GREY_800)
        )

    def calcular_gamificacao():
        con = conectar_banco()
        cur = con.cursor()
        
        # Streak (Foguinho)
        cur.execute("SELECT data FROM acessos_vocais ORDER BY data DESC")
        datas = [datetime.strptime(r[0], "%Y-%m-%d").date() for r in cur.fetchall()]
        streak = 0
        if datas:
            hoje_date = obter_agora_br().date()
            ontem_date = hoje_date - timedelta(days=1)
            if datas[0] == hoje_date or datas[0] == ontem_date:
                streak = 1
                for i in range(1, len(datas)):
                    if (datas[i-1] - datas[i]) == timedelta(days=1): streak += 1
                    else: break
        txt_ofensiva.value = f"🔥 {streak} dias consecutivos"

        # Progresso (%)
        cur.execute("SELECT COUNT(*) FROM tarefas_vocais")
        total_tarefas = cur.fetchone()[0]
        
        def pct_do_dia(dia_date):
            if total_tarefas == 0: return 0.0
            dia_str = dia_date.strftime("%Y-%m-%d")
            cur.execute("SELECT COUNT(*) FROM checks_vocais WHERE data = %s", (dia_str,))
            feitos = cur.fetchone()[0]
            return (feitos / total_tarefas) * 100.0

        hoje_date = obter_agora_br().date()
        
        cur.execute("SELECT MIN(data) FROM acessos_vocais")
        min_data_str = cur.fetchone()[0]
        data_inicio = datetime.strptime(min_data_str, "%Y-%m-%d").date() if min_data_str else hoje_date

        pct_diario = pct_do_dia(hoje_date)
        
        soma_semana, cont_semana = 0.0, 0
        for d in range(7):
            dia = hoje_date - timedelta(days=d)
            if dia < data_inicio: break
            soma_semana += pct_do_dia(dia)
            cont_semana += 1
        pct_semanal = (soma_semana / cont_semana) if cont_semana else pct_diario

        soma_mes, cont_mes = 0.0, 0
        for d in range(30):
            dia = hoje_date - timedelta(days=d)
            if dia < data_inicio: break
            soma_mes += pct_do_dia(dia)
            cont_mes += 1
        pct_mensal = (soma_mes / cont_mes) if cont_mes else pct_diario

        con.close()
        
        linha_graficos.controls.clear()
        linha_graficos.controls.extend([
            criar_card_pizza("Hoje", pct_diario),
            criar_card_pizza("Semana", pct_semanal),
            criar_card_pizza("Mês", pct_mensal)
        ])
        linha_graficos.update()
        
    # -----------------------------------------------------------------------
    # ABA 1: ROTINA VOCAL
    # -----------------------------------------------------------------------
    conteudo_rotina = ft.Column(horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20)

    NomesFases = {
        1: "FASE 1: O POCKET ROUTINE",
        2: "FASE 2: O RITUAL DE IGNIÇÃO",
        3: "FASE 3: LAPIDAÇÃO FONÈTICA",
        4: "FASE 4: EMPILHAMENTO MÁXIMO"
    }

    def alternar_check(e, id_tarefa, container):
        marcado = e.control.value
        container.bgcolor = ft.Colors.GREEN_900 if marcado else ft.Colors.GREY_900
        container.border = ft.Border.all(1, ft.Colors.GREEN_700 if marcado else ft.Colors.GREY_800)
        container.update()

        def trabalho():
            con = conectar_banco()
            cur = con.cursor()
            if marcado:
                cur.execute("INSERT INTO checks_vocais (tarefa_id, data) VALUES (%s, %s) ON CONFLICT DO NOTHING", (id_tarefa, data_hoje))
            else:
                cur.execute("DELETE FROM checks_vocais WHERE tarefa_id = %s AND data = %s", (id_tarefa, data_hoje))
            con.commit()
            con.close()
            calcular_gamificacao()
            page.update()
        threading.Thread(target=trabalho, daemon=True).start()

    def deletar_tarefa(id_tarefa):
        con = conectar_banco()
        cur = con.cursor()
        cur.execute("DELETE FROM tarefas_vocais WHERE id = %s", (id_tarefa,))
        cur.execute("DELETE FROM checks_vocais WHERE tarefa_id = %s", (id_tarefa,))
        con.commit()
        con.close()
        carregar_ui_rotina()

    def salvar_edicao_criacao(id_tarefa, fase, n, pq, cf, ex, dlg):
        con = conectar_banco()
        cur = con.cursor()
        if id_tarefa == 0: # Nova
            cur.execute("INSERT INTO tarefas_vocais (fase, nome, para_que, como_fazer, exercicio) VALUES (%s, %s, %s, %s, %s)", (fase, n, pq, cf, ex))
        else: # Edição
            cur.execute("UPDATE tarefas_vocais SET nome=%s, para_que=%s, como_fazer=%s, exercicio=%s WHERE id=%s", (n, pq, cf, ex, id_tarefa))
        con.commit()
        con.close()
        
        # Fecha a janela de forma compatível com a nova versão do Flet
        if hasattr(page, "close"):
            page.close(dlg)
        else:
            dlg.open = False
            page.update()
            
        carregar_ui_rotina()

    def abrir_modal_tarefa(id_tarefa, fase, n="", pq="", cf="", ex=""):
        titulo = "Editar Tarefa" if id_tarefa > 0 else f"Nova Tarefa - Fase {fase}"
        
        c_nome = ft.TextField(label="Nome / Título", value=n, width=300)
        c_pq = ft.TextField(label="Para que serve?", value=pq, multiline=True, min_lines=2, width=300)
        c_cf = ft.TextField(label="Como fazer?", value=cf, multiline=True, min_lines=2, width=300)
        c_ex = ft.TextField(label="Exercício / Texto", value=ex, multiline=True, min_lines=3, width=300)
        
        dlg = ft.AlertDialog(
            title=ft.Text(titulo),
            content=ft.Column([c_nome, c_pq, c_cf, c_ex], tight=True, scroll=ft.ScrollMode.AUTO)
        )
        
        def fechar_dlg(e):
            if hasattr(page, "close"):
                page.close(dlg)
            else:
                dlg.open = False
                page.update()

        dlg.actions = [
            ft.TextButton("Cancelar", on_click=fechar_dlg),
            ft.FilledButton("Salvar", on_click=lambda e: salvar_edicao_criacao(id_tarefa, fase, c_nome.value, c_pq.value, c_cf.value, c_ex.value, dlg), bgcolor=ft.Colors.GREEN_700)
        ]
        
        # Abre a janela testando a versão do Flet para nunca falhar
        if hasattr(page, "open"):
            page.open(dlg)
        else:
            page.dialog = dlg
            dlg.open = True
            page.update()

    def criar_card_tarefa(id_tarefa, nome, para_que, como_fazer, exercicio, ja_feito, fase):
        container = ft.Container(
            padding=12, border_radius=12, width=360,
            bgcolor=ft.Colors.GREEN_900 if ja_feito else ft.Colors.GREY_900,
            border=ft.Border.all(1, ft.Colors.GREEN_700 if ja_feito else ft.Colors.GREY_800)
        )
        
        chk = ft.Checkbox(value=ja_feito, fill_color=ft.Colors.GREEN_600, on_change=lambda e: alternar_check(e, id_tarefa, container))
        
        btn_edit = ft.IconButton(icon=ft.Icons.EDIT_OUTLINED, icon_color=ft.Colors.BLUE_400, icon_size=18, padding=0, width=32, height=32, on_click=lambda e: abrir_modal_tarefa(id_tarefa, fase, nome, para_que, como_fazer, exercicio))
        btn_del = ft.IconButton(icon=ft.Icons.DELETE_OUTLINE, icon_color=ft.Colors.RED_400, icon_size=18, padding=0, width=32, height=32, on_click=lambda e: deletar_tarefa(id_tarefa))
        
        linha_topo = ft.Row([
            ft.Row([chk, ft.Text(nome, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, expand=True)], spacing=0, expand=True),
            ft.Row([btn_edit, btn_del], spacing=0, tight=True)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        
        col_textos = ft.Column([
            linha_topo,
            ft.Container(height=4),
            ft.Text(f"🎯 Para quê: {para_que}", size=16, color=ft.Colors.BLUE_200, italic=True) if para_que else ft.Container(),
            ft.Container(height=14),
            ft.Text(f"🛠️ Como fazer: {como_fazer}", size=16, color=ft.Colors.GREY_400) if como_fazer else ft.Container(),
            ft.Container(height=14),
            ft.Container(
                content=ft.Text(exercicio, size=17, weight=ft.FontWeight.W_500, color=ft.Colors.WHITE),
                bgcolor=ft.Colors.BLACK45, padding=12, border_radius=8
            )
        ], spacing=2)

        container.content = col_textos
        return container

    def carregar_ui_rotina():
        conteudo_rotina.controls.clear()
        
        con = conectar_banco()
        cur = con.cursor()
        
        # Busca checks de hoje
        cur.execute("SELECT tarefa_id FROM checks_vocais WHERE data = %s", (data_hoje,))
        feitos = set(r[0] for r in cur.fetchall())
        
        # Busca tarefas ordenadas por fase
        cur.execute("SELECT id, fase, nome, para_que, como_fazer, exercicio FROM tarefas_vocais ORDER BY fase, id")
        tarefas = cur.fetchall()
        con.close()

        # Agrupa por fase
        fases_dict = {1: [], 2: [], 3: [], 4: []}
        for t in tarefas:
            fases_dict[t[1]].append(t)
            
        for fase_num, lista in fases_dict.items():
            titulo_fase = ft.Text(NomesFases[fase_num], size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_ACCENT, text_align=ft.TextAlign.CENTER)
            conteudo_rotina.controls.append(titulo_fase)
            
            for (id_tarefa, f, nome, pq, cf, ex) in lista:
                card = criar_card_tarefa(id_tarefa, nome, pq, cf, ex, (id_tarefa in feitos), f)
                conteudo_rotina.controls.append(card)
                
            # Botão de adicionar específico para o final do bloco
            btn_add = ft.FilledButton(
                f"+ Adicionar na Fase {fase_num}", 
                icon=ft.Icons.ADD, bgcolor=ft.Colors.GREY_800, color=ft.Colors.WHITE, width=360,
                on_click=lambda e, f=fase_num: abrir_modal_tarefa(0, f)
            )
            conteudo_rotina.controls.append(btn_add)
            conteudo_rotina.controls.append(ft.Divider(height=25, thickness=2, color=ft.Colors.GREY_800))
            
        calcular_gamificacao()
        page.update()

    # -----------------------------------------------------------------------
    # NAVEGAÇÃO E INICIALIZAÇÃO
    # -----------------------------------------------------------------------
    conteudo_metas.controls.extend([
        ft.Text("Central de Metas", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
        ft.Container(height=10),
        linha_graficos,
        ft.Container(height=20),
        ft.Text("Complete todos os exercícios da aba Treino para fechar os anéis!", color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER)
    ])

    def aba_treino(e):
        btn_treino.bgcolor = ft.Colors.GREEN_700
        btn_metas.bgcolor = ft.Colors.GREY_800
        conteudo_rotina.visible = True
        conteudo_metas.visible = False
        page.update()

    def aba_metas(e):
        btn_treino.bgcolor = ft.Colors.GREY_800
        btn_metas.bgcolor = ft.Colors.GREEN_700
        conteudo_rotina.visible = False
        conteudo_metas.visible = True
        calcular_gamificacao()
        page.update()

    btn_treino = ft.FilledButton("📋 Meu Treino", bgcolor=ft.Colors.GREEN_700, on_click=aba_treino, width=150)
    btn_metas = ft.FilledButton("🎯 Metas", bgcolor=ft.Colors.GREY_800, on_click=aba_metas, width=150)
    linha_abas = ft.Row([btn_treino, btn_metas], alignment=ft.MainAxisAlignment.CENTER, spacing=20)

    # Montagem Final da Tela
    page.add(
        cabecalho,
        ft.Divider(height=20),
        linha_abas,
        ft.Container(height=10),
        conteudo_rotina,
        conteudo_metas
    )
    
    carregar_ui_rotina()

porta_nuvem = int(os.environ.get("PORT", 8080))
ft.app(target=main, view=ft.AppView.WEB_BROWSER, host="0.0.0.0", port=porta_nuvem)