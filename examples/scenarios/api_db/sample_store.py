"""Small stdlib-only API/database contract fixture; no network listener."""
import sqlite3


def create_store() -> sqlite3.Connection:
    db = sqlite3.connect(':memory:')
    db.execute('CREATE TABLE sample (sample_id TEXT PRIMARY KEY, value REAL NOT NULL CHECK(value >= 0))')
    return db


def add_sample(db: sqlite3.Connection, sample_id: str, value: float) -> dict:
    if not sample_id.strip():
        return {'status': 400, 'error': 'sample_id is required'}
    if value < 0:
        return {'status': 422, 'error': 'value must be nonnegative'}
    try:
        db.execute('INSERT INTO sample(sample_id, value) VALUES (?, ?)', (sample_id.strip(), value))
        db.commit()
    except sqlite3.IntegrityError:
        return {'status': 409, 'error': 'sample_id already exists'}
    return {'status': 201, 'sample': {'sample_id': sample_id.strip(), 'value': value}}
