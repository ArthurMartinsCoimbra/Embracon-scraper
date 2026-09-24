from datetime import datetime
import time
import random
import math
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException

import threading
import pyautogui

def rodador(grupo, cota):

    # Desativa a trava de canto de tela do PyAutoGUI
    pyautogui.FAILSAFE = False

    # Flag de controle da Thread do mouse
    MANTEM_MOUSE_MOVENDO = True

    # ============================================================
    # CONFIGURAÇÕES
    # ============================================================


    GRUPO_BUSCA = grupo
    COTA_BUSCA = cota

    TEMPO_ESPERA = 15

    # Troque para 0 para DESATIVAR ou 1 para ATIVAR o movimento do mouse:
    ATIVAR_MOVIMENTO_MOUSE = 0


    # ============================================================
    # FUNÇÕES AUXILIARES
    # ============================================================



    def mover_cursor_continuamente(driver=None):
            """Gera movimentos humanos restritos estritamente ao contêiner principal do portal."""
            
            while MANTEM_MOUSE_MOVENDO and ATIVAR_MOVIMENTO_MOUSE == 1:
                try:
                    # Limites padrão de segurança (área útil central da tela)
                    min_x, max_x, min_y, max_y = 150, 1100, 120, 750
                    
                    # Captura dinamicamente os limites reais do portal no navegador
                    if driver:
                        try:
                            elemento_principal = driver.find_element(By.ID, "principal")
                            localizacao = elemento_principal.location_once_scrolled_into_view
                            tamanho = elemento_principal.size
                            
                            # Margem interna de 30px para nunca escapar para o fundo cinza
                            min_x = localizacao['x'] + 30
                            max_x = localizacao['x'] + tamanho['width'] - 30
                            min_y = localizacao['y'] + 50
                            max_y = localizacao['y'] + tamanho['height'] - 50
                        except Exception:
                            pass

                    x_atual, y_atual = pyautogui.position()
                    
                    # Se o cursor estiver fora da área permitida (áreas com X), reposiciona-o suavemente para o centro
                    if x_atual < min_x or x_atual > max_x or y_atual < min_y or y_atual > max_y:
                        x_centro = (min_x + max_x) // 2
                        y_centro = (min_y + max_y) // 2
                        pyautogui.moveTo(x_centro, y_centro, duration=random.uniform(0.1, 0.2))
                        x_atual, y_atual = x_centro, y_centro

                    # Escolhe o estilo do movimento
                    estilo = random.choice(["circulo_agressivo", "espiral", "sacudida_rapida"])
                    
                    if estilo == "circulo_agressivo":
                        raio = random.randint(40, 90)
                        passos = random.randint(8, 14)
                        sentido = random.choice([1, -1])
                        
                        for i in range(passos):
                            angulo = (2 * math.pi / passos) * i * sentido
                            r = max(15, raio + random.randint(-10, 10))
                            
                            nx = x_atual + int(r * math.cos(angulo))
                            ny = y_atual + int(r * math.sin(angulo))
                            
                            # Trava o movimento dentro do contêiner principal
                            nx = max(min_x, min(max_x, nx))
                            ny = max(min_y, min(max_y, ny))
                            
                            pyautogui.moveTo(nx, ny, duration=random.uniform(0.01, 0.03))
                            
                    elif estilo == "espiral":
                        passos = random.randint(8, 15)
                        for i in range(passos):
                            angulo = i * 0.7
                            raio = i * random.randint(5, 10)
                            
                            nx = x_atual + int(raio * math.cos(angulo))
                            ny = y_atual + int(raio * math.sin(angulo))
                            
                            nx = max(min_x, min(max_x, nx))
                            ny = max(min_y, min(max_y, ny))
                            
                            pyautogui.moveTo(nx, ny, duration=random.uniform(0.01, 0.04))

                    elif estilo == "sacudida_rapida":
                        for _ in range(random.randint(3, 6)):
                            nx = x_atual + random.randint(-70, 70)
                            ny = y_atual + random.randint(-70, 70)
                            
                            nx = max(min_x, min(max_x, nx))
                            ny = max(min_y, min(max_y, ny))
                            
                            pyautogui.moveTo(nx, ny, duration=random.uniform(0.02, 0.05))

                    # Pequeno ajuste final mantendo o cursor dentro do contêiner
                    px = max(min_x, min(max_x, x_atual + random.randint(-15, 15)))
                    py = max(min_y, min(max_y, y_atual + random.randint(-15, 15)))
                    pyautogui.moveTo(px, py, duration=random.uniform(0.03, 0.07))

                except Exception:
                    pass

                time.sleep(random.uniform(0.4, 1.3))


    def clicar_com_rato_real(driver, elemento, tempo_mover=0.3):
        """
        Calcula as coordenadas reais do elemento na tela do navegador
        e movimenta o cursor físico até ele para realizar o clique real.
        """
        # Garante que o elemento está visível na área de exibição
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", elemento)
        pausa(0.5)

        # Captura a posição do elemento dentro da viewport do navegador
        rect = driver.execute_script("""
            var r = arguments[0].getBoundingClientRect();
            return {left: r.left, top: r.top, width: r.width, height: r.height};
        """, elemento)

        # Posição da janela do navegador na tela do sistema
        win_x = driver.execute_script("return window.screenX || window.screenLeft;")
        win_y = driver.execute_script("return window.screenY || window.screenTop;")
        
        # Altura das barras de topo do navegador (abas/URL)
        outer_h = driver.execute_script("return window.outerHeight;")
        inner_h = driver.execute_script("return window.innerHeight;")
        barra_topo = outer_h - inner_h if outer_h > inner_h else 85

        # Calcula o ponto central do elemento com um pequeno desvio humano aleatório
        centro_x = int(win_x + rect['left'] + (rect['width'] / 2) + random.randint(-5, 5))
        centro_y = int(win_y + barra_topo + rect['top'] + (rect['height'] / 2) + random.randint(-3, 3))

        # Move o rato suavemente e clica
        pyautogui.moveTo(centro_x, centro_y, duration=random.uniform(tempo_mover, tempo_mover + 0.2), tween=pyautogui.easeOutQuad)
        pausa(0.2)
        pyautogui.click()
        pausa(0.3)


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

        clicar_com_rato_real(driver, atendimento)

        pausa()

        print("[2] Abrindo Atendimento a Clientes...")

        atendimento_clientes = esperar(driver).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//div[@id='subs']//a[contains(text(),'Atendimento a Clientes')]"
            ))
        )

        clicar_com_rato_real(driver, atendimento_clientes)

        pausa()

        print("[3] Abrindo Posição do Consorciado...")

        posicao = esperar(driver).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//*[contains(text(),'Posição do Consorciado')]"
            ))
        )

        clicar_com_rato_real(driver, posicao)

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

        clicar_com_rato_real(driver, botao)

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

        clicar_com_rato_real(driver, botao)

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

                clicar_com_rato_real(driver, checkbox)

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

        # Clique real com PyAutoGUI
        clicar_com_rato_real(driver, botao)

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
                    clicar_com_rato_real(driver, checkbox)

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

                    clicar_com_rato_real(driver, botao_emitir)

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

    def voltar_pagina_inicial(driver):
        print("\n[11] Retornando para a Página Inicial...")

        aguardar_pagina_portal(driver, timeout=90)

        # Localiza o link ou o span da "Página Inicial" dentro do menu principal
        btn_home = esperar(driver, 30).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//div[@id='tabs_principal']//a[contains(@href, 'frmMain.aspx') or contains(., 'Página Inicial')]"
            ))
        )

        # Clique real com PyAutoGUI no menu inicial
        clicar_com_rato_real(driver, btn_home)

        pausa(3)
        aguardar_pagina_portal(driver, timeout=90)

        print("Retornado à Página Inicial com sucesso.")

    # ============================================================
    # PROGRAMA PRINCIPAL
    # ============================================================

    def main():
        nonlocal MANTEM_MOUSE_MOVENDO
        driver = None

        try:
            driver = conectar_chrome()

            # Inicia o movimento do cursor passando o driver para limitar a área
            if ATIVAR_MOVIMENTO_MOUSE == 1:
                thread_mouse = threading.Thread(
                    target=mover_cursor_continuamente, 
                    args=(driver,), 
                    daemon=True
                )
                thread_mouse.start()
                print("[SISTEMA] Movimento de cursor ativado (restrito à área útil).")

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

            # Retorna para a Página Inicial ao concluir as emissões
            voltar_pagina_inicial(driver)

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

    # Executa o fluxo principal para a cota atual
    main()

