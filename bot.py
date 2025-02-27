import asyncio
import json
import datetime
from datetime import datetime
import re
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram import Update
import json
from datetime import datetime
from disparo_email import enviar_email



async def avaliar(update: Update, context) -> None:
    # Verifica se o usuário está logado
    if not context.user_data.get('logado', False):
        await update.message.reply_text("Você precisa estar logado para avaliar pedidos. Use /login.")
        return

    # Recupera o ID do cliente logado
    id_cliente = context.user_data.get('id_usuario')
    if id_cliente is None:
        await update.message.reply_text("Erro: ID do cliente não encontrado. Faça login novamente.")
        return

    # Carrega os pedidos do arquivo JSON
    pedidos = ler_json_bot('pedidos.json')

    # Filtra os pedidos entregues do cliente
    pedidos_entregues = [pedido for pedido in pedidos if pedido['id_cliente'] == id_cliente and pedido['status_pedido'] == 'entregue']

    #print(f"Pedidos entregues: {pedidos_entregues}")  # Debug
    if not pedidos_entregues:
        await update.message.reply_text("Você não possui pedidos entregues para avaliar.")
        return

    # Exibe os pedidos entregues
    mensagem = "📋 *Pedidos Entregues:*\n\n"
    for pedido in pedidos_entregues:
        data_pedido = pedido['data_pedido']
        data_formatada = datetime.strptime(data_pedido, '%Y-%m-%dT%H:%M:%S.%f').strftime('%d/%m/%Y %H:%M')
        mensagem += f"🆔 *ID do Pedido:* {pedido['id_pedido']}\n"
        mensagem += f"📅 *Data do Pedido:* {data_formatada}\n"
        mensagem += f"📌 *Status do Pedido:* {pedido['status_pedido']}\n"
        mensagem += f"⭐ *Avaliação:* {pedido.get('avaliacao_pedido', 'Não avaliado')}\n\n"

    mensagem += "Digite o ID do pedido que deseja avaliar:"
    await update.message.reply_text(mensagem, parse_mode="Markdown")

    # Define o estado para aguardar o ID do pedido
    context.user_data['estado'] = 'aguardando_id_pedido_avaliar'

async def status(update: Update, context) -> None:
    # Verifica se o usuário está logado
    if not context.user_data.get('logado', False):
        await update.message.reply_text("Você precisa estar logado para verificar o status dos pedidos. Use /login.")
        return

    # Recupera o ID do cliente logado
    id_cliente = context.user_data.get('id_usuario')
    if id_cliente is None:
        await update.message.reply_text("Erro: ID do cliente não encontrado. Faça login novamente.")
        return

    # Carrega os pedidos do arquivo JSON
    pedidos = ler_json_bot('pedidos.json')

    # Filtra os pedidos do cliente
    pedidos_cliente = [pedido for pedido in pedidos if pedido['id_cliente'] == id_cliente]

    if not pedidos_cliente:
        await update.message.reply_text("Você não possui pedidos registrados.")
        return

    # Exibe os pedidos do cliente
    mensagem = "📋 *Seus Pedidos:*\n\n"
    for pedido in pedidos_cliente:
        mensagem += (
            f"🆔 *ID do Pedido:* {pedido['id_pedido']}\n"
            f"📅 *Data do Pedido:* {pedido['data_pedido']}\n"
            f"🛒 *Itens do Pedido:*\n"
        )

        # Lista os itens do pedido
        for item in pedido['itens_pedido']:
            if 'id_prato' in item:
                prato = next((p for p in ler_json_bot('pratos.json') if p['id_prato'] == item['id_prato']), None)
                if prato:
                    mensagem += f"🔹 {prato['nome_prato']} - {item['quantidade']} unidade(s)\n"
            elif 'id_bebida' in item:
                bebida = next((b for b in ler_json_bot('bebidas.json') if b['id_bebida'] == item['id_bebida']), None)
                if bebida:
                    mensagem += f"🔹 {bebida['nome_bebida']} - {item['quantidade']} unidade(s)\n"

        mensagem += (
            f"💵 *Valor Total:* R$ {pedido['valor_total_pedido']:.2f}\n"
            f"⏱️ *Tempo Estimado:* {pedido['tempo_total_pedido']} minutos\n"
            f"🏠 *Endereço de Entrega:* {pedido['endereco_entrega']}\n"
            f"💳 *Método de Pagamento:* {pedido['metodo_pagamento']}\n"
            f"📝 *Observações:* {pedido['observacoes_cliente']}\n"
            f"📌 *Status do Pedido:* {pedido['status_pedido']}\n\n"
        )

    await update.message.reply_text(mensagem, parse_mode="Markdown")
