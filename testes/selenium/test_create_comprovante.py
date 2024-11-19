import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture(scope="session")
def driver():
    """Configura o WebDriver para todos os testes."""
    driver = webdriver.Chrome()  # Substitua pelo WebDriver de sua preferência
    yield driver
    driver.quit()

@pytest.fixture(scope="session")
def logged_in_driver(driver):
    """Realiza login no Drupal e retorna o driver logado."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")
    username = os.getenv("DRUPAL_USERNAME")
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

def test_create_comprovante(logged_in_driver):
    """Testa a criação de um novo comprovante no Drupal."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")
    logged_in_driver.get(f"{base_url}/node/add/comprovantes")

    # Aguarda o carregamento do formulário
    WebDriverWait(logged_in_driver, 10).until(
        EC.presence_of_element_located((By.ID, "edit-field-tipodocumento-wrapper"))
    )

    # Seleciona o tipo de comprovante
    tipo_field = Select(logged_in_driver.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-field-tipodocumento'] select"))
    tipo_field.select_by_visible_text("Energia")  # Substitua pela opção desejada

    # Verifica se o campo "Data de Envio" está preenchido automaticamente
    data_envio_wrapper = logged_in_driver.find_element(By.ID, "edit-field-data-de-envio-wrapper")
    data_value = data_envio_wrapper.find_element(By.CSS_SELECTOR, "input").get_attribute("value")
    assert data_value, "O campo 'Data de Envio' não está preenchido automaticamente."

    # Faz upload de um arquivo
    file_wrapper = logged_in_driver.find_element(By.ID, "edit-field-arquivo-wrapper")
    file_input = file_wrapper.find_element(By.CSS_SELECTOR, "input[type='file']")
    file_path = os.path.abspath("caminho/para/seu/arquivo.pdf")  # Substitua pelo caminho real do arquivo
    file_input.send_keys(file_path)

    # Aguarda o upload do arquivo
    WebDriverWait(logged_in_driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".file-uploaded"))
    )

    # Submete o formulário
    logged_in_driver.find_element(By.ID, "edit-submit").click()

    # Aguarda a mensagem de confirmação
    WebDriverWait(logged_in_driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".messages--status"))
    )

    # Verifica se a mensagem de sucesso está presente
    success_message = logged_in_driver.find_element(By.CSS_SELECTOR, ".messages--status").text
    assert "foi criado" in success_message, "O comprovante não foi criado com sucesso."

    # Verifica se o comprovante aparece na lista
    logged_in_driver.get(f"{base_url}/documents-list")
    WebDriverWait(logged_in_driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table.views-table"))
    )
    table = logged_in_driver.find_element(By.CSS_SELECTOR, "table.views-table")
    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
    assert any("Energia" in row.text for row in rows), "O comprovante não aparece na lista."
