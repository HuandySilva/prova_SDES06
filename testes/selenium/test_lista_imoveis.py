import pytest
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Fixture para configurar o WebDriver
@pytest.fixture(scope="session")
def driver():
    """Configura o WebDriver para todos os testes (login único)."""
    driver = webdriver.Chrome()  # Substitua pelo WebDriver que preferir
    yield driver
    driver.quit()

# Fixture para realizar login uma vez
@pytest.fixture(scope="session")
def logged_in_driver(driver):
    """Faz login uma vez e mantém a sessão para todos os testes."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")  # URL padrão é localhost
    username = os.getenv("DRUPAL_USERNAME")
    password = os.getenv("DRUPAL_PASSWORD")

    assert username and password, "As variáveis DRUPAL_USERNAME e DRUPAL_PASSWORD precisam estar configuradas."

    print("Realizando login...")
    driver.get(f"{base_url}/user/login")

    # Preencher campos de login e senha
    driver.find_element(By.ID, "edit-name").send_keys(username)
    driver.find_element(By.ID, "edit-pass").send_keys(password)
    driver.find_element(By.ID, "edit-pass").send_keys(Keys.RETURN)

    # Esperar redirecionamento pós-login
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".page-title"))  # Ajuste conforme necessário
    )
    print("Login realizado com sucesso!")
    return driver

# Teste para verificar se a página da view pode ser acessada
def test_view_page_access(logged_in_driver):
    """Testa se a página da View '/properties-list' pode ser acessada."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")
    logged_in_driver.get(f"{base_url}/properties-list")
    assert "Imóveis" in logged_in_driver.title, "O título da página da View '/properties-list' está incorreto."

# Teste para verificar se a tabela da View existe
def test_view_table_exists(logged_in_driver):
    """Testa se a tabela da View '/properties-list' existe."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")
    logged_in_driver.get(f"{base_url}/properties-list")
    table = logged_in_driver.find_element(By.CSS_SELECTOR, "table.views-table")
    assert table is not None, "A tabela da View '/properties-list' não foi encontrada."

# Teste para verificar se a tabela contém linhas
def test_view_table_has_rows(logged_in_driver):
    """Testa se a tabela da View '/properties-list' contém linhas."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")
    logged_in_driver.get(f"{base_url}/properties-list")
    table = logged_in_driver.find_element(By.CSS_SELECTOR, "table.views-table")
    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
    assert len(rows) > 0, "A tabela da View '/properties-list' não contém nenhuma linha."

# Teste para verificar o conteúdo de uma célula específica na tabela
def test_view_table_row_content(logged_in_driver):
    """Testa o conteúdo de uma célula específica na tabela da View."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")
    logged_in_driver.get(f"{base_url}/properties-list")
    table = logged_in_driver.find_element(By.CSS_SELECTOR, "table.views-table")
    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
    first_cell = rows[0].find_element(By.CSS_SELECTOR, "td.views-field-title").text
    assert first_cell, "O valor esperado na célula da coluna 'Título' não foi encontrado."