# Função para ler os dados dos JSONs
def ler_json_bot(nome_json):
    try:
        with open(nome_json, 'r') as arquivo:
            dados = json.load(arquivo)
    except FileNotFoundError:
        dados = []
    return dados


# Função para salvar os dados no JSON
def salvar_json_bot(nome_json, dados):
    with open(nome_json, 'w') as arquivo:
        json.dump(dados, arquivo, indent=4)



# Função para calcular o valor total do pedido
def calcular_valor_total(itens_pedido, pratos, bebidas):
    valor_total = 0.0
    for item in itens_pedido:
        if 'id_prato' in item:
            prato = next((p for p in pratos if p['id_prato'] == item['id_prato']), None)
            if prato:
                valor_total += prato['preco_prato'] * item['quantidade']
        elif 'id_bebida' in item:
            bebida = next((b for b in bebidas if b['id_bebida'] == item['id_bebida']), None)
            if bebida:
                valor_total += bebida['preco_bebida'] * item['quantidade']
    return valor_total

# Função para calcular o tempo total do pedido
def calcular_tempo_total(itens_pedido, pratos, bebidas):
    tempo_total = 0
    for item in itens_pedido:
        if 'id_prato' in item:
            prato = next((p for p in pratos if p['id_prato'] == item['id_prato']), None)
            if prato:
                tempo_total += prato['tempo_preparo_prato']
        elif 'id_bebida' in item:
            bebida = next((b for b in bebidas if b['id_bebida'] == item['id_bebida']), None)
            if bebida:
                tempo_total += bebida['tempo_preparo_bebida']
    return tempo_total

# Comando /pedidos
async def pedidos(update: Update, context) -> None:
    # Verifica se o usuário está cadastrado
    clientes = ler_json_bot('clientes.json')
    usuario_id = update.message.from_user.id
    cliente = next((c for c in clientes if c['id_usuario'] == usuario_id), None)

    if not context.user_data.get('logado', False):  # Padrão é False
        await update.message.reply_text("Você precisa estar logado para fazer um pedido. Use /login.")
        return

    # Inicia o processo de pedido
    await update.message.reply_text("Vamos fazer seu pedido! Primeiro, escolha um prato pelo ID:")
    pratos = ler_json_bot('pratos.json')
    bebidas = ler_json_bot('bebidas.json')

    # Mostra os pratos disponíveis
    for prato in pratos:
        imagem_prato = prato.get("imagem_prato", "")  # Obtém o caminho da imagem, se existir

        # Tenta enviar a imagem do prato, caso exista
        try:
            if imagem_prato:
                await update.message.reply_photo(photo=imagem_prato)
        except Exception as e:
            print(f"⚠️ Erro ao enviar imagem do prato *{prato['nome_prato']}*: {e}")

        # Envia os detalhes do prato
        await update.message.reply_text(f"🍽 *Prato:* {prato['nome_prato']}", parse_mode="Markdown")
        await update.message.reply_text(f"🆔 *ID:* {prato['id_prato']}", parse_mode="Markdown")
        await update.message.reply_text(f"💰 *Preço:* R$ {prato['preco_prato']:.2f}", parse_mode="Markdown")
        await update.message.reply_text(f"⏳ *Tempo de preparo:* {prato['tempo_preparo_prato']} min",
                                        parse_mode="Markdown")
        await update.message.reply_text(f"🥗 *Ingredientes:* {', '.join(prato['ingredientes_prato'])}",
                                        parse_mode="Markdown")

    context.user_data['estado'] = 'aguardando_prato'
    context.user_data['itens_pedido'] = []
    context.user_data['cliente'] = cliente