def carregar_cotas_excel(caminho_arquivo):
    df = pd.read_excel(caminho_arquivo, sheet_name='Ajustado', dtype=str)
    
    lista_venc_10 = []
    lista_venc_15 = []
    lista_venc_20 = []
    
    for index, row in df.iterrows():
        total_colunas = len(row)

        # Venc 10 -> Colunas E e F (Índices 4 e 5)
        if total_colunas > 5:
            grupo_10 = str(row.iloc[5]).strip()
            cota_10 = str(row.iloc[6]).strip()
            if grupo_10 not in ['nan', 'Grupo', 'None', 'Venc 10'] and cota_10 not in ['nan', 'Cota', 'None']:
                lista_venc_10.append({"grupo": grupo_10.zfill(6), "cota": cota_10.zfill(4)})

        # Venc 15 -> Colunas I e J (Índices 8 e 9)
        if total_colunas > 9:
            grupo_15 = str(row.iloc[8]).strip()
            cota_15 = str(row.iloc[9]).strip()
            if grupo_15 not in ['nan', 'Grupo', 'None', 'Venc 15'] and cota_15 not in ['nan', 'Cota', 'None']:
                lista_venc_15.append({"grupo": grupo_15.zfill(6), "cota": cota_15.zfill(4)})

        # Venc 20 -> Colunas L e M (Índices 11 e 12)
        if total_colunas > 12:
            grupo_20 = str(row.iloc[11]).strip()
            cota_20 = str(row.iloc[12]).strip()
            if grupo_20 not in ['nan', 'Grupo', 'None', 'Venc 20'] and cota_20 not in ['nan', 'Cota', 'None']:
                lista_venc_20.append({"grupo": grupo_20.zfill(6), "cota": cota_20.zfill(4)})

    return lista_venc_10, lista_venc_15, lista_venc_20

