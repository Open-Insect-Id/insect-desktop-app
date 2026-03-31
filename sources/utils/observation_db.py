"""Module for SQLite based observation history.
The database is minimal and stored locally in the project root.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import logging

from utils.logger import setup_logger

logger = setup_logger(__name__)

import config


def get_db_path() -> Path:
    """Return the configured path to the observation database."""
    # Default to a local file in the data directory, but allow override from config
    if hasattr(config, "OBSERVATION_DB_PATH"):
        return Path(config.OBSERVATION_DB_PATH)
    project_root = Path(__file__).parent.parent.parent
    return project_root / "data" / "observations.db"


def init_observation_db() -> None:
    """Create the observation database and tables if they do not exist."""
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f"Initialisation de la base d'observations: {db_path}")

    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS observations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                image_path TEXT,
                species TEXT,
                confidence REAL,
                reliable INTEGER
            )"""
        )
        conn.commit()
    logger.debug("Table observations créée/vérifiée")


def add_observation(
    image_path: str | None,
    species_name: str | None,
    confidence: float | None,
    reliable: bool | None,
    timestamp: str | None = None,
) -> None:
    """Insert an observation record into the database."""
    timestamp = timestamp or datetime.now().isoformat(sep=" ", timespec="seconds")
    db_path = get_db_path()

    logger.info(
        f"Ajout d'observation: {species_name}, conf: {confidence}, img: {image_path}"
    )
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute(
            """INSERT INTO observations (timestamp, image_path, species, confidence, reliable)
            VALUES (?, ?, ?, ?, ?)""",
            (
                timestamp,
                image_path,
                species_name,
                None if confidence is None else float(confidence),
                1 if reliable else 0,
            ),
        )
        conn.commit()
    logger.debug("Observation enregistrée")


def delete_observation(observation_id: int) -> None:
    """Delete a single observation record by its ID."""
    db_path = get_db_path()
    logger.info(f"Suppression de l'observation ID: {observation_id}")

    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("DELETE FROM observations WHERE id = ?", (observation_id,))
        conn.commit()
    logger.debug("Observation supprimée")


def fetch_observations(limit: int | None = None) -> list[dict]:
    """Return all observations as a list of dicts, newest first."""
    db_path = get_db_path()
    if not db_path.exists():
        logger.warning(f"Base d'observations non trouvée: {db_path}")
        return []

    query = "SELECT id, timestamp, image_path, species, confidence, reliable FROM observations"
    query += " ORDER BY timestamp DESC"
    if limit is not None:
        query += " LIMIT ?"

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        if limit is not None:
            c.execute(query, (limit,))
        else:
            c.execute(query)
        rows = c.fetchall()

    observations = [dict(row) for row in rows]
    logger.info(f"{len(observations)} observations récupérées")
    return observations
