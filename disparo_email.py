import smtplib
from email.message import EmailMessage
import time


def enviar_relatorio(relatorio):
    # Perguntar o email para o qual enviar o relatório
    email_destino = input("Digite o e-mail para o qual deseja enviar o relatório: ")

    # Configurar o e-mail
    hora = time.strftime('%H:%M:%S')
    msg = EmailMessage()
    msg['Subject'] = 'Relatório de Vendas'
    msg['From'] = 'cyberpythonedux@gmail.com'
    msg['To'] = email_destino

    # Adiciona o corpo do e-mail com HTML
    msg.add_alternative(f"""
               <html>
                   <head>
                       <title>Relatório de Vendas</title>
                   </head>
                   <body>
                       <h1>Relatório de Vendas - {hora}</h1>
                       <p><strong>Valor Total de Vendas:</strong> R$ {relatorio['valor_total_vendas']:.2f}</p>
                       <h3>Vendas por Produto:</h3>
                       <ul>
                           {''.join([f"<li>{produto}: R$ {valor:.2f}</li>" for produto, valor in relatorio['vendas_por_produto'].items()])}
                       </ul>
                       <h3>Vendas por Cliente:</h3>
                       <ul>
                           {''.join([f"<li>Cliente ID {cliente}: R$ {total:.2f}</li>" for cliente, total in relatorio['vendas_por_cliente'].items()])}
                       </ul>
                       <p><strong>Média de Itens por Pedido:</strong> {relatorio['media_itens_por_pedido']:.2f}</p>
                       <p><strong>Média das Avaliações:</strong> {relatorio['media_avaliacoes']:.2f}</p>
                       <p><strong>Quantidade de Avaliações Feitas:</strong> {relatorio['quantidade_avaliacoes']}</p>
                       <br>
                       <p>Obrigado por utilizar nosso sistema! 😊</p>
                   </body>
               </html>
           """, subtype="html")

    # Configuração do servidor de e-mail
    try:
        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()
        servidor.login('cyberpythonedux@gmail.com', 'sua senha')  # Substitua com a senha corretamente
        servidor.send_message(msg)
        servidor.quit()
        print(f"Relatório enviado com sucesso para {email_destino}!")
    except Exception as e:
        print(f"Erro ao enviar o relatório: {e}")
def enviar_email_promocional(clientes):
    for cliente in clientes:
        msg = EmailMessage()
        msg['Subject'] = 'Promoção Imperdível!'
        msg['From'] = 'seuemail@gmail.com'
        msg['To'] = cliente['email']

        msg.add_alternative(f"""
            <html>
                <head>Olá {cliente['nome_cliente']}</head>
                <body>
                    <h1>Temos novidades para você!</h1>
                    <p>Preços mais baixos em seus pratos favoritos. Confira agora!</p>
                </body>
            </html>
        """, subtype='html')

        try:
            servidor = smtplib.SMTP('smtp.gmail.com', 587)
            servidor.starttls()
            servidor.login('cyberpythonedux@gmail.com', 'sua senha')
            servidor.send_message(msg)
            servidor.quit()
            print(f"E-mail enviado para {cliente['nome_cliente']}")
        except Exception as e:
            print(f"Erro ao enviar e-mail para {cliente['nome_cliente']}: {e}")

def enviar_email(cliente,pedido):
    # falta verificar se o email ja existe
    hora = time.strftime('%H:%M:%S')
    # appendar json

    if cliente:


        msg = EmailMessage()
        msg['Subject'] = 'Confirmação de pedido'
        msg['From'] = 'cyberpythonedux@gmail.com'
        msg['To'] = cliente['email']

        msg.add_alternative(f"""
                   <html>
                       <head>
                           <title>Pedido Confirmado</title>
                       </head>
                       <body>
                           <h1>Olá {cliente['nome_cliente']}, seu pedido foi confirmado! 🎉</h1>
                           <p>Detalhes do pedido:</p>
                           <p><strong>Valor total:</strong> R$ {pedido["valor_total_pedido"]:.2f}</p>
                           <p><strong>Tempo estimado de entrega:</strong> {pedido["tempo_total_pedido"]} minutos</p>
                           <p><strong>Endereço de entrega:</strong> {pedido["endereco_entrega"]}</p>
                           <p><strong>Método de pagamento:</strong> {pedido["metodo_pagamento"]}</p>
                           <br>
                           <p>Obrigado por comprar conosco! 😊</p>
                       </body>
                   </html>
               """, subtype="html")

        servidor = smtplib.SMTP('smtp.gmail.com', 587)
        servidor.starttls()
        servidor.login('cyberpythonedux@gmail.com', 'sua senha')
        servidor.send_message(msg)
        servidor.quit()

