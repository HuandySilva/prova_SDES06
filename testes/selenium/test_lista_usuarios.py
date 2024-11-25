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

# Teste para acesso à página da View
#def test_view_page_access(logged_in_driver):
    """Testa se a página da View '/user-list' pode ser acessada."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")
    logged_in_driver.get(f"{base_url}/user-list")
    assert "Usuários | SIGEIMA" in logged_in_driver.title, "O título da página da View '/user-list' está incorreto."

# Teste para verificar se a tabela existe
#def test_view_table_exists(logged_in_driver):
    """Testa se a tabela da View '/user-list' existe."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")
    logged_in_driver.get(f"{base_url}/user-list")
    table = logged_in_driver.find_element(By.CSS_SELECTOR, "table.views-table.cols-4")
    assert table is not None, "A tabela da View '/user-list' não foi encontrada."

# Teste para verificar se a tabela contém linhas
#def test_view_table_has_rows(logged_in_driver):
    """Testa se a tabela da View '/user-list' contém linhas."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")
    logged_in_driver.get(f"{base_url}/user-list")
    table = logged_in_driver.find_element(By.CSS_SELECTOR, "table.views-table.cols-4")
    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
    assert len(rows) > 0, "A tabela da View '/user-list' não contém nenhuma linha."

# Teste para verificar conteúdo de uma célula específica
#def test_view_table_row_content(logged_in_driver):
    """Testa o conteúdo de uma célula específica na tabela da View."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")
    logged_in_driver.get(f"{base_url}/user-list")
    table = logged_in_driver.find_element(By.CSS_SELECTOR, "table.views-table.cols-4")
    rows = table.find_elements(By.CSS_SELECTOR, "tbody tr")
    first_cell = rows[0].find_element(By.CSS_SELECTOR, "td").text
    assert "super-user" in first_cell, "O valor esperado na primeira célula da tabela não está presente."

# Teste para o link 'Editar'
def test_click_edit_link(logged_in_driver):
    """Testa se o link 'Editar' redireciona para uma URL contendo 'edit'."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")
    logged_in_driver.get(f"{base_url}/user-list")

    print("Acessando o link de edição do usuário...")
    # Seleciona a célula da coluna 'Editar' na primeira linha
    edit_link = logged_in_driver.find_element(By.CSS_SELECTOR, "tbody tr:first-child td.views-field-edit-user a")
    print(f"Link encontrado: {edit_link.get_attribute('href')}")
    edit_link.click()

    print("Link clicado. Verificando URL atual...")
    try:
        # Espera que a URL contenha "edit"
        WebDriverWait(logged_in_driver, 30).until(
            lambda driver: "edit" in driver.current_url
        )
        print(f"Página de edição carregada com sucesso! URL atual: {logged_in_driver.current_url}")
    except Exception as e:
        print(f"Erro durante o redirecionamento: {e}")
        print(f"URL atual: {logged_in_driver.current_url}")
        raise

    # Validar que a URL contém "edit"
    current_url = logged_in_driver.current_url
    assert "edit" in current_url, "O link não redirecionou para uma URL contendo 'edit'."



# Teste para o link 'Visualizar'
def test_click_view_link(logged_in_driver):
    """Testa se o link 'Visualizar' redireciona para a página de visualização do usuário correto."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")
    logged_in_driver.get(f"{base_url}/user-list")

    print("Acessando o link de visualização do usuário...")
    # Seleciona a célula da coluna 'Visualizar' na primeira linha
    view_link = logged_in_driver.find_element(By.CSS_SELECTOR, "tbody tr:first-child td.views-field-nothing-1 a")
    print(f"Link encontrado: {view_link.get_attribute('href')}")
    view_link.click()

    print("Link clicado. Verificando URL atual...")
    # Espera que a URL contenha /user-profile/ seguido de um ID
    try:
        WebDriverWait(logged_in_driver, 30).until(
            lambda driver: "/user-profile/" in driver.current_url and any(char.isdigit() for char in driver.current_url)
        )
        print(f"Página de visualização carregada com sucesso! URL atual: {logged_in_driver.current_url}")
    except Exception as e:
        print(f"Erro durante o redirecionamento: {e}")
        print(f"URL atual: {logged_in_driver.current_url}")
        raise

    # Validar que a URL contém '/user-profile/' e um ID
    current_url = logged_in_driver.current_url
    assert "/user-profile/" in current_url, "O link não redirecionou para a página de visualização do usuário."
    assert any(char.isdigit() for char in current_url.split("/user-profile/")[-1]), "A URL não contém um ID válido."

# Teste para o link 'Excluir'
def test_click_delete_link(logged_in_driver):
    """Testa se o link 'Excluir' redireciona para a página de cancelamento do usuário correto."""
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")
    logged_in_driver.get(f"{base_url}/user-list")

    print("Acessando o link de exclusão...")
    # Seleciona a célula da coluna 'Excluir' na primeira linha
    delete_link = logged_in_driver.find_element(By.CSS_SELECTOR, "tbody tr:first-child td.views-field-nothing a")
    print("Link encontrado. Clique será executado agora.")
    
    delete_link.click()

    print("Link clicado. Verificando carregamento da página de exclusão...")
    try:
        # Aguarde até que o h1 com o texto esperado esteja presente
        confirmation_header = WebDriverWait(logged_in_driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//h1[contains(text(), 'Você tem certeza que deseja cancelar a conta')]"))
        )
        print(f"Página de exclusão carregada com sucesso! Texto encontrado: {confirmation_header.text}")
    except Exception as e:
        print("Erro ao carregar a página de exclusão.")
        print(f"URL atual: {logged_in_driver.current_url}")
        raise

    # Verifique se a URL contém '/cancel'
    assert "/cancel" in logged_in_driver.current_url, "O link 'Excluir' não redirecionou corretamente."
