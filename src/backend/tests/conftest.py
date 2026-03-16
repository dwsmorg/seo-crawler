"""Globale Test-Fixtures fuer pytest.

Stellt gemeinsame Fixtures fuer alle Tests bereit.
"""

import pytest
from fastapi.testclient import TestClient

from backend.api.app import create_app


@pytest.fixture
def app() -> TestClient:
    """Erstellt einen Test-Client fuer die FastAPI-Anwendung.

    Returns:
        TestClient-Instanz
    """
    return TestClient(create_app())
