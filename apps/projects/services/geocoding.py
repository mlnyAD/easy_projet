

"""
Service de géocodage des projets.

Ce module transforme l'adresse métier d'un projet en coordonnées
géographiques à l'aide de Google Geocoding API.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from decimal import Decimal
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from django.conf import settings

from ..models import Project


GOOGLE_GEOCODING_URL = (
    "https://maps.googleapis.com/maps/api/geocode/json"
)


class ProjectGeocodingError(Exception):
    """
    Erreur rencontrée pendant le géocodage d'un projet.
    """


@dataclass(frozen=True)
class ProjectCoordinates:
    latitude: Decimal
    longitude: Decimal


class ProjectGeocodingService:
    """
    Géocodage de l'adresse d'un projet.
    """

    @staticmethod
    def build_address(project: Project) -> str:
        """
        Construit l'adresse complète utilisable pour le géocodage.
        """

        parts = [
            project.address_1,
            project.address_2,
            project.address_3,
            project.postal_code,
            project.city,
            project.country,
        ]

        return ", ".join(
            part.strip()
            for part in parts
            if part and part.strip()
        )

    @classmethod
    def geocode(
        cls,
        project: Project,
    ) -> ProjectCoordinates | None:
        """
        Retourne les coordonnées correspondant à l'adresse du projet.

        None est retourné lorsqu'aucune adresse n'est renseignée.
        """

        address = cls.build_address(project)

        if not address:
            return None

        api_key = settings.GOOGLE_MAPS_API_KEY

        if not api_key:
            raise ProjectGeocodingError(
                "La clé Google Maps n'est pas configurée."
            )

        query = urlencode(
            {
                "address": address,
                "key": api_key,
            }
        )

        url = f"{GOOGLE_GEOCODING_URL}?{query}"

        try:
            with urlopen(
                url,
                timeout=10,
            ) as response:
                payload = json.load(response)

        except (HTTPError, URLError, TimeoutError) as exc:
            raise ProjectGeocodingError(
                "Le service Google Geocoding est indisponible."
            ) from exc

        status = payload.get("status")

        if status == "ZERO_RESULTS":
            return None

        if status != "OK":
            error_message = payload.get(
                "error_message",
                status,
            )

            raise ProjectGeocodingError(
                f"Google Geocoding : {error_message}"
            )

        results = payload.get("results", [])

        if not results:
            return None

        location = (
            results[0]
            .get("geometry", {})
            .get("location", {})
        )

        latitude = location.get("lat")
        longitude = location.get("lng")

        if latitude is None or longitude is None:
            raise ProjectGeocodingError(
                "Google Geocoding n'a pas retourné "
                "de coordonnées."
            )

        return ProjectCoordinates(
            latitude=Decimal(str(latitude)),
            longitude=Decimal(str(longitude)),
        )

    @classmethod
    def geocode_and_save(
        cls,
        project: Project,
    ) -> ProjectCoordinates | None:
        """
        Géocode l'adresse du projet et enregistre
        les coordonnées obtenues.
        """

        coordinates = cls.geocode(project)

        if coordinates is None:
            project.latitude = None
            project.longitude = None
        else:
            project.latitude = coordinates.latitude
            project.longitude = coordinates.longitude

        project.save(
            update_fields=[
                "latitude",
                "longitude",
                "updated_at",
            ]
        )

        return coordinates