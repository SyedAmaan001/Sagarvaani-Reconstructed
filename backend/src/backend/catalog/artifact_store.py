"""
Sagarvani Reconstructed — Path-Safe, Bounded Raw Artifact Store
Stores raw response payloads under artifacts/runs/<run_id>/<task_id>.json.
Enforces:
- Path-traversal protection (sanitized run_id and filename).
- Maximum payload byte limit.
- Atomic file writes (via temporary file rename).
- SHA-256 payload checksumming.
"""

import hashlib
import json
import os
from pathlib import Path
import re
from typing import Any, Dict, Optional, Tuple

from backend.core.config import settings


class ArtifactStoreError(Exception):
    """Base exception for artifact store failures."""
    pass


class PayloadTooLargeError(ArtifactStoreError):
    """Raised when an artifact exceeds maximum byte limit."""
    pass


class InvalidPathError(ArtifactStoreError):
    """Raised when a path-traversal or invalid character pattern is detected."""
    pass


class ArtifactStore:
    """Manages run-scoped raw artifact files on the local filesystem."""

    SAFE_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_\-]+$")

    def __init__(self, base_dir: Optional[str] = None, max_bytes: Optional[int] = None):
        self.base_dir = Path(base_dir or settings.artifacts_dir).resolve()
        self.max_bytes = max_bytes or settings.max_artifact_bytes

    def _validate_safe_component(self, name: str, label: str) -> None:
        """Ensure name contains only alphanumeric characters, underscores, or dashes."""
        if not name or not self.SAFE_NAME_PATTERN.match(name):
            raise InvalidPathError(f"Invalid {label} '{name}': only alphanumeric, underscore, and dash are permitted.")

    def save_artifact(
        self,
        run_id: str,
        task_id: str,
        payload: Dict[str, Any],
    ) -> Tuple[str, str, int]:
        """
        Atomically saves payload as JSON under <base_dir>/runs/<run_id>/<task_id>.json.
        Returns:
            (relative_artifact_ref, sha256_checksum, byte_size)
        """
        self._validate_safe_component(run_id, "run_id")
        self._validate_safe_component(task_id, "task_id")

        run_dir = (self.base_dir / "runs" / run_id).resolve()
        # Verify no directory escape
        if not str(run_dir).startswith(str(self.base_dir)):
            raise InvalidPathError(f"Security error: path escape detected for run_id '{run_id}'")

        run_dir.mkdir(parents=True, exist_ok=True)

        json_bytes = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
        byte_size = len(json_bytes)

        if byte_size > self.max_bytes:
            raise PayloadTooLargeError(
                f"Artifact size ({byte_size} bytes) exceeds maximum limit of {self.max_bytes} bytes."
            )

        checksum = hashlib.sha256(json_bytes).hexdigest()
        target_path = run_dir / f"{task_id}.json"
        temp_path = run_dir / f".tmp_{task_id}_{os.getpid()}.json"

        # Atomic write via rename
        try:
            with open(temp_path, "wb") as f:
                f.write(json_bytes)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temp_path, target_path)
        except Exception as e:
            if temp_path.exists():
                try:
                    temp_path.unlink()
                except Exception:
                    pass
            raise ArtifactStoreError(f"Failed to write artifact '{target_path}': {str(e)}") from e

        relative_ref = f"artifacts/runs/{run_id}/{task_id}.json"
        return relative_ref, checksum, byte_size

    def read_artifact(self, run_id: str, task_id: str) -> Dict[str, Any]:
        """Reads and verifies an artifact from disk."""
        self._validate_safe_component(run_id, "run_id")
        self._validate_safe_component(task_id, "task_id")

        target_path = (self.base_dir / "runs" / run_id / f"{task_id}.json").resolve()
        if not target_path.exists():
            raise ArtifactStoreError(f"Artifact not found: '{target_path}'")

        with open(target_path, "rb") as f:
            data = f.read()

        return json.loads(data.decode("utf-8"))

    def compute_file_checksum(self, file_path: Path) -> Tuple[str, int]:
        """Computes SHA-256 and byte size for an existing file."""
        if not file_path.exists() or not file_path.is_file():
            raise ArtifactStoreError(f"File not found: '{file_path}'")

        sha = hashlib.sha256()
        total_bytes = 0
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                sha.update(chunk)
                total_bytes += len(chunk)

        return sha.hexdigest(), total_bytes
