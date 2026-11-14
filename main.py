# -*- coding: utf-8 -*-
"""
Root Entry Point: VQuant Quantitative Algorithmic Trading Ecosystem
Author: Nguyễn Mạnh Cường_B22DCCN099
Institution: Posts and Telecommunications Institute of Technology (PTIT)
"""

import os
import sys

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.main import main_loop

if __name__ == "__main__":
    main_loop()
