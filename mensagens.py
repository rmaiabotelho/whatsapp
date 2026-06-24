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

    # 2. Carregar a lista de contatos do Excel
    df = pd.read_csv('clientes.csv')

    # 3. Inicializar o Navegador (Firefox)
    options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(options=options)
    driver.maximize_window()

    # Abre o WhatsApp Web
    driver.get("https://web.whatsapp.com")
    print("Aguardando leitura do QR Code... Aguarde o carregamento completo das conversas.")
    input("Após escanear o QR Code e as conversas carregarem, pressione ENTER aqui no terminal para iniciar...")

    # 4. Loop de envio para cada contato
    for index, linha in df.iterrows():
        nome = linha.get('Nome', 'Cliente')
        telefone = str(linha['Telefone']).strip().replace(".0", "").replace(" ", "").replace("-", "")
        
        print(f"\n[{index + 1}/{len(df)}] Preparando envio para: {nome} ({telefone})")
        
        url = f"https://web.whatsapp.com/send?phone={telefone}&text={mensagem_codificada}"
        driver.get(url)
        
        try:
            # --- VERIFICAÇÃO DE NÚMERO INVÁLIDO ---
            # Tenta detectar se a caixa de "Número inválido" apareceu nos primeiros 10 segundos
            try:
                # Procura pelo botão "OK" da mensagem de erro do WhatsApp
                erro_popup = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//div[contains(text(), "inválido")]/parent::div//button | //button[contains(., "OK")]'))
                )
                print(f"⚠️ O número {telefone} não possui WhatsApp. Fechando aviso e pulando...")
                erro_popup.click()
                time.sleep(2)
                continue  # Pula o restante do bloco atual e vai direto para o próximo contato do 'for'
            except:
                # Se não achou o aviso de erro em 10 segundos, assume que o número é válido e continua o envio normal
                pass

            # Aguarda o botão de enviar ficar clicável
            botao_enviar = WebDriverWait(driver, 25).until(
                EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]|//button[@aria-label="Enviar"]'))
            )
            
            time.sleep(random.uniform(1.5, 3.5))
            botao_enviar.click()
            print(f"Mensagem enviada com sucesso para {nome}!")
            
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
            time.sleep(4)

    print("\nProcesso de automação finalizado!")
    driver.quit()


# Configuração do Texto da Mensagem
mensagem = """*AVISO DE NOVO ENDEREÇO*

Informamos aos nossos clientes que estamos atendendo em um novo local:

📍 *Rua Presidente Costa e Silva, n.º 117, sala 420, Centro, Itaboraí - RJ.*

Atenciosamente,

Dr. Rodrigo Octávio - OAB/RJ 220.797"""

whatsapp_message_sender(mensagem)