DARK_THEME = """
QMainWindow, QWidget {
    background-color: #111827;
    color: #e5e7eb;
    font-family: 'Segoe UI', 'Ubuntu', sans-serif;
}
QScrollArea {
    border: none;
    background-color: #111827;
}
QScrollBar:vertical {
    background: #1f2937;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background: #374151;
    border-radius: 4px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QLineEdit {
    background-color: #1f2937;
    border: 1px solid #374151;
    border-radius: 8px;
    padding: 10px 16px;
    color: #f9fafb;
    font-size: 15px;
}
QLineEdit:focus {
    border-color: #6366f1;
}
QPushButton#search_btn {
    background-color: #6366f1;
    border: none;
    border-radius: 8px;
    padding: 10px 24px;
    color: white;
    font-size: 15px;
    font-weight: bold;
}
QPushButton#search_btn:hover {
    background-color: #4f46e5;
}
QPushButton#search_btn:disabled {
    background-color: #374151;
    color: #6b7280;
}
QPushButton#download_btn {
    background-color: #10b981;
    border: none;
    border-radius: 6px;
    padding: 8px 20px;
    color: white;
    font-weight: bold;
}
QPushButton#download_btn:hover {
    background-color: #059669;
}
QPushButton#download_btn:disabled {
    background-color: #374151;
    color: #6b7280;
}
QPushButton#back_btn {
    background-color: transparent;
    border: 1px solid #374151;
    border-radius: 6px;
    padding: 6px 14px;
    color: #9ca3af;
}
QPushButton#back_btn:hover {
    background-color: #1f2937;
    color: #f9fafb;
}
QTableWidget {
    background-color: #1f2937;
    border: none;
    border-radius: 8px;
    gridline-color: #374151;
    selection-background-color: #312e81;
}
QTableWidget::item {
    padding: 8px;
    border-bottom: 1px solid #374151;
}
QTableWidget::item:selected {
    background-color: #312e81;
    color: #f9fafb;
}
QHeaderView::section {
    background-color: #1f2937;
    color: #9ca3af;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #374151;
    font-size: 12px;
    font-weight: bold;
    text-transform: uppercase;
}
QProgressBar {
    background-color: #374151;
    border-radius: 4px;
    text-align: center;
    height: 8px;
}
QProgressBar::chunk {
    background-color: #6366f1;
    border-radius: 4px;
}
QLabel#status_label {
    color: #6b7280;
    font-size: 13px;
}
"""
