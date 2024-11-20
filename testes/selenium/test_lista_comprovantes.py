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

# Teste para verificar o acesso à página
def test_view_page_access(logged_in_driver):
    """Testa se a página da View '/documents-list' pode ser acessada."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")
    logged_in_driver.get(f"{base_url}/documents-list")
    assert "lista de comprovantes" in logged_in_driver.title, "O título da página da View '/documents-list' está incorreto."

# Teste para verificar se a tabela existe
def test_view_table_exists(logged_in_driver):
    """Testa se a tabela da View '/documents-list' existe."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")
    logged_in_driver.get(f"{base_url}/documents-list")

    # Espera até que a tabela esteja presente na página
    WebDriverWait(logged_in_driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table.views-table.cols-6"))
    )

    table = logged_in_driver.find_element(By.CSS_SELECTOR, "table.views-table.cols-6")
    assert table is not None, "A tabela da View '/documents-list' não foi encontrada."

# Teste para verificar se a tabela contém linhas
def test_view_table_has_rows(logged_in_driver):
    """Testa se a tabela da View '/documents-list' contém linhas."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")
    logged_in_driver.get(f"{base_url}/documents-list")

    # Espera até que a tabela esteja presente na página
    WebDriverWait(logged_in_driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table.views-table.cols-6"))
    )

    table = logged_in_driver.find_element(By.CSS_SELECTOR, "table.views-table.cols-6")
    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
    assert len(rows) > 0, "A tabela da View '/documents-list' não contém nenhuma linha."

# Teste para verificar o conteúdo de células específicas na tabela
def test_view_table_row_content(logged_in_driver):
    """Testa o conteúdo de células específicas na tabela da View."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")
    logged_in_driver.get(f"{base_url}/documents-list")

    # Espera até que a tabela esteja presente na página
    WebDriverWait(logged_in_driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table.views-table.cols-6"))
    )

    table = logged_in_driver.find_element(By.CSS_SELECTOR, "table.views-table.cols-6")
    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")

    # Verifica o Tipo do Comprovante
    type_cell = rows[0].find_element(By.CSS_SELECTOR, "td.views-field-field-categoria").text
    assert type_cell, "O tipo do comprovante não foi encontrado."

    # Verifica a Data de Envio
    date_cell = rows[0].find_element(By.CSS_SELECTOR, "td.views-field-created").text

    assert date_cell, "A data de envio não foi encontrada."

# Teste para "Visualizar Arquivo"
def test_view_document(logged_in_driver):
    """Testa se o link na coluna 'Arquivo' redireciona corretamente para o PDF."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")
    logged_in_driver.get(f"{base_url}/documents-list")

    # Espera até que a tabela esteja presente na página
    WebDriverWait(logged_in_driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table.views-table.cols-6"))
    )

    # Localiza o link do arquivo na coluna 'Arquivo'
    file_link = logged_in_driver.find_element(By.CSS_SELECTOR, "tbody tr:first-child td.views-field-field-arquivo a")
    file_url = file_link.get_attribute("href")
    file_name = file_link.text.strip()
    assert file_url.endswith(".pdf"), f"O link '{file_name}' não redireciona para um PDF."

    # Clique no link
    file_link.click()

    # Verifica se a URL redirecionada é a do arquivo PDF
    WebDriverWait(logged_in_driver, 10).until(
        lambda driver: driver.current_url == file_url
    )
    print(f"PDF aberto com sucesso: {logged_in_driver.current_url}")

# Teste para "Apagar"
def test_delete_document(logged_in_driver):
    """Testa se o botão 'Apagar' redireciona para a página de exclusão."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")
    logged_in_driver.get(f"{base_url}/documents-list")

    # Espera até que a tabela esteja presente na página
    WebDriverWait(logged_in_driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "table.views-table.cols-6"))
    )

    # Localiza o botão 'Excluir' na coluna 'Excluir'
    delete_button = logged_in_driver.find_element(By.CSS_SELECTOR, "tbody tr:first-child td.views-field-delete-node a")
    delete_url = delete_button.get_attribute("href")
    assert "/delete" in delete_url, "O botão 'Excluir' não redireciona para uma URL válida."

    # Clique no botão
    delete_button.click()

    # Verifica se a URL redirecionada é a da página de exclusão
    WebDriverWait(logged_in_driver, 10).until(
        lambda driver: "/delete" in driver.current_url
    )
    print(f"Página de exclusão carregada com sucesso: {logged_in_driver.current_url}")
    confirm_button = WebDriverWait(logged_in_driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "input[data-drupal-selector='edit-submit']"))
    )
    confirm_button.click()

    # Aguarda a mensagem de confirmação após a exclusão
    WebDriverWait(logged_in_driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".messages--status"))
    )

    # Verifica a mensagem de sucesso
    success_message = logged_in_driver.find_element(By.CSS_SELECTOR, ".messages--status").text
    assert "foi excluído" in success_message, "A exclusão do comprovante não foi concluída com sucesso."
    print("Comprovante excluído com sucesso!")