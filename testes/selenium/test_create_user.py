import os
import pytest
from faker import Faker
from cpf_generator import CPF  # Corrigido: Função para gerar CPF válido
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

faker = Faker()

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
    username = os.getenv("DRUPAL_USERNAME")  # Nome de usuário padrão
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

def test_create_user_with_profile(logged_in_driver):
    """Testa a criação de um novo usuário no Drupal com perfil de cliente associado."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")

    logged_in_driver.get(f"{base_url}/admin/people/create")

    # Aguarda o carregamento do formulário
    WebDriverWait(logged_in_driver, 10).until(
        EC.presence_of_element_located((By.ID, "user-register-form"))
    )

    # Localiza o formulário pelo ID
    user_form = logged_in_driver.find_element(By.ID, "user-register-form")

    # Gera dados aleatórios com Faker e CPF com cpf-generator
    random_email = faker.email()
    random_username = faker.user_name()
    random_phone = faker.phone_number()
    random_cpf = CPF.generate()  # Gera um CPF válido
    random_birthdate = faker.date_of_birth(minimum_age=18, maximum_age=100).strftime("%d-%m-%Y")
    # Preenche o campo Email
    email_input = user_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-mail']")
    email_input.send_keys(random_email)

    # Preenche o campo Nome de Usuário
    username_input = user_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-name']")
    username_input.send_keys(random_username)

    # Preenche o campo Senha
    password_input = user_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-pass-pass1']")
    password_input.send_keys("Test@123")

    # Confirma a Senha
    confirm_password_input = user_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-pass-pass2']")
    confirm_password_input.send_keys("Test@123")

    # Preenche o campo Telefone no perfil do cliente
    telefone_input = user_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-cliente-profiles-0-entity-field-telefone-0-value']")
    telefone_input.send_keys(random_phone)

    # Preenche o campo CPF no perfil do cliente
    cpf_input = user_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-cliente-profiles-0-entity-field-cpf-0-value']")
    cpf_input.send_keys(random_cpf)

    # Preenche o campo Data de Nascimento no perfil do cliente
    nascimento_input = user_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-cliente-profiles-0-entity-field-data-de-nascimento-0-value-date']")
    nascimento_input.send_keys(random_birthdate)

    # Seleciona o Imóvel da combobox
    imovel_select = user_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-cliente-profiles-0-entity-field-nome-de-imovel']")
    Select(imovel_select).select_by_visible_text("Imóvel Teste")

    # Localiza e clica no botão de submissão
    submit_button = user_form.find_element(By.CSS_SELECTOR, "[data-drupal-selector='edit-submit']")
    try:
        submit_button.click()
        print("Botão clicado com sucesso!")
    except Exception as e:
        print(f"Erro ao clicar no botão de submissão: {e}")

    # Aguarda a mensagem de confirmação
    # Aguarda o elemento de mensagem de status
    WebDriverWait(logged_in_driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-drupal-selector='messages']"))
    )

    # Verifica a mensagem de sucesso
    success_message = logged_in_driver.find_element(By.CSS_SELECTOR, "div.messages__content").text
    expected_message = "Criada uma nova conta de usuário para"
    assert expected_message in success_message, f"A mensagem esperada não foi encontrada. Recebido: {success_message}"
    print("Usuário criado com sucesso!")
