from datetime import date
import pandas as pd
import time
import random
import urllib.parse
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def whatsapp_message_sender(mensagem):
    mensagem_codificada = urllib.parse.quote(mensagem)  # Codifica a mensagem para URL

    # 1. Carregar a lista de contatos do Excel
    df = pd.read_csv('/home/rodrigo/Gdrive/clientes.csv')

    # 2. Inicializar o Navegador (Firefox)
    options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(options=options)
    driver.maximize_window()

    # Abre o WhatsApp Web
    driver.get("https://web.whatsapp.com")
    print("Aguardando leitura do QR Code... Aguarde o carregamento completo das conversas.")
    input("Após escanear o QR Code e as conversas carregarem, pressione ENTER aqui no terminal para iniciar...")

    # --- CONTADORES E LISTAS DE RELATÓRIO ---
    sucessos = 0
    erros_nao_whatsapp = []
    erros_timeout = []

    # 3. Loop de envio para cada contato
    for index, linha in df.iterrows():
        nome = linha.get('Nome', 'Cliente')
        telefone = str(linha['Telefone']).strip().replace(".0", "").replace(" ", "").replace("-", "")
        
        print(f"\n[{index + 1}/{len(df)}] Preparando envio para: {nome} ({telefone})")
        
        url = f"https://web.whatsapp.com/send?phone={telefone}&text={mensagem_codificada}"
        driver.get(url)
        
        try:
            # --- VERIFICAÇÃO DE NÚMERO INVÁLIDO ---
            try:
                erro_popup = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "inválido")]/parent::div//button | //button[contains(., "OK")]'))
                )
                print(f"⚠️ O número {telefone} não possui WhatsApp. Fechando aviso e pulando...")
                
                # Armazena o contato na lista de erros por falta de WhatsApp
                erros_nao_whatsapp.append(f"{nome} ({telefone})")
                
                erro_popup.click()
                time.sleep(2)
                continue  
            except:
                pass

            # Aguarda o botão de enviar ficar clicável
            botao_enviar = WebDriverWait(driver, 25).until(
                EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]|//button[@aria-label="Enviar"]'))
            )
            
            time.sleep(random.uniform(1.5, 3.5))
            botao_enviar.click()
            print(f"Mensagem enviada com sucesso para {nome}!")
            
            # Incrementa o contador de sucesso
            sucessos += 1
            
            # Intervalo dinâmico de segurança
            tempo_espera = random.randint(10, 15)
            
            if (index + 1) % 5 == 0:
                pausa_extra = random.randint(30, 50)
                print(f"Pausa em bloco (5 envios concluídos). Aguardando {tempo_espera + pausa_extra} segundos...")
                time.sleep(tempo_espera + pausa_extra)
            else:
                print(f"Aguardando {tempo_espera} segundos para o próximo contato...")
                time.sleep(tempo_espera)
                
        except Exception as e:
            print(f"Erro inesperado ou timeout ao processar o número {telefone}. Pulando para o próximo...")
            # Armazena o contato na lista de erros por timeout/sistema
            erros_timeout.append(f"{nome} ({telefone})")
            time.sleep(4)

    print("\n" + "="*40)
    print("      PROCESSO DE AUTOMAÇÃO FINALIZADO!      ")
    print("="*40)
    print(f"📈 Total de mensagens enviadas com sucesso: {sucessos}")
    print(f"❌ Total de números sem WhatsApp: {len(erros_nao_whatsapp)}")
    print(f"⏳ Total de erros por timeout/sistema: {len(erros_timeout)}")
    
    if erros_nao_whatsapp:
        print("\n🚫 Contatos que NÃO possuem WhatsApp:")
        for item in erros_nao_whatsapp:
            print(f"  - {item}")
            
    if erros_timeout:
        print("\n⚠️ Contatos que deram erro de sistema/timeout (recomenda-se tentar novamente):")
        for item in erros_timeout:
            print(f"  - {item}")
    print("="*40)

    driver.quit()


