from PyQt6.QtWidgets import QFrame


def create_settings_card() -> QFrame:
    card = QFrame()
    card.setStyleSheet(
        """
        QFrame {
            background: white;
            border-radius: 12px;
        }
        QLabel {
            font-size: 16px;
            color: #555;
            font-weight: bold;
        }
        """
    )
    return card
