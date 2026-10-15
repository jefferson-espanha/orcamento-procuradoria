import os
import re
from nicegui import app, ui

# Libera arquivos estáticos
app.add_static_files('/static', '.')

# Estrutura de dados em memória por Ano Exercício
BANCO_DADOS = {
    '2026': {
        'link_dotacao': 'https://www.franciscomorato.sp.gov.br/orcamento-2026',
        'fichas': []
    },
    '2025': {
        'link_dotacao': '',
        'fichas': []
    }
}

# Converte qualquer texto de moeda ou número para float de forma precisa
def moeda_para_float(texto):
    if isinstance(texto, (int, float)):
        return float(texto)
    digitos = re.sub(r'\D', '', str(texto or ''))
    if not digitos:
        return 0.0
    return int(digitos) / 100.0

# Formata float puro para R$ X.XXX,XX
def float_para_moeda(valor_float):
    return f"R$ {valor_float:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

# Formatação em tempo real estilo calculadora ao digitar
def formatar_moeda_calculadora(valor_str):
    val_float = moeda_para_float(valor_str)
    return float_para_moeda(val_float)

@ui.page('/')
def orcamento_page():
    ui.colors(primary='#1e3a8a')

    # Cabeçalho da Página
    with ui.header().classes('bg-blue-950 text-white p-4 flex justify-between items-center shadow-lg'):
        with ui.row().classes('items-center gap-3'):
            ui.icon('account_balance_wallet', size='32px').classes('text-blue-300')
            ui.label('Procuradoria do Município').classes('text-2xl font-bold tracking-wide')
        
        ui.button('Voltar ao Portal', on_click=lambda: ui.open('https://portal-sistemas-procuradoria.onrender.com')).classes('bg-blue-800 text-white text-sm')

    # Container Principal
    with ui.column().classes('w-full p-6 max-w-6xl mx-auto items-center'):
        
        # Título + Seletor de Ano Exercício
        with ui.column().classes('text-center my-2 w-full items-center'):
            ui.label('Módulo de Gestão Orçamentária').classes('text-3xl font-extrabold text-gray-800 mb-1')
            
            with ui.row().classes('items-center gap-4 my-2'):
                ui.label('Ano Exercício:').classes('text-base font-bold text-gray-700')
                select_ano = ui.select(
                    options=['2024', '2025', '2026', '2027'], 
                    value='2026', 
                    on_change=lambda e: carregar_dados_ano(e.value)
                ).classes('w-32').props('outlined dense bg-color=white')

        # Banner de Link Oficial da Dotação
        with ui.card().classes('w-full p-4 shadow-sm border border-blue-200 bg-blue-50/50 rounded-xl my-2 flex-col sm:flex-row items-center justify-between gap-4'):
            with ui.row().classes('items-center gap-2 flex-grow'):
                ui.icon('link', size='24px').classes('text-blue-900')
                input_link_dotacao = ui.input(
                    label='Link Atual da Dotação do Exercício:',
                    placeholder='https://...'
                ).classes('w-full').props('outlined dense bg-color=white')
            
            with ui.row().classes('gap-2'):
                def salvar_link():
                    ano = select_ano.value
                    BANCO_DADOS[ano]['link_dotacao'] = input_link_dotacao.value
                    ui.notify(f'Link da dotação de {ano} atualizado!', type='positive')

                def abrir_link_dotacao():
                    url = input_link_dotacao.value
                    if url and url.startswith('http'):
                        ui.run_javascript(f'window.open("{url}", "_blank");')
                    else:
                        ui.notify('Insira um link válido com http/https', type='warning')

                ui.button('Salvar Link', on_click=salvar_link).classes('bg-blue-800 text-white text-xs')
                ui.button('Acessar Link ↗', on_click=abrir_link_dotacao).classes('bg-emerald-700 text-white text-xs')

        # Form de Cadastro de Nova Ficha
        with ui.card().classes('w-full p-6 shadow-md rounded-xl border border-gray-200 bg-white my-4'):
            ui.label('Nova Ficha Orçamentária').classes('text-lg font-bold text-gray-800 mb-2')
            
            with ui.column().classes('w-full gap-4'):
                
                # Linha 1: Nº Ficha + Ação + Natureza da despesa
                with ui.row().classes('w-full gap-4 flex-col sm:flex-row'):
                    num_ficha = ui.input(label='Nº Ficha:', placeholder='Ex: 102').classes('w-full sm:w-1/4').props('outlined dense')
                    acao_ficha = ui.input(label='Ação:', placeholder='Ex: 2002').classes('w-full sm:w-1/4').props('outlined dense')
                    natureza_despesa = ui.input(label='Natureza da despesa:', placeholder='Ex: 3.3.90.30 - Material de Consumo').classes('w-full sm:w-2/4').props('outlined dense')

                # Linha 2: Detalhamento com Auto-Ajuste (autosize)
                descricao = ui.textarea(
                    label='Detalhamento das despesas absorvidas nessa ficha:', 
                    placeholder='Especifique aqui o destino das despesas...'
                ).classes('w-full').props('outlined dense autogrow rows=1')

                # Linha 3: Valores Financeiros e Link do Planejamento
                with ui.row().classes('w-full gap-4 flex-col sm:flex-row'):
                    dotacao_inicial = ui.input(label='Dotação Inicial:', value='R$ 0,00').classes('w-full sm:w-1/3').props('outlined dense')
                    gastos = ui.input(label='Despesas/Empenhos:', value='R$ 0,00').classes('w-full sm:w-1/3').props('outlined dense')
                    link_planejamento = ui.input(label='Link Planejamento Orçamentário (Ano Seguinte):', placeholder='https://...').classes('w-full sm:w-1/3').props('outlined dense')

                # Máscara em tempo real estilo calculadora
                def aplicar_mascara_dotacao(e):
                    dotacao_inicial.value = formatar_moeda_calculadora(e.args)

                def aplicar_mascara_gastos(e):
                    gastos.value = formatar_moeda_calculadora(e.args)

                dotacao_inicial.on('update:model-value', aplicar_mascara_dotacao)
                gastos.on('update:model-value', aplicar_mascara_gastos)

                # Cadastrar Ficha
                def salvar_ficha():
                    ano = select_ano.value
                    if not num_ficha.value or not natureza_despesa.value:
                        ui.notify('Preencha pelo menos o Nº e a Natureza da despesa!', type='warning')
                        return
                    
                    dot_in = moeda_para_float(dotacao_inicial.value)
                    gastos_val = moeda_para_float(gastos.value)
                    saldo_restante = dot_in - gastos_val
                    
                    nova_ficha = {
                        'num': num_ficha.value,
                        'acao': acao_ficha.value or '-',
                        'natureza': natureza_despesa.value,
                        'descricao': descricao.value or 'Sem detalhamento',
                        'dot_in_val': dot_in,
                        'gastos_val': gastos_val,
                        'saldo_restante_val': saldo_restante,
                        'dot_in_txt': float_para_moeda(dot_in),
                        'gastos_txt': float_para_moeda(gastos_val),
                        'saldo_restante_txt': float_para_moeda(saldo_restante),
                        'link_plan': link_planejamento.value or ''
                    }
                    
                    BANCO_DADOS[ano]['fichas'].append(nova_ficha)
                    atualizar_tabela()
                    
                    # Limpeza dos campos
                    num_ficha.value = ''
                    acao_ficha.value = ''
                    natureza_despesa.value = ''
                    descricao.value = ''
                    dotacao_inicial.value = 'R$ 0,00'
                    gastos.value = 'R$ 0,00'
                    link_planejamento.value = ''
                    
                    ui.notify(f'Ficha cadastrada com sucesso no exercício de {ano}!', type='positive')

                with ui.row().classes('w-full justify-end mt-2'):
                    ui.button('Cadastrar Ficha', icon='add', on_click=salvar_ficha).classes('bg-blue-900 text-white font-bold py-2 px-6 rounded-lg shadow-md')

        # Seção de Tabela de Informações
        with ui.column().classes('w-full mt-4'):
            with ui.row().classes('w-full justify-between items-center mb-2'):
                ui.label('Fichas do Exercício (Duplo clique para Alterar / Excluir)').classes('text-lg font-bold text-gray-800')
                ui.button('Gerar Relatório PDF 🖨️', on_click=lambda: gerar_pdf_relatorio(select_ano.value)).classes('bg-emerald-800 text-white text-xs font-bold py-2 px-4 rounded-lg shadow-sm')

            colunas = [
                {'name': 'num', 'label': 'Nº Ficha', 'field': 'num', 'align': 'left', 'sortable': True},
                {'name': 'acao', 'label': 'Ação', 'field': 'acao', 'align': 'left', 'sortable': True},
                {'name': 'natureza', 'label': 'Natureza da despesa', 'field': 'natureza', 'align': 'left', 'sortable': True},
                {'name': 'descricao', 'label': 'Detalhamento', 'field': 'descricao', 'align': 'left'},
                {'name': 'dot_in_txt', 'label': 'Dotação Inicial', 'field': 'dot_in_txt', 'align': 'right'},
                {'name': 'gastos_txt', 'label': 'Despesas / Empenhos', 'field': 'gastos_txt', 'align': 'right'},
                {'name': 'saldo_restante_txt', 'label': 'Saldo Restante', 'field': 'saldo_restante_txt', 'align': 'right'},
                {'name': 'link_plan', 'label': 'Link Plan. Ano Seguinte', 'field': 'link_plan', 'align': 'center'},
            ]

            tabela = ui.table(columns=colunas, rows=[], row_key='num').classes('w-full shadow-md rounded-xl border border-gray-100 bg-white cursor-pointer')
            
            # Formatação da coluna de link do planejamento na tabela
            tabela.add_slot('body-cell-link_plan', '''
                <q-td :props="props">
                    <a v-if="props.value" :href="props.value" target="_blank" class="text-blue-700 font-bold underline">Acessar Plan. ↗</a>
                    <span v-else class="text-gray-400">-</span>
                </q-td>
            ''')

            # Modal de Alteração / Exclusão por duplo clique
            with ui.dialog() as modal_edicao, ui.card().classes('w-full max-w-lg p-6'):
                ui.label('Editar / Excluir Ficha').classes('text-xl font-bold mb-4 text-gray-800')
                
                edit_num = ui.input('Nº Ficha').classes('w-full').props('outlined dense readonly')
                edit_acao = ui.input('Ação').classes('w-full').props('outlined dense')
                edit_natureza = ui.input('Natureza da despesa').classes('w-full').props('outlined dense')
                edit_desc = ui.textarea('Detalhamento').classes('w-full').props('outlined dense autogrow rows=1')
                edit_dot = ui.input('Dotação Inicial').classes('w-full').props('outlined dense')
                edit_gastos = ui.input('Despesas / Empenhos').classes('w-full').props('outlined dense')
                edit_link_plan = ui.input('Link Plan. Ano Seguinte').classes('w-full').props('outlined dense')

                edit_dot.on('update:model-value', lambda e: setattr(edit_dot, 'value', formatar_moeda_calculadora(e.args)))
                edit_gastos.on('update:model-value', lambda e: setattr(edit_gastos, 'value', formatar_moeda_calculadora(e.args)))

                def salvar_edicao():
                    ano = select_ano.value
                    dot_in = moeda_para_float(edit_dot.value)
                    gast_val = moeda_para_float(edit_gastos.value)
                    saldo_restante = dot_in - gast_val
                    
                    for f in BANCO_DADOS[ano]['fichas']:
                        if f['num'] == edit_num.value:
                            f['acao'] = edit_acao.value or '-'
                            f['natureza'] = edit_natureza.value
                            f['descricao'] = edit_desc.value
                            f['dot_in_val'] = dot_in
                            f['gastos_val'] = gast_val
                            f['saldo_restante_val'] = saldo_restante
                            f['dot_in_txt'] = float_para_moeda(dot_in)
                            f['gastos_txt'] = float_para_moeda(gast_val)
                            f['saldo_restante_txt'] = float_para_moeda(saldo_restante)
                            f['link_plan'] = edit_link_plan.value or ''
                            break
                    
                    atualizar_tabela()
                    modal_edicao.close()
                    ui.notify('Ficha alterada com sucesso!', type='positive')

                def excluir_ficha():
                    ano = select_ano.value
                    BANCO_DADOS[ano]['fichas'] = [f for f in BANCO_DADOS[ano]['fichas'] if f['num'] != edit_num.value]
                    atualizar_tabela()
                    modal_edicao.close()
                    ui.notify('Ficha excluída!', type='negative')

                with ui.row().classes('w-full justify-between mt-4'):
                    ui.button('Excluir Ficha', color='red', on_click=excluir_ficha).classes('text-white')
                    with ui.row().classes('gap-2'):
                        ui.button('Cancelar', on_click=modal_edicao.close).props('flat')
                        ui.button('Salvar Alterações', color='primary', on_click=salvar_edicao)

            # Ação de Duplo Clique na linha da tabela
            def on_row_dblclick(e):
                row = e.args[1]
                edit_num.value = row['num']
                edit_acao.value = row.get('acao', '')
                edit_natureza.value = row['natureza']
                edit_desc.value = row['descricao']
                edit_dot.value = row['dot_in_txt']
                edit_gastos.value = row['gastos_txt']
                edit_link_plan.value = row.get('link_plan', '')
                modal_edicao.open()

            tabela.on('row-dblclick', on_row_dblclick)

    # Funções de Controle de Estado e Troca de Ano
    def carregar_dados_ano(ano):
        if ano not in BANCO_DADOS:
            BANCO_DADOS[ano] = {'link_dotacao': '', 'fichas': []}
        
        input_link_dotacao.value = BANCO_DADOS[ano]['link_dotacao']
        atualizar_tabela()

    def atualizar_tabela():
        ano = select_ano.value
        tabela.rows = BANCO_DADOS[ano]['fichas']
        tabela.update()

    # Inicializa a tela com o ano 2026
    carregar_dados_ano(select_ano.value)

    # Rodapé
    with ui.footer().classes('bg-gray-100 text-gray-600 p-4 text-center text-sm border-t mt-12'):
        ui.label('Prefeitura Municipal de Francisco Morato — Procuradoria do Município © 2026')

