import random
import time
import traceback
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from dbconfig import guardar_documento

# Configuración de Selenium Grid
selenium_grid_url = "http://selenium-hub:4444/wd/hub"
chrome_options = webdriver.ChromeOptions()

# Configuración avanzada de Chrome
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
# chrome_options.add_argument("--headless")  # Ejecutar sin interfaz gráfica
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1366,768")
chrome_options.add_argument("--ignore-certificate-errors")

# # Configurar el proxy SOCKS5 de Tor
# tor_proxy = "socks5://tor:9050"  # Usa el nombre del servicio Docker para Tor
# chrome_options.add_argument(f"--proxy-server={tor_proxy}")

# Lista de User-Agents populares
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_4_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Mobile Safari/537.36"
    # "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    # "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    # "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
    # "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36"
]

# Seleccionar un User-Agent aleatorio
random_user_agent = random.choice(USER_AGENTS)
chrome_options.add_argument(f"user-agent={random_user_agent}")

# Extra capabilities
capabilities = DesiredCapabilities.CHROME.copy()
capabilities['goog:chromeOptions'] = {
    'excludeSwitches': ['enable-automation'],  # Remove "Chrome is being controlled" message
}

# Eliminar el mensaje "Chrome is being controlled"
# chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])

driver = None

# Channels en Live TV
try:

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
    channels = driver.find_elements(By.CSS_SELECTOR, "#channels .channel_card__list_item")

    # Lista para almacenar los datos de todos los canales
    channels_data = []
    
    time.sleep(10)

    # Recorrer cada canal
    for index, channel in enumerate(channels):        
        try:
            first_channel = None

            # Verificar si el canal ya está seleccionado
            try:
                first_channel = channel.find_element(By.CSS_SELECTOR, "div.channel_card.selected")
                print(f"🔹 Canal ya seleccionado. URL actual: {driver.current_url}")
            except NoSuchElementException:
                pass  # Si no encuentra el elemento, continúa con la búsqueda del enlace
            
            
            if not first_channel:
                try:               
                    # Buscar el enlace del canal
                    link_element = channel.find_element(By.CSS_SELECTOR, "a.channel_card")

                    link_element.click()
                    print("✅ Click en el canal.")
                    time.sleep(3)

                    print(f"✅ Canal cambiado. Nueva URL: {driver.current_url}")
            
                except NoSuchElementException:
                    print("❌ No se encontró el enlace del canal.")
                    continue # Saltar al siguiente canal si el cambio no ocurre

                except TimeoutException:
                    print("⚠️ No se detectó el cambio de canal a tiempo.")
                    continue # Saltar al siguiente canal si el cambio no ocurre

            try:
                # Esperar hasta que la clase `.selected` aparezca en el canal
                channel_card_selected = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".channel_card.selected"))
                )

                channel_url = driver.current_url
                channel_name = channel_url.split("/live/")[-1] if channel_url else None
                channel_name = channel_name.replace("-", " ").title() if channel_name else "N/A"

                # Extraer logo
                try:
                    logo_element = channel_card_selected.find_element(By.CSS_SELECTOR, ".channel_logo img")
                    logo_url = logo_element.get_attribute("src") if logo_element else None
                except NoSuchElementException:
                    print("⚠️ Advertencia: No se encontró el logo del canal.")
                    logo_url = "N/A"

                # Extraer calidad
                try:
                    # Esperar hasta que el elemento esté presente en el DOM (máximo 10 segundos)
                    quality_element = channel_card_selected.find_element(By.CSS_SELECTOR, ".channel_logo__signpost_badge")
                    quality = quality_element.text
                except NoSuchElementException:
                    print("⚠️ Advertencia: No se encontró el elemento de calidad en el DOM.")
                    quality = "N/A"

                # Extraer información del programa actual
                try:
                    title_element = channel_card_selected.find_element(By.CSS_SELECTOR, ".channel_card__metadata__title")
                    title = title_element.text if title_element else "Unknown"
                except NoSuchElementException:
                    print("⚠️ Advertencia: No se encontró el título del programa.")
                    title = "N/A"

                try:
                    # Buscar todos los <span> dentro de .channel_card__metadata__element
                    metadata_spans = channel_card_selected.find_elements(By.CSS_SELECTOR, ".sdui_inline_text_and_icon_element")

                    # Extraer el primer y segundo elemento de los 7 existentes
                    if len(metadata_spans) >= 2:
                        time_slot = metadata_spans[1].text.strip()  # Segundo elemento (índice 1)
                        category = metadata_spans[2].text.strip()  # Tercer elemento (índice 2)

                except NoSuchElementException:
                    print("⚠️ Advertencia: No se encontró la metadata del programa.")
                    time_slot = "N/A"
                    category = "N/A"

                try:
                    description_element = channel_card_selected.find_element(By.CSS_SELECTOR, ".channel_card__metadata__description p")
                    description = description_element.text if description_element else "No description available"
                except NoSuchElementException:
                    print("⚠️ Advertencia: No se encontró la descripción del programa.")
                    description = "N/A"

                # Agregar canal a la lista
                channels_data.append({
                    "name": channel_name,
                    "url": channel_url,
                    "logo": logo_url,
                    "quality": quality,
                    "current_program": {
                        "title": title,
                        "time_slot": time_slot,
                        "category": category,
                        "description": description
                    }
                })

            except TimeoutException:
                print("⚠️ No se pudo extraer la información del canal a tiempo.")

        except Exception as e:
            print(f"Error procesando el canal: {e}")

