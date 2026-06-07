"""
AnkIA - Context Manager
CRUD de contextos/vocabularios. Cada contexto es un archivo .txt en la carpeta decks/.
También gestiona metadata.json para recordar los idiomas asociados a cada contexto.
"""

import os
import re
import json

# Ruta base de los decks (relativa al directorio del proyecto)
DECKS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "decks")
METADATA_FILE = os.path.join(DECKS_DIR, "metadata.json")

def _ensure_decks_dir():
    """Crea la carpeta de decks si no existe."""
    os.makedirs(DECKS_DIR, exist_ok=True)

def _load_metadata() -> dict:
    """Carga los metadatos desde metadata.json."""
    if not os.path.exists(METADATA_FILE):
        return {}
    try:
        with open(METADATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def _save_metadata(data: dict):
    """Guarda los metadatos en metadata.json."""
    _ensure_decks_dir()
    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def _sanitize_name(name: str) -> str:
    """Sanitiza el nombre del contexto para usarlo como nombre de archivo.

    Reemplaza caracteres problemáticos pero mantiene legibilidad.
    Ejemplo: 'Vocabulario ES→DE' → 'Vocabulario ES-DE'
    """
    # Reemplazar flechas y caracteres especiales
    name = name.replace("→", "-").replace("->", "-").replace("←", "-").replace("<-", "-")
    # Eliminar caracteres no permitidos en nombres de archivo Windows
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # Eliminar espacios al inicio y final
    name = name.strip()
    # Reemplazar múltiples espacios por uno solo
    name = re.sub(r'\s+', ' ', name)
    return name

def list_contexts() -> list[dict]:
    """Lista todos los contextos disponibles.

    Returns:
        Lista de dicts con {name, path, card_count, source_lang, target_lang, level, description}
    """
    _ensure_decks_dir()
    contexts = []
    metadata = _load_metadata()

    for filename in sorted(os.listdir(DECKS_DIR)):
        if filename.endswith(".txt"):
            name = filename[:-4]  # Quitar .txt
            path = os.path.join(DECKS_DIR, filename)
            card_count = _count_cards(path)
            ctx_meta = metadata.get(name, {})
            
            contexts.append({
                "name": name,
                "path": path,
                "card_count": card_count,
                "source_lang": ctx_meta.get("source_lang", "Desconocido"),
                "target_lang": ctx_meta.get("target_lang", "Desconocido"),
                "level": ctx_meta.get("level", "B2"),
                "description": ctx_meta.get("description", ""),
            })

    return contexts

def create_context(name: str, source_lang: str, target_lang: str, level: str = "B2", description: str = "") -> dict:
    """Crea un nuevo contexto (archivo .txt vacío y guarda sus idiomas y nivel).

    Args:
        name: Nombre del contexto (ej: 'Vocabulario ES→DE')
        source_lang: Idioma de origen
        target_lang: Idioma de destino
        level: Nivel (ej: 'B2')
        description: Descripción opcional para contextualizar las recomendaciones (ej: 'vocabulario de cocina')

    Returns:
        Dict con {name, path, source_lang, target_lang, level, description} del contexto creado

    Raises:
        ValueError: Si el nombre es vacío o el contexto ya existe
    """
    _ensure_decks_dir()

    safe_name = _sanitize_name(name)
    if not safe_name:
        raise ValueError("El nombre del contexto no puede estar vacío.")

    path = os.path.join(DECKS_DIR, f"{safe_name}.txt")

    if os.path.exists(path):
        raise ValueError(f"El contexto '{safe_name}' ya existe.")

    # Crear archivo vacío
    with open(path, "w", encoding="utf-8") as f:
        pass  # Archivo vacío, sin cabeceras

    # Actualizar metadata
    metadata = _load_metadata()
    metadata[safe_name] = {
        "source_lang": source_lang,
        "target_lang": target_lang,
        "level": level,
        "description": description,
    }
    _save_metadata(metadata)

    return {"name": safe_name, "path": path, "source_lang": source_lang, "target_lang": target_lang, "level": level, "description": description}

def delete_context(name: str) -> bool:
    """Elimina un contexto (borra el archivo .txt y su metadata).

    Args:
        name: Nombre del contexto

    Returns:
        True si se eliminó, False si no existía
    """
    path = get_deck_path(name)
    deleted = False
    if path and os.path.exists(path):
        os.remove(path)
        deleted = True
    
    metadata = _load_metadata()
    if name in metadata:
        del metadata[name]
        _save_metadata(metadata)
        deleted = True
        
    return deleted

def get_deck_path(name: str) -> str | None:
    """Obtiene la ruta completa del archivo de un contexto.

    Args:
        name: Nombre del contexto

    Returns:
        Ruta completa o None si no existe
    """
    _ensure_decks_dir()
    safe_name = _sanitize_name(name)
    path = os.path.join(DECKS_DIR, f"{safe_name}.txt")

    if os.path.exists(path):
        return path
    return None

def get_context_metadata(name: str) -> dict:
    """Obtiene los idiomas de un contexto.
    
    Args:
        name: Nombre del contexto
        
    Returns:
        Dict con {"source_lang": "...", "target_lang": "...", "level": "...", "description": "..."}
    """
    metadata = _load_metadata()
    default = {"source_lang": "Español", "target_lang": "Alemán", "level": "B2", "description": ""}
    return metadata.get(name, default)

def _count_cards(path: str) -> int:
    """Cuenta las tarjetas válidas en un archivo.

    Args:
        path: Ruta al archivo .txt

    Returns:
        Número de líneas no vacías (tarjetas)
    """
    if not os.path.exists(path):
        return 0

    count = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip() and ";" in line:
                count += 1
    return count

def context_exists(name: str) -> bool:
    """Verifica si un contexto existe.

    Args:
        name: Nombre del contexto

    Returns:
        True si el contexto existe
    """
    return get_deck_path(name) is not None
