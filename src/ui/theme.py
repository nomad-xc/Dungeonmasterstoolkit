def load_stylesheet():
    return """
    QMainWindow {
        background-color: #1a1a1a;
    }

    QWidget {
        background-color: #1a1a1a;
        color: white;
        font-size: 12pt;
    }

    QListWidget {
        background-color: #232323;
        border: none;
        padding: 10px;
        outline: none;
    }

    QListWidget::item {
        padding: 14px;
        border-radius: 8px;
        margin-bottom: 4px;
    }

    QListWidget::item:selected {
        background-color: #8c6239;
        color: white;
    }

    QListWidget::item:hover {
        background-color: #444444;
    }

    QLabel {
        color: white;
    }
    """