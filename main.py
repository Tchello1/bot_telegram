#Marcelo Lopes da Silva
import json
from collections import Counter
from relatorio_vendas import gerar_relatorio
from bot import bot
import threading
from disparo_email import enviar_email_promocional


pratos = []
bebidas = []

clientes =[]
pedidos = []




def ler_json_clientes_pedidos(nome_json):
    try:
        # Tenta carregar os dados existentes do arquivo
        with open(nome_json, 'r') as arquivo:
            dados_clientes_pedidos = json.load(arquivo)
    except FileNotFoundError:
        dados_clientes_pedidos = []

    return dados_clientes_pedidos


def listar_pedidos():
    print("\n" + "=" * 40)
    print("|||        PEDIDOS ATUAIS        |||")
    print("=" * 40)

    pedidos = ler_json_clientes_pedidos('pedidos.json')

    if not pedidos:
        print("\033[91m❌ Nenhum pedido registrado.\033[0m")
        return

    # Perguntar ao usuário se deseja filtrar pedidos não entregues
    filtro = input("Deseja ver apenas pedidos não entregues? (S/N): ").strip().lower()
    if filtro == 's':
        pedidos = [pedido for pedido in pedidos if pedido['status_pedido'] != "entregue"]

    if not pedidos:
        print("\033[91m❌ Nenhum pedido encontrado com esse filtro.\033[0m")
        return

    print("\n📌 \033[94mPedidos Registrados:\033[0m")
    print("-" * 40)

    for pedido in pedidos:
        print(f"🔹 \033[92mID Pedido:\033[0m {pedido['id_pedido']} | "
              f"\033[92mID Cliente:\033[0m {pedido['id_cliente']} | "
              f"\033[93mStatus:\033[0m {pedido['status_pedido']} | "
              f"\033[94mTempo Total:\033[0m {pedido['tempo_total_pedido']} min | "
              f"\033[92mValor Total:\033[0m R$ {pedido['valor_total_pedido']:.2f} | "
              f"\033[96mData do Pedido:\033[0m {pedido['data_pedido']}")

        if 'metodo_pagamento' in pedido:
            print(f"   💳 \033[94mMétodo de Pagamento:\033[0m {pedido['metodo_pagamento']}")

        if 'endereco_entrega' in pedido:
            print(f"   🏠 \033[94mEndereço de Entrega:\033[0m {pedido['endereco_entrega']}")

        if 'observacoes_cliente' in pedido:
            print(f"   📝 \033[94mObservações do Cliente:\033[0m {pedido['observacoes_cliente']}")

        print("   📦 \033[94mItens do Pedido:\033[0m")
        for item in pedido['itens_pedido']:
            if 'id_prato' in item:
                prato = next((p for p in pratos if int(p['id_prato']) == int(item['id_prato'])), None)
                if prato:
                    print(f"     🍽️ {prato['nome_prato']} (ID: {item['id_prato']}) | Quantidade: {item['quantidade']} | Preço: R$ {prato['preco_prato']:.2f}")
                else:
                    print(f"     ❌ Prato ID {item['id_prato']} não encontrado")
            elif 'id_bebida' in item:
                bebida = next((b for b in bebidas if int(b['id_bebida']) == int(item['id_bebida'])), None)
                if bebida:
                    print(f"     🥤 {bebida['nome_bebida']} (ID: {item['id_bebida']}) | Quantidade: {item['quantidade']} | Preço: R$ {bebida['preco_bebida']:.2f}")
                else:
                    print(f"     ❌ Bebida ID {item['id_bebida']} não encontrada")

        print("-" * 40)

    print("=" * 40)
    pedidos = ler_json_clientes_pedidos('pedidos.json')
    # Atualizar status do pedido
    try:
        id_atualizar = int(input("\nDigite o ID do pedido para atualizar o status (ou 0 para sair): "))
        if id_atualizar == 0:
            return

        pedido_encontrado = next((p for p in pedidos if p['id_pedido'] == id_atualizar), None)

        if pedido_encontrado:
            print("\nEscolha o novo status:")
            print("1 - Em preparo")
            print("2 - Pronto")
            print("3 - Entregue")

            opcao = input("Digite o número correspondente ao novo status: ").strip()

            status_map = {
                "1": "em preparo",
                "2": "pronto",
                "3": "entregue"
            }

            if opcao in status_map:
                # Atualiza o status apenas do pedido encontrado
                pedido_encontrado['status_pedido'] = status_map[opcao]
                #print(pedidos)
                # Aqui estamos salvando apenas a alteração no arquivo
                salvar_json_clientes_pedidos('pedidos.json', pedidos)  # Salva as alterações no arquivo JSON
                print("\033[92m✅ Status atualizado com sucesso!\033[0m")
            else:
                print("\033[91m❌ Opção inválida. Status não atualizado.\033[0m")
        else:
            print("\033[91m❌ Pedido não encontrado.\033[0m")

    except ValueError:
        print("\033[91m❌ Entrada inválida. Digite um número válido.\033[0m")





