"""DBSCAN clustering of attacker behavior.

Why DBSCAN:
- Attack volumes are uneven; there is no reliable k for K-Means.
- Scanners form dense blobs; interactive sessions are sparser outliers.
- Outliers are labeled as noise (cluster -1), which is honest for novel behavior.

Labels are interpretations of feature averages, not attributions to named groups.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import SessionLocal
from app.models import Attacker, Event

logger = logging.getLogger(__name__)

CLUSTER_NAMES = {
    0: "Credential spraying / brute force",
    1: "Interactive shell exploration",
    2: "Automated scanner",
    3: "Downloader / staging",
    4: "Persistent repeat attacker",
    -1: "Unclustered / novel behavior",
}


def _features(attacker: Attacker) -> list[float]:
    span = max(1.0, (attacker.last_seen - attacker.first_seen).total_seconds() / 3600.0)
    return [
        float(attacker.login_attempts),
        float(attacker.session_count),
        float(attacker.command_count),
        float(attacker.download_count),
        float(attacker.event_count),
        float(attacker.event_count) / span,
        float(attacker.login_attempts) / max(1, attacker.session_count),
        float(attacker.command_count) / max(1, attacker.session_count),
    ]


def _interpret(mean: np.ndarray) -> str:
    logins, sessions, commands, downloads, events, rate, logins_per_session, cmds_per_session = mean
    if downloads >= 1 and commands >= 2:
        return CLUSTER_NAMES[3]
    if logins >= 15 and commands < 2:
        return CLUSTER_NAMES[0]
    if cmds_per_session >= 3:
        return CLUSTER_NAMES[1]
    if rate >= 20 and commands < 1:
        return CLUSTER_NAMES[2]
    if events >= 40:
        return CLUSTER_NAMES[4]
    return "Mixed / low-confidence behavior"


def train_and_apply() -> dict:
    settings = get_settings()
    db: Session = SessionLocal()
    try:
        attackers = db.scalars(select(Attacker)).all()
        if len(attackers) < settings.ml_min_attackers:
            return {"status": "skipped", "reason": "not_enough_attackers", "count": len(attackers)}

        matrix = np.array([_features(a) for a in attackers], dtype=float)
        scaled = StandardScaler().fit_transform(matrix)
        model = DBSCAN(eps=0.9, min_samples=3)
        labels = model.fit_predict(scaled)

        means: dict[int, list[np.ndarray]] = defaultdict(list)
        for row, label in zip(matrix, labels):
            means[int(label)].append(row)

        interpretations = {}
        for label, rows in means.items():
            avg = np.mean(np.vstack(rows), axis=0)
            interpretations[label] = CLUSTER_NAMES.get(label, _interpret(avg)) if label == -1 else _interpret(avg)

        for attacker, label in zip(attackers, labels):
            attacker.behavior_cluster = int(label)
            attacker.cluster_label = interpretations.get(int(label), CLUSTER_NAMES[-1])

        events = db.scalars(select(Event)).all()
        cluster_by_ip = {a.ip: a.behavior_cluster for a in attackers}
        for event in events:
            event.behavior_cluster = cluster_by_ip.get(event.source_ip)

        db.commit()
        summary = {
            "status": "ok",
            "algorithm": "DBSCAN",
            "attackers": len(attackers),
            "clusters": {str(k): interpretations[k] for k in interpretations},
            "counts": {str(k): int(sum(1 for x in labels if x == k)) for k in set(labels)},
            "trained_at": datetime.now(timezone.utc).isoformat(),
            "disclaimer": "Clusters describe similar observed behavior. They do not identify criminal groups.",
        }
        logger.info("ML clustering complete: %s", summary["counts"])
        return summary
    except Exception:
        db.rollback()
        logger.exception("ML clustering failed")
        return {"status": "error"}
    finally:
        db.close()