def whatsapp_aniversario_sender():
    # 1. Identificar o dia e mês de hoje
    hoje = date.today()
    dia_hoje = hoje.day
    mes_hoje = hoje.month

    # 2. Carregar a lista de contatos do CSV
    df = pd.read_csv('/home/rodrigo/Gdrive/clientes.csv')
    
    # Converte a coluna para o formato de data do Pandas (trata formatos YYYY-MM-DD)
    df['Data_Nascimento'] = pd.to_datetime(df['Data_Nascimento'], errors='coerce')

    # Filtra o DataFrame para manter apenas quem faz aniversário hoje (mesmo dia e mês)
    aniversariantes = df[
        (df['Data_Nascimento'].dt.day == dia_hoje) & 
        (df['Data_Nascimento'].dt.month == mes_hoje)
    ]

    if aniversariantes.empty:
        print(f"Nenhum aniversariante encontrado para a data de hoje ({hoje.strftime('%d/%m')}).")
        return

    print(f"🎉 Encontrado(s) {len(aniversariantes)} aniversariante(s) hoje!")

    # 3. Inicializar o Navegador (Firefox)
    options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(options=options)
    driver.maximize_window()

    # Abre o WhatsApp Web
    driver.get("https://web.whatsapp.com")
    print("Aguardando leitura do QR Code... Aguarde o carregamento completo das conversas.")
    input("Após escanear o QR Code, pressione ENTER no terminal para iniciar os envios...")

    # Contadores para o relatório
    sucessos = 0
    erros_nao_whatsapp = []
    erros_timeout = []

    # 4. Loop de envio apenas para os aniversariantes
    for index, (_, linha) in enumerate(aniversariantes.iterrows()):
        nome = linha.get('Nome', 'Cliente')
        telefone = str(linha['Telefone']).strip().replace(".0", "").replace(" ", "").replace("-", "")
        
        # Mensagem personalizada com o nome do cliente
        mensagem_texto = f"""Olá, {nome}! 🎂

Nós, do escritório do Dr. Rodrigo Octávio, passamos para lhe desejar um feliz aniversário! 

Que este novo ciclo seja repleto de saúde, paz, felicidade e muito sucesso. É um privilégio ter você como nosso cliente.

Parabéns! 🎉🎈"""
        
        mensagem_codificada = urllib.parse.quote(mensagem_texto)
        
        print(f"\n[{index + 1}/{len(aniversariantes)}] Enviando parabéns para: {nome} ({telefone})")
        
        url = f"https://web.whatsapp.com/send?phone={telefone}&text={mensagem_codificada}"
        driver.get(url)
        
        try:
            # --- VERIFICAÇÃO DE NÚMERO INVÁLIDO ---
            try:
                erro_popup = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "inválido")]/parent::div//button | //button[contains(., "OK")]'))
                )
                print(f"⚠️ O número {telefone} não possui WhatsApp. Pulando...")
                erros_nao_whatsapp.append(f"{nome} ({telefone})")
                erro_popup.click()
                time.sleep(2)
                continue  
            except:
                pass

            # Aguarda o botão de enviar ficar clicável
            botao_enviar = WebDriverWait(driver, 25).until(
                EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]|//button[@aria-label="Enviar"]'))
            )
            
            time.sleep(random.uniform(1.5, 3.5))
            botao_enviar.click()
            print(f"Mensagem de aniversário enviada com sucesso para {nome}!")
            
            sucessos += 1
            
            # Intervalo dinâmico de segurança
            tempo_espera = random.randint(10, 15)
            
            if (index + 1) % 5 == 0:
                pausa_extra = random.randint(30, 50)
                print(f"Pausa em bloco. Aguardando {tempo_espera + pausa_extra} segundos...")
                time.sleep(tempo_espera + pausa_extra)
            else:
                print(f"Aguardando {tempo_espera} segundos...")
                time.sleep(tempo_espera)
                
        except Exception as e:
            print(f"Erro inesperado ou timeout ao processar o número {telefone}. Pulando...")
            erros_timeout.append(f"{nome} ({telefone})")
            time.sleep(4)

    # Relatório Final
    print("\n" + "="*40)
    print("      RELATÓRIO DE ANIVERSARIANTES      ")
    print("="*40)
    print(f"📈 Mensagens enviadas com sucesso: {sucessos}")
    print(f"❌ Números sem WhatsApp: {len(erros_nao_whatsapp)}")
    print(f"⏳ Erros de timeout: {len(erros_timeout)}")
    print("="*40)

    driver.quit()




# Configuração do Texto da Mensagem geral - Não serve para aniversariantes, apenas para avisos gerais

mensagem = """*AVISO DE NOVO ENDEREÇO*

Informamos aos nossos clientes que estamos atendendo em um novo local:

📍 *Rua Presidente Costa e Silva, n.º 117, sala 420, Centro, Itaboraí - RJ.*

Atenciosamente,

Dr. Rodrigo Octávio - OAB/RJ 220.797"""

whatsapp_message_sender(mensagem)