# Gerador do Relatório de Impressão / PDF
def gerar_pdf_relatorio(ano):
    fichas = BANCO_DADOS.get(ano, {}).get('fichas', [])
    
    total_dot = sum(f.get('dot_in_val', 0.0) for f in fichas)
    total_gast = sum(f.get('gastos_val', 0.0) for f in fichas)
    total_saldo = total_dot - total_gast
    
    linhas_html = ""
    for f in fichas:
        linhas_html += f"""
        <tr>
            <td>{f.get('num', '-')}</td>
            <td>{f.get('acao', '-')}</td>
            <td>{f.get('natureza', '-')}</td>
            <td>{f.get('descricao', '-')}</td>
            <td style="text-align: right;">{f.get('dot_in_txt', 'R$ 0,00')}</td>
            <td style="text-align: right;">{f.get('gastos_txt', 'R$ 0,00')}</td>
            <td style="text-align: right; font-weight: bold;">{f.get('saldo_restante_txt', 'R$ 0,00')}</td>
        </tr>
        """
        
    html_relatorio = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Relatório Orçamentário {ano} - Procuradoria</title>
        <style>
            body {{ font-family: Arial, sans-serif; padding: 20px; color: #333; }}
            h1 {{ text-align: center; color: #1e3a8a; margin-bottom: 5px; }}
            h3 {{ text-align: center; color: #555; font-weight: normal; margin-top: 0; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 12px; }}
            th, td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
            th {{ background-color: #1e3a8a; color: white; }}
            tr:nth-child(even) {{ background-color: #f9f9f9; }}
            .totais {{ margin-top: 20px; text-align: right; font-size: 14px; font-weight: bold; }}
        </style>
    </head>
    <body onload="window.print()">
        <h1>PREFEITURA MUNICIPAL DE FRANCISCO MORATO</h1>
        <h3>Procuradoria do Município — Relatório de Fichas Orçamentárias ({ano})</h3>
        <hr>
        <table>
            <thead>
                <tr>
                    <th>Nº Ficha</th>
                    <th>Ação</th>
                    <th>Natureza da Despesa</th>
                    <th>Detalhamento</th>
                    <th>Dotação Inicial</th>
                    <th>Despesas / Empenhos</th>
                    <th>Saldo Restante</th>
                </tr>
            </thead>
            <tbody>
                {linhas_html if linhas_html else '<tr><td colspan="7" style="text-align:center;">Nenhuma ficha cadastrada neste exercício.</td></tr>'}
            </tbody>
        </table>
        <div class="totais">
            <p>Total Dotação Inicial: {float_para_moeda(total_dot)}</p>
            <p>Total Despesas / Empenhos: {float_para_moeda(total_gast)}</p>
            <p style="color: #047857; font-size: 16px;">Saldo Restante Total: {float_para_moeda(total_saldo)}</p>
        </div>
    </body>
    </html>
    """
    
    # Abre janela de impressão embutida
    ui.run_javascript(f"""
        var win = window.open("", "_blank");
        win.document.write(`{html_relatorio}`);
        win.document.close();
    """)

if __name__ in {"__main__", "__mp_main__"}:
    PORT = int(os.environ.get('PORT', 8080))
    ui.run(host='0.0.0.0', port=PORT, reload=False)
