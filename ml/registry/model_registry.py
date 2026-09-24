"""Lightweight JSON-backed Model Registry for OlistIQ Machine Learning artifacts."""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import joblib

from ml.config.ml_config import ml_config

logger = logging.getLogger("olistiq.ml.registry")


class ModelRegistry:
    """Manages model serialization, version tracking, metadata, and status lifecycle."""

    def __init__(
        self,
        artifacts_dir: Optional[Path] = None,
        metadata_file: Optional[Path] = None
    ):
        self.artifacts_dir = artifacts_dir or ml_config.ARTIFACTS_PATH
        self.metadata_file = metadata_file or ml_config.REGISTRY_METADATA_FILE
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self._init_registry()

    def _init_registry(self) -> None:
        """Initializes empty registry file if not present."""
        if not self.metadata_file.exists():
            with open(self.metadata_file, "w", encoding="utf-8") as f:
                json.dump({"models": {}, "last_updated": datetime.utcnow().isoformat()}, f, indent=2)

    def _read_registry(self) -> Dict[str, Any]:
        """Reads registry metadata."""
        if not self.metadata_file.exists():
            self._init_registry()
        try:
            with open(self.metadata_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error("Failed to read model registry: %s", str(e))
            return {"models": {}, "last_updated": datetime.utcnow().isoformat()}

    def _save_registry(self, data: Dict[str, Any]) -> None:
        """Atomically saves registry metadata."""
        data["last_updated"] = datetime.utcnow().isoformat()
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def register_model(
        self,
        model_name: str,
        version: str,
        model_object: Any,
        model_type: str,
        features: List[str],
        evaluation_metrics: Dict[str, Any],
        hyperparameters: Dict[str, Any],
        description: str,
        status: str = "active",
        extra_metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Saves model artifact and records metadata in registry."""
        filename = f"{model_name}_{version}.joblib"
        artifact_path = self.artifacts_dir / filename
        
        # Serialize model artifact
        joblib.dump(model_object, artifact_path)
        logger.info("Saved model artifact to %s", artifact_path)

        metadata_entry = {
            "model_name": model_name,
            "version": version,
            "model_type": model_type,
            "artifact_file": filename,
            "artifact_path": str(artifact_path),
            "status": status,
            "features": features,
            "evaluation_metrics": evaluation_metrics,
            "hyperparameters": hyperparameters,
            "description": description,
            "created_at": datetime.utcnow().isoformat(),
            "extra_metadata": extra_metadata or {}
        }

        registry_data = self._read_registry()
        if model_name not in registry_data["models"]:
            registry_data["models"][model_name] = {}
            
        registry_data["models"][model_name][version] = metadata_entry
        self._save_registry(registry_data)
        logger.info("Registered model '%s' version '%s' successfully.", model_name, version)
        return str(artifact_path)

    def get_model_metadata(self, model_name: str, version: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Fetches metadata for specific model version or latest active."""
        registry_data = self._read_registry()
        if model_name not in registry_data["models"]:
            return None
            
        versions = registry_data["models"][model_name]
        if version and version in versions:
            return versions[version]
            
        # Return latest registered active version
        for v in reversed(list(versions.keys())):
            if versions[v].get("status") == "active":
                return versions[v]
                
        return list(versions.values())[-1] if versions else None

    def load_model(self, model_name: str, version: Optional[str] = None) -> Any:
        """Loads serialized model artifact."""
        meta = self.get_model_metadata(model_name, version)
        if not meta:
            raise FileNotFoundError(f"Model '{model_name}' (version: {version}) not found in registry.")
            
        artifact_path = Path(meta["artifact_path"])
        if not artifact_path.exists():
            # Try relative to artifacts dir
            artifact_path = self.artifacts_dir / meta["artifact_file"]
            if not artifact_path.exists():
                raise FileNotFoundError(f"Model artifact file {artifact_path} does not exist.")
                
        return joblib.load(artifact_path)

    def list_models(self) -> List[Dict[str, Any]]:
        """Lists all registered models with their active metadata."""
        registry_data = self._read_registry()
        summary = []
        for model_name, versions in registry_data.get("models", {}).items():
            latest = self.get_model_metadata(model_name)
            if latest:
                summary.append(latest)
        return summary


# Global singleton instance
model_registry = ModelRegistry()
