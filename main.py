from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import pytest
import json
import time
import os
import logging
from datetime import datetime


BASE_URL = "https://prueba-jd-022026.dev-jdoutstanding.com"
CREDENCIALES = {
    "Correo" : "cristian@yopmail.com",
    "Contrasena": "Jdk@12345"
}

SCREENSHOTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
REPORTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reportes")

logger = logging.getLogger("test_clientes")
logger.setLevel(logging.INFO)
_log_fmt = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
_fh = logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_log.log"), encoding="utf-8", mode="w")
_fh.setFormatter(_log_fmt)
_sh = logging.StreamHandler()
_sh.setFormatter(_log_fmt)
logger.addHandler(_fh)
logger.addHandler(_sh)


@pytest.fixture
def driver():
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    driver.set_page_load_timeout(60)
    yield driver
    driver.quit()


""" def test_login(driver: WebDriver):
    driver.get(BASE_URL)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "login_username")))
    correo_input = driver.find_element(By.ID, "login_username")
    contrasena_input = driver.find_element(By.ID, "login_password")
    login_button = driver.find_element(By.XPATH, "//button[@type='submit']")
    correo_input.send_keys(CREDENCIALES["Correo"])
    contrasena_input.send_keys(CREDENCIALES["Contrasena"])
    login_button.click()
    WebDriverWait(driver, 15).until(EC.url_to_be(f"{BASE_URL}/clientes"))
    assert driver.current_url == f"{BASE_URL}/clientes" """


def quitar_focus(driver):
    """Quita el focus del elemento activo usando JavaScript, sin cerrar el modal."""
    try:
        driver.execute_script("document.activeElement.blur();")
        time.sleep(1)
    except Exception:
        pass


def seleccionar_dropdown(driver, label_texto, valor_titulo, timeout=10):
    try:
        form_item = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, f"//label[contains(text(),'{label_texto}')]/ancestor::div[contains(@class,'ant-form-item')]"))
        )
        select_container = form_item.find_element(By.CSS_SELECTOR, ".ant-select")
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'})", select_container)
        time.sleep(1)

        if "ant-select-disabled" in select_container.get_attribute("class"):
            WebDriverWait(driver, timeout).until(
                lambda d: "ant-select-disabled" not in form_item.find_element(By.CSS_SELECTOR, ".ant-select").get_attribute("class")
            )
            select_container = form_item.find_element(By.CSS_SELECTOR, ".ant-select")

        select_container.click()
        time.sleep(1)

        if valor_titulo:
            search_input = select_container.find_elements(By.CSS_SELECTOR, "input[type='search']")
            if search_input:
                search_input[0].send_keys(valor_titulo)
                time.sleep(2)

            option = None
            try:
                option = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class,'ant-select-dropdown') and not(contains(@class,'ant-select-dropdown-hidden'))]//div[contains(@class,'ant-select-item-option') and @title='{valor_titulo}']"))
                )
            except Exception:
                pass

            if not option:
                try:
                    option = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, f"//div[contains(@class,'ant-select-dropdown') and not(contains(@class,'ant-select-dropdown-hidden'))]//div[contains(@class,'ant-select-item-option')]"))
                    )
                except Exception:
                    pass

            if option:
                option.click()
            else:
                logger.warning(f"No se encontro opcion para '{valor_titulo}'")
                quitar_focus(driver)
                return False
        else:
            time.sleep(1)
            options = driver.find_elements(By.XPATH, "//div[contains(@class,'ant-select-dropdown') and not(contains(@class,'ant-select-dropdown-hidden'))]//div[contains(@class,'ant-select-item-option')]")
            if options:
                options[0].click()

        time.sleep(2)
        logger.info(f"Dropdown '{label_texto}' -> '{valor_titulo or 'primero disponible'}'")
        return True
    except Exception as ex:
        logger.warning(f"Error dropdown '{label_texto}': {ex}")
        quitar_focus(driver)
        return False