except WebDriverException as e:
    print(f"❌ Error al iniciar WebDriver: {e}")

# Channels en TV Guide
try:
#     # Inicializar WebDriver correctamente (SIN `desired_capabilities`)
#     print("🔄 Iniciando WebDriver...")
#     driver = webdriver.Remote(command_executor=selenium_grid_url, options=chrome_options)

#     # Iniciar el cronómetro
#     start_time = time.time()

#     # URL base
    url_guide = "https://tvguide.9now.com.au/guide"
    driver.get(url_guide)

    print("✅ Página cargada correctamente.")

#     # # Esperar que la lista de canales cargue
#     # WebDriverWait(driver, 15).until(
#     #     EC.presence_of_element_located((By.CSS_SELECTOR, ".guide__grid"))
#     # )

#     # # Obtener la lista de días de navegación
#     # day_nav_list = WebDriverWait(driver, 10).until(
#     #     EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".day-nav__list__item"))
#     # )
#     # print(f"🔹 Días de navegación extraídos: {len(day_nav_list)}")

#     # # Lista para almacenar los datos de todos los canales
#     # channels_data = []
    
#     # # Recorrer cada canal
#     # for day_nav in day_nav_list:        
#     #     try:
#     #         print("\n🔄 Procesando un nuevo día...")

#     #         # Subir al inicio de la página
#     #         driver.execute_script("window.scrollTo(0, 0);")

#     #         # Extraer el enlace del día
#     #         day_nav_link = day_nav.find_element(By.CSS_SELECTOR, "a")

#     #         # Obtener la fecha de cada day_nav
#     #         day_nav_date = day_nav_link.get_attribute("data-date")
#     #         day_nav_link.click()
#     #         print(f"\n\n✅ Click en el día {day_nav_date}.\nURL actual: {driver.current_url}")
            
#     #         # Esperar que la grilla de programas cargue
#     #         WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".footer")))
            
#         #     # Obtener la filas de la grilla (canales menos el ON DEMAND)
#         #     guide_rows = WebDriverWait(driver, 10).until(
#         #         EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".guide__grid .guide__row:not(.guide__row--sticky)"))
#         #     )            
#         #     print(f"🔹 Filas extraídas: {len(guide_rows)}")

#         #     for grid_row in guide_rows:
#         #         try:
#         #             channel_name = grid_row.get_attribute("data-channel-name")
#         #             print(f"🔹 Canal: {channel_name}")

