"""
main.py - Entry point for GreenWave Ticketing System
Run: python main.py
"""

from src.gui import GreenWaveApp

def main():
    # GUI already loads storage through "from . import storage"
    app = GreenWaveApp()
    app.mainloop()

if __name__ == "__main__":
    main()
