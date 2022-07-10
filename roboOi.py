from playwright.sync_api import sync_playwright
from datetime import datetime
from pytz import timezone

from pycpfcnpj import cpfcnpj
import time
import pandas as pd
import logging
import os
import traceback

arquivo = r'./CNPJ_OI.txt'
cpfCnpj = open(arquivo, 'r', encoding='ISO-8859-1')
qtd_divida = 0
vrs = '1.0.8'
lista = []


try:
    logging.basicConfig(filename="RoboConsultaCNPJ_OI.log",
                        level=logging.INFO,
                        format = "%(asctime)s :: %(levelno)s :: %(lineno)d :: %(message)s")

    logging.info(f'Iniciando robô de cosulta OI {vrs}')

    print(f"Iniciando aplicação de automação consulta OI - vrs:{vrs}")


    #Imprime data atual
    def formata_data_hora():
        dataHora = datetime.now()
        fuso_horario = timezone("America/Araguaina")
        agora = dataHora.astimezone(fuso_horario)
        #agora_formatado = agora.strftime('%d/%m/%Y %H:%M')
        data_formatada= agora.strftime('%d/%m/%Y %H:%M:%S')

        return(data_formatada)

    def escrever_txt(lista):
        with open('verificados_oi.txt', 'w', encoding='ISO-8859-1') as f:
            logging.info('Gerando arquivo de CNPJ com pendências em aberto')
            for linha in lista:
                f.write(linha + '\n')
    data_hora = formata_data_hora()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True) #headless = True oculta navegador Chromium
        page = browser.new_page()
        page.goto("https://www.oi.com.br/negociacao/")
        logging.info('Carregando robô... Por favor aguarde')
        time.sleep(20)

        
        for i in cpfCnpj:
            logging.info('Iniciando processo...')
            print('Iniciando processo...')
            #Validar CNPJ
            

            if (cpfcnpj.validate(i.replace('\n',''))) == False:
                print(f"CNPJ inválido:{i}")
            else:
                print(f"Validando CNPJ {i}")
                logging.info(f'Verificando CNPJ {i}')
                #Acessando input CPF/CNPJ
                page.fill("input[name='cpfCnpj']", i)
                page.wait_for_timeout(9000)

                #clicar botão ConsultarDividas
                page.click("button[data-context='btn_landing_consultar-dividas']")
                page.wait_for_timeout(11000)

                sem_divida = page.locator("#simple-page-body > div > div:nth-child(1) > div.Container__ContainerStyle-sc-1iqy2ia-0.jGfLwr > div > form > div.Container__ContainerStyle-sc-1iqy2ia-0.bUsUIY > div.Container__ContainerStyle-sc-1iqy2ia-0.jLIESq > div > p.Text__TextStyle-sc-fp0yjz-0.evkJPn").all_text_contents()
                if sem_divida == ['Tudo certo!']:
                    print("Sem pendências!")
                    logging.info(f"{data_hora} CPF {i}: {sem_divida}")
                    page.click("button[data-context='btn_landing_nova-consulta']")
 


                nome_produto = page.locator("p[data-context='info_product-name']").all_text_contents()
                vlr_produto =  page.locator(
                            "#simple-page-body > div.Container__ContainerStyle-sc-1iqy2ia-0.iLdNJk > div.Container__ContainerStyle-sc-1iqy2ia-0.iovtgz > div > div.Container__ContainerStyle-sc-1iqy2ia-0.bFydGe > div.Container__ContainerStyle-sc-1iqy2ia-0.cwRmTB > div > div.Container__ContainerStyle-sc-1iqy2ia-0.jkVxrx > div > p > span").all_text_contents()
                consultado =  page.locator(
                            "#application > div > div > div > div.Container__ContainerStyle-sc-1iqy2ia-0.dtwiMy > div.Container__ContainerStyle-sc-1iqy2ia-0.fEQXxn > div.Container__ContainerStyle-sc-1iqy2ia-0.gzWcKd > div > p.Text__TextStyle-sc-fp0yjz-0.fxdzOW").all_text_contents()

                #if nome_produto != []:
                logging.info(len(nome_produto))
                try:
                    if (len(nome_produto)) > 0:
                        for l in range(len(nome_produto)):

                            a = (nome_produto[l]).replace('/','')
                            b = (vlr_produto[l])
                            dados = (f"{data_hora};{i};{a};{b}")
                            lista.append(dados)
                            print(f'CNPJ {i} possui pendências:{a} - {b} ')
                            logging.info(f'CNPJ {i} possui pendências:{a} - {b} ')
                        time.sleep(5)
                        page.click("p[class='Text__TextStyle-sc-fp0yjz-0 iGqJGi']")

                    page.wait_for_timeout(8000)
                except Exception:
                    traceback.print_exc()
                    logging.info(logging.info())
        escrever_txt(lista)
        print("Processo finalizado, favor verificar arquivo de extração.")
        browser.close()
        logging.info(f"{data_hora} - Aplicação encerrada {vrs}")
except OSError as e:
    logging.info(f"Error:{e.strerror}")