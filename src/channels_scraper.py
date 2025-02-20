import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from dbconfig import guardar_documento

# Configuración de Selenium Grid
selenium_grid_url = "http://selenium-hub:4444/wd/hub"
chrome_options = webdriver.ChromeOptions()

# Configuración avanzada de Chrome
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
#chrome_options.add_argument("--headless")  # Ejecutar sin interfaz gráfica
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1366,768")
chrome_options.add_argument("--ignore-certificate-errors")

# Lista de User-Agents populares
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36"
]

# Seleccionar un User-Agent aleatorio
random_user_agent = random.choice(USER_AGENTS)
chrome_options.add_argument(f"user-agent={random_user_agent}")

# Eliminar el mensaje "Chrome is being controlled"
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

# Inicializar WebDriver correctamente (SIN `desired_capabilities`)
driver = webdriver.Remote(command_executor=selenium_grid_url, options=chrome_options)

# URL base
url_base = "https://www.9now.com.au/live"
driver.get(url_base)

# Esperar que la lista de canales cargue
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "channels"))
)

# Obtener la lista de canales
channels = driver.find_elements(By.CSS_SELECTOR, "#channels .channel_card")

# Lista para almacenar los datos de todos los canales
channels_data = []

# Recorrer cada canal
for channel in channels:
    try:
        # Hacer scroll hasta el canal
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", channel)
        time.sleep(1)

        # Hacer clic en el canal
        channel.click()

        # Esperar a que aparezca la clase "selected"
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".channel_card.selected"))
        )

        # Extraer URL y nombre del canal
        channel_url = channel.get_attribute("href")
        channel_name = channel_url.split("/live/")[-1] if channel_url else None

        # Extraer logo
        logo_element = channel.find_element(By.CSS_SELECTOR, ".channel_logo img")
        logo_url = logo_element.get_attribute("src") if logo_element else None

        # Extraer calidad
        quality_element = channel.find_element(By.CSS_SELECTOR, ".channel_logo__signpost_badge")
        quality = quality_element.text if quality_element else "Unknown"

        # Extraer información del programa actual
        title_element = channel.find_element(By.CSS_SELECTOR, ".channel_card__metadata__title")
        title = title_element.text if title_element else "Unknown"

        time_slot_element = channel.find_element(By.CSS_SELECTOR, ".channel_card__metadata__epg")
        time_slot = time_slot_element.text if time_slot_element else "Unknown"

        category_element = channel.find_element(By.XPATH, "//span[contains(text(),'Live')]/following-sibling::span")
        category = category_element.text if category_element else "Unknown"

        description_element = channel.find_element(By.CSS_SELECTOR, ".channel_card__metadata__description p")
        description = description_element.text if description_element else "No description available"

        # Agregar canal a la lista
        channels_data.append({
            "name": channel_name,
            "url": f"https://www.9now.com.au{channel_url}",
            "logo": logo_url,
            "quality": quality,
            "current_program": {
                "title": title,
                "time_slot": time_slot,
                "category": category,
                "description": description
            }
        })

    except Exception as e:
        print(f"Error procesando el canal {channel_name}: {e}")

# Guardar el documento completo en MongoDB
documento = {"channels": channels_data}
guardar_documento(documento)
print(f"Se han guardado {len(channels_data)} canales en MongoDB.")

# Cerrar Selenium
driver.quit()