# Agents.md: Reglas y Buenas Prácticas de Desarrollo

Este documento establece las directrices técnicas obligatorias para la generación de código y asistencia en este proyecto. Se basa en los estándares de **FastAPI**, **SQLModel**, **Pydantic** y **PostgreSQL**.

## Context7 - Documentación de Librerías

* **Uso de Context7:** Cuando el usuario pregunte sobre librerías, frameworks, APIs, configuración o ejemplos de código, se debe usar **Context7** para obtener documentación actualizada.
* **Activación:** Agregar `use context7` al final del prompt o usar las herramientas `resolve-library-id` y `query-docs` disponibles en el MCP de Context7.
* **Verificar Versión:** Cuando el usuario mencione una versión específica de la librería, usar esa versión al consultar la documentación.

## Skills Disponibles

El agente tiene acceso a las siguientes skills que debe usar cuando sea relevante:

* **fastapi:** Para todo lo relacionado con FastAPI y Pydantic
* **pytest-coverage:** Para ejecutar tests y aumentar coverage
* **ci-cd-best-practices:** Para pipelines CI/CD y DevOps
* **turnobarrio:** Sistema de gestión de turnos (solo si es relevante)
* **find-skills:** Para descubrir e instalar nuevas skills

* **Carga de Skill:** Cuando el usuario solicite algo relacionado a una skill, usar la herramienta `skill` para cargar las instrucciones completas de esa skill.

## 9. Protocolo de Interacción y Confirmación

* **Aprobación Obligatoria:** El agente **nunca debe ejecutar cambios en archivos, crear directorios o instalar dependencias** sin una confirmación explícita del usuario por cada acción.
* **Plan de Acción:** Antes de realizar cualquier tarea técnica, el agente debe presentar un **plan de acción detallado** que incluya:
    1. Objetivo de la tarea.
    2. Archivos que serán modificados o creados.
    3. Comandos de terminal que se pretenden ejecutar.

* **Seguridad de Comandos:** Dado que ciertos comandos pueden ejecutar código arbitrario, el agente debe advertir sobre riesgos potenciales en directorios no confiables o configuraciones de Git/Hooks sensibles.

## 11. Arquitectura y Principios SOLID

* **Responsabilidad Única (SRP):** El código debe estar organizado en capas claras:
  * **Controladores (Path Operations):** Solo reciben la petición, validan la entrada básica y llaman al servicio.
  * **Servicios:** Contienen la lógica de negocio pura.
  * **Repositorios:** Capa exclusiva para interactuar con la base de datos a través de **SQLModel**.
* **Modularidad:** Para aplicaciones de mayor escala, se debe organizar el código en múltiples archivos para mantener la mantenibilidad.

## 12. Validación de Esquemas (DTOs)

* **Validación con Pydantic:** Antes de interactuar con la base de datos, se deben usar modelos de Pydantic para verificar la existencia de campos obligatorios y tipos de datos.
* **Validación de Email:** Para campos de correo electrónico, se debe asegurar que el valor sea un email válido utilizando el tipo `EmailStr` de Pydantic (que requiere la dependencia `email-validator`).
* **Conversión Automática:** Aprovechar la capacidad de FastAPI para convertir datos de red (JSON) directamente a modelos de Python antes de procesar la lógica.

## 13. Manejo de Errores y Middleware

* **Middleware de Error Global:** Se debe implementar un manejador de excepciones global para evitar que la aplicación falle (crash) ante errores inesperados.
* **Respuesta Estándar:** Cualquier excepción capturada debe ser devuelta al cliente en un formato JSON estándar: `{ "error": "Mensaje legible", "code": 500 }`.
* **HTTP Exceptions:** Utilizar `HTTPException` de FastAPI para errores controlados por el desarrollador (ej. 404, 403) [1].

## 14. Logging Estructurado

* **Niveles de Log:** No utilizar `print()`. Se deben emplear logs con niveles definidos (`Info`, `Warning`, `Error`) para facilitar la depuración en producción.
* **Trazabilidad:** Los logs deben incluir **timestamps** y, opcionalmente, información de validación (como los proporcionados por herramientas como Pydantic Logfire) para entender fallos en las entradas.

## 15. Seguridad y Privacidad de Credenciales

* **Acceso Restringido:** El agente tiene **estrictamente prohibido el acceso, lectura o modificación de archivos `.env`** o cualquier archivo que contenga secretos y credenciales del sistema.
* **Gestión de Secretos:** Las variables de entorno deben ser manejadas por el sistema operativo o por el almacén de secretos de CI/CD (GitHub Secrets), nunca expuestas en el código fuente.

