# Prueba Tecnica QA - Selenium

Automatizacion del modulo de nuevo cliente con Selenium y Pytest.

## Como correr

1. Tener Python 3.10+ y Chrome instalado
2. Instalar dependencias:

```
pip install -r requirements.txt
```

3. Ejecutar:

```
pytest main.py -s -v
```

## Archivos

- `main.py` - script de pruebas
- `clientes.json` - datos de los 10 clientes de prueba (5 juridica, 5 natural)
- `requirements.txt` - dependencias (selenium, pytest)

## Que genera

- Reporte HTML en la carpeta `reportes/`
- Screenshots de fallos en `screenshots/`
- Log en `test_log.log`

## Credenciales

- Usuario: cristian@yopmail.com
- Contraseña: Jdk@12345