def llenar_campo(driver, element_id, valor):
    try:
        el = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, element_id)))
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'})", el)
        time.sleep(1)
        driver.execute_script("arguments[0].removeAttribute('readonly')", el)
        el.click()
        time.sleep(0.5)
        el.send_keys(Keys.CONTROL + "a")
        time.sleep(0.3)
        el.send_keys(valor)
        logger.info(f"Campo '{element_id}': {valor}")
        return True
    except Exception as ex:
        logger.warning(f"Error campo '{element_id}': {ex}")
        return False


def recuperar_pagina(driver):
    try:
        logger.info("Recuperando pagina - navegando a /clientes")
        driver.get(f"{BASE_URL}/clientes")
        time.sleep(10)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//span[contains(text(),'Nuevo Cliente')]"))
        )
        time.sleep(3)
        return True
    except Exception:
        try:
            logger.info("Reintentando con login completo")
            driver.get(BASE_URL)
            time.sleep(10)
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "login_username")))
            driver.find_element(By.ID, "login_username").send_keys(CREDENCIALES["Correo"])
            driver.find_element(By.ID, "login_password").send_keys(CREDENCIALES["Contrasena"])
            driver.find_element(By.XPATH, "//button[@type='submit']").click()
            time.sleep(10)
            WebDriverWait(driver, 20).until(EC.url_contains("/clientes"))
            time.sleep(3)
            return True
        except Exception:
            logger.error("No se pudo recuperar la pagina")
            return False