## 10. Metodología de Desarrollo

* **Explicación Post-Implementación:** Tras la confirmación y ejecución de un cambio, el agente debe explicar brevemente qué se hizo y por qué se siguió esa lógica basada en los estándares de **FastAPI**.
* **Validadción de Entorno:** Antes de proponer una solución que requiera librerías externas, el agente debe verificar que el usuario esté en un **entorno virtual** activo para evitar conflictos de dependencias globales.
* **Código Intuitivo:** Las soluciones deben priorizar la **legibilidad y el tipado de Python** (PEP 8), asegurando que el código sea fácil de aprender y mantener, siguiendo la filosofía de FastAPI y SQLModel.

## 1. Estándares de Python y Tipado

* **Versiones y Tipado:** Se debe utilizar **Python 3.9+** con anotaciones de tipo estándar para mejorar la validación y el soporte del editor.
* **Programación Asíncrona:** Se prefiere el uso de `async def` para los endpoints de la API si se requiere manejar concurrencia de alto rendimiento.
* **Sintaxis Limpia:** El código debe seguir la filosofía de Python de ser **intuitivo, fácil de aprender y de lectura clara**.

## 2. Desarrollo con FastAPI

* **Instalación:** Utilizar siempre la instalación estándar mediante `pip install "fastapi[standard]"`, la cual incluye **Uvicorn** y otras dependencias críticas para el rendimiento.
* **Rendimiento:** Las aplicaciones deben ejecutarse bajo **Uvicorn** para garantizar que sea uno de los frameworks de Python más rápidos disponibles .
* **Inyección de Dependencias:** Utilizar el sistema `Depends()` para gestionar la lógica de negocio, como la sesión de la base de datos, lo cual facilita las pruebas y la modularidad.
* **Estándares API:** El código debe ser totalmente compatible con los estándares abiertos **OpenAPI** y **JSON Schema**.

## 4. Validación y Serialización (Pydantic)

* **Validación de Datos:** Aprovechar que Pydantic está basado en tipos de Python y que su núcleo está escrito en **Rust** para obtener la máxima velocidad en la validación.
* **Manejo de Errores:** Las validaciones deben devolver errores claros y automáticos cuando los datos de entrada no coincidan con el esquema definido.

## 5. Entorno y Herramientas de Terminal

* **Aislamiento:** Es obligatorio trabajar dentro de un **entorno virtual** activado antes de instalar cualquier dependencia como `fastapi`.
* **CLI de Desarrollo:** Durante el desarrollo local, utilizar el comando `fastapi dev` para habilitar el servidor con **auto-recarga** automática al detectar cambios en el código.
* **Herramientas CLI Adicionales:** Si el proyecto requiere herramientas de terminal, se recomienda usar **Typer**, conocido como el "FastAPI de las CLIs".

## 7. Control de Versiones con Git

* **Gestión de Cambios:** Utilizar Git como sistema de control de versiones **distribuido, rápido y escalable** para registrar la historia del proyecto.
* **Flujo de Trabajo Diario:** Seguir el conjunto mínimo de comandos de "Everyday Git": `add` para indexar, `status` para verificar, `commit` para registrar, y `push/pull` para sincronizar con el repositorio remoto.
* **Seguridad del Repositorio:**  
  * No ejecutar comandos en directorios `.git` de fuentes no confiables para evitar la ejecución de scripts maliciosos.
  * Git cuenta con protecciones para rechazar operaciones si el repositorio pertenece a otro usuario, lo cual debe respetarse en entornos ulti-usuario.
* **Archivos Ignorados:** Mantener siempre un archivo `.gitignore` actualizado para evitar el rastreo de archivos temporales o sensibles no deseados.

## 8. CI/CD con GitHub Actions

* **Automatización de Workflows:** Configurar acciones para **construir, probar y desplegar** el código automáticamente ante cualquier evento de GitHub (como un `push` o `pull_request`).
* **Matrix Builds:** Optimizar el tiempo de desarrollo utilizando flujos de trabajo de matriz para probar la API simultáneamente en **múltiples sistemas operativos** (Linux, macOS, Windows) y versiones de Python.
* **Gestión de Secretos:** Utilizar el **almacén de secretos integrado (Secret Store)** para manejar credenciales, tokens y claves de API, asegurando que nunca se expongan en los archivos de configuración del repositorio.
* **Depuración Eficiente:** Utilizar los **logs en tiempo real** para identificar fallos rápidamente mediante enlaces directos a las líneas de código donde falló la integración continua.
