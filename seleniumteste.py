from datetime import datetime
import time
import random
import math

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException

import threading
import pyautogui

# Desativa a trava de canto de tela do PyAutoGUI
pyautogui.FAILSAFE = False

# Flag de controle da Thread do mouse
MANTEM_MOUSE_MOVENDO = True

# ============================================================
# CONFIGURAÇÕES
# ============================================================

GRUPO_BUSCA = "007275"
COTA_BUSCA = "2634"

TEMPO_ESPERA = 15

# Troque para 0 para DESATIVAR ou 1 para ATIVAR o movimento do mouse:
ATIVAR_MOVIMENTO_MOUSE = 1


# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def mover_cursor_continuamente():
    """Gera movimentos circulares, espirais e oscilações agressivas simulando o movimento humano de pulso/braço."""
    
    largura_tela, altura_tela = pyautogui.size()
    
    while MANTEM_MOUSE_MOVENDO and ATIVAR_MOVIMENTO_MOUSE == 1:
        try:
            x_centro, y_centro = pyautogui.position()
            
            # Decide aleatoriamente qual "gesto" agressivo fazer
            estilo_movimento = random.choice(["circulo_agressivo", "espiral", "sacudida_rapida"])
            
            if estilo_movimento == "circulo_agressivo":
                # Faz um movimento circular rápido com raio grande
                raio = random.randint(60, 140)
                passos = random.randint(8, 15)
                sentido = random.choice([1, -1])  # Horário ou anti-horário
                
                for i in range(passos):
                    angulo = (2 * math.pi / passos) * i * sentido
                    # Adiciona um "ruído/desvio" ao raio para não ser um círculo perfeito
                    ruido = random.randint(-15, 15)
                    r = max(20, raio + ruido)
                    
                    nx = x_centro + int(r * math.cos(angulo))
                    ny = y_centro + int(r * math.sin(angulo))
                    
                    # Limita às bordas da tela
                    nx = max(30, min(largura_tela - 30, nx))
                    ny = max(30, min(altura_tela - 30, ny))
                    
                    pyautogui.moveTo(nx, ny, duration=random.uniform(0.01, 0.03))
                    
            elif estilo_movimento == "espiral":
                # Desenha uma espiral se expandindo ou contraindo rapidamente
                passos = random.randint(10, 18)
                for i in range(passos):
                    angulo = i * 0.8
                    raio = i * random.randint(6, 12)
                    
                    nx = x_centro + int(raio * math.cos(angulo))
                    ny = y_centro + int(raio * math.sin(angulo))
                    
                    nx = max(30, min(largura_tela - 30, nx))
                    ny = max(30, min(altura_tela - 30, ny))
                    
                    pyautogui.moveTo(nx, ny, duration=random.uniform(0.01, 0.04))

            elif estilo_movimento == "sacudida_rapida":
                # Vários impulsos rápidos em zigue-zague (como se estivesse chacoalhando o mouse)
                for _ in range(random.randint(4, 8)):
                    nx = x_centro + random.randint(-120, 120)
                    ny = y_centro + random.randint(-120, 120)
                    
                    nx = max(30, min(largura_tela - 30, nx))
                    ny = max(30, min(altura_tela - 30, ny))
                    
                    pyautogui.moveTo(nx, ny, duration=random.uniform(0.02, 0.05))

            # Volta o cursor próximo à posição inicial com uma leve oscilação
            pyautogui.moveTo(
                x_centro + random.randint(-10, 10), 
                y_centro + random.randint(-10, 10), 
                duration=random.uniform(0.03, 0.08)
            )

        except Exception:
            pass

        # Intervalos imprevisíveis (às vezes rápido, às vezes uma pequena pausa)
        time.sleep(random.uniform(0.3, 1.2))

def pausa(segundos=2):
    """Pequena pausa para permitir atualização/renderização da interface."""
    time.sleep(segundos)


def esperar(driver, segundos=TEMPO_ESPERA):
    """Retorna um WebDriverWait padronizado."""
    return WebDriverWait(driver, segundos)


def verificar_pagina(driver):
    """
    Verifica se o navegador aparentemente caiu em uma página
    interna de erro do Chrome.

    Não tenta atualizar automaticamente, pois isso pode repetir
    um POST/PostBack ou alterar o estado da página ASP.NET.
    """

    url = driver.current_url

    if url.startswith("chrome-error://"):
        raise RuntimeError(
            "O Chrome entrou em uma página de erro de conexão.\n"
            f"URL atual: {url}"
        )


# ============================================================
# CONEXÃO COM CHROME EXISTENTE
# ============================================================

