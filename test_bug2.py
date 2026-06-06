"""Test exhaustivo del bug snap_to_right."""
import sys
import os
sys.path.insert(0, r"C:\Users\josem\Desktop\AnkIA")
os.chdir(r"C:\Users\josem\Desktop\AnkIA")

from PySide6.QtCore import QTimer, QEventLoop, QPoint
from PySide6.QtWidgets import QApplication
from widget import AnkiaWidget


def wait_ms(ms):
    loop = QEventLoop()
    QTimer.singleShot(ms, loop.quit)
    loop.exec()


def dump(label, w):
    g = w.geometry()
    fg = w.frameGeometry()
    s = w.screen().availableGeometry() if w.screen() else None
    print(f"  [{label}]")
    print(f"    geometry      : {g}")
    print(f"    frameGeometry : {fg}")
    print(f"    isVisible     : {w.isVisible()}")
    print(f"    isHidden      : {w.isHidden()}")
    print(f"    size          : {w.size()}")
    print(f"    main_panel.vis: {w.main_panel.isVisible()}")
    if s:
        print(f"    screen        : {s}")
        on_screen = (g.x() >= s.x() and g.x() + g.width() <= s.x() + s.width()
                     and g.y() >= s.y() and g.y() + g.height() <= s.y() + s.height())
        print(f"    on_screen     : {on_screen}")


app = QApplication(sys.argv)
widget = AnkiaWidget()
widget.show()
wait_ms(300)

print("=" * 70)
print("ESCENARIO 1: Colapsar -> Expandir (sin drag)")
print("=" * 70)
dump("inicial", widget)
widget.snap_to_right()
wait_ms(500)
dump("tras 1er click (colapsado)", widget)
widget.snap_to_right()
wait_ms(500)
dump("tras 2do click (expandido)", widget)

print()
print("=" * 70)
print("ESCENARIO 2: Arrastrar a la izquierda -> Colapsar -> Expandir")
print("=" * 70)
# Simular arrastre: mover el widget a la izquierda
widget.move(100, 200)
wait_ms(100)
dump("tras drag a (100,200)", widget)
widget.snap_to_right()
wait_ms(500)
dump("tras colapsar", widget)
widget.snap_to_right()
wait_ms(500)
dump("tras expandir", widget)

print()
print("=" * 70)
print("ESCENARIO 3: Arrastrar abajo -> Colapsar -> Expandir")
print("=" * 70)
widget.move(500, 800)
wait_ms(100)
dump("tras drag a (500,800)", widget)
widget.snap_to_right()
wait_ms(500)
dump("tras colapsar", widget)
widget.snap_to_right()
wait_ms(500)
dump("tras expandir", widget)

print()
print("=" * 70)
print("ESCENARIO 4: Clicks rápidos (durante animación)")
print("=" * 70)
widget.move(1500, 200)
wait_ms(100)
dump("inicio", widget)
widget.snap_to_right()  # colapsar
wait_ms(50)  # muy pronto
print("  -> click 2 durante animacion 1")
widget.snap_to_right()  # expandir
wait_ms(500)
dump("tras clicks rapidos", widget)

print()
print("=" * 70)
print("ESCENARIO 5: Colapsar -> Drag -> Expandir")
print("=" * 70)
widget.snap_to_right()
wait_ms(500)
dump("colapsado", widget)
widget.move(100, 100)  # drag mientras esta colapsado
wait_ms(100)
dump("tras drag en estado colapsado", widget)
widget.snap_to_right()  # expandir
wait_ms(500)
dump("tras expandir", widget)

app.quit()
