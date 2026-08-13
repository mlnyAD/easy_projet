

"""
Chargement de la configuration locale de développement.

Les variables déjà définies dans l'environnement système
restent prioritaires sur celles du fichier .env.local.
"""

from __future__ import annotations

import os
from pathlib import Path


def load_local_environment(base_dir: Path) -> None:
    """
    Charge les variables définies dans .env.local.

    Une variable déjà présente dans l'environnement n'est
    jamais remplacée.
    """

    env_file = base_dir / ".env.local"

    if not env_file.is_file():
        return

    with env_file.open(
        "r",
        encoding="utf-8",
    ) as file:
        for raw_line in file:
            line = raw_line.strip()

            if not line:
                continue

            if line.startswith("#"):
                continue

            if "=" not in line:
                continue

            name, value = line.split("=", 1)

            name = name.strip()
            value = value.strip()

            if not name:
                continue

            os.environ.setdefault(
                name,
                value,
            )