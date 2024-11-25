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
    """Testa a criação de um novo imóvel no formulário atualizado."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")

    # Acessa a página do formulário
    logged_in_driver.get(f"{base_url}/form/registro-de-imoveis")

    # Aguarda o carregamento do formulário
    WebDriverWait(logged_in_driver, 10).until(
        EC.presence_of_element_located((By.ID, "webform-submission-registro-de-imoveis-add-form"))
    )

    # Localiza o formulário pelo ID
    imovel_form = logged_in_driver.find_element(By.ID, "webform-submission-registro-de-imoveis-add-form")

    # Preenche o nome do imóvel
    nome_input = imovel_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-nome']")
    nome_input.send_keys("Imóvel Teste")

    # Seleciona o tipo do imóvel
    tipo_select = imovel_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-tipo']")
    Select(tipo_select).select_by_visible_text("Apartamento")

    # Seleciona o status do imóvel
    status_select = imovel_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-status']")
    Select(status_select).select_by_visible_text("Disponível")

    # Seleciona o estado
    estado_select = imovel_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-estado']")
    Select(estado_select).select_by_visible_text("São Paulo")

    # Preenche a cidade
    cidade_input = imovel_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-cidade']")
    cidade_input.send_keys("Campinas")

    # Preenche o bairro
    bairro_input = imovel_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-bairro']")
    bairro_input.send_keys("Centro")

    # Preenche a rua
    rua_input = imovel_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-rua']")
    rua_input.send_keys("Rua das Flores")

    # Preenche o número
    numero_input = imovel_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-numero']")
    numero_input.send_keys("123")

    # Opcional: Preenche o complemento
    complemento_input = imovel_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-complemento']")
    complemento_input.send_keys("Apto 101")

    # Não preenche o campo "locatário" se o status for "Disponível"
    if "Disponível" not in Select(status_select).first_selected_option.text:
        locatario_select = imovel_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-locatario']")
        Select(locatario_select).select_by_visible_text("João")

    # Localiza e clica no botão de submissão
    submit_button = imovel_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-submit']")
    try:
        submit_button.click()
        print("Botão clicado com sucesso!")
    except Exception as e:
        print(f"Erro ao clicar no botão de submissão: {e}")

    # Aguarda até que um link ou outra confirmação de sucesso esteja disponível (se aplicável)
    WebDriverWait(logged_in_driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/form/registro-de-imoveis']"))
    )

    print("Imóvel criado com sucesso!")