#         #             # Extraer la lista de programas
#         #             programs = grid_row.find_elements(By.CSS_SELECTOR, ".guide__row__block")
#         #             print(f"✅ Programas extraídos: {len(programs)}")

#         #             for index, program in enumerate(programs):
#         #                 try:
#         #                     # Extraer el título del programa
#         #                     program_title = program.find_element(By.CSS_SELECTOR, "h4").text.strip()

#         #                     try:
#         #                         # Ver el detalle del programa
#         #                         WebDriverWait(driver, 10).until(
#         #                             EC.visibility_of_element_located((By.CSS_SELECTOR, "a"))
#         #                         )
#         #                         time.sleep(1)  
#         #                         program_link = program.find_element(By.CSS_SELECTOR, "a")
#         #                         program_link.click()
#         #                         time.sleep(2)
#         #                     except NoSuchElementException:
#         #                         print(f"⚠️ Advertencia: No se encontró enlace clickeable para '{program_title}'.")
#         #                         continue

#         #                     print(f"✅ Cargando detalles de: {program_title}...")

#         #                     # if index == 0:
#         #                     #     time.sleep(5)
#         #                     # else:
#         #                     #     time.sleep(3)

#         #                     # Esperar que cargue el detalle del programa
#         #                     program_content = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".show-down__content")))

#         #                     # Extraer la hora de inicio y fin del programa
#         #                     try:
#         #                         program_time = program_content.find_element(By.CSS_SELECTOR, ".show-down__timeFromTo").text.strip()
#         #                     except NoSuchElementException:
#         #                         program_time = "N/A"

#         #                     # Extraer la descripción del programa
#         #                     try:
#         #                         program_description = program_content.find_element(By.CSS_SELECTOR, ".show-down__description").text.strip()
#         #                     except NoSuchElementException:
#         #                         program_description = "N/A"

#         #                     # Extraer los tags del programa
#         #                     try:
#         #                         program_tags = program_content.find_element(By.CSS_SELECTOR, ".show-down__tags").text
#         #                     except NoSuchElementException:
#         #                         program_tags = "N/A"

#         #                     print(f" ✅ Titulo: {program_title}")   
#         #                     print(f"    Hora: {program_time}")   
#         #                     print(f"    Descripción: {program_description}")
#         #                     print(f"    Tags: {program_tags}")

#         #                     # Hacer clic en el botón de cerrar SOLO si es el último programa de la lista
#         #                     if index == len(programs) - 1:
#         #                         try:
#         #                             program_close = program_content.find_element(By.CSS_SELECTOR, ".show-down__close")
#         #                             program_close.click()
#         #                             print("🛑 Cierre del detalle del último programa exitoso.")
#         #                         except NoSuchElementException:
#         #                             print("⚠️ Advertencia: No se encontró el botón para cerrar el detalle del programa.")

#         #                 except NoSuchElementException:
#         #                     print("⚠️ Advertencia: No se encontró información del programa.")
#         #                     continue

#         #         except NoSuchElementException:
#         #             print("⚠️ Advertencia: No se encontró información del canal.")
#         #             continue

# #         except TimeoutException:
# #             print("⚠️ No se pudo extraer la información del canal a tiempo.")

# #         except Exception as e:
# #             print(f"Error procesando el canal: {e}")
# #             print(traceback.format_exc())

except WebDriverException as e:
    print(f"❌ Error al iniciar WebDriver: {e}")

# Cerrar Selenium
finally:
    if driver:
        driver.quit()
        print("✅ WebDriver cerrado correctamente.")

    # Guardar el documento completo en MongoDB
    if channels_data:
        documento = {"channels": channels_data}
        guardar_documento(documento)
        print(f"✅ Se han guardado {len(channels_data)} canales en MongoDB.")

    # Finalizar el cronómetro
    # end_time = time.time()  
    # # Calcular la duración
    # execution_time = end_time - start_time
    # minutes = int(execution_time // 60)
    # seconds = int(execution_time % 60)
    # print(f"\n⏳ Tiempo total de ejecución: {minutes} min {seconds} sec.")
