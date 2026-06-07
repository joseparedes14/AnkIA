import sys
import os
from PySide6.QtCore import Qt, QThread, Signal, QSize, QTimer
from PySide6.QtGui import QColor, QCursor, QGuiApplication
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QLineEdit, QListWidget, QListWidgetItem, QStackedWidget,
    QFrame, QComboBox, QSpinBox, QMessageBox, QScrollArea, QGraphicsDropShadowEffect,
    QFileDialog, QCheckBox
)

from utils import anki_manager, context_manager, ollama_client

# ─────────────────────────────────────────────
# Estilos — Distribución premium, acento ámbar
# Paleta: negro profundo + ámbar (#f59e0b) + blanco
# Contraste fuerte, personalidad cálida
# ─────────────────────────────────────────────
GLOBAL_STYLES = """
QWidget {
    font-family: "Inter", "Segoe UI", sans-serif;
    color: #fafafa;
    font-size: 13px;
}

QLabel {
    color: #fafafa;
    background: transparent;
}

QLabel#BrandLabel {
    font-size: 24px;
    font-weight: 200;
    letter-spacing: 0.45em;
    color: #fafafa;
    padding: 0;
    margin: 0;
}

QLabel#SectionLabel {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.3em;
    color: #f59e0b;
    text-transform: uppercase;
    padding: 0;
}

QLabel#MetaLabel {
    font-size: 10px;
    color: #a1a1aa;
    font-weight: 500;
    letter-spacing: 0.14em;
    padding: 0;
}

QLabel#FrontLabel {
    font-size: 14px;
    color: #ffffff;
    font-weight: 600;
}

QLabel#TranslationLabel {
    font-size: 12px;
    color: #c084fc;
    font-weight: 400;
}

QLabel#ExampleLabel {
    font-size: 11px;
    color: #a1a1aa;
    font-style: italic;
    padding-left: 10px;
    border-left: 1px solid rgba(245, 158, 11, 0.35);
}

QLabel#IndexLabel {
    font-size: 9px;
    color: #52525b;
    font-weight: 700;
    letter-spacing: 0.15em;
}

QLabel#FieldLabel {
    font-size: 9px;
    font-weight: 700;
    color: #52525b;
    letter-spacing: 0.25em;
}

/* ── Panel Principal ── */
#MainPanel {
    background-color: #0a0a0f;
    border-left: 1px solid rgba(255, 255, 255, 0.04);
}

/* ── Handle (pestaña lateral) — ámbar ── */
#HandleButton {
    background-color: #0a0a0f;
    border: none;
    border-left: 2px solid #f59e0b;
    color: #f59e0b;
    font-size: 22px;
    font-weight: 300;
    padding: 0;
}
#HandleButton:hover {
    background-color: #1c1c28;
    color: #fbbf24;
    border-left: 2px solid #fbbf24;
}

/* ── Botones ── */
QPushButton {
    background-color: transparent;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 2px;
    padding: 11px 16px;
    color: #fafafa;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.22em;
    text-transform: uppercase;
}
QPushButton:hover {
    border-color: #f59e0b;
    color: #f59e0b;
    background-color: rgba(245, 158, 11, 0.05);
}
QPushButton:pressed {
    background-color: rgba(245, 158, 11, 0.12);
}
QPushButton:disabled {
    color: #3f3f46;
    border-color: rgba(255, 255, 255, 0.04);
}

QPushButton#PrimaryButton {
    background-color: #f59e0b;
    border: 1px solid #f59e0b;
    color: #0a0a0f;
    font-weight: 800;
}
QPushButton#PrimaryButton:hover {
    background-color: #fbbf24;
    border-color: #fbbf24;
    color: #0a0a0f;
}
QPushButton#PrimaryButton:disabled {
    background-color: rgba(245, 158, 11, 0.15);
    border-color: rgba(245, 158, 11, 0.15);
    color: rgba(10, 10, 15, 0.4);
}

QPushButton#DangerButton {
    border-color: rgba(251, 113, 133, 0.3);
    color: #fb7185;
}
QPushButton#DangerButton:hover {
    border-color: #fb7185;
    background-color: rgba(251, 113, 133, 0.08);
    color: #fb7185;
}

QPushButton#GhostButton {
    border: none;
    color: #71717a;
    padding: 6px 4px;
    letter-spacing: 0.22em;
}
QPushButton#GhostButton:hover {
    color: #f59e0b;
    background: transparent;
}

QPushButton#IconButton {
    border: none;
    background: transparent;
    color: #52525b;
    font-size: 16px;
    padding: 0;
    font-weight: 200;
}
QPushButton#IconButton:hover {
    color: #f59e0b;
    background: transparent;
}

/* ── Inputs ── */
QLineEdit {
    background-color: transparent;
    border: none;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding: 12px 2px;
    font-size: 13px;
    color: #fafafa;
    selection-background-color: rgba(245, 158, 11, 0.3);
}
QLineEdit:focus {
    border-bottom: 1px solid #f59e0b;
}
QLineEdit:disabled {
    color: #3f3f46;
}

/* ── ComboBox ── */
QComboBox {
    background-color: transparent;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 2px;
    padding: 9px 12px;
    color: #fafafa;
    font-size: 11px;
}
QComboBox:hover {
    border-color: #f59e0b;
}
QComboBox QAbstractItemView {
    background-color: #15151f;
    color: #fafafa;
    selection-background-color: rgba(245, 158, 11, 0.25);
    selection-color: #0a0a0f;
    border: 1px solid #f59e0b;
    outline: none;
    padding: 4px;
}

/* ── SpinBox ── */
QSpinBox {
    background-color: transparent;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 2px;
    padding: 7px 10px;
    color: #fafafa;
    font-size: 12px;
}
QSpinBox:hover {
    border-color: #f59e0b;
}
QSpinBox::up-button, QSpinBox::down-button {
    background: transparent;
    border: none;
    width: 16px;
}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {
    background: rgba(245, 158, 11, 0.1);
}

/* ── CheckBox ── */
QCheckBox {
    color: #fafafa;
    font-size: 12px;
    spacing: 10px;
}
QCheckBox::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 2px;
    background: transparent;
}
QCheckBox::indicator:hover {
    border-color: #f59e0b;
}
QCheckBox::indicator:checked {
    background: #f59e0b;
    border-color: #f59e0b;
}

/* ── ListWidget ── */
QListWidget {
    background-color: transparent;
    border: none;
    outline: none;
    padding: 0;
}
QListWidget::item {
    padding: 18px 14px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    color: #fafafa;
}
QListWidget::item:hover {
    background-color: rgba(245, 158, 11, 0.04);
    color: #f59e0b;
}
QListWidget::item:selected {
    background-color: rgba(245, 158, 11, 0.1);
    color: #f59e0b;
    border-left: 2px solid #f59e0b;
    padding-left: 16px;
}

/* ── Card de vocabulario — fondo sólido para contraste ── */
#VocabCard {
    background-color: #15151f;
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 2px;
    border-left: 2px solid #f59e0b;
}
#VocabCard:hover {
    background-color: #1c1c28;
    border-color: rgba(255, 255, 255, 0.1);
}

/* ── ScrollArea ── */
QScrollArea {
    background: transparent;
    border: none;
}
QScrollBar:vertical {
    background: transparent;
    width: 4px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background: rgba(245, 158, 11, 0.3);
    border-radius: 2px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background: #f59e0b;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
    background: transparent;
}

/* ── Toast ── */
#ToastLabel {
    background-color: rgba(21, 21, 31, 0.96);
    color: #f59e0b;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    border: 1px solid rgba(245, 158, 11, 0.45);
    border-radius: 2px;
    padding: 10px 18px;
}

/* ── Líneas decorativas ── */
#AccentLine {
    background-color: #f59e0b;
    max-height: 2px;
    min-height: 2px;
    border: none;
}

#AccentLineDim {
    background-color: rgba(255, 255, 255, 0.07);
    max-height: 1px;
    min-height: 1px;
    border: none;
}
"""