def aguardar_pagina_portal(driver, timeout=90):
    """
    Aguarda uma eventual página intermediária de validação
    do portal terminar.

    Não atualiza a página, não clica no challenge e não tenta
    contorná-lo. Apenas espera o próprio portal concluir.
    """

    print("Verificando se a página está disponível...")

    inicio = time.time()
    challenge_informado = False

    while time.time() - inicio < timeout:

        try:
            titulo = driver.title.lower()
            url = driver.current_url.lower()
            pagina = driver.page_source.lower()

            # Página interna de erro do Chrome
            if url.startswith("chrome-error://"):
                raise RuntimeError(
                    "O navegador entrou em uma página de erro de conexão.\n"
                    f"URL atual: {driver.current_url}"
                )

            # Verifica se estamos na página intermediária
            challenge = (
                "challenge validation" in titulo
                or "processando sua solicitação" in pagina
                or "sec-cpt-if" in pagina
            )

            if challenge:

                if not challenge_informado:
                    print(
                        "Validação intermediária detectada. "
                        "Aguardando o próprio portal liberar..."
                    )

                    challenge_informado = True

                time.sleep(3)
                continue

            print("Página do portal disponível.")
            return

        except RuntimeError:
            raise

        except Exception:
            time.sleep(2)

    raise TimeoutError(
        "A validação do portal não terminou dentro de "
        f"{timeout} segundos. O processo foi interrompido."
    )



def conectar_chrome():
    print("Conectando ao Chrome...")

    options = Options()

    options.add_experimental_option(
        "debuggerAddress",
        "127.0.0.1:9222"
    )

    driver = webdriver.Chrome(options=options)

    print("Chrome conectado com sucesso.")

    return driver


# ============================================================
# NAVEGAÇÃO PRINCIPAL
# ============================================================

def abrir_posicao_consorciado(driver):

    print("\n[1] Abrindo Atendimento...")

    atendimento = esperar(driver).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//div[@id='tabs_principal']//span[contains(text(),'Atendimento')]"
            " | "
            "//div[@id='tabs_principal']//a[contains(text(),'Atendimento')]"
        ))
    )

    atendimento.click()

    pausa()

    print("[2] Abrindo Atendimento a Clientes...")

    atendimento_clientes = esperar(driver).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//div[@id='subs']//a[contains(text(),'Atendimento a Clientes')]"
        ))
    )

    atendimento_clientes.click()

    pausa()

    print("[3] Abrindo Posição do Consorciado...")

    posicao = esperar(driver).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//*[contains(text(),'Posição do Consorciado')]"
        ))
    )

    posicao.click()

    pausa()


# ============================================================
# LOCALIZAÇÃO DO GRUPO / COTA
# ============================================================

def localizar_cota(driver, grupo, cota):

    print(
        f"\n[4] Localizando Grupo {grupo} / Cota {cota}..."
    )

    campo_grupo = esperar(driver).until(
        EC.presence_of_element_located((
            By.ID,
            "ctl00_Conteudo_edtGrupo"
        ))
    )

    campo_grupo.clear()
    campo_grupo.send_keys(grupo)

    campo_cota = driver.find_element(
        By.ID,
        "ctl00_Conteudo_edtCota"
    )

    campo_cota.clear()
    campo_cota.send_keys(cota)

    pausa(1)

    botao = esperar(driver).until(
        EC.element_to_be_clickable((
            By.ID,
            "ctl00_Conteudo_btnLocalizar"
        ))
    )

    botao.click()

    print("Aguardando dados do cliente...")

    esperar(driver).until(
        EC.presence_of_element_located((
            By.XPATH,
            "//td[contains(text(),'Cota:')]"
            " | "
            "//*[contains(text(),'Plano de Venda')]"
        ))
    )

    print("Cliente localizado.")

    pausa()


# ============================================================
# EMISSÃO DE COBRANÇA
# ============================================================

