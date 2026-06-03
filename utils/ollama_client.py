"""
AnkIA - Ollama Client
Comunicación con Ollama (IA local) para obtener traducciones y ejemplos de uso.

Ollama debe estar corriendo en http://localhost:11434
Modelos recomendados: llama3.2, translategemma
"""

import json
import requests

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "gpt-oss:120b-cloud"
REQUEST_TIMEOUT = 60  # segundos


def check_status() -> dict:
    """Verifica si Ollama está corriendo y qué modelos tiene disponibles.

    Returns:
        {
            "available": bool,
            "models": list[str],  # nombres de modelos disponibles
            "error": str | None
        }
    """
    try:
        # Verificar que Ollama responde
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [m["name"] for m in data.get("models", [])]
            return {
                "available": True,
                "models": models,
                "error": None,
            }
        else:
            return {
                "available": False,
                "models": [],
                "error": f"Ollama respondió con código {response.status_code}",
            }
    except requests.ConnectionError:
        return {
            "available": False,
            "models": [],
            "error": "No se pudo conectar con Ollama. ¿Está corriendo en localhost:11434?",
        }
    except requests.Timeout:
        return {
            "available": False,
            "models": [],
            "error": "Ollama no respondió a tiempo.",
        }
    except Exception as e:
        return {
            "available": False,
            "models": [],
            "error": f"Error inesperado: {str(e)}",
        }


def translate_word(
    word: str,
    source_lang: str,
    target_lang: str,
    context_name: str,
    model: str = DEFAULT_MODEL,
) -> dict:
    """Traduce una palabra usando Ollama y genera un ejemplo de uso.

    Args:
        word: Palabra a traducir (ej: 'foot')
        source_lang: Idioma origen (ej: 'Español')
        target_lang: Idioma destino (ej: 'Alemán')
        context_name: Nombre del contexto para dar background a la IA
        model: Modelo de Ollama a usar

    Returns:
        {
            "success": bool,
            "translation": str,    # traducción con info gramatical
            "example": str,        # frase de ejemplo
            "front": str,          # campo frontal (significado en idioma origen)
            "error": str | None
        }
    """
    system_prompt = (
        f"Eres un experto lingüista y traductor entre {source_lang} y {target_lang}. "
        f"Estás traduciendo para un contexto o temática específica: '{context_name}'. "
        f"Ten muy en cuenta este contexto ('{context_name}') para elegir la traducción y el ejemplo más apropiados.\n\n"
        f"INSTRUCCIONES ESTRICTAS DE FORMATO:\n"
        f"Dependiendo del tipo de palabra, debes formatear los valores del JSON EXACTAMENTE así:\n\n"
        f"REGLA 1 - SI ES UN SUSTANTIVO:\n"
        f"- \"front\": La palabra en {source_lang} (puedes añadir sinónimos con '/'). ¡NO añadas el tipo de palabra ni etiquetas como '(noun)'! Ej: 'idea / concepto'\n"
        f"- \"translation\": Estructura estricta: (artículo) traducción. NO AÑADAS género ni plural. Ej: '(die) Vorstellung' o '(the) car'\n"
        f"- \"example\": Frase de ejemplo en {target_lang}.\n\n"
        f"REGLA 2 - SI ES CUALQUIER OTRA COSA (Verbos, Adjetivos, etc.):\n"
        f"- \"front\": La palabra en {source_lang}. ¡NO añadas etiquetas! Ej: 'disolver'\n"
        f"- \"translation\": Solo la traducción en {target_lang}. Ej: 'auflösen'\n"
        f"- \"example\": Frase de ejemplo en {target_lang}.\n\n"
        f"Responde ÚNICAMENTE con JSON válido, sin texto adicional ni markdown.\n"
        f"Formato: {{\"front\": \"...\", \"translation\": \"...\", \"example\": \"...\"}}"
    )

    user_prompt = f"Traduce la palabra: '{word}'"

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": False,
                "options": {
                    "temperature": 0.3,  # Baja temperatura para traducciones precisas
                },
            },
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code != 200:
            return {
                "success": False,
                "translation": "",
                "example": "",
                "front": word,
                "error": f"Ollama respondió con código {response.status_code}",
            }

        data = response.json()
        content = data.get("message", {}).get("content", "")

        # Intentar parsear el JSON de la respuesta
        result = _parse_ollama_response(content)

        if result:
            return {
                "success": True,
                "translation": result.get("translation", ""),
                "example": result.get("example", ""),
                "front": result.get("front", word),
                "error": None,
            }
        else:
            return {
                "success": False,
                "translation": "",
                "example": "",
                "front": word,
                "error": f"No se pudo parsear la respuesta de Ollama: {content[:200]}",
            }

    except requests.ConnectionError:
        return {
            "success": False,
            "translation": "",
            "example": "",
            "front": word,
            "error": "No se pudo conectar con Ollama.",
        }
    except requests.Timeout:
        return {
            "success": False,
            "translation": "",
            "example": "",
            "front": word,
            "error": "Ollama tardó demasiado en responder.",
        }
    except Exception as e:
        return {
            "success": False,
            "translation": "",
            "example": "",
            "front": word,
            "error": f"Error: {str(e)}",
        }


def _parse_ollama_response(content: str) -> dict | None:
    """Intenta parsear el JSON de la respuesta de Ollama.

    Maneja casos donde Ollama envuelve el JSON en markdown code blocks.

    Args:
        content: Texto de respuesta de Ollama

    Returns:
        Dict parseado o None si no se pudo parsear
    """
    content = content.strip()

    # Intentar parseo directo
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Intentar extraer JSON de bloques de código markdown
    # Patrón: ```json ... ``` o ``` ... ```
    import re
    json_match = re.search(r"```(?:json)?\s*\n?(.*?)\n?\s*```", content, re.DOTALL)
    if json_match:
        try:
            return json.loads(json_match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # Intentar encontrar un objeto JSON en el texto
    json_match = re.search(r"\{[^{}]*\}", content)
    if json_match:
        try:
            return json.loads(json_match.group(0))
        except json.JSONDecodeError:
            pass

    return None


def get_available_models() -> list[str]:
    """Obtiene la lista de modelos disponibles en Ollama.

    Returns:
        Lista de nombres de modelos, vacía si Ollama no está disponible
    """
    status = check_status()
    return status["models"]
