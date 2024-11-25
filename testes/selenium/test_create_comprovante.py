import os
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
import re

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
    username = os.getenv("DRUPAL_USERNAME_CLIENTE", "joao")  # Nome de usuário padrão: joao
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
    """Testa a criação de um novo comprovante no Drupal e aguarda pela mensagem de confirmação."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")
    file_path = os.getenv("DRUPAL_FILE_PATH", r"C:\Users\huand\dummy.pdf")

    assert os.path.exists(file_path), f"O arquivo especificado em DRUPAL_FILE_PATH não foi encontrado: {file_path}"

    logged_in_driver.get(f"{base_url}/form/registro-de-comprovante")

    # Aguarda o carregamento do formulário
    WebDriverWait(logged_in_driver, 10).until(
        EC.presence_of_element_located((By.ID, "webform-submission-registro-de-comprovante-add-form"))
    )

    # Localiza o formulário pelo ID
    comprovante_form = logged_in_driver.find_element(By.ID, "webform-submission-registro-de-comprovante-add-form")

    # Seleciona a categoria
    categoria_select = comprovante_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-categoria']")
    Select(categoria_select).select_by_visible_text("Energia")

    # Faz upload de um arquivo
    file_input = comprovante_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-arquivo-upload']")
    file_input.send_keys(file_path)

    # Aguarda até que o link do arquivo carregado apareça
    WebDriverWait(logged_in_driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "a[href*='/sites/default/files/webform/registro_de_comprovante/']"))
    )
    print("Arquivo carregado com sucesso!")

    # Localiza e clica no botão de submissão
    submit_button = comprovante_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-submit']")
    try:
        submit_button.click()
        print("Botão clicado com sucesso!")
    except Exception as e:
        print(f"Erro ao clicar no botão de submissão: {e}")

    # Aguarda a mensagem de confirmação aparecer
    confirmation_message = WebDriverWait(logged_in_driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".webform-confirmation__message"))
    )
    assert "O comprovante foi enviado com sucesso" in confirmation_message.text, \
        f"Mensagem de confirmação não encontrada ou incorreta: {confirmation_message.text}"
    print("Mensagem de confirmação recebida com sucesso!")
