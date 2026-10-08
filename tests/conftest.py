"""Pytest fixtures for sqlit integration tests."""

import pytest

from tests.fixtures.cli import *
from tests.fixtures.bigquery import *
from tests.fixtures.clickhouse import *
from tests.fixtures.cockroachdb import *
from tests.fixtures.db2 import *
from tests.fixtures.d1 import *
from tests.fixtures.duckdb import *
from tests.fixtures.exasol import *
from tests.fixtures.firebird import *
from tests.fixtures.flight import *
from tests.fixtures.impala import *
from tests.fixtures.mariadb import *
from tests.fixtures.mariadb_charset import *
from tests.fixtures.mssql import *
from tests.fixtures.mysql import *
from tests.fixtures.mysql_charset import *
from tests.fixtures.oracle import *
from tests.fixtures.oracle_legacy import *
from tests.fixtures.presto import *
from tests.fixtures.postgres import *
from tests.fixtures.trino import *
from tests.fixtures.ssh import *
from tests.fixtures.spanner import *
from tests.fixtures.sqlite import *
from tests.fixtures.surrealdb import *
from tests.fixtures.turso import *
from tests.fixtures.utils import *


@pytest.fixture(autouse=True)
def _reset_mock_docker_containers():
    """Ensure mock Docker containers do not leak between tests."""
    from sqlit.mock_settings import set_mock_docker_containers

    set_mock_docker_containers(None)
    yield
    set_mock_docker_containers(None)


@pytest.fixture(autouse=True)
def _no_host_ghostty_theme(monkeypatch, tmp_path):
    """Keep the developer's own Ghostty config from leaking into tests."""
    from sqlit.domains.shell.app import ghostty

    monkeypatch.setattr(ghostty, "GHOSTTY_CONFIG_DIR", tmp_path / "no-ghostty")


def pytest_addoption(parser):
    """Add shared CLI options for integration tests."""
    try:
        parser.addoption(
            "--run-docker-container",
            action="store_true",
            default=False,
            help="Run tests that can spin up temporary Docker containers",
        )
    except ValueError:
        pass
