from datetime import datetime, timedelta
import json
from disparo_email import enviar_relatorio


def filtrar_pedidos_por_data(pedidos, dias):
    # Define a data limite para os últimos 'dias' dias
    data_limite = datetime.now() - timedelta(days=dias)

    pedidos_filtrados = []

    for pedido in pedidos:
        try:
            # Tenta converter a data com fração de segundo
            data_pedido = datetime.strptime(pedido['data_pedido'], '%Y-%m-%dT%H:%M:%S.%f')
        except ValueError:
            # Se falhar, tenta converter a data sem fração de segundo
            data_pedido = datetime.strptime(pedido['data_pedido'], '%Y-%m-%dT%H:%M:%S')

        # Adiciona o pedido se for dentro do intervalo de tempo
        if data_pedido >= data_limite:
            pedidos_filtrados.append(pedido)

    return pedidos_filtrados


def gerar_relatorio(pedidos, pratos, bebidas, dias=15):
    # Filtra os pedidos dos últimos 'dias' dias
    pedidos = filtrar_pedidos_por_data(pedidos, dias)

    # Relatório 1: Valor Total de Vendas
    valor_total_vendas = 0
    for pedido in pedidos:
        for item in pedido['itens_pedido']:
            if 'id_prato' in item:
                prato = next((p for p in pratos if p['id_prato'] == item['id_prato']), None)
                if prato:
                    valor_total_vendas += prato['preco_prato'] * item['quantidade']
            elif 'id_bebida' in item:
                bebida = next((b for b in bebidas if b['id_bebida'] == item['id_bebida']), None)
                if bebida:
                    valor_total_vendas += bebida['preco_bebida'] * item['quantidade']

    # Relatório 2: Vendas por Produto
    vendas_por_produto = {}
    for pedido in pedidos:
        for item in pedido['itens_pedido']:
            if 'id_prato' in item:
                prato = next((p for p in pratos if p['id_prato'] == item['id_prato']), None)
                if prato:
                    vendas_por_produto[prato['nome_prato']] = vendas_por_produto.get(prato['nome_prato'], 0) + prato[
                        'preco_prato'] * item['quantidade']
            elif 'id_bebida' in item:
                bebida = next((b for b in bebidas if b['id_bebida'] == item['id_bebida']), None)
                if bebida:
                    vendas_por_produto[bebida['nome_bebida']] = vendas_por_produto.get(bebida['nome_bebida'], 0) + \
                                                                bebida['preco_bebida'] * item['quantidade']

    # Relatório 4: Vendas por Cliente
    vendas_por_cliente = {}
    for pedido in pedidos:
        cliente_id = pedido['id_cliente']
        total_cliente = 0
        for item in pedido['itens_pedido']:
            if 'id_prato' in item:
                prato = next((p for p in pratos if p['id_prato'] == item['id_prato']), None)
                if prato:
                    total_cliente += prato['preco_prato'] * item['quantidade']
            elif 'id_bebida' in item:
                bebida = next((b for b in bebidas if b['id_bebida'] == item['id_bebida']), None)
                if bebida:
                    total_cliente += bebida['preco_bebida'] * item['quantidade']
        vendas_por_cliente[cliente_id] = vendas_por_cliente.get(cliente_id, 0) + total_cliente

    # Relatório 6: Média de Itens por Pedido
    total_itens = 0
    total_pedidos = len(pedidos)
    for pedido in pedidos:
        for item in pedido['itens_pedido']:
            total_itens += item['quantidade']

    media_itens_por_pedido = total_itens / total_pedidos if total_pedidos else 0

    # Relatório 7: Média das Avaliações
    total_avaliacoes = 0
    count_avaliacoes = 0
    quantidade_avaliacoes = 0  # Para contar quantas avaliações válidas foram feitas
    for pedido in pedidos:
        if 'avaliacao_pedido' in pedido:
            avaliacao = pedido['avaliacao_pedido']
            if isinstance(avaliacao, (int, float)):  # Verifica se é número
                total_avaliacoes += avaliacao
                count_avaliacoes += 1
                quantidade_avaliacoes += 1  # Conta as avaliações válidas
            elif avaliacao.isdigit():  # Caso a avaliação seja uma string numérica
                total_avaliacoes += int(avaliacao)
                count_avaliacoes += 1
                quantidade_avaliacoes += 1  # Conta as avaliações válidas

    media_avaliacoes = total_avaliacoes / count_avaliacoes if count_avaliacoes else 0

    # Criar o dicionário com os relatórios
    relatorio = {
        "valor_total_vendas": valor_total_vendas,
        "vendas_por_produto": vendas_por_produto,
        "vendas_por_cliente": vendas_por_cliente,
        "media_itens_por_pedido": media_itens_por_pedido,
        "media_avaliacoes": media_avaliacoes,
        "quantidade_avaliacoes": quantidade_avaliacoes  # Adicionando a quantidade de avaliações válidas
    }

    # Gravar o relatório em um arquivo JSON
    with open("relatorio_vendas.json", "w") as file:
        json.dump(relatorio, file, indent=4)

    # Exibindo relatórios no console
    print("\nRelatório de Vendas (últimos 15 dias)")
    print("=" * 40)
    print(f"1. Valor Total de Vendas: R$ {valor_total_vendas:.2f}")
    print("2. Vendas por Produto:")
    for produto, valor in vendas_por_produto.items():
        print(f"   - {produto}: R$ {valor:.2f}")
    print("3. Vendas por Cliente:")
    for cliente, total in vendas_por_cliente.items():
        print(f"   - Cliente ID {cliente}: R$ {total:.2f}")
    print(f"4. Média de Itens por Pedido: {media_itens_por_pedido:.2f}")
    print(f"5. Média das Avaliações: {media_avaliacoes:.2f}")
    print(f"6. Quantidade de Avaliações Feitas: {quantidade_avaliacoes}")
    print("=" * 40)

    # Chamar a função de envio de email, caso necessário
    escolha = input("Deseja enviar o relatorio para o email? 1 - sim | 0 - Não: ")
    if escolha == '1':
        enviar_relatorio(relatorio)  # Descomente essa linha se tiver uma função de disparo
    elif escolha == '0':
        return