def salvar_json_clientes_pedidos(nome_json,pedidos):
    with open(nome_json, 'w') as arquivo:
        json.dump(pedidos, arquivo, indent=4)
    '''
    with open('bebidas.json', 'w') as arquivo:
        json.dump(bebidas, arquivo, indent=4)
     '''


def listar_clientes():
    print("\n" + "=" * 40)
    print("|||        CLIENTES ATUAIS        |||")
    print("=" * 40)

    clientes = ler_json_clientes_pedidos('clientes.json')

    if clientes:
        print("\n📌 \033[94mClientes Cadastrados:\033[0m")
        print("-" * 40)
        for cliente in clientes:
            print(f"🔹 \033[92mID:\033[0m {cliente['id_usuario']} | "
                  f"\033[93mNome:\033[0m {cliente['nome_cliente']} | "
                  f"\033[91mEmail:\033[0m {cliente['email']} | "
                  f"\033[96mCPF:\033[0m {cliente['cpf']} | "
                  f"\033[95mEndereço:\033[0m {cliente['endereco_entrega']} | "
                  f"\033[95mQuantidade de pedidos:\033[0m {cliente['quantidade_pedidos']} | "
                  f"\033[94mTelefone:\033[0m {cliente['telefone']}")
            print("-" * 40)
    else:
        print("\033[91m❌ Nenhum cliente cadastrado.\033[0m")

    print("=" * 40)

    return clientes


def ler_json():
    try:
        # Tenta carregar os dados existentes do arquivo
        with open('pratos.json', 'r') as arquivo:
            dados_pratos = json.load(arquivo)
    except FileNotFoundError:
        dados_pratos = []

    #dados_pratos.extend(pratos)  # aqui ele "tira a lista" e adiciona o dic a niva lista

    try:
        # Tenta carregar os dados existentes do arquivo
        with open('bebidas.json', 'r') as arquivo:
            dados_bebidas = json.load(arquivo)
    except FileNotFoundError:
        dados_bebidas = []


    return dados_pratos,dados_bebidas

#teria que colocar uma condicionar em criar_json entao resolvi fazer assim
def salvar_json():
    with open('pratos.json', 'w') as arquivo:
        json.dump(pratos, arquivo, indent=4)

    with open('bebidas.json', 'w') as arquivo:
        json.dump(bebidas, arquivo, indent=4)

    #print("Produtos atualizados com sucesso!")
def criar_json():
    dados_pratos, dados_bebidas = ler_json()

    # Criar um conjunto de IDs existentes para evitar duplicação
    ids_pratos_existentes = {prato['id_prato'] for prato in dados_pratos}
    ids_bebidas_existentes = {bebida['id_bebida'] for bebida in dados_bebidas}

    # Adiciona somente os pratos que ainda não existem
    for prato in pratos:
        if prato['id_prato'] not in ids_pratos_existentes:
            dados_pratos.append(prato)

    # Adiciona somente as bebidas que ainda não existem
    for bebida in bebidas:
        if bebida['id_bebida'] not in ids_bebidas_existentes:
            dados_bebidas.append(bebida)


    with open('pratos.json', 'w') as arquivo:
        json.dump(dados_pratos, arquivo, indent=4)

    with open('bebidas.json', 'w') as arquivo:
        json.dump(dados_bebidas, arquivo, indent=4)

    print("Produtos atualizados com sucesso!")

