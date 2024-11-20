import os

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

@pytest.fixture(scope="session")
def driver():
    """Configura o WebDriver para todos os testes."""
    driver = webdriver.Chrome()  # Substitua pelo WebDriver de sua preferência
    yield driver
    driver.quit()

@pytest.fixture(scope="session")
def logged_in_driver(driver):
    """Realiza login no Drupal com credenciais obtidas de variáveis de ambiente."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")
    username = os.getenv("DRUPAL_USERNAME")  # Nome de usuário padrão: joao
    password = os.getenv("DRUPAL_PASSWORD")

    assert username and password, "As variáveis DRUPAL_USERNAME e DRUPAL_PASSWORD precisam estar configuradas."

    driver.get(f"{base_url}/user/login")

    # Preenche os campos de login
    driver.find_element(By.ID, "edit-name").send_keys(username)
    driver.find_element(By.ID, "edit-pass").send_keys(password)
    driver.find_element(By.ID, "edit-pass").submit()

    # Aguarda o redirecionamento pós-login
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".page-title"))
    )
    return driver


def test_create_imovel(logged_in_driver):
    """Testa a criação de um novo imóvel no Drupal."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")

    logged_in_driver.get(f"{base_url}/node/add/imovel")

    # Aguarda o carregamento do formulário
    WebDriverWait(logged_in_driver, 10).until(
        EC.presence_of_element_located((By.ID, "node-imovel-form"))
    )

    # Localiza o formulário pelo ID
    imovel_form = logged_in_driver.find_element(By.ID, "node-imovel-form")

    # Preenche o campo Título
    titulo_input = imovel_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-title-0-value']")
    titulo_input.send_keys("Imóvel Teste")

    # Preenche o campo Bairro
    bairro_input = imovel_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-field-bairro-0-value']")
    bairro_input.send_keys("Centro")

    # Preenche o campo Cidade
    cidade_input = imovel_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-field-cidade-0-value']")
    cidade_input.send_keys("São Paulo")

    # Seleciona o Estado
    estado_select = imovel_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-field-estado']")
    Select(estado_select).select_by_visible_text("São Paulo")

    # Preenche o campo Rua
    rua_input = imovel_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-field-rua-0-value']")
    rua_input.send_keys("Rua Teste")

    # Preenche o campo Número
    numero_input = imovel_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-field-numero-0-value']")
    numero_input.send_keys("123")

    # Seleciona o Tipo do Imóvel
    tipo_select = imovel_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-field-tipo']")
    Select(tipo_select).select_by_visible_text("Apartamento")

    # Seleciona o Status
    status_select = imovel_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-field-status']")
    Select(status_select).select_by_visible_text("Disponível")

    # Localiza e clica no botão de submissão
    submit_button = imovel_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-submit']")
    try:
        submit_button.click()
        print("Botão clicado com sucesso!")
    except Exception as e:
        print(f"Erro ao clicar no botão de submissão: {e}")

    # Aguarda a mensagem de confirmação
    WebDriverWait(logged_in_driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".messages--status"))
    )

    # Verifica a mensagem de sucesso
    success_message = logged_in_driver.find_element(By.CSS_SELECTOR, ".messages--status").text
    assert "foi criado" in success_message, "O imóvel não foi criado com sucesso."
    print("Imóvel criado com sucesso!")