def abrir_emissao_cobranca(driver):

    print("\n[5] Abrindo Emissão de Cobrança...")

    botao = esperar(driver).until(
        EC.element_to_be_clickable((
            By.XPATH,
            "//a[contains(@id,'hlkFormulario') "
            "and contains(text(),'Emissão de Cobrança')]"
        ))
    )

    botao.click()

    print("Aguardando abertura da tela...")

    # Se aparecer Challenge Validation,
    # aguarda o próprio portal concluir.
    aguardar_pagina_portal(
        driver,
        timeout=90
    )

    verificar_pagina(driver)

    # ----------------------------------------------------
    # A página possui layouts diferentes dependendo
    # da situação da cota.
    #
    # Portanto, não exigimos mais que exista
    # edtDataVencimentoInicial ou div_UnificarParcelas.
    # ----------------------------------------------------

    print("Identificando layout da tela de cobrança...")

    esperar(driver, 30).until(
        lambda d: (
            len(d.find_elements(
                By.ID,
                "ctl00_Conteudo_edtDataVencimentoInicial"
            )) > 0
            or
            len(d.find_elements(
                By.ID,
                "ctl00_Conteudo_grdBoleto_Avulso"
            )) > 0
            or
            len(d.find_elements(
                By.ID,
                "ctl00_Conteudo_btnLocalizar"
            )) > 0
        )
    )

    print("Tela de Emissão de Cobrança carregada.")


# ============================================================
# CÁLCULO DAS DATAS
# ============================================================

def calcular_periodo_proximo_mes():

    hoje = datetime.now()

    if hoje.month == 12:
        mes = 1
        ano = hoje.year + 1

    else:
        mes = hoje.month + 1
        ano = hoje.year

    data_inicio = f"01/{mes:02d}/{ano}"
    data_fim = f"28/{mes:02d}/{ano}"

    return data_inicio, data_fim


# ============================================================
# UNIFICAÇÃO DAS PARCELAS
# ============================================================

def configurar_unificacao(driver):

    print(
        "\n[6] Verificando opção "
        "'Listar parcelas de outras cotas'..."
    )

    elementos = driver.find_elements(
        By.ID,
        "ctl00_Conteudo_div_UnificarParcelas"
    )

    if not elementos:
        print("Opção de unificação não encontrada.")
        return False

    div = elementos[0]

    if not div.is_displayed():
        print("Opção de unificação existe, mas não está visível.")
        return False

    print("Opção de unificação encontrada.")

    try:

        checkbox = div.find_element(
            By.XPATH,
            ".//input[@type='checkbox']"
        )

        if not checkbox.is_selected():

            print("Marcando opção de unificação...")

            checkbox.click()

            pausa(2)

        else:
            print("Opção já estava marcada.")

        return True

    except Exception as erro:

        print(
            "Não foi possível marcar a opção "
            f"de unificação: {erro}"
        )

        return False


# ============================================================
# PREENCHIMENTO DAS DATAS
# ============================================================

def preencher_datas(driver, data_inicio, data_fim):

    campos_inicio = driver.find_elements(
        By.ID,
        "ctl00_Conteudo_edtDataVencimentoInicial"
    )

    campos_fim = driver.find_elements(
        By.ID,
        "ctl00_Conteudo_edtDataVencimentoFinal"
    )

    if not campos_inicio or not campos_fim:

        print(
            "\n[7] Campos de período não disponíveis "
            "neste layout."
        )

        print(
            "O portal já apresentou as pendências "
            "diretamente."
        )

        return False

    print(
        f"\n[7] Preenchendo período: "
        f"{data_inicio} até {data_fim}"
    )

    # Campo DATA INICIAL
    campo_inicio = esperar(driver).until(
        EC.presence_of_element_located((
            By.ID,
            "ctl00_Conteudo_edtDataVencimentoInicial"
        ))
    )

    # Campo DATA FINAL
    campo_fim = esperar(driver).until(
        EC.presence_of_element_located((
            By.ID,
            "ctl00_Conteudo_edtDataVencimentoFinal"
        ))
    )

    # JavaScript para alterar o valor e disparar os eventos
    script = """
        const campo = arguments[0];
        const valor = arguments[1];

        campo.focus();

        campo.value = valor;

        campo.dispatchEvent(
            new Event('input', { bubbles: true })
        );

        campo.dispatchEvent(
            new Event('change', { bubbles: true })
        );

        campo.dispatchEvent(
            new Event('blur', { bubbles: true })
        );
    """

    # Preenche data inicial
    driver.execute_script(
        script,
        campo_inicio,
        data_inicio
    )

    # Preenche data final
    driver.execute_script(
        script,
        campo_fim,
        data_fim
    )

    time.sleep(1)

    # Confere o que realmente ficou nos campos
    valor_inicio = campo_inicio.get_attribute("value")
    valor_fim = campo_fim.get_attribute("value")

    print(f"Data inicial preenchida: {valor_inicio}")
    print(f"Data final preenchida:   {valor_fim}")

    return True
# ============================================================
# LOCALIZAR PENDÊNCIAS
# ============================================================

# ============================================================
# LOCALIZAR PENDÊNCIAS
# ============================================================

# ============================================================
# LOCALIZAR PENDÊNCIAS
# ============================================================

