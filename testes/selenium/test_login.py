import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

@pytest.fixture
def driver():
    # Configurar o WebDriver
    driver = webdriver.Chrome()
    yield driver
    # Fechar o navegador após o teste
    driver.quit()

def test_login(driver):
    # Acessar o site
    driver.get("http://localhost/user/login")

    # Localizar os campos de login e senha
    username = driver.find_element(By.ID, "edit-name")
    password = driver.find_element(By.ID, "edit-pass")

    # Inserir as credenciais e submeter
    username.send_keys("imobiliaria")
    password.send_keys("gp2024123")
    password.send_keys(Keys.RETURN)

    # Aguarde carregar a página e verificar se o login foi bem-sucedido
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    assert "Início" in driver.page_source  # Substitua por um texto ou elemento específico do site

def test_login_invalid_text_check(driver):
    # Acessar o site
    driver.get("http://localhost/user/login")

    # Localizar os campos de login e senha
    username = driver.find_element(By.ID, "edit-name")
    password = driver.find_element(By.ID, "edit-pass")

    # Inserir credenciais inválidas
    username.send_keys("usuario_invalido")
    password.send_keys("senha_incorreta")
    password.send_keys(Keys.RETURN)

    # Aguarde carregar a página
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    # Verificar se o texto de erro esperado está presente na página
    page_text = driver.find_element(By.TAG_NAME, "body").text
    assert "Credenciais inválidas" in page_text or "Nome de usuário ou senha não reconhecidos." in page_text  # Adapte o texto conforme seu site
