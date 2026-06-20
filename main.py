"""
main.py
=======
Điểm khởi chạy chính của Vietcombank Digibank Pro Simulator.

Cách chạy:
    python main.py
"""

import sys
import os

# Đảm bảo thư mục gốc của project nằm trong Python path
sys.path.insert(0, os.path.dirname(__file__))

from utils.menu import run_menu


if __name__ == "__main__":
    run_menu()