def ler_json_bot(nome_json):
    try:
        with open(nome_json, 'r') as arquivo:
            dados = json.load(arquivo)
    except FileNotFoundError:
        dados = []
    return dados

# Função para salvar o pedido no arquivo JSON
def salvar_pedido(pedido):
    pedidos = ler_json_bot('pedidos.json')
    pedidos.append(pedido)
    with open('pedidos.json', 'w') as f:
        json.dump(pedidos, f, indent=4)

# Função para gerar o próximo ID de pedido
def gerar_proximo_id_pedidos(pedidos):
    if pedidos:
        return max(pedido['id_pedido'] for pedido in pedidos) + 1
    return 1



# Verificar login antes de certos comandos
def verificar_login(update: Update, context) -> bool:
    if not context.user_data.get("logado"):
        update.message.reply_text("Você precisa estar logado para usar este comando. Use /login.")
        return False
    return True
# Função para ler o JSON
def ler_json_bot(nome_json):
    try:
        with open(nome_json, 'r') as arquivo:
            dados = json.load(arquivo)
    except FileNotFoundError:
        dados = []
    return dados

# Função para salvar no JSON
def salvar_json_bot(nome_json, dados):
    with open(nome_json, 'w') as arquivo:
        json.dump(dados, arquivo, indent=4)

# Função para gerar o próximo ID
def gerar_proximo_id(clientes):
    if not clientes:
        return 1
    return max(cliente['id_usuario'] for cliente in clientes) + 1

# Função para validar CPF
def validar_cpf(cpf):
    return bool(re.match(r'^\d{3}\.\d{3}\.\d{3}-\d{2}$', cpf))


# Comando /login
async def login(update: Update, context) -> None:
    await update.message.reply_text("Digite seu email:")
    context.user_data["estado"] = "aguardando_email_login"


# Comando /logout
async def logout(update: Update, context) -> None:
    context.user_data["logado"] = False
    context.user_data.pop("id_usuario", None)
    await update.message.reply_text("Você saiu da sua conta com sucesso.")



async def cardapio(update: Update, context) -> None:
    pratos = ler_json_bot('pratos.json')
    bebidas = ler_json_bot('bebidas.json')

    if not pratos and not bebidas:
        await update.message.reply_text("⚠️ O cardápio está indisponível no momento.")
        return

    mensagem = "🍽️ *Cardápio do Cyber Restaurante* 🍽️\n\n"

    # Exibir pratos
    if pratos:
        await update.message.reply_text("🍕 *Pratos:*\n", parse_mode="Markdown")
        for prato in pratos:
            ingredientes = ", ".join(prato["ingredientes_prato"])  # Junta os ingredientes
            imagem_prato = prato.get("imagem_prato", "")  # Pega o caminho da imagem

            # Tenta enviar a imagem, ignora se houver erro
            try:
                if imagem_prato:
                    await update.message.reply_photo(photo=imagem_prato)
            except Exception as e:
                print(f"Erro ao enviar imagem do prato {prato['nome_prato']}: {e}")

            # Enviar informações do prato
            mensagem = (
                f"🔹 *{prato['nome_prato']}* - R$ {prato['preco_prato']:.2f}\n"
                f"🕒 Tempo de preparo: {prato['tempo_preparo_prato']} min\n"
                f"🥗 Ingredientes: {ingredientes}\n\n"
            )
            await update.message.reply_text(mensagem, parse_mode="Markdown")

    # Exibir bebidas
    if bebidas:
        await update.message.reply_text("🥤 *Bebidas:*\n", parse_mode="Markdown")
        for bebida in bebidas:
            ingredientes = ", ".join(bebida["ingredientes_bebida"])  # Junta os ingredientes
            imagem_bebida = bebida.get("imagem_bebida", "")  # Pega o caminho da imagem

            # Tenta enviar a imagem, ignora se houver erro
            try:
                if imagem_bebida:
                    await update.message.reply_photo(photo=imagem_bebida)
            except Exception as e:
                print(f"Erro ao enviar imagem da bebida {bebida['nome_bebida']}: {e}")

            # Enviar informações da bebida
            mensagem = (
                f"🔹 *{bebida['nome_bebida']}* - R$ {bebida['preco_bebida']:.2f}\n"
                f"🕒 Tempo de preparo: {bebida['tempo_preparo_bebida']} min\n"
                f"🥗 Ingredientes: {ingredientes}\n\n"
            )
            await update.message.reply_text(mensagem, parse_mode="Markdown")
            await update.message.reply_text("⚠️ utilize /pedido para realizar um pedido")
