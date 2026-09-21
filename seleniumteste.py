import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 1. Conexão com o Chrome aberto
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)

print("Conectado ao Chrome com sucesso!")

try:
    # ==========================================================================
    # PASSO 1: NAVEGAÇÃO PELOS MENUS
    # ==========================================================================
    print("\n[1/4] Clicando na aba 'Atendimento'...")
    menu_atendimento = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@id='tabs_principal']//span[contains(text(), 'Atendimento')] | //div[@id='tabs_principal']//a[contains(text(), 'Atendimento')]"))
    )
    menu_atendimento.click()

    print("[2/4] Clicando em 'Atendimento a Clientes'...")
    sub_atendimento = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//div[@id='subs']//a[contains(text(), 'Atendimento a Clientes')]"))
    )
    driver.execute_script("arguments[0].click();", sub_atendimento)
    time.sleep(2)

    print("[3/4] Clicando em 'Posição do Consorciado'...")
    posicao_consorciado = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[contains(text(), 'Posição do Consorciado')]"))
    )
    posicao_consorciado.click()

    # ==========================================================================
    # PASSO 2: PREENCHIMENTO DO GRUPO E COTA
    # ==========================================================================
    grupo_busca = "007271"
    cota_busca = "0368"

    print(f"\n[4/4] Preenchendo Grupo ({grupo_busca}) e Cota ({cota_busca})...")
    campo_grupo = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "ctl00_Conteudo_edtGrupo"))
    )
    campo_grupo.clear()
    campo_grupo.send_keys(grupo_busca)

    campo_cota = driver.find_element(By.ID, "ctl00_Conteudo_edtCota")
    campo_cota.clear()
    campo_cota.send_keys(cota_busca)

    print("Clicando em Localizar...")
    btn_localizar = driver.find_element(By.ID, "ctl00_Conteudo_btnLocalizar")
    btn_localizar.click()

    # ==========================================================================
    # PASSO 3: NAVEGAÇÃO PARA 'EMISSÃO DE COBRANÇA' (TELA DE BOLETOS)
    # ==========================================================================
    print("\n[Passo 5] Aguardando o resultado da busca (painel do cliente)...")
    
    # 1. Espera obrigatoriamente aparecer a tabela de dados do consorciado
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.XPATH, "//td[contains(text(), 'Cota:')] | //*[contains(text(), 'Plano de Venda')]"))
    )
    print("Dados do cliente localizados!")

    # 2. Pausa tática para garantir que o menu lateral 'Operações' renderizou por completo
    time.sleep(2)

    print("[Passo 6] Clicando em 'Emissão de Cobrança' no menu do cliente...")
    
    # Busca especificamente o link 'Emissão de Cobrança' que está no painel de Operações da Cota (usando o id hlkFormulario)
    btn_emissao_cobranca = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(@id, 'hlkFormulario') and contains(text(), 'Emissão de Cobrança')]"))
    )
    
    # Executa o clique nativo via JavaScript para disparar o formulário da cota
    driver.execute_script("arguments[0].click();", btn_emissao_cobranca)
    
    time.sleep(3)
    print("\nSucesso! Abrindo a tela de Emissão de Cobrança da cota.")


    # ==========================================================================
    # PASSO 4: VERIFICAÇÃO CONDICIONAL DA DIV "Listar parcelas de outras cotas"
    # ==========================================================================
    print("\n[Passo 7] Verificando existência de opções de parcelas unificadas...")
    time.sleep(2)  # Garante renderização da tela de cobrança

    # Busca o elemento por ID
    div_unificar = driver.find_elements(By.ID, "ctl00_Conteudo_div_UnificarParcelas")

    # Verifica se a DIV existe no DOM e está visível para o usuário
    if len(div_unificar) > 0 and div_unificar[0].is_displayed():
        print(" -> [DECISÃO] A opção 'Listar parcelas de outras cotas' ESTÁ PRESENTE nesta cota.")
        # Futuramente: adicione aqui o código do que fazer quando a div existir
    else:
        print(" -> [DECISÃO] A opção 'Listar parcelas de outras cotas' NÃO EXISTE para esta cota.")
        # Futuramente: adicione aqui o código para quando ela não existir

except Exception as e:
    print(f"\nErro no processo: {type(e).__name__} - {e}")