# ─────────────────────────────────────────────
# Worker Thread para Ollama
# ─────────────────────────────────────────────
class TranslationWorker(QThread):
    finished_signal = Signal(dict)

    def __init__(self, word, source_lang, target_lang, context_name, context_description=""):
        super().__init__()
        self.word = word
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.context_name = context_name
        self.context_description = context_description

    def run(self):
        result = ollama_client.translate_word(
            word=self.word,
            source_lang=self.source_lang,
            target_lang=self.target_lang,
            context_name=self.context_name,
            context_description=self.context_description,
        )
        self.finished_signal.emit(result)


class RecommendationWorker(QThread):
    finished_signal = Signal(dict)

    def __init__(self, amount, existing_words, context_name, level, source_lang, target_lang, context_description=""):
        super().__init__()
        self.amount = amount
        self.existing_words = existing_words
        self.context_name = context_name
        self.level = level
        self.source_lang = source_lang
        self.target_lang = target_lang
        self.context_description = context_description

    def run(self):
        result = ollama_client.generate_recommendations(
            amount=self.amount,
            existing_words=self.existing_words,
            context_name=self.context_name,
            level=self.level,
            source_lang=self.source_lang,
            target_lang=self.target_lang,
            context_description=self.context_description,
        )
        self.finished_signal.emit(result)


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
def _accent_line(dim: bool = False) -> QFrame:
    line = QFrame()
    line.setObjectName("AccentLineDim" if dim else "AccentLine")
    line.setFixedHeight(1)
    return line


