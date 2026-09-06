"""
Project package.

Loading the .env file here means every entry point (the ingester, the
dashboard and the tests) picks up local configuration without each one
having to remember to do it.
"""

from pathlib import Path

from dotenv import load_dotenv


load_dotenv(
    Path(__file__).resolve().parents[1] / ".env"
)