def localizar_pendencias(driver):

    print("\n[8] Localizando pendências...")

    # Aguarda validações pendentes
    aguardar_pagina_portal(driver, timeout=90)

    # Localiza o botão "Localizar pendências"
    botao = esperar(driver, 30).until(
        EC.presence_of_element_located((
            By.ID,
            "ctl00_Conteudo_btnLocalizar"
        ))
    )

    # Rola a tela até o botão
    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        botao
    )

    pausa(1)

    print("Clicando em 'Localizar pendências'...")

    # Clique forçado via JavaScript para disparar o PostBack do ASP.NET
    driver.execute_script("arguments[0].click();", botao)

    print("Clique efetuado. Aguardando atualização do portal...")

    # Tempo para o PostBack iniciar e processar
    pausa(4)
    aguardar_pagina_portal(driver, timeout=90)

    # Aguarda a tabela atualizada estar pronta na tela
    esperar(driver, 60).until(
        EC.presence_of_element_located((
            By.ID,
            "ctl00_Conteudo_grdBoleto_Avulso"
        ))
    )

    print("Tabela de pendências atualizada com sucesso.")

# ============================================================
# MAPEAMENTO DAS PARCELAS
# ============================================================

def mapear_parcelas(driver):

    print(
        "\n[9] Mapeando parcelas com histórico 001-0..."
    )

    tabela = esperar(driver).until(
        EC.presence_of_element_located((
            By.ID,
            "ctl00_Conteudo_grdBoleto_Avulso"
        ))
    )

    linhas = tabela.find_elements(
        By.XPATH,
        ".//tr[td]"
    )

    mapa = {}

    for linha in linhas:

        colunas = linha.find_elements(
            By.TAG_NAME,
            "td"
        )

        if len(colunas) < 5:
            continue

        historico = colunas[3].text.strip()
        vencimento = colunas[4].text.strip()

        if "001-0" not in historico:
            continue

        try:

            checkbox = colunas[0].find_element(
                By.TAG_NAME,
                "input"
            )

            checkbox_id = checkbox.get_attribute("id")
            tipo_input = checkbox.get_attribute("type")

            print(
                f"Encontrado: "
                f"histórico={historico} | "
                f"vencimento={vencimento} | "
                f"id={checkbox_id} | "
                f"type={tipo_input}"
            )

        except Exception:
            continue

        if not checkbox_id:
            continue

        if vencimento not in mapa:
            mapa[vencimento] = []

        mapa[vencimento].append(
            checkbox_id
        )

    print(
        f"{len(mapa)} data(s) de vencimento "
        "encontrada(s)."
    )

    for data, ids in mapa.items():

        print(
            f" - {data}: "
            f"{len(ids)} parcela(s)"
        )

    return mapa


# ============================================================
# EMISSÃO
# ============================================================

# ============================================================
# EMISSÃO
# ============================================================

def fechar_janelas_secundarias(driver, aba_principal):
    """Varre e fecha qualquer aba ou janela popup que tenha surgido."""
    try:
        janelas = driver.window_handles
        for janela in janelas:
            if janela != aba_principal:
                print("Lidando com janela secundária de download/boleto...")
                driver.switch_to.window(janela)
                pausa(2)  # dá tempo de o download disparar
                driver.close()
                print("Janela secundária fechada com sucesso.")
        
        # Volta para a janela do portal
        driver.switch_to.window(aba_principal)
    except Exception as e:
        print(f"Aviso ao tentar fechar janelas: {e}")
        driver.switch_to.window(aba_principal)


