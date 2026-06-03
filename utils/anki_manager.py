"""
AnkIA - Anki Manager
Gestión de lectura/escritura de archivos .txt con formato Anki.

Formato de cada línea:
    significado;traducción_con_gramática <br><br> <i>frase_ejemplo</i>

Ejemplo:
    idea / concepto;die Vorstellung, -en <br><br> <i>Meine Vorstellung von Heimat ist ein Ort voller Frieden.</i>
"""

import os
import re


SEPARATOR = ";"
EXAMPLE_TEMPLATE = " <br><br> <i>{example}</i>"


def format_card(front: str, translation: str, example: str) -> str:
    """Formatea una tarjeta al formato Anki.

    Args:
        front: Significado en idioma origen (ej: 'idea / concepto')
        translation: Traducción con info gramatical (ej: 'die Vorstellung, -en')
        example: Frase de ejemplo (ej: 'Meine Vorstellung von Heimat...')

    Returns:
        Línea formateada lista para escribir en el .txt
    """
    front = front.strip()
    translation = translation.strip()
    example = example.strip()

    back = translation + EXAMPLE_TEMPLATE.format(example=example)
    return f"{front}{SEPARATOR}{back}"


def parse_card(line: str) -> dict | None:
    """Parsea una línea del .txt y extrae los campos.

    Args:
        line: Línea del archivo .txt

    Returns:
        Diccionario con {front, translation, example} o None si la línea es inválida
    """
    line = line.strip()
    if not line or SEPARATOR not in line:
        return None

    # Separar por el primer punto y coma
    parts = line.split(SEPARATOR, 1)
    if len(parts) != 2:
        return None

    front = parts[0].strip()
    back = parts[1].strip()

    # Extraer traducción y ejemplo del campo dorso
    # Patrón: "traducción <br><br> <i>ejemplo</i>"
    match = re.match(r"^(.*?)\s*<br><br>\s*<i>(.*?)</i>\s*$", back)

    if match:
        translation = match.group(1).strip()
        example = match.group(2).strip()
    else:
        # Si no tiene el formato esperado, todo es traducción sin ejemplo
        translation = back
        example = ""

    return {
        "front": front,
        "translation": translation,
        "example": example,
    }


def add_card(deck_path: str, front: str, translation: str, example: str) -> None:
    """Añade una tarjeta al final del archivo .txt.

    Args:
        deck_path: Ruta completa al archivo .txt del deck
        front: Significado en idioma origen
        translation: Traducción con gramática
        example: Frase de ejemplo
    """
    card_line = format_card(front, translation, example)

    # Asegurar que el archivo termina con newline antes de añadir
    if os.path.exists(deck_path) and os.path.getsize(deck_path) > 0:
        with open(deck_path, "r", encoding="utf-8") as f:
            content = f.read()
        if content and not content.endswith("\n"):
            card_line = "\n" + card_line

    with open(deck_path, "a", encoding="utf-8") as f:
        f.write(card_line + "\n")


def read_cards(deck_path: str) -> list[dict]:
    """Lee todas las tarjetas de un archivo .txt.

    Args:
        deck_path: Ruta completa al archivo .txt del deck

    Returns:
        Lista de diccionarios con {front, translation, example, index}
    """
    cards = []

    if not os.path.exists(deck_path):
        return cards

    with open(deck_path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            card = parse_card(line)
            if card:
                card["index"] = i
                cards.append(card)

    return cards


def delete_card(deck_path: str, index: int) -> bool:
    """Elimina una tarjeta por su índice de línea.

    Args:
        deck_path: Ruta completa al archivo .txt
        index: Índice de la línea a eliminar (0-based)

    Returns:
        True si se eliminó correctamente, False si no se encontró
    """
    if not os.path.exists(deck_path):
        return False

    with open(deck_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    if index < 0 or index >= len(lines):
        return False

    lines.pop(index)

    with open(deck_path, "w", encoding="utf-8") as f:
        f.writelines(lines)

    return True


def card_exists(deck_path: str, front: str) -> bool:
    """Verifica si ya existe una tarjeta con el mismo campo 'front'.

    Args:
        deck_path: Ruta completa al archivo .txt
        front: Campo frontal a buscar

    Returns:
        True si ya existe una tarjeta con ese frente
    """
    cards = read_cards(deck_path)
    front_lower = front.strip().lower()
    return any(card["front"].lower() == front_lower for card in cards)
