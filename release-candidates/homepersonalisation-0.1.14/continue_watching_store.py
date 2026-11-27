"""Candidate storage; caller must resolve active Kodi profile directory."""
import sqlite3
from pathlib import Path
from contextlib import closing
from continue_watching_candidate import dismiss

class DismissalStore:
    def __init__(self, profile_dir):
        self.path = Path(profile_dir) / 'addon_data' / 'plugin.video.tvstreaming.homepersonalisation' / 'continue_watching.sqlite3'

    def connect(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(str(self.path), timeout=5)
        db.execute('CREATE TABLE IF NOT EXISTS dismissed (identity TEXT PRIMARY KEY, label TEXT NOT NULL)')
        db.execute('CREATE TABLE IF NOT EXISTS activity (identity TEXT PRIMARY KEY, sequence INTEGER NOT NULL)')
        db.execute('CREATE TABLE IF NOT EXISTS pending_viewing (id INTEGER PRIMARY KEY, report TEXT NOT NULL)')
        return db

    def read(self):
        with closing(self.connect()) as db:
            return {key: {'label': label} for key, label in db.execute('SELECT identity, label FROM dismissed')}

    def hide(self, key, label):
        validated = dismiss({}, key, label)
        with closing(self.connect()) as db, db:
            db.execute('INSERT OR REPLACE INTO dismissed VALUES (?, ?)', (key, validated[key]['label']))
            # Conservatively invalidate queued viewing on any newer manual dismissal.
            db.execute('DELETE FROM pending_viewing')

    def viewed(self, key, *, verified=False):
        if not verified:
            return
        dismiss({}, key, '')
        with closing(self.connect()) as db, db:
            db.execute('DELETE FROM dismissed WHERE identity = ?', (key,))

    def activity(self):
        with closing(self.connect()) as db:
            return dict(db.execute('SELECT identity, sequence FROM activity'))

    def record_viewing(self, key):
        dismiss({}, key, '')
        with closing(self.connect()) as db, db:
            db.execute('BEGIN IMMEDIATE')
            sequence = db.execute('SELECT COALESCE(MAX(sequence), 0)+1 FROM activity').fetchone()[0]
            db.execute('INSERT OR REPLACE INTO activity VALUES (?, ?)', (key, sequence))
            db.execute('DELETE FROM dismissed WHERE identity = ?', (key,))

    def journal(self, stage):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.with_name('cw-stage.txt').open('w', encoding='utf-8') as f:
            f.write(stage)
            f.flush()
            import os
            os.fsync(f.fileno())

    def queue(self, report):
        import json
        with closing(self.connect()) as db, db:
            db.execute('CREATE TABLE IF NOT EXISTS pending_viewing (id INTEGER PRIMARY KEY, report TEXT NOT NULL)')
            db.execute('INSERT INTO pending_viewing(report) VALUES (?)', (json.dumps(report),))

    def pending(self):
        import json
        with closing(self.connect()) as db:
            db.execute('CREATE TABLE IF NOT EXISTS pending_viewing (id INTEGER PRIMARY KEY, report TEXT NOT NULL)')
            return [(i,json.loads(r)) for i,r in db.execute('SELECT id, report FROM pending_viewing ORDER BY id')]

    def finish(self, i):
        with closing(self.connect()) as db, db:
            db.execute('DELETE FROM pending_viewing WHERE id = ?', (i,))

    def commit_pending(self, i, key):
        dismiss({}, key, '')
        with closing(self.connect()) as db, db:
            db.execute('BEGIN IMMEDIATE')
            if not db.execute('SELECT 1 FROM pending_viewing WHERE id=?', (i,)).fetchone():
                return False
            sequence = db.execute('SELECT COALESCE(MAX(sequence),0)+1 FROM activity').fetchone()[0]
            db.execute('INSERT OR REPLACE INTO activity VALUES (?,?)', (key,sequence))
            db.execute('DELETE FROM dismissed WHERE identity=?', (key,))
            db.execute('DELETE FROM pending_viewing WHERE id=?', (i,))
            return True