# ============================================================
# EXECUÇÃO DO FLUXO
# ============================================================

CAMINHO_EXCEL = "C:\\Users\\Dell\\Downloads\\Cotas.xlsx"  # Altere para o nome/caminho do seu arquivo

# Carrega as 3 listas
venc_10, venc_15, venc_20 = carregar_cotas_excel(CAMINHO_EXCEL)

print(f"Total Venc 10: {len(venc_10)} item(ns)")
print(f"Total Venc 15: {len(venc_15)} item(ns)")
print(f"Total Venc 20: {len(venc_20)} item(ns)")


# Exemplo: Executando apenas as cotas do Vencimento 10
print("\n--- INICIANDO PROCESSAMENTO VENCIMENTO 10 ---")
for item in venc_10:
    print(f"\nProcessando Grupo: {item['grupo']} | Cota: {item['cota']}")
    rodador(item['grupo'], item['cota'])

# Descomente abaixo para rodar as outras listas sequencialmente se desejar:
# print("\n--- INICIANDO PROCESSAMENTO VENCIMENTO 15 ---")
# for item in venc_15:
#     rodador(item['grupo'], item['cota'])

# print("\n--- INICIANDO PROCESSAMENTO VENCIMENTO 20 ---")
# for item in venc_20:
#     rodador(item['grupo'], item['cota'])