def cadastrar_produtos():
    dados_pratos, dados_bebidas = ler_json()

    # Encontrar o maior ID de pratos e bebidas
    maior_id_prato = max([prato["id_prato"] for prato in dados_pratos], default=0)
    maior_id_bebida = max([bebida["id_bebida"] for bebida in dados_bebidas], default=0)

    while True:
        print("\n\033[1m---- Informe o produto que quer cadastrar ----\033[0m")
        print("1 - Pratos")
        print("2 - Bebidas")
        print("0 - Sair")
        tipo_produto = input("Digite sua escolha: ")

        if tipo_produto == '1':
            nome_produto = input('Informe o nome do prato: ')
            preco_produto = float(input('Informe o preço do prato: '))
            tempo_preparo_prato = int(input('Informe o tempo de preparo do prato (em minutos): '))
            imagem_prato = input('Informe o caminho da imagem do prato (ex: assets/images/pizza.jpg): ')
            ingredientes_prato = input('Informe os ingredientes do prato (separados por vírgula): ').split(',')

            maior_id_prato += 1  # Garante que cada novo prato tenha um ID único
            prato = {
                'id_prato': maior_id_prato,
                'nome_prato': nome_produto,
                'preco_prato': preco_produto,
                'tempo_preparo_prato': tempo_preparo_prato,
                'imagem_prato': imagem_prato,
                'ingredientes_prato': [ingrediente.strip() for ingrediente in ingredientes_prato]  # Remove espaços extras
            }
            pratos.append(prato)  # Mantendo o uso de 'pratos' como variáveis globais
            print(f"\033[92m✅ Prato '{nome_produto}' cadastrado com sucesso!\033[0m")

        elif tipo_produto == '2':
            nome_produto = input('Informe o nome da bebida: ')
            preco_produto = float(input('Informe o preço da bebida: '))
            tempo_preparo_bebida = int(input('Informe o tempo de preparo da bebida (em minutos): '))
            imagem_bebida = input('Informe o caminho da imagem da bebida (ex: assets/images/suco.jpg): ')
            ingredientes_bebida = input('Informe os ingredientes da bebida (separados por vírgula): ').split(',')

            maior_id_bebida += 1  # Garante que cada nova bebida tenha um ID único
            bebida = {
                'id_bebida': maior_id_bebida,
                'nome_bebida': nome_produto,
                'preco_bebida': preco_produto,
                'tempo_preparo_bebida': tempo_preparo_bebida,
                'imagem_bebida': imagem_bebida,
                'ingredientes_bebida': [ingrediente.strip() for ingrediente in ingredientes_bebida]  # Remove espaços extras
            }
            bebidas.append(bebida)  # Mantendo o uso de 'bebidas' como variáveis globais
            print(f"\033[92m✅ Bebida '{nome_produto}' cadastrada com sucesso!\033[0m")

        elif tipo_produto == '0':
            criar_json()  # Salva os dados antes de sair
            print("\033[94m💾 Dados salvos com sucesso. Saindo...\033[0m")
            break

        else:
            print("\033[91m❌ Opção inválida! Escolha uma opção válida.\033[0m")