# ─────────────────────────────────────────────
# Widget Principal
# ─────────────────────────────────────────────
class AnkiaWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.expanded_width = 380
        self.handle_width = 30
        self.active_context = None
        self.pending_recommendations = []
        self._collapsed = False
        self._dragging = False
        self._drag_offset = None
        self._preferred_y = 0

        self._update_screen_rect()
        self._apply_geometry()

        self.setup_ui()
        self._position_children()
        QTimer.singleShot(0, self.refresh_contexts)  # Cargar mazos tras mostrar ventana

    # ─────────────────────────────────────────────
    # Anclaje a la derecha — helpers
    # ─────────────────────────────────────────────
    def _current_screen(self):
        win = self.windowHandle()
        if win is not None:
            s = win.screen()
            if s is not None:
                return s
        s = QGuiApplication.screenAt(QCursor.pos())
        if s is not None:
            return s
        return QGuiApplication.primaryScreen()

    def _update_screen_rect(self):
        screen = self._current_screen()
        self._sr = screen.availableGeometry()
        self._wh = int(self._sr.height() * 0.7)
        center = self._sr.y() + (self._sr.height() - self._wh) // 2
        if self._preferred_y == 0:
            self._preferred_y = center
        self._clamp_y()

    def _clamp_y(self):
        top = self._sr.y()
        bot = self._sr.bottom() - self._wh
        if self._preferred_y < top:
            self._preferred_y = top
        elif self._preferred_y > bot:
            self._preferred_y = bot

    def _full_w(self):
        return self.expanded_width + self.handle_width

    def _right_x(self, w):
        return self._sr.x() + self._sr.width() - w

    def _apply_geometry(self):
        w = self.handle_width if self._collapsed else self._full_w()
        self.setGeometry(self._right_x(w), self._preferred_y, w, self._wh)

    def _position_children(self):
        if not hasattr(self, 'handle_btn') or not hasattr(self, 'main_panel'):
            return
        w = self.width()
        h = self.height()
        hw = self.handle_width
        pw = self.expanded_width

        self.handle_btn.move(w - hw, max(0, (h - 80) // 2))

        if self._collapsed:
            self.main_panel.hide()
            self.toast_label.hide()
        else:
            self.main_panel.setGeometry(w - hw - pw, 0, pw, h)
            self.main_panel.show()

    def showEvent(self, event):
        super().showEvent(event)
        self._update_screen_rect()
        self._apply_geometry()
        self._position_children()
        self.raise_()
        
    def setup_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Handle — posicionado absolutamente via resizeEvent
        self.handle_btn = QPushButton("›", self)
        self.handle_btn.setObjectName("HandleButton")
        self.handle_btn.setFixedSize(self.handle_width, 80)
        self.handle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.handle_btn.clicked.connect(self.snap_to_right)

        # Panel principal — posicionado absolutamente via resizeEvent
        self.main_panel = QFrame(self)
        self.main_panel.setObjectName("MainPanel")
        self.main_panel.setFixedWidth(self.expanded_width)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 180))
        shadow.setOffset(-4, 0)
        self.main_panel.setGraphicsEffect(shadow)

        self.panel_layout = QVBoxLayout(self.main_panel)
        self.panel_layout.setContentsMargins(0, 0, 0, 0)
        self.panel_layout.setSpacing(0)

        self.stacked_widget = QStackedWidget()
        self.panel_layout.addWidget(self.stacked_widget)

        # Solo se crea la vista principal al inicio; el resto se crean bajo demanda
        self._settings_created = False
        self._deck_created = False
        self._recs_created = False
        self.setup_main_view()

        # Toast
        self.toast_label = QLabel("", self)
        self.toast_label.setObjectName("ToastLabel")
        self.toast_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.toast_label.hide()

        self.setStyleSheet(GLOBAL_STYLES)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._position_children()

    def setup_main_view(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 32, 32, 28)
        layout.setSpacing(0)

        # Header — ANKIA centrado, "IA" en ámbar + botón cerrar
        brand = QLabel(
            '<span style="color:#fafafa;">ANK</span>'
            '<span style="color:#f59e0b;">IA</span>'
        )
        brand.setObjectName("BrandLabel")
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand_wrap = QHBoxLayout()
        brand_wrap.setContentsMargins(0, 0, 0, 0)
        brand_wrap.addStretch()
        brand_wrap.addWidget(brand)
        brand_wrap.addStretch()
        close_btn = QPushButton("×")
        close_btn.setObjectName("IconButton")
        close_btn.setFixedSize(20, 20)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self.close_app)
        brand_wrap.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        layout.addLayout(brand_wrap)
        layout.addSpacing(16)
        layout.addWidget(_accent_line())
        layout.addSpacing(36)

        # MAZOS
        section = QLabel("MAZOS")
        section.setObjectName("SectionLabel")
        layout.addWidget(section)
        layout.addSpacing(14)
        self.list_contexts = QListWidget()
        self.list_contexts.itemSelectionChanged.connect(self.on_context_selected)
        self.list_contexts.itemDoubleClicked.connect(self.open_deck_detail)
        layout.addWidget(self.list_contexts)
        layout.addSpacing(16)

        # Acción
        actions = QHBoxLayout()
        actions.setSpacing(8)
        btn_new = QPushButton("+ NUEVO MAZO")
        btn_new.setObjectName("GhostButton")
        btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_new.clicked.connect(self.open_settings_view)
        actions.addWidget(btn_new)
        actions.addStretch()
        layout.addLayout(actions)
        layout.addSpacing(36)

        # AÑADIR
        section_add = QLabel("AÑADIR")
        section_add.setObjectName("SectionLabel")
        layout.addWidget(section_add)
        layout.addSpacing(14)
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Escribe y pulsa Enter")
        self.input_field.returnPressed.connect(self.on_enter_pressed)
        layout.addWidget(self.input_field)

        layout.addStretch()
        self.stacked_widget.addWidget(page)
        self.main_page = page

    def setup_settings_view(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 32, 32, 28)
        layout.setSpacing(0)

        # Header
        header = QHBoxLayout()
        title = QLabel("NUEVO MAZO")
        title.setStyleSheet("font-size: 14px; font-weight: 700; letter-spacing: 0.3em; color: #5eead4;")
        header.addWidget(title)
        header.addStretch()
        btn_back = QPushButton("VOLVER")
        btn_back.setObjectName("GhostButton")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.main_page))
        header.addWidget(btn_back)
        layout.addLayout(header)
        layout.addSpacing(14)
        layout.addWidget(_accent_line())
        layout.addSpacing(24)

        # Nombre
        lbl_name = QLabel("NOMBRE")
        lbl_name.setObjectName("FieldLabel")
        layout.addWidget(lbl_name)
        layout.addSpacing(6)
        self.new_ctx_name = QLineEdit()
        self.new_ctx_name.setPlaceholderText("Nombre del mazo")
        layout.addWidget(self.new_ctx_name)
        layout.addSpacing(20)

        # Idiomas
        h_layout = QHBoxLayout()
        h_layout.setSpacing(12)
        v1 = QVBoxLayout()
        v1.setSpacing(6)
        lbl_de = QLabel("DE")
        lbl_de.setObjectName("FieldLabel")
        v1.addWidget(lbl_de)
        self.combo_source = QComboBox()
        self.combo_source.addItems(["Español", "Inglés", "Alemán", "Francés", "Italiano", "Portugués", "Japonés", "Chino", "Coreano", "Ruso", "Árabe"])
        self.combo_source.setCurrentText("Inglés")
        v1.addWidget(self.combo_source)
        h_layout.addLayout(v1)

        v2 = QVBoxLayout()
        v2.setSpacing(6)
        lbl_a = QLabel("A")
        lbl_a.setObjectName("FieldLabel")
        v2.addWidget(lbl_a)
        self.combo_target = QComboBox()
        self.combo_target.addItems(["Español", "Inglés", "Alemán", "Francés", "Italiano", "Portugués", "Japonés", "Chino", "Coreano", "Ruso", "Árabe"])
        self.combo_target.setCurrentText("Español")
        v2.addWidget(self.combo_target)
        h_layout.addLayout(v2)
        layout.addLayout(h_layout)
        layout.addSpacing(20)

        # Nivel
        v3 = QVBoxLayout()
        v3.setSpacing(6)
        lbl_nivel = QLabel("NIVEL")
        lbl_nivel.setObjectName("FieldLabel")
        v3.addWidget(lbl_nivel)
        self.combo_level = QComboBox()
        self.combo_level.addItems(["A1", "A2", "B1", "B2", "C1", "C2"])
        self.combo_level.setCurrentText("B2")
        v3.addWidget(self.combo_level)
        layout.addLayout(v3)
        layout.addSpacing(20)

        # Descripción (opcional)
        v_desc = QVBoxLayout()
        v_desc.setSpacing(6)
        lbl_desc = QLabel("DESCRIPCIÓN (OPCIONAL)")
        lbl_desc.setObjectName("FieldLabel")
        v_desc.addWidget(lbl_desc)
        self.new_ctx_description = QLineEdit()
        self.new_ctx_description.setPlaceholderText("Ej: vocabulario de cocina")
        v_desc.addWidget(self.new_ctx_description)
        layout.addLayout(v_desc)
        layout.addSpacing(24)

        # Crear
        btn_create = QPushButton("CREAR MAZO")
        btn_create.setObjectName("PrimaryButton")
        btn_create.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_create.clicked.connect(self.create_context)
        layout.addWidget(btn_create)

        layout.addStretch()
        self.stacked_widget.addWidget(page)
        self.settings_page = page

    def setup_deck_view(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 32, 32, 28)
        layout.setSpacing(0)

        # Header
        header = QHBoxLayout()
        btn_back = QPushButton("‹ VOLVER")
        btn_back.setObjectName("GhostButton")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.main_page))
        header.addWidget(btn_back)
        header.addStretch()
        btn_delete_mazo = QPushButton("ELIMINAR")
        btn_delete_mazo.setObjectName("GhostButton")
        btn_delete_mazo.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_delete_mazo.clicked.connect(self.delete_active_mazo)
        header.addWidget(btn_delete_mazo)
        layout.addLayout(header)
        layout.addSpacing(24)

        # Title
        self.deck_title_label = QLabel("MAZO")
        self.deck_title_label.setObjectName("SectionLabel")
        layout.addWidget(self.deck_title_label)
        layout.addSpacing(8)
        self.deck_meta_label = QLabel("")
        self.deck_meta_label.setObjectName("MetaLabel")
        self.deck_meta_label.setWordWrap(True)
        layout.addWidget(self.deck_meta_label)
        layout.addSpacing(18)
        layout.addWidget(_accent_line())
        layout.addSpacing(24)

        # Actions
        actions = QHBoxLayout()
        actions.setSpacing(8)
        self.btn_download = QPushButton("DESCARGAR")
        self.btn_download.setObjectName("PrimaryButton")
        self.btn_download.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_download.clicked.connect(self.download_deck)
        actions.addWidget(self.btn_download)
        self.btn_open_recs = QPushButton("RECOMENDAR")
        self.btn_open_recs.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_open_recs.clicked.connect(self.open_recommendations_view)
        actions.addWidget(self.btn_open_recs)
        layout.addLayout(actions)
        layout.addSpacing(28)

        # TARJETAS
        section = QLabel("TARJETAS")
        section.setObjectName("SectionLabel")
        layout.addWidget(section)
        layout.addSpacing(12)

        # Scroll
        self.deck_cards_scroll = QScrollArea()
        self.deck_cards_scroll.setWidgetResizable(True)
        self.deck_cards_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.deck_cards_container = QWidget()
        self.deck_cards_layout = QVBoxLayout(self.deck_cards_container)
        self.deck_cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.deck_cards_layout.setContentsMargins(0, 0, 0, 0)
        self.deck_cards_layout.setSpacing(10)
        self.deck_cards_scroll.setWidget(self.deck_cards_container)
        layout.addWidget(self.deck_cards_scroll)

        self.stacked_widget.addWidget(page)
        self.deck_page = page

    def setup_recommendations_view(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(32, 32, 32, 28)
        layout.setSpacing(0)

        # Header
        header = QHBoxLayout()
        btn_back = QPushButton("‹ VOLVER")
        btn_back.setObjectName("GhostButton")
        btn_back.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_back.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.deck_page))
        header.addWidget(btn_back)
        header.addStretch()
        layout.addLayout(header)
        layout.addSpacing(20)

        # Title
        title = QLabel("RECOMENDACIONES")
        title.setObjectName("SectionLabel")
        layout.addWidget(title)
        layout.addSpacing(6)
        self.rec_meta_label = QLabel("")
        self.rec_meta_label.setObjectName("MetaLabel")
        self.rec_meta_label.setWordWrap(True)
        layout.addWidget(self.rec_meta_label)
        layout.addSpacing(16)
        layout.addWidget(_accent_line())
        layout.addSpacing(20)

        # Generation controls
        gen = QHBoxLayout()
        gen.setSpacing(12)
        v_amount = QVBoxLayout()
        v_amount.setSpacing(6)
        lbl_amount = QLabel("CANTIDAD")
        lbl_amount.setObjectName("FieldLabel")
        v_amount.addWidget(lbl_amount)
        self.spin_amount = QSpinBox()
        self.spin_amount.setRange(1, 20)
        self.spin_amount.setValue(5)
        v_amount.addWidget(self.spin_amount)
        gen.addLayout(v_amount)
        gen.addStretch()
        self.btn_generate = QPushButton("GENERAR")
        self.btn_generate.setObjectName("PrimaryButton")
        self.btn_generate.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_generate.clicked.connect(self.start_generate_recommendations)
        gen.addWidget(self.btn_generate, alignment=Qt.AlignmentFlag.AlignBottom)
        layout.addLayout(gen)
        layout.addSpacing(20)

        # Section
        section = QLabel("RESULTADO")
        section.setObjectName("SectionLabel")
        layout.addWidget(section)
        layout.addSpacing(10)

        # Scroll
        self.rec_scroll = QScrollArea()
        self.rec_scroll.setWidgetResizable(True)
        self.rec_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.rec_container = QWidget()
        self.rec_layout = QVBoxLayout(self.rec_container)
        self.rec_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.rec_layout.setContentsMargins(0, 0, 0, 0)
        self.rec_layout.setSpacing(8)
        self.rec_scroll.setWidget(self.rec_container)
        layout.addWidget(self.rec_scroll)

        # Save
        self.btn_save_recs = QPushButton("GUARDAR SELECCIONADAS")
        self.btn_save_recs.setObjectName("PrimaryButton")
        self.btn_save_recs.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save_recs.clicked.connect(self.save_selected_recommendations)
        self.btn_save_recs.hide()
        layout.addWidget(self.btn_save_recs)

        self.stacked_widget.addWidget(page)
        self.recs_page = page

    # ─────────────────────────────────────────────
    # Arrastrar + anclar a la derecha
    # ─────────────────────────────────────────────
    def _is_in_drag_area(self, pos) -> bool:
        if pos.y() >= 64:
            return False
        child = self.childAt(pos)
        if child is None:
            return True
        if isinstance(child, (QPushButton, QLineEdit, QComboBox, QSpinBox, QCheckBox)):
            return False
        return True

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self._is_in_drag_area(event.position().toPoint()):
            self._dragging = True
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self._dragging and (event.buttons() & Qt.MouseButton.LeftButton):
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return
        if not self._dragging and self._is_in_drag_area(event.position().toPoint()):
            self.setCursor(Qt.CursorShape.SizeAllCursor)
        else:
            self.unsetCursor()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._dragging and event.button() == Qt.MouseButton.LeftButton:
            self._dragging = False
            self._preferred_y = self.geometry().y()
            self._update_screen_rect()
            self._apply_geometry()
            self.raise_()
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def close_app(self):
        QApplication.quit()

    def snap_to_right(self):
        self._collapsed = not self._collapsed
        self._update_handle_arrow()
        self._update_screen_rect()
        self._apply_geometry()
        self._position_children()
        self.raise_()

    def _update_handle_arrow(self):
        self.handle_btn.setText("‹" if self._collapsed else "›")

    # ─────────────────────────────────────────────
    # Lógica de la App
    # ─────────────────────────────────────────────
    def refresh_contexts(self):
        self.list_contexts.clear()
        for ctx in context_manager.list_contexts():
            item = QListWidgetItem(ctx['name'])
            item.setSizeHint(QSize(0, 52))
            item.setData(Qt.ItemDataRole.UserRole, ctx['name'])
            self.list_contexts.addItem(item)

    def on_context_selected(self):
        items = self.list_contexts.selectedItems()
        if items:
            ctx_name = items[0].data(Qt.ItemDataRole.UserRole)
            self.input_field.setPlaceholderText(f"Añadir a '{ctx_name}'")

    def create_context(self):
        name = self.new_ctx_name.text().strip()
        if not name:
            self.show_toast("Nombre vacío")
            return
        try:
            context_manager.create_context(
                name,
                self.combo_source.currentText(),
                self.combo_target.currentText(),
                self.combo_level.currentText(),
                self.new_ctx_description.text().strip(),
            )
            self.refresh_contexts()
            self.new_ctx_name.clear()
            self.new_ctx_description.clear()
            self.stacked_widget.setCurrentWidget(self.main_page)
            self.show_toast(f"Mazo '{name}' creado")
        except Exception as e:
            self.show_toast(f"Error: {e}")

    def delete_context(self, name=None):
        if name is None:
            items = self.list_contexts.selectedItems()
            if not items:
                self.show_toast("Selecciona un mazo primero")
                return
            name = items[0].data(Qt.ItemDataRole.UserRole)
        reply = QMessageBox.question(
            self,
            "Confirmar",
            f"¿Eliminar el mazo '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            context_manager.delete_context(name)
            self.refresh_contexts()
            if self.active_context == name:
                self.active_context = None
            self.show_toast("Mazo eliminado")

    def on_enter_pressed(self):
        word = self.input_field.text().strip()
        if not word:
            return

        items = self.list_contexts.selectedItems()
        if not items:
            self.show_toast("Selecciona un mazo primero")
            return

        ctx_name = items[0].data(Qt.ItemDataRole.UserRole)
        ctx_meta = context_manager.get_context_metadata(ctx_name)
        source_lang = ctx_meta.get("source_lang", "Español")
        target_lang = ctx_meta.get("target_lang", "Alemán")

        self.input_field.setEnabled(False)
        self.input_field.setText("… procesando con IA")

        ctx_description = ctx_meta.get("description", "")
        self.worker = TranslationWorker(word, source_lang, target_lang, ctx_name, ctx_description)
        self.worker.finished_signal.connect(self.on_translation_finished)
        self.worker.start()

    def on_translation_finished(self, result):
        self.input_field.setEnabled(True)
        self.input_field.clear()
        self.input_field.setFocus()

        if result["success"]:
            items = self.list_contexts.selectedItems()
            if items:
                ctx_name = items[0].data(Qt.ItemDataRole.UserRole)
                deck_path = context_manager.get_deck_path(ctx_name)

                if anki_manager.card_exists(deck_path, result["front"]):
                    self.show_toast("La tarjeta ya existe")
                else:
                    anki_manager.add_card(
                        deck_path,
                        result["front"],
                        result["translation"],
                        result["example"],
                    )
                    self.show_toast(f"Añadido: {result['front']}")
                    self.refresh_contexts()
        else:
            self.show_toast("Error de IA")

    def show_toast(self, message):
        self.toast_label.setText(message)
        self.toast_label.adjustSize()
        h = self._wh if hasattr(self, '_wh') else self.height()
        x = int(self.handle_width + (self.expanded_width - self.toast_label.width()) / 2)
        y = h - self.toast_label.height() - 20
        self.toast_label.move(x, y)
        self.toast_label.show()
        QTimer.singleShot(3000, self.toast_label.hide)

    # ─────────────────────────────────────────────
    # Vista detalle del mazo (tarjetas, descargar, IA)
    # ─────────────────────────────────────────────
    def _clear_layout(self, layout):
        """Elimina todos los widgets de un layout (recursivo)."""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                child_layout = item.layout()
                if child_layout is not None:
                    self._clear_layout(child_layout)

    def _make_card_widget(self, card, is_recommendation=False):
        frame = QFrame()
        frame.setObjectName("VocabCard")
        card_layout = QVBoxLayout(frame)
        card_layout.setContentsMargins(14, 12, 14, 12)
        card_layout.setSpacing(5)

        if is_recommendation:
            top = QHBoxLayout()
            top.setContentsMargins(0, 0, 0, 0)
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            top.addWidget(checkbox)
            top.addStretch()
            card_layout.addLayout(top)
            frame.checkbox = checkbox
            frame.rec_data = card
        else:
            top = QHBoxLayout()
            top.setContentsMargins(0, 0, 0, 0)
            top.setSpacing(8)
            idx_label = QLabel(f"{card['index'] + 1:02d}")
            idx_label.setObjectName("IndexLabel")
            top.addWidget(idx_label)
            top.addStretch()
            btn_del = QPushButton("×")
            btn_del.setObjectName("IconButton")
            btn_del.setFixedSize(20, 20)
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
            deck_path = context_manager.get_deck_path(self.active_context)
            idx = card["index"]
            btn_del.clicked.connect(lambda checked=False, dp=deck_path, i=idx: self.delete_card_from_deck(dp, i))
            top.addWidget(btn_del)
            card_layout.addLayout(top)
            frame.card_index = card["index"]

        front_label = QLabel(card.get("front", ""))
        front_label.setObjectName("FrontLabel")
        front_label.setWordWrap(True)
        card_layout.addWidget(front_label)

        trans_label = QLabel(card.get("translation", ""))
        trans_label.setObjectName("TranslationLabel")
        trans_label.setWordWrap(True)
        card_layout.addWidget(trans_label)

        example = card.get("example", "")
        if example:
            ex_label = QLabel(f'"{example}"')
            ex_label.setObjectName("ExampleLabel")
            ex_label.setWordWrap(True)
            card_layout.addWidget(ex_label)

        return frame

    def open_settings_view(self):
        if not self._settings_created:
            self.setup_settings_view()
            self._settings_created = True
        self.stacked_widget.setCurrentWidget(self.settings_page)

    def open_deck_detail(self):
        if not self._deck_created:
            self.setup_deck_view()
            self._deck_created = True
        items = self.list_contexts.selectedItems()
        if not items:
            self.show_toast("Selecciona un mazo primero")
            return
        ctx_name = items[0].data(Qt.ItemDataRole.UserRole)
        self.active_context = ctx_name
        self.render_deck_view()
        self.stacked_widget.setCurrentWidget(self.deck_page)

    def _show_confirm_dialog(self, title: str, text: str) -> int:
        """Diálogo de confirmación con estilo coherente y botones diferenciados."""
        self.raise_()
        self.activateWindow()
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        msg.setDefaultButton(QMessageBox.StandardButton.No)
        msg.setWindowFlags(msg.windowFlags() | Qt.WindowType.Dialog | Qt.WindowType.WindowStaysOnTopHint)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #15151f;
            }
            QMessageBox QLabel {
                color: #fafafa;
                font-size: 12px;
                padding: 4px;
            }
            QMessageBox QPushButton {
                background-color: transparent;
                border: 1px solid #f59e0b;
                border-radius: 2px;
                padding: 9px 24px;
                color: #f59e0b;
                font-size: 10px;
                font-weight: 700;
                letter-spacing: 0.2em;
                min-width: 90px;
                text-transform: uppercase;
            }
            QMessageBox QPushButton:hover {
                background-color: #f59e0b;
                color: #0a0a0f;
            }
            QMessageBox QPushButton:pressed {
                background-color: #fbbf24;
                color: #0a0a0f;
            }
        """)
        return msg.exec()

    def delete_active_mazo(self):
        """Elimina el mazo activo (con confirmación)."""
        if not self.active_context:
            return
        name = self.active_context
        reply = self._show_confirm_dialog(
            "Confirmar",
            f"¿Eliminar el mazo '{name}' y todas sus tarjetas?",
        )
        if reply == QMessageBox.StandardButton.Yes:
            context_manager.delete_context(name)
            self.active_context = None
            self.refresh_contexts()
            self.stacked_widget.setCurrentWidget(self.main_page)
            self.show_toast("Mazo eliminado")

    def render_deck_view(self):
        if not self.active_context:
            return
        deck_path = context_manager.get_deck_path(self.active_context)
        ctx_meta = context_manager.get_context_metadata(self.active_context)

        description = ctx_meta.get("description", "")
        desc_text = f"    //    📌 {description}" if description else ""

        self.deck_title_label.setText("MAZO")
        self.deck_meta_label.setText(
            f"{self.active_context}    //    "
            f"{ctx_meta.get('source_lang', '?')} → {ctx_meta.get('target_lang', '?')}    //    "
            f"NIVEL {ctx_meta.get('level', 'B2')}"
            f"{desc_text}"
        )

        self._clear_layout(self.deck_cards_layout)

        if not deck_path or not os.path.exists(deck_path):
            self._add_empty_state("Mazo no encontrado")
            return

        cards = anki_manager.read_cards(deck_path)
        if not cards:
            self._add_empty_state("Sin tarjetas")
            return

        for card in reversed(cards):
            self.deck_cards_layout.addWidget(self._make_card_widget(card))

    def _add_empty_state(self, text):
        empty = QLabel(text)
        empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
        empty.setStyleSheet(
            "color: #4a4a5c; padding: 32px; font-size: 10px; "
            "letter-spacing: 0.2em; text-transform: uppercase;"
        )
        self.deck_cards_layout.addWidget(empty)

    def delete_card_from_deck(self, deck_path, index):
        if anki_manager.delete_card(deck_path, index):
            self.show_toast("Tarjeta eliminada")
            self.render_deck_view()
            self.refresh_contexts()
        else:
            self.show_toast("No se pudo eliminar")

    def download_deck(self):
        if not self.active_context:
            return
        deck_path = context_manager.get_deck_path(self.active_context)
        if not deck_path or not os.path.exists(deck_path):
            self.show_toast("Mazo no encontrado")
            return

        default_name = f"{self.active_context}.txt"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar mazo para Anki",
            default_name,
            "Archivos de texto (*.txt);;Todos los archivos (*)",
        )
        if not file_path:
            return
        try:
            with open(deck_path, "r", encoding="utf-8") as f:
                content = f.read()
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            self.show_toast(f"Guardado: {os.path.basename(file_path)}")
        except Exception as e:
            self.show_toast(f"Error al guardar: {e}")

    # ─────────────────────────────────────────────
    # Recomendaciones IA
    # ─────────────────────────────────────────────
    def open_recommendations_view(self):
        if not self._recs_created:
            self.setup_recommendations_view()
            self._recs_created = True
        if not self.active_context:
            self.show_toast("Selecciona un mazo primero")
            return
        ctx_meta = context_manager.get_context_metadata(self.active_context)
        self.rec_meta_label.setText(
            f"{self.active_context}    //    "
            f"{ctx_meta.get('source_lang', '?')} → {ctx_meta.get('target_lang', '?')}    //    "
            f"NIVEL {ctx_meta.get('level', 'B2')}\n"
            f"La IA evitará sugerir palabras que ya tengas en el mazo."
        )
        self._clear_layout(self.rec_layout)
        self.btn_save_recs.hide()
        self.pending_recommendations = []
        self.stacked_widget.setCurrentWidget(self.recs_page)

    def start_generate_recommendations(self):
        if not self.active_context:
            return
        if not ollama_client.check_status().get("available"):
            self.show_toast("Ollama no disponible")
            return

        deck_path = context_manager.get_deck_path(self.active_context)
        existing_words = []
        if deck_path and os.path.exists(deck_path):
            existing_words = [c["front"] for c in anki_manager.read_cards(deck_path)]

        ctx_meta = context_manager.get_context_metadata(self.active_context)

        self.btn_generate.setEnabled(False)
        self.btn_generate.setText("GENERANDO…")
        self._clear_layout(self.rec_layout)
        self.btn_save_recs.hide()
        self.pending_recommendations = []

        self.rec_worker = RecommendationWorker(
            amount=self.spin_amount.value(),
            existing_words=existing_words,
            context_name=self.active_context,
            level=ctx_meta.get("level", "B2"),
            source_lang=ctx_meta.get("source_lang", "Español"),
            target_lang=ctx_meta.get("target_lang", "Alemán"),
            context_description=ctx_meta.get("description", ""),
        )
        self.rec_worker.finished_signal.connect(self.on_recommendations_finished)
        self.rec_worker.start()

    def on_recommendations_finished(self, result):
        self.btn_generate.setEnabled(True)
        self.btn_generate.setText("GENERAR")

        if not result.get("success"):
            self.show_toast(result.get("error", "Error desconocido"))
            return

        recs = result.get("recommendations", [])
        if not recs:
            self.show_toast("La IA no devolvió resultados")
            return

        self.pending_recommendations = recs
        for rec in recs:
            self.rec_layout.addWidget(self._make_card_widget(rec, is_recommendation=True))
        self.btn_save_recs.show()

    def save_selected_recommendations(self):
        if not self.active_context or not self.pending_recommendations:
            return
        deck_path = context_manager.get_deck_path(self.active_context)
        if not deck_path:
            self.show_toast("Mazo no encontrado")
            return

        saved = 0
        skipped = 0
        for i in range(self.rec_layout.count()):
            item = self.rec_layout.itemAt(i)
            widget = item.widget() if item else None
            if not widget or not hasattr(widget, "checkbox"):
                continue
            if not widget.checkbox.isChecked():
                continue
            rec = widget.rec_data
            front = (rec.get("front") or "").strip()
            translation = (rec.get("translation") or "").strip()
            example = (rec.get("example") or "").strip()
            if not front:
                continue
            if anki_manager.card_exists(deck_path, front):
                skipped += 1
                continue
            anki_manager.add_card(deck_path, front, translation, example)
            saved += 1

        self.pending_recommendations = []
        msg = f"Guardadas {saved} tarjetas"
        if skipped:
            msg += f" ({skipped} ya existían)"
        if not self._deck_created:
            self.setup_deck_view()
            self._deck_created = True
        self.show_toast(msg)
        self.refresh_contexts()
        self.render_deck_view()
        self.stacked_widget.setCurrentWidget(self.deck_page)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = AnkiaWidget()
    widget.show()
    sys.exit(app.exec())
