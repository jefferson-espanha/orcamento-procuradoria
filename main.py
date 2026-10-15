import os
from nicegui import app, ui

# Libera arquivos estáticos se rodar isoladamente
app.add_static_files('/static', '.')

# Armazenamento em memória organizado por Ano Exercício
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

ANO_ATUAL = ['2026']  # Ponteiro do ano selecionado

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
                    value=ANO_ATUAL[0], 
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

                def abrir_link():
                    url = input_link_dotacao.value
                    if url and url.startswith('http'):
                        ui.open(url, new_tab=True)
                    else:
                        ui.notify('Insira um link válido com http/https', type='warning')

                ui.button('Salvar Link', on_click=salvar_link).classes('bg-blue-800 text-white text-xs')
                ui.button('Acessar Link ↗', on_click=abrir_link).classes('bg-emerald-700 text-white text-xs')

        # Form de Cadastro de Nova Ficha
        with ui.card().classes('w-full p-6 shadow-md rounded-xl border border-gray-200 bg-white my-4'):
            ui.label('Nova Ficha Orçamentária').classes('text-lg font-bold text-gray-800 mb-2')
            
            with ui.column().classes('w-full gap-4'):
                
                # Linha 1: Nº Ficha + Natureza da despesa
                with ui.row().classes('w-full gap-4 flex-col sm:flex-row'):
                    num_ficha = ui.input(label='Nº Ficha:', placeholder='Ex: 102').classes('w-full sm:w-1/3').props('outlined dense')
                    natureza_despesa = ui.input(label='Natureza da despesa:', placeholder='Ex: 3.3.90.30 - Material de Consumo').classes('w-full sm:w-2/3').props('outlined dense')

                # Linha 2: Detalhamento
                descricao = ui.textarea(
                    label='Detalhamento das despesas absorvidas nessa ficha:', 
                    placeholder='Especifique aqui o destino das despesas...'
                ).classes('w-full').props('outlined dense rows=2')

                # Linha 3: Valores Financeiros
                with ui.row().classes('w-full gap-4 flex-col sm:flex-row'):
                    dotacao_inicial = ui.number(label='Dotação Inicial (R$):', placeholder='0.00', value=0.0).classes('w-full sm:w-1/3').props('outlined dense prefix="R$"')
                    gastos = ui.number(label='Despesas/Empenhos (R$):', placeholder='0.00', value=0.0).classes('w-full sm:w-1/3').props('outlined dense prefix="R$"')
                    planejamento_ano_seguinte = ui.number(
                        label=f'Planejamento Orçamentário (Ano Seguinte):', 
                        placeholder='0.00', 
                        value=0.0
                    ).classes('w-full sm:w-1/3').props('outlined dense prefix="R$"')

                # Cadastrar Ficha
                def salvar_ficha():
                    ano = select_ano.value
                    if not num_ficha.value or not natureza_despesa.value:
                        ui.notify('Preencha pelo menos o Nº e a Natureza da despesa!', type='warning')
                        return
                    
                    dot_in = float(dotacao_inicial.value or 0)
                    gastos_val = float(gastos.value or 0)
                    plan_seg = float(planejamento_ano_seguinte.value or 0)
                    saldo_restante = dot_in - gastos_val
                    
                    nova_ficha = {
                        'num': num_ficha.value,
                        'natureza': natureza_despesa.value,
                        'descricao': descricao.value or 'Sem detalhamento',
                        'dot_in_val': dot_in,
                        'gastos_val': gastos_val,
                        'plan_seg_val': plan_seg,
                        'dotacao_inicial': f"R$ {dot_in:,.2f}",
                        'gastos': f"R$ {gastos_val:,.2f}",
                        'saldo_restante': f"R$ {saldo_restante:,.2f}",
                        'planejamento_seguinte': f"R$ {plan_seg:,.2f}"
                    }
                    
                    BANCO_DADOS[ano]['fichas'].append(nova_ficha)
                    atualizar_tabela()
                    
                    # Limpeza dos campos
                    num_ficha.value = ''
                    natureza_despesa.value = ''
                    descricao.value = ''
                    dotacao_inicial.value = 0.0
                    gastos.value = 0.0
                    planejamento_ano_seguinte.value = 0.0
                    
                    ui.notify(f'Ficha cadastrada com sucesso no exercício de {ano}!', type='positive')

                with ui.row().classes('w-full justify-end mt-2'):
                    ui.button('Cadastrar Ficha', icon='add', on_click=salvar_ficha).classes('bg-blue-900 text-white font-bold py-2 px-6 rounded-lg shadow-md')

        # Seção de Tabela de Informações
        with ui.column().classes('w-full mt-4'):
            with ui.row().classes('w-full justify-between items-center mb-2'):
                ui.label('Fichas do Exercício (Duplo clique para Alterar / Excluir)').classes('text-lg font-bold text-gray-800')
            
            colunas = [
                {'name': 'num', 'label': 'Nº Ficha', 'field': 'num', 'align': 'left', 'sortable': True},
                {'name': 'natureza', 'label': 'Natureza da despesa', 'field': 'natureza', 'align': 'left', 'sortable': True},
                {'name': 'descricao', 'label': 'Detalhamento', 'field': 'descricao', 'align': 'left'},
                {'name': 'dotacao_inicial', 'label': 'Dotação Inicial', 'field': 'dotacao_inicial', 'align': 'right'},
                {'name': 'gastos', 'label': 'Despesas / Empenhos', 'field': 'gastos', 'align': 'right'},
                {'name': 'saldo_restante', 'label': 'Saldo Restante', 'field': 'saldo_restante', 'align': 'right'},
                {'name': 'planejamento_seguinte', 'label': 'Plan. Ano Seguinte', 'field': 'planejamento_seguinte', 'align': 'right'},
            ]

            tabela = ui.table(columns=colunas, rows=[], row_key='num').classes('w-full shadow-md rounded-xl border border-gray-100 bg-white cursor-pointer')
            
            # Modal de Alteração / Exclusão por duplo clique
            with ui.dialog() as modal_edicao, ui.card().classes('w-full max-w-lg p-6'):
                ui.label('Editar / Excluir Ficha').classes('text-xl font-bold mb-4 text-gray-800')
                
                edit_num = ui.input('Nº Ficha').classes('w-full').props('outlined dense readonly')
                edit_natureza = ui.input('Natureza da despesa').classes('w-full').props('outlined dense')
                edit_desc = ui.textarea('Detalhamento').classes('w-full').props('outlined dense rows=2')
                edit_dot = ui.number('Dotação Inicial (R$)', format='%.2f').classes('w-full').props('outlined dense prefix="R$"')
                edit_gastos = ui.number('Despesas (R$)', format='%.2f').classes('w-full').props('outlined dense prefix="R$"')
                edit_plan = ui.number('Planejamento Ano Seguinte (R$)', format='%.2f').classes('w-full').props('outlined dense prefix="R$"')
                
                ficha_selecionada = {}

                def salvar_edicao():
                    ano = select_ano.value
                    dot_in = float(edit_dot.value or 0)
                    gast_val = float(edit_gastos.value or 0)
                    plan_val = float(edit_plan.value or 0)
                    
                    for f in BANCO_DADOS[ano]['fichas']:
                        if f['num'] == edit_num.value:
                            f['natureza'] = edit_natureza.value
                            f['descricao'] = edit_desc.value
                            f['dot_in_val'] = dot_in
                            f['gastos_val'] = gast_val
                            f['plan_seg_val'] = plan_val
                            f['dotacao_inicial'] = f"R$ {dot_in:,.2f}"
                            f['gastos'] = f"R$ {gast_val:,.2f}"
                            f['saldo_restante'] = f"R$ {(dot_in - gast_val):,.2f}"
                            f['planejamento_seguinte'] = f"R$ {plan_val:,.2f}"
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
                edit_natureza.value = row['natureza']
                edit_desc.value = row['descricao']
                edit_dot.value = row.get('dot_in_val', 0.0)
                edit_gastos.value = row.get('gastos_val', 0.0)
                edit_plan.value = row.get('plan_seg_val', 0.0)
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

    # Inicializa o carregamento do ano padrão
    carregar_dados_ano(select_ano.value)

    # Rodapé
    with ui.footer().classes('bg-gray-100 text-gray-600 p-4 text-center text-sm border-t mt-12'):
        ui.label('Prefeitura Municipal de Francisco Morato — Procuradoria do Município © 2026')

if __name__ in {"__main__", "__mp_main__"}:
    PORT = int(os.environ.get('PORT', 8080))
    ui.run(host='0.0.0.0', port=PORT, reload=False)
