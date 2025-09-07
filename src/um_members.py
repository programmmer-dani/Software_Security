# src/um_members.py

import sys
import os

# Add src to path when running directly
if __name__ == "__main__":
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from presentation import cli


def main():
    print("App starting…")
    cli.run()


if __name__ == "__main__":
    main()