async def cadastrar(update: Update, context) -> None:
    await update.message.reply_text("Vamos fazer seu cadastro. Para cancelar, digite 'cancelar'.\n\nDigite seu nome completo:")
    context.user_data['estado'] = 'aguardando_nome'

# Handler para mensagens
async def handle_message(update: Update, context) -> None:
    estado = context.user_data.get('estado')
    mensagem = update.message.text.strip().lower()

    # Cancelar cadastro ou pedido
    if mensagem == "cancelar":
        await update.message.reply_text("Operação cancelada.")
        #context.user_data.clear()
        return

    # Fluxo de cadastro
    if estado == 'aguardando_nome':
        context.user_data['nome'] = update.message.text
        await update.message.reply_text("Ótimo! Agora, qual é o seu email?")
        context.user_data['estado'] = 'aguardando_email'

    elif estado == 'aguardando_email':
        context.user_data['email'] = update.message.text
        await update.message.reply_text("Escolha uma senha:")
        context.user_data['estado'] = 'aguardando_senha'

    elif estado == 'aguardando_senha':
        context.user_data['senha'] = update.message.text
        await update.message.reply_text("Agora, informe seu CPF (Formato: 123.456.789-00):")
        context.user_data['estado'] = 'aguardando_cpf'

    elif estado == 'aguardando_cpf':
        if not validar_cpf(update.message.text):
            await update.message.reply_text("CPF inválido! Digite no formato correto: 123.456.789-00")
            return
        context.user_data['cpf'] = update.message.text
        await update.message.reply_text("Qual é o seu endereço de entrega?")
        context.user_data['estado'] = 'aguardando_endereco'

    elif estado == 'aguardando_endereco':
        context.user_data['endereco'] = update.message.text
        await update.message.reply_text("Por último, qual é o seu telefone? (Formato: 123456789)")
        context.user_data['estado'] = 'aguardando_telefone'

    elif estado == 'aguardando_telefone':
        context.user_data['telefone'] = update.message.text

        # Exibe os dados para confirmação
        nome = context.user_data['nome']
        email = context.user_data['email']
        senha_oculta = '*' * len(context.user_data['senha'])
        cpf = context.user_data['cpf']
        endereco = context.user_data['endereco']
        telefone = context.user_data['telefone']

        await update.message.reply_text(
            f"Confirme seus dados:\n\n"
            f"Nome: {nome}\n"
            f"Email: {email}\n"
            f"CPF: {cpf}\n"
            f"Endereço: {endereco}\n"
            f"Telefone: {telefone}\n\n"
            f"Se estiver correto, digite 'confirmar'. Caso contrário, digite 'cancelar'."
        )

        context.user_data['estado'] = 'aguardando_confirmacao'

    elif estado == 'aguardando_confirmacao':
        if mensagem.lower() == "confirmar":
            clientes = ler_json_bot('clientes.json')

            email_existente = any(cliente['email'] == context.user_data['email'] for cliente in clientes)
            cpf_existente = any(cliente['cpf'] == context.user_data['cpf'] for cliente in clientes)

            if email_existente:
                await update.message.reply_text("⚠️ Este e-mail já está cadastrado! Tente novamente com outro e-mail.")
                return

            if cpf_existente:
                await update.message.reply_text("⚠️ Este CPF já está cadastrado! Tente novamente com outro CPF.")
                return

            id_usuario = gerar_proximo_id(clientes)

            novo_cliente = {
                "id_usuario": id_usuario,
                "email": context.user_data['email'],
                "senha": context.user_data['senha'],
                "nome_cliente": context.user_data['nome'],
                "cpf": context.user_data['cpf'],
                "endereco_entrega": context.user_data['endereco'],
                "telefone": context.user_data['telefone'],
                "quantidade_pedidos": 0
            }

            clientes.append(novo_cliente)
            salvar_json_bot('clientes.json', clientes)

            await update.message.reply_text("Cadastro realizado com sucesso!")
            context.user_data.clear()

        else:
            await update.message.reply_text("Cadastro cancelado.")
            context.user_data.clear()

    # Fluxo de login
    elif estado == 'aguardando_email_login':
        email_informado = update.message.text.strip()
        clientes = ler_json_bot('clientes.json')

        cliente_encontrado = next((cliente for cliente in clientes if cliente['email'] == email_informado), None)
        if cliente_encontrado:
            context.user_data['email'] = email_informado
            await update.message.reply_text("Email encontrado! Agora, por favor, digite sua senha.")
            context.user_data['estado'] = 'aguardando_senha_login'
        else:
            await update.message.reply_text("⚠️ Email não encontrado. Tente novamente ou cadastre-se.")
            context.user_data['estado'] = 'aguardando_email'

    elif estado == 'aguardando_senha_login':
        senha_informada = update.message.text.strip()
        clientes = ler_json_bot('clientes.json')

        cliente_encontrado = next((cliente for cliente in clientes if cliente['email'] == context.user_data['email']), None)
        if cliente_encontrado and cliente_encontrado['senha'] == senha_informada:
            context.user_data['cliente'] = cliente_encontrado
            context.user_data['id_usuario'] = cliente_encontrado['id_usuario']
            context.user_data['nome_usuario'] = cliente_encontrado['nome_cliente']
            context.user_data['logado'] = True
            await update.message.reply_text("Login realizado com sucesso!")
            await update.message.reply_text("utilize /help para conhecer todos os comandos disponiveis")
        else:
            await update.message.reply_text("⚠️ Senha incorreta. Tente novamente.")
            context.user_data['estado'] = 'aguardando_senha_login'

    # Fluxo de pedidos
    elif estado == 'aguardando_prato':
        try:
            id_prato = int(update.message.text)
            pratos = ler_json_bot('pratos.json')
            prato = next((p for p in pratos if p['id_prato'] == id_prato), None)

            if prato:
                context.user_data['item_atual'] = {'id_prato': id_prato}
                await update.message.reply_text(f"Você escolheu {prato['nome_prato']}. Quantas unidades?")
                context.user_data['estado'] = 'aguardando_quantidade_prato'
            else:
                await update.message.reply_text("Prato não encontrado. Tente novamente.")
        except ValueError:
            await update.message.reply_text("Por favor, insira um ID válido.")

    elif estado == 'aguardando_quantidade_prato':
        try:
            quantidade = int(update.message.text)
            if quantidade > 0:
                context.user_data['item_atual']['quantidade'] = quantidade
                context.user_data['itens_pedido'].append(context.user_data['item_atual'])
                await update.message.reply_text("Prato adicionado ao pedido. Deseja adicionar outro prato? (sim/não)")
                context.user_data['estado'] = 'aguardando_outro_prato'
            else:
                await update.message.reply_text("Quantidade inválida. Tente novamente.")
        except ValueError:
            await update.message.reply_text("Por favor, insira um número válido.")

    elif estado == 'aguardando_outro_prato':
        if mensagem == 'sim':
            await update.message.reply_text("Escolha outro prato pelo ID:")
            context.user_data['estado'] = 'aguardando_prato'
        else:
            await update.message.reply_text("Agora, escolha uma bebida pelo ID:")
            bebidas = ler_json_bot('bebidas.json')
            for bebida in bebidas:
                imagem_bebida = bebida.get("imagem_bebida", "")  # Obtém o caminho da imagem, se existir

                # Tenta enviar a imagem da bebida, caso exista
                try:
                    if imagem_bebida:
                        await update.message.reply_photo(photo=imagem_bebida)
                except Exception as e:
                    print(f"⚠️ Erro ao enviar imagem da bebida *{bebida['nome_bebida']}*: {e}")

                # Envia os detalhes da bebida
                await update.message.reply_text(f"🥤 *Bebida:* {bebida['nome_bebida']}", parse_mode="Markdown")
                await update.message.reply_text(f"🆔 *ID:* {bebida['id_bebida']}", parse_mode="Markdown")
                await update.message.reply_text(f"💰 *Preço:* R$ {bebida['preco_bebida']:.2f}", parse_mode="Markdown")
                await update.message.reply_text(f"⏳ *Tempo de preparo:* {bebida['tempo_preparo_bebida']} min",
                                                parse_mode="Markdown")
                await update.message.reply_text(f"📝 *Ingredientes:* {', '.join(bebida['ingredientes_bebida'])}",
                                                parse_mode="Markdown")
            context.user_data['estado'] = 'aguardando_bebida'

    elif estado == 'aguardando_bebida':
        try:
            id_bebida = int(update.message.text)
            bebidas = ler_json_bot('bebidas.json')
            bebida = next((b for b in bebidas if b['id_bebida'] == id_bebida), None)

            if bebida:
                context.user_data['item_atual'] = {'id_bebida': id_bebida}
                await update.message.reply_text(f"Você escolheu {bebida['nome_bebida']}. Quantas unidades?")
                context.user_data['estado'] = 'aguardando_quantidade_bebida'
            else:
                await update.message.reply_text("Bebida não encontrada. Tente novamente.")
        except ValueError:
            await update.message.reply_text("Por favor, insira um ID válido.")

    elif estado == 'aguardando_quantidade_bebida':
        try:
            quantidade = int(update.message.text)
            if quantidade > 0:
                context.user_data['item_atual']['quantidade'] = quantidade
                context.user_data['itens_pedido'].append(context.user_data['item_atual'])
                await update.message.reply_text("Bebida adicionada ao pedido. Deseja adicionar outra bebida? (sim/não)")
                context.user_data['estado'] = 'aguardando_outra_bebida'
            else:
                await update.message.reply_text("Quantidade inválida. Tente novamente.")
        except ValueError:
            await update.message.reply_text("Por favor, insira um número válido.")

    elif estado == 'aguardando_outra_bebida':
        if mensagem == 'sim':
            await update.message.reply_text("Escolha outra bebida pelo ID:")
            context.user_data['estado'] = 'aguardando_bebida'
        else:
            await update.message.reply_text("O endereço de entrega será o mesmo do cadastro? (sim/não)")
            context.user_data['estado'] = 'aguardando_endereco_pedido'

    elif estado == 'aguardando_endereco_pedido':
        if mensagem == 'sim':
            # Recupera o ID do cliente logado
            id_cliente = context.user_data.get('id_usuario')

            if id_cliente is None:
                await update.message.reply_text("Erro: ID do cliente não encontrado. Faça login novamente.")
                return

            # Carrega os clientes do JSON
            clientes = ler_json_bot('clientes.json')

            # Encontra o cliente pelo ID
            cliente = next((c for c in clientes if c['id_usuario'] == id_cliente), None)

            if cliente is None:
                await update.message.reply_text("Erro: Cliente não encontrado no sistema.")
                return

            # Define o endereço de entrega
            context.user_data['endereco_entrega'] = cliente['endereco_entrega']
            await update.message.reply_text("Escolha o método de pagamento: dinheiro, cartão ou pix.")
            context.user_data['estado'] = 'aguardando_metodo_pagamento'
        else:
            await update.message.reply_text("Qual será o endereço de entrega?")
            context.user_data['estado'] = 'aguardando_novo_endereco'


    elif estado == 'aguardando_novo_endereco':
        context.user_data['endereco_entrega'] = update.message.text
        await update.message.reply_text("Escolha o método de pagamento: dinheiro, cartão ou pix.")
        context.user_data['estado'] = 'aguardando_metodo_pagamento'

    elif estado == 'aguardando_metodo_pagamento':
        metodo_pagamento = update.message.text.lower()
        if metodo_pagamento in ['dinheiro', 'cartão', 'pix']:
            context.user_data['metodo_pagamento'] = metodo_pagamento
            await update.message.reply_text("Alguma observação para o pedido? (Caso não, digite 'não')")
            context.user_data['estado'] = 'aguardando_observacoes'
        else:
            await update.message.reply_text("Método de pagamento inválido. Escolha entre dinheiro, cartão ou pix.")


    elif estado == 'aguardando_observacoes':

        observacoes = update.message.text

        if observacoes.lower() == 'não':
            observacoes = ""

        # Calcula valor e tempo total

        valor_total = calcular_valor_total(context.user_data['itens_pedido'], ler_json_bot('pratos.json'),
                                           ler_json_bot('bebidas.json'))

        tempo_total = calcular_tempo_total(context.user_data['itens_pedido'], ler_json_bot('pratos.json'),
                                           ler_json_bot('bebidas.json'))

        # Armazena os valores no context.user_data

        context.user_data['valor_total'] = valor_total

        context.user_data['tempo_total'] = tempo_total

        context.user_data['observacoes'] = observacoes

        # Exibe os detalhes do pedido para confirmação

        mensagem_confirmacao = (

            f"📝 *Confirme seu pedido:*\n\n"

            f"🍽️ *Itens do pedido:*\n"

        )

        # Lista os pratos e bebidas escolhidos

        for item in context.user_data['itens_pedido']:

            if 'id_prato' in item:

                prato = next((p for p in ler_json_bot('pratos.json') if p['id_prato'] == item['id_prato']), None)

                if prato:
                    mensagem_confirmacao += f"🔹 {prato['nome_prato']} - {item['quantidade']} unidade(s) - R$ {prato['preco_prato'] * item['quantidade']:.2f}\n"

            elif 'id_bebida' in item:

                bebida = next((b for b in ler_json_bot('bebidas.json') if b['id_bebida'] == item['id_bebida']), None)

                if bebida:
                    mensagem_confirmacao += f"🔹 {bebida['nome_bebida']} - {item['quantidade']} unidade(s) - R$ {bebida['preco_bebida'] * item['quantidade']:.2f}\n"

        mensagem_confirmacao += (

            f"\n💵 *Valor total:* R$ {valor_total:.2f}\n"

            f"⏱️ *Tempo estimado:* {tempo_total} minutos\n"

            f"🏠 *Endereço de entrega:* {context.user_data['endereco_entrega']}\n"

            f"💳 *Método de pagamento:* {context.user_data['metodo_pagamento']}\n"

            f"📝 *Observações:* {observacoes}\n\n"

            f"Digite 'confirmar' para finalizar o pedido ou 'cancelar' para descartá-lo."

        )

        await update.message.reply_text(mensagem_confirmacao)

        context.user_data['estado'] = 'aguardando_confirmacao_pedido'

    elif estado == 'aguardando_confirmacao_pedido':
        if mensagem.lower() == 'confirmar':
            # Recupera os valores do context.user_data
            valor_total = context.user_data.get('valor_total')
            tempo_total = context.user_data.get('tempo_total')
            observacoes = context.user_data.get('observacoes')

            # Cria o pedido
            pedido = {
                "id_pedido": gerar_proximo_id_pedidos(ler_json_bot('pedidos.json')),
                "id_cliente": context.user_data.get('id_usuario'),
                "itens_pedido": context.user_data['itens_pedido'],
                "status_pedido": "em preparo",
                "tempo_total_pedido": tempo_total,
                "valor_total_pedido": valor_total,
                "data_pedido": datetime.now().isoformat(),
                "metodo_pagamento": context.user_data['metodo_pagamento'],
                "endereco_entrega": context.user_data['endereco_entrega'],
                "observacoes_cliente": observacoes,
                "avaliacao_pedido": 'não avaliado'
            }

            # Salva o pedido
            pedidos = ler_json_bot('pedidos.json')
            pedidos.append(pedido)
            salvar_json_bot('pedidos.json', pedidos)

            # Atualiza a quantidade de pedidos do cliente
            clientes = ler_json_bot('clientes.json')
            for c in clientes:
                if c['id_usuario'] == context.user_data.get('id_usuario'):
                    c['quantidade_pedidos'] += 1
                    pedido_cliente = next(
                        (p for p in pedidos if p["id_cliente"] == c["id_usuario"]), None
                    )
                    enviar_email(c,pedido_cliente)
                    break
            salvar_json_bot('clientes.json', clientes)

            # Confirmação final
            await update.message.reply_text("Pedido confirmado e salvo com sucesso!")

        else:
            await update.message.reply_text("Pedido cancelado.")

    elif estado == 'aguardando_id_pedido_avaliar':
        try:
            id_pedido = int(update.message.text)
            pedidos = ler_json_bot('pedidos.json')

            # Verifica se o pedido existe e pertence ao cliente
            pedido = next((p for p in pedidos if
                           p['id_pedido'] == id_pedido and p['id_cliente'] == context.user_data.get('id_usuario') and p[
                               'status_pedido'] == 'entregue'), None)

            if pedido is None:
                await update.message.reply_text("Pedido não encontrado ou não está entregue. Tente novamente.")
                return

            # Armazena o ID do pedido para avaliação
            context.user_data['id_pedido_avaliar'] = id_pedido

            # Pergunta pela avaliação
            await update.message.reply_text("Por favor, avalie o pedido de 1 a 5 estrelas (digite um número de 1 a 5):")
            context.user_data['estado'] = 'aguardando_avaliacao'
        except ValueError:
            await update.message.reply_text("Por favor, insira um ID válido.")

    elif estado == 'aguardando_avaliacao':
        try:
            avaliacao = int(update.message.text)
            if avaliacao < 1 or avaliacao > 5:
                await update.message.reply_text("A avaliação deve ser um número entre 1 e 5. Tente novamente.")
                return

            # Recupera o ID do pedido
            id_pedido = context.user_data.get('id_pedido_avaliar')
            if id_pedido is None:
                await update.message.reply_text("Erro: ID do pedido não encontrado. Tente novamente.")
                return

            # Carrega os pedidos do arquivo JSON
            pedidos = ler_json_bot('pedidos.json')

            # Encontra o pedido e atualiza a avaliação
            for pedido in pedidos:
                if pedido['id_pedido'] == id_pedido:
                    pedido['avaliacao_pedido'] = avaliacao
                    break

            # Salva os pedidos atualizados
            salvar_json_bot('pedidos.json', pedidos)

            # Confirmação
            await update.message.reply_text(f"Avaliação do pedido {id_pedido} salva com sucesso! Obrigado por avaliar.")
            #context.user_data.clear()  # Limpa os dados temporários
        except ValueError:
            await update.message.reply_text("Por favor, insira um número válido de 1 a 5.")





