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


def test_view_comprovantes_pintura_page_access(logged_in_driver):
    """Testa se a página da View '/documents-list-painting' pode ser acessada."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")
    logged_in_driver.get(f"{base_url}/documents-list-painting")
    assert "Comprovantes de pintura" in logged_in_driver.title, "O título da página está incorreto."


def test_view_comprovantes_pintura_table_exists(logged_in_driver):
    """Testa se a tabela da View 'documents-list-painting' existe."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")
    logged_in_driver.get(f"{base_url}/documents-list-painting")
    table = logged_in_driver.find_element(By.CSS_SELECTOR, "table.views-table.cols-6")
    assert table is not None, "A tabela da View 'documents-list-painting' não foi encontrada."


def test_view_comprovantes_pintura_table_has_rows(logged_in_driver):
    """Testa se a tabela da View 'documents-list-painting' contém linhas."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")
    logged_in_driver.get(f"{base_url}/documents-list-painting")
    table = logged_in_driver.find_element(By.CSS_SELECTOR, "table.views-table.cols-6")
    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
    assert len(rows) > 0, "A tabela da View 'documents-list-painting' não contém nenhuma linha."


def test_view_comprovantes_pintura_table_row_content(logged_in_driver):
    """Testa o conteúdo de células específicas na tabela da View."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")
    logged_in_driver.get(f"{base_url}/documents-list-painting")
    table = logged_in_driver.find_element(By.CSS_SELECTOR, "table.views-table.cols-6")
    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")

    # Testa se a célula de cliente contém um valor
    client_cell = rows[0].find_element(By.CSS_SELECTOR, "td.views-field-uid").text
    assert client_cell != "", "A célula de cliente está vazia."

    # Testa se a célula de status contém texto
    status_cell = rows[0].find_element(By.CSS_SELECTOR, "td.views-field-field-status-de-aprovacao").text
    assert status_cell != "", "A célula de status está vazia."

    # Testa se a imagem do arquivo está presente
    file_image = rows[0].find_element(By.CSS_SELECTOR, "td.views-field-filename")
    assert file_image is not None, "A imagem do arquivo não foi encontrada na célula correspondente."


def test_click_delete_comprovante_pintura(logged_in_driver):
    """Testa se o botão 'Excluir' redireciona para a página de exclusão e realiza a exclusão."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")
    logged_in_driver.get(f"{base_url}/documents-list-painting")

    # Seleciona o botão 'Excluir' na primeira linha
    delete_button = logged_in_driver.find_element(By.CSS_SELECTOR, "a[href*='/delete?destination=/documents-list-painting']")
    delete_button.click()

    # Aguarda a página de confirmação de exclusão
    WebDriverWait(logged_in_driver, 10).until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-drupal-selector='edit-node-comprovante-de-pintura-delete-form']"))
)

    # Localiza e clica no botão de confirmação de exclusão
    confirm_delete_button = logged_in_driver.find_element(By.CSS_SELECTOR, "input[data-drupal-selector='edit-submit']")

    confirm_delete_button.click()

    # Aguarda o redirecionamento de volta para a lista
    WebDriverWait(logged_in_driver, 10).until(
        EC.url_to_be(f"{base_url}/documents-list-painting")
    )

    # Verifica se o conteúdo foi realmente excluído (pode ser ajustado para verificar se o item específico não está mais presente)
    assert "delete" not in logged_in_driver.current_url, "O item não foi excluído ou houve falha no redirecionamento."
    print("O item foi excluído com sucesso e o redirecionamento ocorreu corretamente.")