def mostrar_pratos_bebidas(dados_pratos, dados_bebidas):
    print("\n" + "=" * 40)
    print("|||        🍽️  CARDÁPIO ATUAL        |||")
    print("=" * 40)

    if dados_pratos:
        print("\n📌 \033[94mPRATOS DISPONÍVEIS:\033[0m")
        print("-" * 40)
        for prato in dados_pratos:
            print(f"🔹 \033[92mID:\033[0m {prato['id_prato']} | "
                  f"\033[93mNome:\033[0m {prato['nome_prato']} | "
                  f"\033[91mPreço:\033[0m R$ {prato['preco_prato']:.2f} | "
                  f"⏱️ \033[95mTempo de preparo:\033[0m {prato['tempo_preparo_prato']} minutos | "
                  f"🖼️ \033[96mImagem:\033[0m {prato['imagem_prato']} | "
                  f"🍽️ \033[94mIngredientes:\033[0m {', '.join(prato['ingredientes_prato'])}")
        print("-" * 40)
    else:
        print("\033[91m❌ Nenhum prato cadastrado.\033[0m")

    if dados_bebidas:
        print("\n🥤 \033[94mBEBIDAS DISPONÍVEIS:\033[0m")
        print("-" * 40)
        for bebida in dados_bebidas:
            print(f"🔹 \033[92mID:\033[0m {bebida['id_bebida']} | "
                  f"\033[93mNome:\033[0m {bebida['nome_bebida']} | "
                  f"\033[91mPreço:\033[0m R$ {bebida['preco_bebida']:.2f} | "
                  f"⏱️ \033[95mTempo de preparo:\033[0m {bebida['tempo_preparo_bebida']} minutos | "
                  f"🖼️ \033[96mImagem:\033[0m {bebida['imagem_bebida']} | "
                  f"🍹 \033[94mIngredientes:\033[0m {', '.join(bebida['ingredientes_bebida'])}")
        print("-" * 40)
    else:
        print("\033[91m❌ Nenhuma bebida cadastrada.\033[0m")

    print("=" * 40)


def deletar_item():
    print("\n" + "=" * 40)
    print("|||        EXCLUIR ITEM        |||")
    print("=" * 40)

    pratos = ler_json_clientes_pedidos('pratos.json')
    bebidas = ler_json_clientes_pedidos('bebidas.json')

    if not pratos and not bebidas:
        print("\033[91m❌ Nenhum item cadastrado para exclusão.\033[0m")
        return

    # Listar pratos
    if pratos:
        print("\n🍽️ \033[94mPRATOS DISPONÍVEIS:\033[0m")
        for prato in pratos:
            print(f"🔹 ID: {prato['id_prato']} | Nome: {prato['nome_prato']} | Preço: R$ {prato['preco_prato']:.2f}")

    # Listar bebidas
    if bebidas:
        print("\n🥤 \033[94mBEBIDAS DISPONÍVEIS:\033[0m")
        for bebida in bebidas:
            print(f"🔹 ID: {bebida['id_bebida']} | Nome: {bebida['nome_bebida']} | Preço: R$ {bebida['preco_bebida']:.2f}")

    print("=" * 40)

    # Pergunta ao usuário o que deseja deletar
    tipo = input("Deseja excluir um PRATO (P) ou uma BEBIDA (B)? ou qualquer outro para cancelar ").strip().lower()

    if tipo not in ['p', 'b']:
        print("\033[91m❌ Opção inválida. Operação cancelada.\033[0m")
        return

    try:
        id_excluir = int(input("Digite o ID do item que deseja excluir: ").strip())
    except ValueError:
        print("\033[91m❌ Entrada inválida. Digite um número válido.\033[0m")
        return

    if tipo == 'p':
        # Filtrar e remover o prato pelo ID
        novo_pratos = [prato for prato in pratos if prato['id_prato'] != id_excluir]
        if len(novo_pratos) == len(pratos):
            print("\033[91m❌ Prato não encontrado.\033[0m")
            return
        salvar_json_clientes_pedidos('pratos.json', novo_pratos)
        print("\033[92m✅ Prato removido com sucesso!\033[0m")

    elif tipo == 'b':
        # Filtrar e remover a bebida pelo ID
        novo_bebidas = [bebida for bebida in bebidas if bebida['id_bebida'] != id_excluir]
        if len(novo_bebidas) == len(bebidas):
            print("\033[91m❌ Bebida não encontrada.\033[0m")
            return
        salvar_json_clientes_pedidos('bebidas.json', novo_bebidas)
        print("\033[92m✅ Bebida removida com sucesso!\033[0m")

    print("=" * 40)

