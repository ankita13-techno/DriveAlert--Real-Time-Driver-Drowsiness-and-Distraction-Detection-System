"""
DriveAlert — Local SQLite Offline Incident Logging System
"""

import sqlite3
import time
import os
from datetime import datetime


class IncidentLogger:
    """
    Manages local SQLite database (drivealert_logs.db) to record trip safety events.
    Thread-safe and persistent for post-trip telemetry analysis.
    """
    def __init__(self, db_path: str = "drivealert_logs.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS incident_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    duration_seconds REAL NOT NULL,
                    ear_value REAL NOT NULL,
                    mar_value REAL NOT NULL,
                    yaw_angle REAL NOT NULL,
                    pitch_angle REAL NOT NULL
                )
            """)
            conn.commit()

    def log_incident(self, event_type: str, duration_seconds: float, ear_val: float, mar_val: float, yaw: float, pitch: float):
        """
        Records a safety incident (MICRO_SLEEP, YAWN, DISTRACTION) into SQLite DB.
        """
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO incident_logs (timestamp, event_type, duration_seconds, ear_value, mar_value, yaw_angle, pitch_angle)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (now_str, event_type, round(duration_seconds, 2), round(ear_val, 3), round(mar_val, 3), round(yaw, 1), round(pitch, 1)))
            conn.commit()
        print(f"[IncidentLogger] Logged Event: {event_type} | Duration: {duration_seconds:.1f}s | EAR: {ear_val:.3f} | MAR: {mar_val:.3f} | Yaw: {yaw:.1f}°")
