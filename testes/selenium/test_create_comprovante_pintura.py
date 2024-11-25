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


def test_create_comprovante_pintura(logged_in_driver):
    """Test the creation of a painting proof submission with image upload."""
    # Base URL for the Drupal application
    base_url = os.getenv("DRUPAL_BASE_URL", "http://localhost")
    # Path to the dummy image
    image_path = os.path.join(os.getcwd(), "images", "dummy_image.png")

    # Verify if the image exists before proceeding
    assert os.path.exists(image_path), f"The specified image file was not found: {image_path}"

    # Navigate to the form page
    logged_in_driver.get(f"{base_url}/form/registro-de-comprovante-de-pintu/")

    # Wait until the form loads
    WebDriverWait(logged_in_driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "webform-submission-form"))
    )

    # Locate the file input field and upload the image
    file_input = logged_in_driver.find_element(By.CSS_SELECTOR, "input[data-drupal-selector='edit-nome-de-usuario-upload']")
    file_input.send_keys(image_path)

    # Locate and click the "Carregar" button
    upload_button = logged_in_driver.find_element(By.CSS_SELECTOR, "input[data-drupal-selector='edit-nome-de-usuario-upload-button']")
    upload_button.click()

    # Wait for the image preview or confirmation of upload
    WebDriverWait(logged_in_driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "#edit-nome-de-usuario img"))
    )
    print("Image uploaded successfully!")

    # Locate and click the "Enviar" button
    submit_button = logged_in_driver.find_element(By.CSS_SELECTOR, "input[data-drupal-selector='edit-submit']")
    

    submit_button = logged_in_driver.find_element(By.ID, "edit-submit")
    submit_button.click()

    # Verify successful submission by checking for a confirmation message
    confirmation_message = WebDriverWait(logged_in_driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".webform-confirmation__message"))
    )
    assert "Comprovante de pintura enviado com sucesso." in confirmation_message.text, \
        f"Confirmation message not found or incorrect: {confirmation_message.text}"
    print("Submission confirmation received successfully!")