def atualizar_produtos():
    global pratos, bebidas  # Permite modificar as variáveis globais

    pratos, bebidas = ler_json()
    while True:
        print("\n" + "=" * 40)
        print("|||     🔄 ATUALIZAÇÃO DE PRODUTOS     |||")
        print("=" * 40)
        print("\033[94m1 - Atualizar Prato 🍽️\033[0m")
        print("\033[92m2 - Atualizar Bebida 🥤\033[0m")
        print("\033[91m0 - Cancelar ❌\033[0m")
        print("=" * 40)

        opcao_escolhida = input("Informe a opção escolhida: ")

        if opcao_escolhida == '1':
            if not pratos:
                print("\033[91m❌ Nenhum prato cadastrado para atualizar.\033[0m")
                continue

            print("\n📌 \033[94mPRATOS DISPONÍVEIS PARA ATUALIZAÇÃO:\033[0m")
            print("-" * 40)
            for prato in pratos:
                print(f"🔹 \033[92mID:\033[0m {prato['id_prato']} | "
                      f"\033[93mNome:\033[0m {prato['nome_prato']} | "
                      f"\033[91mPreço:\033[0m R$ {prato['preco_prato']:.2f} | "
                      f"⏱️ \033[95mTempo de preparo:\033[0m {prato['tempo_preparo_prato']} minutos | "
                      f"🖼️ \033[96mImagem:\033[0m {prato['imagem_prato']} | "
                      f"🍽️ \033[94mIngredientes:\033[0m {', '.join(prato['ingredientes_prato'])}")
            print("-" * 40)

            id_atualizar = int(input("\nDigite o ID do prato que deseja atualizar: "))

            for prato in pratos:
                if prato['id_prato'] == id_atualizar:
                    novo_nome = input(f"Novo nome (pressione Enter para manter o atual - {prato['nome_prato']}):  ") or \
                                prato['nome_prato']
                    novo_preco = input(
                        f"Novo preço (pressione Enter para manter o atual - {prato['preco_prato']}): ") or prato[
                                     'preco_prato']
                    novo_tempo_preparo = input(
                        f"Novo tempo de preparo (pressione Enter para manter o atual - {prato['tempo_preparo_prato']} minutos): ") or \
                                         prato['tempo_preparo_prato']
                    nova_imagem = input(
                        f"Nova imagem (pressione Enter para manter o atual - {prato['imagem_prato']}): ") or prato[
                                      'imagem_prato']
                    novos_ingredientes = input(
                        f"Novos ingredientes (pressione Enter para manter os atuais - {', '.join(prato['ingredientes_prato'])}): ") or ", ".join(
                        prato['ingredientes_prato'])

                    prato['nome_prato'] = novo_nome
                    prato['preco_prato'] = float(novo_preco)
                    prato['tempo_preparo_prato'] = int(novo_tempo_preparo)
                    prato['imagem_prato'] = nova_imagem
                    prato['ingredientes_prato'] = [ingrediente.strip() for ingrediente in novos_ingredientes.split(',')]

                    print("\033[92m✅ Prato atualizado com sucesso!\033[0m")
                    salvar_json()  # Chama sua função que salva as alterações
                    break
            else:
                print("\033[91m❌ ID não encontrado.\033[0m")

        elif opcao_escolhida == '2':
            if not bebidas:
                print("\033[91m❌ Nenhuma bebida cadastrada para atualizar.\033[0m")
                continue

            print("\n🥤 \033[94mBEBIDAS DISPONÍVEIS PARA ATUALIZAÇÃO:\033[0m")
            print("-" * 40)
            for bebida in bebidas:
                print(f"🔹 \033[92mID:\033[0m {bebida['id_bebida']} | "
                      f"\033[93mNome:\033[0m {bebida['nome_bebida']} | "
                      f"\033[91mPreço:\033[0m R$ {bebida['preco_bebida']:.2f} | "
                      f"⏱️ \033[95mTempo de preparo:\033[0m {bebida['tempo_preparo_bebida']} minutos | "
                      f"🖼️ \033[96mImagem:\033[0m {bebida['imagem_bebida']} | "
                      f"🍹 \033[94mIngredientes:\033[0m {', '.join(bebida['ingredientes_bebida'])}")
            print("-" * 40)

            id_atualizar = int(input("\nDigite o ID da bebida que deseja atualizar: "))

            for bebida in bebidas:
                if bebida['id_bebida'] == id_atualizar:
                    novo_nome = input(f"Novo nome (pressione Enter para manter o atual) {bebida['nome_bebida']} : ") or \
                                bebida['nome_bebida']
                    novo_preco = input(
                        f"Novo preço (pressione Enter para manter o atual) {bebida['preco_bebida']} : ") or bebida[
                                     'preco_bebida']
                    novo_tempo_preparo = input(
                        f"Novo tempo de preparo (pressione Enter para manter o atual - {bebida['tempo_preparo_bebida']} minutos): ") or \
                                         bebida['tempo_preparo_bebida']
                    nova_imagem = input(
                        f"Nova imagem (pressione Enter para manter o atual - {bebida['imagem_bebida']}): ") or bebida[
                                      'imagem_bebida']
                    novos_ingredientes = input(
                        f"Novos ingredientes (pressione Enter para manter os atuais - {', '.join(bebida['ingredientes_bebida'])}): ") or ", ".join(
                        bebida['ingredientes_bebida'])

                    bebida['nome_bebida'] = novo_nome
                    bebida['preco_bebida'] = float(novo_preco)
                    bebida['tempo_preparo_bebida'] = int(novo_tempo_preparo)
                    bebida['imagem_bebida'] = nova_imagem
                    bebida['ingredientes_bebida'] = [ingrediente.strip() for ingrediente in
                                                     novos_ingredientes.split(',')]

                    print("\033[92m✅ Bebida atualizada com sucesso!\033[0m")
                    salvar_json()
                    break
            else:
                print("\033[91m❌ ID não encontrado.\033[0m")

        elif opcao_escolhida == '0':
            print("\033[93m⚠️ Atualização cancelada.\033[0m")
            break

        else:
            print("\033[91m❌ Opção inválida! Escolha uma opção válida.\033[0m")

