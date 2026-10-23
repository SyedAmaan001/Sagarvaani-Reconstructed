"""
Sagarvani Reconstructed — Catalog Package
Exports ArtifactStore, CatalogService, and dataset registration functions.
"""

from backend.catalog.artifact_store import (
    ArtifactStore,
    ArtifactStoreError,
    InvalidPathError,
    PayloadTooLargeError,
)
from backend.catalog.dataset_registry import catalog_known_datasets
from backend.catalog.migrations import apply_migrations
from backend.catalog.service import CatalogService

__all__ = [
    "ArtifactStore",
    "ArtifactStoreError",
    "InvalidPathError",
    "PayloadTooLargeError",
    "apply_migrations",
    "CatalogService",
    "catalog_known_datasets",
]