def emitir_boletos(driver, mapa):

    print("\n[10] Iniciando emissão...")

    # Guarda a aba principal (onde fica a tela do portal)
    aba_principal = driver.current_window_handle

    pausa(5)

    for vencimento, ids in mapa.items():

        print("\n" + "-" * 50)
        print(f"Processando vencimento: {vencimento}")
        print(f"Quantidade de parcelas: {len(ids)}")

        # Antes de começar um novo grupo
        aguardar_pagina_portal(driver, timeout=90)
        verificar_pagina(driver)

        pausa(3)

        # ====================================================
        # MARCAR CHECKBOXES
        # ====================================================

        for numero, checkbox_id in enumerate(ids, start=1):

            print(f"Marcando parcela {numero}/{len(ids)}...")

            aguardar_pagina_portal(driver, timeout=90)
            verificar_pagina(driver)

            checkbox = esperar(driver, 30).until(
                EC.element_to_be_clickable((
                    By.ID,
                    checkbox_id
                ))
            )

            if not checkbox.is_selected():
                checkbox.click()

            print("OK.")
            pausa(3)
            verificar_pagina(driver)

        print("Todas as parcelas da data foram selecionadas.")

        # ====================================================
        # PREPARAR EMISSÃO
        # ====================================================

        print("\nParcelas selecionadas. Preparando emissão...")

        pausa(5)
        aguardar_pagina_portal(driver, timeout=120)
        verificar_pagina(driver)

        # ====================================================
        # LOCALIZAR E CLICAR NO BOTÃO DE EMISSÃO
        # ====================================================

        print("Localizando botão 'Emitir Cobrança'...")

        for tentativa in range(1, 4):

            try:
                botao_emitir = esperar(driver, 30).until(
                    EC.element_to_be_clickable((
                        By.ID,
                        "ctl00_Conteudo_btnEmitir"
                    ))
                )

                print("Botão disponível. Clicando em 'Emitir Cobrança'...")
                pausa(1)

                botao_emitir.click()

                print("Solicitação enviada. Aguardando abertura do boleto...")
                break

            except StaleElementReferenceException:
                print(f"O DOM foi atualizado (tentativa {tentativa}/3)...")
                if tentativa == 3:
                    raise
                pausa(2)

        # ====================================================
        # FECHAR A NOVA JANELA DO BOLETO / DOWNLOAD
        # ====================================================

        print("Aguardando geração do boleto...")
        pausa(6)  # Pausa para dar tempo da popup abrir e baixar

        # Fecha qualquer janela secundária popup que tenha aberto
        fechar_janelas_secundarias(driver, aba_principal)

        # ====================================================
        # FINALIZAÇÃO DO VENCIMENTO
        # ====================================================

        pausa(5)
        verificar_pagina(driver)
        aguardar_pagina_portal(driver, timeout=120)
        verificar_pagina(driver)

        print(f"Emissão de {vencimento} concluída e janela limpa.")

        # Pausa antes do próximo vencimento
        pausa(5)

# ============================================================
# PROGRAMA PRINCIPAL
# ============================================================

def main():
    global MANTEM_MOUSE_MOVENDO
    driver = None

    # Inicia o movimento do cursor em segundo plano
    thread_mouse = threading.Thread(target=mover_cursor_continuamente, daemon=True)
    thread_mouse.start()
    print("[SISTEMA] Movimento de cursor ativado em segundo plano.")

    try:

        driver = conectar_chrome()

        abrir_posicao_consorciado(driver)

        localizar_cota(
            driver,
            GRUPO_BUSCA,
            COTA_BUSCA
        )

        abrir_emissao_cobranca(driver)

        # Tenta configurar a unificação.
        # Se o cliente possuir apenas uma cota, a opção pode não existir.
        configurar_unificacao(driver)

        # As datas devem ser preenchidas independentemente
        # de existir ou não a opção de unificação.
        data_inicio, data_fim = (
            calcular_periodo_proximo_mes()
        )

        datas_preenchidas = preencher_datas(
            driver,
            data_inicio,
            data_fim
        )

        # Verifica se o próprio portal já apresentou
        # a tabela de pendências.
        # CÓDIGO NOVO (SEMPRE EXECUTA):
        localizar_pendencias(driver)

        mapa = mapear_parcelas(driver)

        if not mapa:

            print(
                "\nNenhuma parcela 001-0 "
                "foi encontrada."
            )

            # Desliga a thread do rato antes de sair
            MANTEM_MOUSE_MOVENDO = False
            return

        emitir_boletos(
            driver,
            mapa
        )

        print(
            "\n========================================"
        )

        print(
            "PROCESSO CONCLUÍDO COM SUCESSO"
        )

        print(
            "========================================"
        )

    except TimeoutException as erro:

        print(
            "\n[TIMEOUT]"
        )

        print(
            "Um elemento esperado não apareceu "
            "dentro do tempo limite."
        )

        print(
            f"Detalhes: {erro}"
        )

        if driver:

            print(
                f"URL atual: {driver.current_url}"
            )

    except RuntimeError as erro:

        print(
            "\n[ERRO DE NAVEGAÇÃO]"
        )

        print(erro)

    except Exception as erro:

        print(
            f"\n[ERRO] {type(erro).__name__}: "
            f"{erro}"
        )

        if driver:

            try:
                print(
                    f"URL atual: {driver.current_url}"
                )
            except Exception:
                pass

    finally:
        # Garante que a thread do rato é desativada quando o script termina
        MANTEM_MOUSE_MOVENDO = False

if __name__ == "__main__":
    main()