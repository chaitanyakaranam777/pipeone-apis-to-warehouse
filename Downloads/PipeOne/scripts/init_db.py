#!/usr/bin/env python3
"""Initialise the database."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.connection import init_db, health_check
if __name__ == "__main__":
    print("Initialising database...")
    init_db()
    ok = health_check()
    print(f"Health check: {'OK' if ok else 'FAILED'}")