# Comando /help
async def help(update: Update, context) -> None:
    nome_usuario = context.user_data.get('nome_usuario', 'Usuário')
    if context.user_data.get('logado', False):
        # Usuário logado
        await update.message.reply_text(
            f'bem vindo {nome_usuario} \n'
            '/status: Verifique o status dos pedidos\n'
            '/pedido: Faça um novo pedido\n'
            '/cardapio: Verifique nosso cardapio\n'
            '/avaliar: Avaliar pedidos\n'
            '/help: Veja as funções disponíveis\n'
            'utilize a palavra: cancelar para encerrar qualquer operação\n'
        )
    else:
        # Usuário não logado
        await update.message.reply_text(
            '/start: Para boas vindas\n'
            '/help: Veja as funções disponíveis\n'
            '/cardapio: Verifique nosso cardapio\n'
            '/login: Faça login para acessar os outros comandos.\n'
            '/cadastrar: Para realizar seu cadastro\n'
            'utilize a palavra: cancelar para encerrar qualquer operação\n'
        )


# Comando /start
async def start(update: Update, context) -> None:
    await update.message.reply_text("Olá, bem-vindo ao Cyber Restaurante.")
    await update.message.reply_text("Para conhecer os comandos disponíveis, digite /help")
    await update.message.reply_text("Utilize a palavra cancelar para encerrar qualquer operação")

# Função principal do bot
def bot():
    token = "seu token"
    application = Application.builder().token(token).build()

    application.add_handler(CommandHandler('help', help))
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('cadastrar', cadastrar))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CommandHandler('cardapio', cardapio))
    application.add_handler(CommandHandler('login', login))
    application.add_handler(CommandHandler('logout', logout))
    application.add_handler(CommandHandler('pedido', pedidos))
    application.add_handler(CommandHandler('status', status))
    application.add_handler(CommandHandler('avaliar', avaliar))

    #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_login))

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(application.run_polling())
