from src.db.backend.memory import FileDataBase
from src.db.tui import TUI

if __name__ == '__main__':
    app = TUI()
    app.loop()