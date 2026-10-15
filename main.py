import os
from nicegui import app, ui

# Garante acesso aos arquivos estáticos se rodar este arquivo de forma independente
app.add_static_files('/static', '.')

@ui.page('/orcamento')
def orcamento_page():
    ui.colors(primary='#1e3a8a')

    # Cabeçalho da Página
    with ui.header().classes('bg-blue-950 text-white p-4 flex justify-between items-center shadow-lg'):
        with ui.row().classes('items-center gap-3'):
            ui.icon('account_balance_wallet', size='32px').classes('text-blue-300')
            ui.label('Procuradoria do Município').classes('text-2xl font-bold tracking-wide')
        
        ui.button('Voltar ao Portal', on_click=lambda: ui.open('/')).classes('bg-blue-800 text-white text-sm')

    # Container Principal
    with ui.column().classes('w-full p-6 max-w-6xl mx-auto items-center'):
        
        # Título
        with ui.column().classes('text-center my-4'):
            ui.label('Módulo de Gestão Orçamentária').classes('text-3xl font-extrabold text-gray-800 mb-1')
            ui.label('Cadastre e acompanhe o saldo inicial e disponível das fichas:').classes('text-base text-gray-600')

        # Form do Cadastro de Ficha
        with ui.card().classes('w-full p-6 shadow-md rounded-xl border border-gray-200 bg-white my-4'):
            ui.label('Nova Ficha Orçamentária').classes('text-lg font-bold text-gray-800 mb-2')
            
            with ui.column().classes('w-full gap-4'):
                
                # Linha 1: Nº Ficha + Nome da Ficha
                with ui.row().classes('w-full gap-4 flex-col sm:flex-row'):
                    num_ficha = ui.input(label='Nº Ficha:', placeholder='Ex: 102').classes('w-full sm:w-1/3').props('outlined dense')
                    nome_ficha = ui.input(label='Nome da Ficha:', placeholder='Ex: Material de Escritório').classes('w-full sm:w-2/3').props('outlined dense')

                # Linha 2: Descrição
                descricao = ui.textarea(label='Descrição:', placeholder='Detalhamento da ficha...').classes('w-full').props('outlined dense rows=2')

                # Linha 3: Valores Financeiros
                with ui.row().classes('w-full gap-4 flex-col sm:flex-row'):
                    dotacao_inicial = ui.number(label='Dotação Inicial (R$):', placeholder='0.00', value=0.0).classes('w-full sm:w-1/2').props('outlined dense prefix="R$"')
                    gastos = ui.number(label='Despesas/Empenhos (R$):', placeholder='0.00', value=0.0).classes('w-full sm:w-1/2').props('outlined dense prefix="R$"')

                # Função de Salvar Ficha
                def salvar_ficha():
                    if not num_ficha.value or not nome_ficha.value:
                        ui.notify('Preencha pelo menos o Nº e o Nome da Ficha!', type='warning')
                        return
                    
                    dot_in = float(dotacao_inicial.value or 0)
                    gastos_val = float(gastos.value or 0)
                    saldo_restante = dot_in - gastos_val
                    
                    nova_linha = {
                        'num': num_ficha.value,
                        'nome': nome_ficha.value,
                        'descricao': descricao.value or 'Sem descrição',
                        'dotacao_inicial': f"R$ {dot_in:,.2f}",
                        'gastos': f"R$ {gastos_val:,.2f}",
                        'saldo_restante': f"R$ {saldo_restante:,.2f}",
                    }
                    
                    tabela.add_rows([nova_linha])
                    
                    # Limpeza dos campos
                    num_ficha.value = ''
                    nome_ficha.value = ''
                    descricao.value = ''
                    dotacao_inicial.value = 0.0
                    gastos.value = 0.0
                    
                    ui.notify('Ficha adicionada com sucesso!', type='positive')

                with ui.row().classes('w-full justify-end mt-2'):
                    ui.button('Cadastrar Ficha', icon='add', on_click=salvar_ficha).classes('bg-blue-900 text-white font-bold py-2 px-6 rounded-lg shadow-md')

        # Seção de Informações sobre as Fichas
        with ui.column().classes('w-full mt-6'):
            ui.label('Informações sobre as Fichas').classes('text-xl font-bold text-gray-800 mb-3')
            
            # Tabela de Exibição
            colunas = [
                {'name': 'num', 'label': 'Nº Ficha', 'field': 'num', 'align': 'left', 'sortable': True},
                {'name': 'nome', 'label': 'Nome da Ficha', 'field': 'nome', 'align': 'left', 'sortable': True},
                {'name': 'descricao', 'label': 'Descrição', 'field': 'descricao', 'align': 'left'},
                {'name': 'dotacao_inicial', 'label': 'Dotação Inicial', 'field': 'dotacao_inicial', 'align': 'right', 'sortable': True},
                {'name': 'gastos', 'label': 'Despesas / Empenhos', 'field': 'gastos', 'align': 'right', 'sortable': True},
                {'name': 'saldo_restante', 'label': 'Saldo Restante', 'field': 'saldo_restante', 'align': 'right', 'sortable': True},
            ]

            tabela = ui.table(columns=colunas, rows=[], row_key='num').classes('w-full shadow-md rounded-xl border border-gray-100 bg-white')

# Rodapé
    with ui.footer().classes('bg-gray-100 text-gray-600 p-4 text-center text-sm border-t mt-12'):
        ui.label('Prefeitura Municipal de Francisco Morato — Procuradoria do Município © 2026')

if __name__ in {"__main__", "__mp_main__"}:
    PORT = int(os.environ.get('PORT', 8080))
    ui.run(host='0.0.0.0', port=PORT, reload=False)