def test_nuevo_cliente(driver: WebDriver):
    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    logger.info("=== INICIO test_nuevo_cliente ===")
    driver.get(BASE_URL)
    time.sleep(5)

    logger.info("Realizando login")
    WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.ID, "login_username")))
    driver.find_element(By.ID, "login_username").send_keys(CREDENCIALES["Correo"])
    time.sleep(1)
    driver.find_element(By.ID, "login_password").send_keys(CREDENCIALES["Contrasena"])
    time.sleep(1)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    time.sleep(10)
    WebDriverWait(driver, 20).until(EC.url_contains("/clientes"))
    logger.info("Login exitoso")
    time.sleep(5)

    with open("clientes.json", "r", encoding="utf-8") as f:
        clientes = json.load(f)

    resultados = []
    tiempo_inicio_total = time.time()

    for i, cliente in enumerate(clientes):
        tiempo_inicio_cliente = time.time()
        nombre_display = cliente.get("nombre_razon_social", f"{cliente.get('nombres', '')} {cliente.get('apellidos', '')}")
        logger.info(f"\n{'='*60}")
        logger.info(f"Cliente {i+1}/10: {nombre_display} ({cliente['tipo']})")
        logger.info(f"{'='*60}")
        screenshot_path = ""

        try:
            WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Nuevo Cliente')]/ancestor::button"))
            )
            time.sleep(3)
            driver.find_element(By.XPATH, "//span[contains(text(),'Nuevo Cliente')]/ancestor::button").click()
            time.sleep(5)
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "ant-modal-content")))
            time.sleep(3)
            logger.info("Modal abierto")

            if cliente["tipo"] == "juridica":
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "general_info_nit_number")))
                time.sleep(2)
                logger.info("Tab General visible")

                if cliente.get("es_extranjero"):
                    try:
                        extranjero_labels = driver.find_elements(By.XPATH, "//span[contains(text(),'extranjero')]/ancestor::label")
                        if extranjero_labels:
                            extranjero_labels[0].click()
                            time.sleep(2)
                            logger.info("Checkbox extranjero activado")
                    except Exception:
                        pass

                nit_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "general_info_nit_number")))
                nit_input.click()
                time.sleep(1)
                nit_input.send_keys(cliente["nit"])
                logger.info(f"NIT ingresado: {cliente['nit']}")
                time.sleep(5)

                try:
                    autocomplete_visible = driver.find_elements(By.CSS_SELECTOR, ".ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option")
                    if autocomplete_visible:
                        autocomplete_visible[0].click()
                        time.sleep(5)
                        logger.info("Autocompletado seleccionado")
                    else:
                        quitar_focus(driver)
                        time.sleep(2)
                        logger.info("Sin autocompletado - focus quitado")
                except Exception:
                    quitar_focus(driver)
                    time.sleep(2)

                time.sleep(3)
                llenar_campo(driver, "general_info_nrc_number", cliente["nrc"])
                time.sleep(3)

                llenar_campo(driver, "general_info_name", cliente["nombre_razon_social"])
                time.sleep(3)

                llenar_campo(driver, "general_info_comercial_name", cliente["nombre_comercial"])
                time.sleep(3)

                llenar_campo(driver, "general_info_number_client", cliente["numero_cliente"])
                time.sleep(3)

                seleccionar_dropdown(driver, "Actividad", "", timeout=5)
                time.sleep(3)
                seleccionar_dropdown(driver, "Clasificaci", "", timeout=5)
                time.sleep(3)

                try:
                    modal_body = driver.find_element(By.CSS_SELECTOR, ".ant-modal-content .overflow-y-scroll")
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight / 3", modal_body)
                    time.sleep(3)
                except Exception:
                    pass

                llenar_campo(driver, "contact_email", cliente["correo"])
                time.sleep(3)
                llenar_campo(driver, "contact_phone", cliente["telefono"])
                time.sleep(3)
                llenar_campo(driver, "contact_mobile", cliente.get("movil", ""))
                time.sleep(3)

                try:
                    modal_body = driver.find_element(By.CSS_SELECTOR, ".ant-modal-content .overflow-y-scroll")
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", modal_body)
                    time.sleep(3)
                except Exception:
                    pass

                llenar_campo(driver, "customer_contacts_0_name", cliente["contacto_nombre"])
                time.sleep(3)
                llenar_campo(driver, "customer_contacts_0_lastName", cliente["contacto_apellido"])
                time.sleep(3)
                llenar_campo(driver, "customer_contacts_0_jobTitle", cliente["contacto_rol"])
                time.sleep(3)
                llenar_campo(driver, "customer_contacts_0_phoneNumber", cliente["contacto_telefono"])
                time.sleep(3)
                llenar_campo(driver, "customer_contacts_0_mobileNumber", cliente["contacto_movil"])
                time.sleep(3)
                llenar_campo(driver, "customer_contacts_0_email", cliente["contacto_correo"])
                time.sleep(3)
                logger.info("Campos contacto completados")

                try:
                    continuar_btn = driver.find_element(By.XPATH, "//button[@type='submit']//span[text()='Continuar']/ancestor::button")
                    driver.execute_script("arguments[0].scrollIntoView(true)", continuar_btn)
                    time.sleep(2)
                    continuar_btn.click()
                    logger.info("Continuar clickeado (Tab 1 -> Tab 2)")
                    time.sleep(10)
                except Exception as ex:
                    logger.error(f"Error al clickear Continuar: {ex}")

                tab2_active = driver.find_elements(By.XPATH, "//div[contains(@class,'ant-tabs-tab-active')]//div[contains(text(),'Factura')]")

                if tab2_active:
                    logger.info("Tab 2 Facturacion activo")
                    time.sleep(3)

                    seleccionar_dropdown(driver, "Departamento", cliente["departamento"])
                    time.sleep(5)
                    seleccionar_dropdown(driver, "Municipio", cliente.get("municipio", ""))
                    time.sleep(5)
                    seleccionar_dropdown(driver, "Distrito", cliente.get("distrito", ""))
                    time.sleep(5)

                    try:
                        calle_inputs = driver.find_elements(By.XPATH, "//label[contains(text(),'Calle')]/ancestor::div[contains(@class,'ant-form-item')]//input")
                        if calle_inputs:
                            calle_inputs[0].click()
                            time.sleep(1)
                            calle_inputs[0].clear()
                            calle_inputs[0].send_keys(cliente["calle"])
                            logger.info(f"Calle ingresada")
                            time.sleep(3)
                    except Exception:
                        pass

                    try:
                        continuar_btn2 = driver.find_element(By.XPATH, "//button[@type='submit']//span[text()='Continuar']/ancestor::button")
                        driver.execute_script("arguments[0].scrollIntoView(true)", continuar_btn2)
                        time.sleep(2)
                        continuar_btn2.click()
                        logger.info("Continuar clickeado (Tab 2 -> Tab 3)")
                        time.sleep(10)
                    except Exception as ex:
                        logger.error(f"Error Continuar Tab 2: {ex}")

                    tab3_active = driver.find_elements(By.XPATH, "//div[contains(@class,'ant-tabs-tab-active')]//div[contains(text(),'env') or contains(text(),'Env')]")

                    if tab3_active:
                        logger.info("Tab 3 Envio activo")
                        if cliente.get("usar_misma_direccion"):
                            try:
                                usar_misma = driver.find_elements(By.XPATH, "//span[contains(text(),'misma direcci')]/ancestor::label")
                                if usar_misma:
                                    usar_misma[0].click()
                                    time.sleep(3)
                                    logger.info("Usar misma direccion activado")
                            except Exception:
                                pass

                        try:
                            guardar_btn = driver.find_element(By.XPATH, "//button[@type='submit']//span[text()='Guardar']/ancestor::button")
                            driver.execute_script("arguments[0].scrollIntoView(true)", guardar_btn)
                            time.sleep(2)
                            guardar_btn.click()
                            logger.info("Guardar clickeado")
                            time.sleep(10)
                        except Exception as ex:
                            logger.error(f"Error Guardar: {ex}")

                        modal_cerrado = len(driver.find_elements(By.CSS_SELECTOR, ".ant-modal-content")) == 0
                        tiempo_cliente = round(time.time() - tiempo_inicio_cliente, 2)
                        if modal_cerrado:
                            logger.info(f"*** EXITO *** Cliente {i+1}: {nombre_display} ({tiempo_cliente}s)")
                            resultados.append({"numero": i+1, "nombre": nombre_display, "tipo": cliente["tipo"], "resultado": "EXITO", "error": "", "duracion": tiempo_cliente, "screenshot": ""})
                        else:
                            screenshot_path = os.path.join(SCREENSHOTS_DIR, f"fallo_cliente_{i+1}.png")
                            driver.save_screenshot(screenshot_path)
                            logger.warning(f"*** FALLO *** Cliente {i+1}: Modal no cerrado ({tiempo_cliente}s)")
                            resultados.append({"numero": i+1, "nombre": nombre_display, "tipo": cliente["tipo"], "resultado": "FALLO", "error": "Modal no se cerro despues de Guardar", "duracion": tiempo_cliente, "screenshot": screenshot_path})
                            recuperar_pagina(driver)
                    else:
                        screenshot_path = os.path.join(SCREENSHOTS_DIR, f"fallo_cliente_{i+1}.png")
                        driver.save_screenshot(screenshot_path)
                        tiempo_cliente = round(time.time() - tiempo_inicio_cliente, 2)
                        logger.warning(f"*** FALLO *** No avanzo a tab 3 ({tiempo_cliente}s)")
                        resultados.append({"numero": i+1, "nombre": nombre_display, "tipo": cliente["tipo"], "resultado": "FALLO", "error": "No avanzo a tab 3", "duracion": tiempo_cliente, "screenshot": screenshot_path})
                        recuperar_pagina(driver)
                else:
                    screenshot_path = os.path.join(SCREENSHOTS_DIR, f"fallo_cliente_{i+1}.png")
                    driver.save_screenshot(screenshot_path)
                    tiempo_cliente = round(time.time() - tiempo_inicio_cliente, 2)
                    logger.warning(f"*** FALLO *** No avanzo a tab 2 ({tiempo_cliente}s)")
                    resultados.append({"numero": i+1, "nombre": nombre_display, "tipo": cliente["tipo"], "resultado": "FALLO", "error": "No avanzo a tab 2", "duracion": tiempo_cliente, "screenshot": screenshot_path})
                    recuperar_pagina(driver)

            elif cliente["tipo"] == "natural":
                try:
                    natural_radio = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//input[@type='radio' and @value='natural']/ancestor::label"))
                    )
                    natural_radio.click()
                    time.sleep(5)
                    logger.info("Persona Natural seleccionada")
                except Exception:
                    pass

                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "add-natural-client-form")))
                time.sleep(3)

                if cliente.get("es_contribuyente"):
                    try:
                        contribuyente_labels = driver.find_elements(By.XPATH, "//span[contains(text(),'contribuyente')]/ancestor::label")
                        if contribuyente_labels:
                            contribuyente_labels[0].click()
                            time.sleep(3)
                            logger.info("Contribuyente activado")
                    except Exception:
                        pass

                if cliente.get("es_extranjero"):
                    try:
                        extranjero_labels = driver.find_elements(By.XPATH, "//span[contains(text(),'extranjero')]/ancestor::label")
                        if extranjero_labels:
                            extranjero_labels[0].click()
                            time.sleep(3)
                            logger.info("Extranjero activado")
                    except Exception:
                        pass

                dui_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "general_info_document_number")))
                dui_input.click()
                time.sleep(1)
                dui_input.send_keys(cliente["dui"])
                logger.info(f"DUI: {cliente['dui']}")
                time.sleep(5)

                try:
                    autocomplete_visible = driver.find_elements(By.CSS_SELECTOR, ".ant-select-dropdown:not(.ant-select-dropdown-hidden) .ant-select-item-option")
                    if autocomplete_visible:
                        autocomplete_visible[0].click()
                        time.sleep(5)
                        logger.info("Autocompletado DUI seleccionado")
                    else:
                        quitar_focus(driver)
                        time.sleep(2)
                except Exception:
                    quitar_focus(driver)
                    time.sleep(2)

                time.sleep(3)

                llenar_campo(driver, "general_info_name", cliente["nombres"])
                time.sleep(3)

                llenar_campo(driver, "general_info_last_name", cliente["apellidos"])
                time.sleep(3)

                llenar_campo(driver, "general_info_number_client", cliente["numero_cliente"])
                time.sleep(3)
                llenar_campo(driver, "general_info_email", cliente["correo"])
                time.sleep(3)
                llenar_campo(driver, "general_info_phone", cliente["telefono"])
                time.sleep(3)
                llenar_campo(driver, "general_info_mobile", cliente["movil"])
                time.sleep(3)
                logger.info("Info general completada")

                try:
                    form_scroll = driver.find_element(By.CSS_SELECTOR, "#add-natural-client-form .overflow-y-scroll")
                    driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", form_scroll)
                    time.sleep(5)
                except Exception:
                    pass

                seleccionar_dropdown(driver, "Departamento", cliente["departamento"])
                time.sleep(5)
                seleccionar_dropdown(driver, "Municipio", cliente.get("municipio", ""))
                time.sleep(5)
                seleccionar_dropdown(driver, "Distrito", cliente.get("distrito", ""))
                time.sleep(5)

                try:
                    calle_inputs = driver.find_elements(By.XPATH, "//label[contains(text(),'Calle')]/ancestor::div[contains(@class,'ant-form-item')]//input")
                    if calle_inputs:
                        calle_inputs[0].click()
                        time.sleep(1)
                        calle_inputs[0].clear()
                        calle_inputs[0].send_keys(cliente["calle"])
                        logger.info(f"Calle ingresada")
                        time.sleep(3)
                except Exception:
                    pass

                try:
                    guardar_btn = driver.find_element(By.XPATH, "//button[@type='submit']//span[text()='Guardar']/ancestor::button")
                    driver.execute_script("arguments[0].scrollIntoView(true)", guardar_btn)
                    time.sleep(2)
                    guardar_btn.click()
                    logger.info("Guardar clickeado")
                    time.sleep(10)
                except Exception as ex:
                    logger.error(f"Error Guardar natural: {ex}")

                modal_cerrado = len(driver.find_elements(By.CSS_SELECTOR, ".ant-modal-content")) == 0
                tiempo_cliente = round(time.time() - tiempo_inicio_cliente, 2)
                if modal_cerrado:
                    logger.info(f"*** EXITO *** Cliente {i+1}: {nombre_display} ({tiempo_cliente}s)")
                    resultados.append({"numero": i+1, "nombre": nombre_display, "tipo": cliente["tipo"], "resultado": "EXITO", "error": "", "duracion": tiempo_cliente, "screenshot": ""})
                else:
                    screenshot_path = os.path.join(SCREENSHOTS_DIR, f"fallo_cliente_{i+1}.png")
                    driver.save_screenshot(screenshot_path)
                    logger.warning(f"*** FALLO *** Cliente {i+1}: Modal no cerrado ({tiempo_cliente}s)")
                    resultados.append({"numero": i+1, "nombre": nombre_display, "tipo": cliente["tipo"], "resultado": "FALLO", "error": "Modal no se cerro despues de Guardar", "duracion": tiempo_cliente, "screenshot": screenshot_path})
                    recuperar_pagina(driver)

        except Exception as e:
            tiempo_cliente = round(time.time() - tiempo_inicio_cliente, 2)
            try:
                screenshot_path = os.path.join(SCREENSHOTS_DIR, f"fallo_cliente_{i+1}.png")
                driver.save_screenshot(screenshot_path)
            except Exception:
                screenshot_path = ""
            logger.error(f"*** FALLO (EXCEPCION) *** Cliente {i+1}: {nombre_display} - {str(e)[:150]} ({tiempo_cliente}s)")
            resultados.append({"numero": i+1, "nombre": nombre_display, "tipo": cliente["tipo"], "resultado": "FALLO", "error": str(e)[:200], "duracion": tiempo_cliente, "screenshot": screenshot_path})
            recuperar_pagina(driver)

    tiempo_total = round(time.time() - tiempo_inicio_total, 2)
    exitos = sum(1 for r in resultados if r["resultado"] == "EXITO")
    fallos = sum(1 for r in resultados if r["resultado"] == "FALLO")

    logger.info(f"\n{'='*60}")
    logger.info(f"RESULTADOS FINALES")
    logger.info(f"{'='*60}")
    logger.info(f"Total clientes: {len(resultados)}")
    logger.info(f"Exitos: {exitos}")
    logger.info(f"Fallos: {fallos}")
    logger.info(f"Tiempo total: {tiempo_total}s")
    logger.info(f"{'='*60}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    reporte_path = os.path.join(REPORTS_DIR, f"reporte_{timestamp}.html")

    filas_html = ""
    for r in resultados:
        bg = "#c6efce" if r["resultado"] == "EXITO" else "#ffc7ce"
        screenshot_html = ""
        if r["screenshot"] and os.path.exists(r["screenshot"]):
            screenshot_rel = os.path.relpath(r["screenshot"], REPORTS_DIR)
            screenshot_html = f'<a href="{screenshot_rel}" target="_blank">Ver captura</a>'
        filas_html += f"""<tr style="background:{bg};">
<td>{r['numero']}</td><td>{r['nombre']}</td><td>{r['tipo']}</td>
<td><b>{r['resultado']}</b></td><td>{r['error']}</td>
<td>{r['duracion']}s</td><td>{screenshot_html}</td></tr>"""

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Reporte Pruebas - Nuevo Cliente</title>
<style>
body {{ font-family: Arial, sans-serif; margin: 20px; }}
h1 {{ font-size: 1.5em; }}
h2 {{ font-size: 1.2em; margin-top: 20px; }}
table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
th, td {{ border: 1px solid #999; padding: 6px 10px; text-align: left; font-size: 0.9em; }}
th {{ background: #4472C4; color: white; }}
.stats {{ margin: 15px 0; }}
.stats span {{ margin-right: 30px; }}
a {{ color: #0563C1; }}
</style>
</head>
<body>
<h1>Reporte de Pruebas - Modulo Nuevo Cliente</h1>
<p>Fecha: {datetime.now().strftime("%d/%m/%Y %H:%M:%S")} | Ejecutado por: Cristian Alberto Pineda Blanco</p>

<h2>Resumen</h2>
<div class="stats">
<span><b>Total:</b> {len(resultados)}</span>
<span style="color:green;"><b>Exitosos:</b> {exitos}</span>
<span style="color:red;"><b>Fallidos:</b> {fallos}</span>
<span><b>Tiempo total:</b> {tiempo_total}s</span>
</div>

<h2>Detalle por cliente</h2>
<table>
<tr><th>#</th><th>Nombre / Razon Social</th><th>Tipo</th><th>Resultado</th><th>Error</th><th>Duracion</th><th>Screenshot</th></tr>
{filas_html}
</table>

<br>
<p><small>Reporte generado automaticamente con Selenium + Pytest</small></p>
</body>
</html>"""

    with open(reporte_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    logger.info(f"Reporte HTML generado: {reporte_path}")