"""Script de prueba para reproducir el bug de snap_to_right."""
import sys
import os
sys.path.insert(0, r"C:\Users\josem\Desktop\AnkIA")

# Cambiar al directorio del proyecto
os.chdir(r"C:\Users\josem\Desktop\AnkIA")

from PySide6.QtCore import QTimer, QEventLoop
from PySide6.QtWidgets import QApplication
from widget import AnkiaWidget


def wait_ms(ms):
    """Espera síncronamente ms milisegundos."""
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


app = QApplication(sys.argv)
widget = AnkiaWidget()
widget.show()

# Esperar a que se estabilice
wait_ms(300)

print("=" * 60)
print("ESTADO INICIAL")
print("=" * 60)
print(f"  geometry: {widget.geometry()}")
print(f"  collapsed: {widget.collapsed}")
print(f"  main_panel.isVisible(): {widget.main_panel.isVisible()}")
print(f"  widget.isVisible(): {widget.isVisible()}")
print(f"  screen_rect: {widget.screen_rect}")

# Primer click: colapsar
print()
print("=" * 60)
print("PRIMER CLICK (colapsar)")
print("=" * 60)
widget.snap_to_right()
print(f"  Tras snap_to_right, collapsed: {widget.collapsed}")
print(f"  geometry: {widget.geometry()}")
wait_ms(500)  # esperar a que termine la animación
print(f"  Tras animación, geometry: {widget.geometry()}")
print(f"  collapsed: {widget.collapsed}")
print(f"  main_panel.isVisible(): {widget.main_panel.isVisible()}")
print(f"  widget.isVisible(): {widget.isVisible()}")

# Segundo click: expandir
print()
print("=" * 60)
print("SEGUNDO CLICK (expandir)")
print("=" * 60)
widget.snap_to_right()
print(f"  Tras snap_to_right, collapsed: {widget.collapsed}")
print(f"  geometry: {widget.geometry()}")
print(f"  main_panel.isVisible() ANTES de animación: {widget.main_panel.isVisible()}")
wait_ms(500)  # esperar a que termine la animación
print(f"  Tras animación, geometry: {widget.geometry()}")
print(f"  collapsed: {widget.collapsed}")
print(f"  main_panel.isVisible(): {widget.main_panel.isVisible()}")
print(f"  widget.isVisible(): {widget.isVisible()}")
print(f"  widget.size(): {widget.size()}")
print(f"  widget.x(): {widget.x()}, widget.y(): {widget.y()}")
print(f"  widget.width(): {widget.width()}, widget.height(): {widget.height()}")

# Verificar si está fuera de pantalla
screen = widget.screen().availableGeometry()
print()
print("=" * 60)
print("VERIFICACIÓN")
print("=" * 60)
print(f"  screen.availableGeometry(): {screen}")
print(f"  widget.frameGeometry(): {widget.frameGeometry()}")
g = widget.frameGeometry()
if g.x() < screen.x() or g.x() + g.width() > screen.x() + screen.width():
    print("  ⚠️  EL WIDGET ESTÁ FUERA DE PANTALLA!")
elif g.y() < screen.y() or g.y() + g.height() > screen.y() + screen.height():
    print("  ⚠️  EL WIDGET ESTÁ FUERA DE PANTALLA VERTICALMENTE!")
else:
    print("  ✓ El widget está dentro de la pantalla")

# Esperar y comprobar de nuevo
wait_ms(200)
print()
print("Tras 200ms adicionales:")
print(f"  widget.geometry(): {widget.geometry()}")
print(f"  widget.isVisible(): {widget.isVisible()}")
print(f"  widget.size(): {widget.size()}")

# Forzar repaint y comprobar
widget.repaint()
wait_ms(100)
print()
print("Tras repaint:")
print(f"  widget.geometry(): {widget.geometry()}")
print(f"  widget.isVisible(): {widget.isVisible()}")
print(f"  widget.isHidden(): {widget.isHidden()}")
print(f"  widget.size(): {widget.size()}")
print(f"  widget.width(): {widget.width()}")

app.quit()
