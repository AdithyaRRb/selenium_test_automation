
# Python Selenium script starts here
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    driver.get("https://www.saucedemo.com")
    return driver

def login(driver, username, password):
    driver.find_element(By.ID, "user-name").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "login-button").click()

def verify_products_page(driver):
    WebDriverWait(driver, 10).until(EC.url_to_be("https://www.saucedemo.com/inventory.html"))
    assert "Products" in driver.find_element(By.CLASS_NAME, "title").text

def add_product_to_cart(driver):
    driver.find_element(By.ID, "add-to-cart-sauce-labs-bike-light").click()

def go_to_cart(driver):
    driver.find_element(By.CLASS_NAME, "shopping_cart_link").click()

def checkout(driver):
    driver.find_element(By.ID, "checkout").click()

def fill_checkout_info(driver, first_name, last_name, zip_code):
    driver.find_element(By.ID, "first-name").send_keys(first_name)
    driver.find_element(By.ID, "last-name").send_keys(last_name)
    driver.find_element(By.ID, "postal-code").send_keys(zip_code)
    driver.find_element(By.ID, "continue").click()

def test_purchase_product():
    driver = setup_driver()
    login(driver, "standard_user", "secret_sauce")
    verify_products_page(driver)
    add_product_to_cart(driver)
    go_to_cart(driver)
    checkout(driver)
    fill_checkout_info(driver, "John", "Doe", "12345")
    WebDriverWait(driver, 10).until(EC.url_to_be("https://www.saucedemo.com/checkout-step-two.html"))
    assert "Checkout: Overview" in driver.find_element(By.CLASS_NAME, "title").text
    input("Press Enter to close the browser...")
    driver.quit()

test_purchase_product()
# Python Selenium script ends here
