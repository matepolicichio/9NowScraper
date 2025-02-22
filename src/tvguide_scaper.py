import random
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
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

driver = None

try:

    # Inicializar WebDriver correctamente (SIN `desired_capabilities`)
    driver = webdriver.Remote(command_executor=selenium_grid_url, options=chrome_options)

    # URL base
    url_base = "https://www.9now.com.au/guide"
    driver.get(url_base)

    # Esperar que la lista de canales cargue
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "guide__grid"))
    )

    # Obtener la lista de canales
    day_nav_list = driver.find_elements(By.CSS_SELECTOR, ".day-nav__list__item")

    # Lista para almacenar los datos de todos los canales
    channels_data = []
    
    time.sleep(10)

    # Recorrer cada canal
    for index, day_nav in enumerate(day_nav_list):        
        try:
            # Extraer el enlace del día
            day_nav_link = day_nav.find_element(By.CSS_SELECTOR, "a")

            # Obtener la fecha de cada day_nav
            day_nav_date = day_nav_link.get_attribute("data-date")
            day_nav_link.click()
            print(f"\n\n✅ Click en el día {day_nav_date}.\nURL actual: {driver.current_url}")

            # Esperar que la grilla de canales cargue
            guide_grid = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "guide__grid"))
            )
            
            time.sleep(5)

            guide_rows = guide_grid.find_elements(By.CSS_SELECTOR, ".guide__row")

            for index, grid_row in enumerate(guide_rows):
                try:
                    channel_name = grid_row.get_attribute("data-channel-name")
                    print(f"🔹 Canal: {channel_name}")



                    # Extraer el nombre del canal
                    channel_name = grid_row.find_element(By.CSS_SELECTOR, ".guide__grid__row__channel__name").text

                    # Extraer la lista de programas
                    programs = grid_row.find_elements(By.CSS_SELECTOR, ".guide__grid__row__channel__program")

                    for program in programs:
                        try:
                            # Extraer el título del programa
                            program_title = program.find_element(By.CSS_SELECTOR, ".guide__grid__row__channel__program__title").text

                            # Extraer la hora de inicio y fin del programa
                            program_time = program.find_element(By.CSS_SELECTOR, ".guide__grid__row__channel__program__time").text

                            # Extraer la descripción del programa
                            program_description = program.find_element(By.CSS_SELECTOR, ".guide__grid__row__channel__program__description").text

                            # Agregar programa a la lista
                            channels_data.append({
                                "date": day_nav_date,
                                "channel": channel_name,
                                "program": {
                                    "title": program_title,
                                    "time": program_time,
                                    "description": program_description
                                }
                            })

                        except NoSuchElementException:
                            print("⚠️ Advertencia: No se encontró información del programa.")
                            continue

                except NoSuchElementException:
                    print("⚠️ Advertencia: No se encontró información del canal.")
                    continue


        except TimeoutException:
            print("⚠️ No se pudo extraer la información del canal a tiempo.")

        except Exception as e:
            print(f"Error procesando el canal: {e}")

except WebDriverException as e:
    print(f"❌ Error al iniciar WebDriver: {e}")

# Cerrar Selenium
finally:
    if driver:
        driver.quit()
        print("✅ WebDriver cerrado correctamente.")
    # # Guardar el documento completo en MongoDB
    # if channels_data:
    #     documento = {"channels": channels_data}
    #     guardar_documento(documento)
    #     print(f"✅ Se han guardado {len(channels_data)} canales en MongoDB.")
