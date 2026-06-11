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
    context_description: str = "",
    mode: str = "direct",
) -> dict:
    """Traduce una palabra usando Ollama y genera un ejemplo de uso.

    Args:
        word: Palabra a traducir (ej: 'foot')
        source_lang: Idioma origen (ej: 'Español')
        target_lang: Idioma destino (ej: 'Alemán')
        context_name: Nombre del contexto para dar background a la IA
        model: Modelo de Ollama a usar
        context_description: Descripción opcional adicional del contexto
        mode: "direct" (source→target) o "inverse" (target→source)

    Returns:
        {
            "success": bool,
            "translation": str,    # traducción con info gramatical
            "example": str,        # frase de ejemplo
            "front": str,          # campo frontal (significado en idioma origen)
            "error": str | None
        }
    """
    if mode == "inverse":
        source_lang, target_lang = target_lang, source_lang

    context_extra = ""
    if context_description:
        context_extra = f" Descripción adicional: '{context_description}'."

    system_prompt = (
        f"Eres un experto lingüista y traductor entre {source_lang} y {target_lang}. "
        f"Estás traduciendo para un contexto o temática específica: '{context_name}'."
        f"{context_extra} "
        f"Ten muy en cuenta este contexto para elegir la traducción y el ejemplo más apropiados.\n\n"
        f"INSTRUCCIONES ESTRICTAS DE FORMATO:\n"
        f"Dependiendo del tipo de palabra, debes formatear los valores del JSON EXACTAMENTE así:\n\n"
        f"REGLA 1 - SI ES UN SUSTANTIVO:\n"
        f"- \"front\": La palabra en {source_lang} (puedes añadir sinónimos con '/'). ¡NO añadas el tipo de palabra ni etiquetas como '(noun)'! Ej: 'idea / concepto'\n"
        f"- \"translation\": Estructura estricta: (artículo) traducción. El ARTÍCULO debe estar SIEMPRE en {target_lang}, NUNCA en {source_lang}. NO AÑADAS género ni plural. Ej: '(la) mesa' (correcto), '(the) mesa' (INCORRECTO porque el artículo está en Inglés en vez de Español).\n"
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


def generate_recommendations(
    amount: int,
    existing_words: list[str],
    context_name: str,
    level: str,
    source_lang: str,
    target_lang: str,
    model: str = DEFAULT_MODEL,
    context_description: str = "",
) -> dict:
    """Genera recomendaciones de palabras nuevas usando Ollama.

    Args:
        amount: Cantidad de palabras a generar (1-20).
        existing_words: Lista de palabras frontales que ya existen para no repetirlas.
        context_name: Nombre del contexto.
        level: Nivel CEFR (ej. 'B2').
        source_lang: Idioma de origen.
        target_lang: Idioma de destino.
        model: Modelo de Ollama.
        context_description: Descripción opcional adicional del contexto.

    Returns:
        {
            "success": bool,
            "recommendations": list[dict],
            "error": str | None
        }
    """
    existing_str = ", ".join(existing_words)

    context_extra = ""
    if context_description:
        context_extra = f" Descripción adicional del contexto: '{context_description}'."

    system_prompt = (
        f"Eres un experto lingüista y profesor de vocabulario. "
        f"Tu tarea es recomendar exactamente {amount} palabras NUEVAS para un estudiante de nivel {level} "
        f"en la temática o contexto '{context_name}'."
        f"{context_extra} "
        f"Los idiomas son: origen {source_lang}, destino {target_lang}.\n\n"
        f"RESTRICCIÓN CRÍTICA: NO puedes sugerir ninguna de estas palabras, ya existen en el mazo: [{existing_str}].\n\n"
        f"INSTRUCCIONES ESTRICTAS DE FORMATO:\n"
        f"Dependiendo del tipo de palabra, debes formatear los valores del JSON EXACTAMENTE así:\n\n"
        f"REGLA 1 - SI ES UN SUSTANTIVO:\n"
        f"- \"front\": La palabra en {source_lang} (puedes añadir sinónimos con '/'). ¡NO añadas el tipo de palabra ni etiquetas como '(noun)'! Ej: 'idea / concepto'\n"
        f"- \"translation\": Estructura estricta: (artículo) traducción. El ARTÍCULO debe estar SIEMPRE en {target_lang}, NUNCA en {source_lang}. NO AÑADAS género ni plural. Ej: '(la) mesa' (correcto), '(the) mesa' (INCORRECTO porque el artículo está en Inglés en vez de Español).\n"
        f"- \"example\": Frase de ejemplo en {target_lang}.\n\n"
        f"REGLA 2 - SI ES CUALQUIER OTRA COSA (Verbos, Adjetivos, etc.):\n"
        f"- \"front\": La palabra en {source_lang}. ¡NO añadas etiquetas! Ej: 'disolver'\n"
        f"- \"translation\": Solo la traducción en {target_lang}. Ej: 'auflösen'\n"
        f"- \"example\": Frase de ejemplo en {target_lang}.\n\n"
        f"Responde ÚNICAMENTE con un JSON válido que sea una lista (array) de {amount} objetos con estas claves, sin texto adicional ni markdown.\n"
        f"Formato esperado:\n"
        f"[\n"
        f"  {{\"front\": \"...\", \"translation\": \"...\", \"example\": \"...\"}},\n"
        f"  ...\n"
        f"]"
    )

    user_prompt = f"Genera {amount} palabras relacionadas con '{context_name}' para nivel {level}."

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
                    "temperature": 0.7,
                },
            },
            timeout=REQUEST_TIMEOUT * 2,
        )

        if response.status_code != 200:
            return {"success": False, "recommendations": [], "error": f"Ollama respondió con código {response.status_code}"}

        data = response.json()
        content = data.get("message", {}).get("content", "")
        
        result = _parse_ollama_response(content)
        
        if result is not None and isinstance(result, list):
            return {"success": True, "recommendations": result, "error": None}
        elif result is not None and isinstance(result, dict) and "recommendations" in result:
             return {"success": True, "recommendations": result["recommendations"], "error": None}
        else:
            return {"success": False, "recommendations": [], "error": f"No se pudo parsear como lista: {content[:200]}"}

    except requests.ConnectionError:
        return {"success": False, "recommendations": [], "error": "No se pudo conectar con Ollama."}
    except requests.Timeout:
        return {"success": False, "recommendations": [], "error": "Ollama tardó demasiado en responder."}
    except Exception as e:
        return {"success": False, "recommendations": [], "error": f"Error: {str(e)}"}


def _parse_ollama_response(content: str) -> dict | list | None:
    """Intenta parsear el JSON de la respuesta de Ollama.

    Maneja casos donde Ollama envuelve el JSON en markdown code blocks.

    Args:
        content: Texto de respuesta de Ollama

    Returns:
        Dict o List parseado o None si no se pudo parsear
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
