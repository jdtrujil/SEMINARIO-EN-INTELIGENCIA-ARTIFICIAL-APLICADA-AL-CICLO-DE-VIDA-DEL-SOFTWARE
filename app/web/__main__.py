"""Versión web local: python -m app.web y abrir http://127.0.0.1:8000"""

import sys

from app.web.servidor import main

if __name__ == "__main__":
    sys.exit(main())