def menu_disparar_email():
    clientes = ler_json_clientes_pedidos('clientes.json')

    # Escolha a segmentação
    segmento = input("Enviar para todos (1) ou apenas para quem tem mais de 2 pedidos (2)? ")

    if segmento == "1":
        enviar_email_promocional(clientes)
    elif segmento == "2":
        clientes_filtrados = [c for c in clientes if c.get("quantidade_pedidos", 0) > 2]
        enviar_email_promocional(clientes_filtrados)
    else:
        print("Opção inválida.")
def mostrar_menu():
    while True:
        print("\n" + "=" * 40)
        print("|||      🏪 MENU DE GERENCIAMENTO      |||")
        print("=" * 40)
        print("\033[94m1 - Cadastrar Produtos 📝\033[0m")
        print("\033[92m2 - Listar Produtos 📜\033[0m")
        print("\033[92m3 - Atualizar Produtos 🔄\033[0m")
        print("\033[92m4 - Listar Clientes 📜\033[0m")
        print("\033[92m5 - Listar Pedidos 📜\033[0m")
        print("\033[92m6 - Gerar relatório de vendas 📜\033[0m")
        print("\033[92m7 - Deletar um produto do estoque 📜\033[0m")
        print("\033[92m8 - Disparar emails promoções 📜\033[0m")
        print("\033[91m0 - Desligar Sistema ❌\033[0m")
        print("=" * 40)
        escolha_menu = input('Escolha a opção desejada: ')
        if escolha_menu == '1':
            cadastrar_produtos()
        elif escolha_menu == '2':
            pratos,bebidas = ler_json()
            mostrar_pratos_bebidas(pratos,bebidas)
        elif escolha_menu == '3':
            atualizar_produtos()
        elif escolha_menu == '4':
            clientes = listar_clientes()
        elif escolha_menu == '5':
            pedidos = listar_pedidos()
        elif escolha_menu == '6':
            pedidos = ler_json_clientes_pedidos('pedidos.json')
            pratos, bebidas = ler_json()
            gerar_relatorio(pedidos, pratos, bebidas)
        elif escolha_menu == '7':
            deletar_item()
        elif escolha_menu == '8':
            menu_disparar_email()

        elif escolha_menu == '0':
            break

pedidos = ler_json_clientes_pedidos('pedidos.json')
pratos,bebidas = ler_json()
bot_thread = threading.Thread(target=bot, daemon=True)
bot_thread.start()
mostrar_menu()
