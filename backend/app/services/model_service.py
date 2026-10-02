import os
import joblib
from app.database.collections import get_collection
from app.ml.feature_engine import FeatureExtractor
from app.ml.inference import PredictionEngine
from app.utils.logger import logger

class ModelServiceClass:
    """
    Service responsible for finding the active deployed model version,
    loading its joblib pickles, and returning a cached PredictionEngine instance.
    """
    def __init__(self, models_dir: str = "models", default_version: str = "v1.0.0"):
        self.models_dir = models_dir
        self.default_version = default_version
        self._engine = None
        self._cached_version = None

    def get_active_model_info(self) -> dict:
        """
        Retrieves active model metadata from database.
        """
        try:
            meta_col = get_collection("model_metadata")
            record = meta_col.find_one({"deployed": True})
            if record:
                return record
        except Exception as e:
            logger.error(f"Error checking active model metadata in MongoDB: {str(e)}")
        return None

    def load_engine(self) -> PredictionEngine:
        """
        Loads and returns the active PredictionEngine. Caches the model instance.
        """
        info = self.get_active_model_info()
        version = info["model_version"] if info else self.default_version
        threshold = info["threshold"] if info else 0.65

        # Return cached instance if active version hasn't changed
        if self._engine is not None and self._cached_version == version:
            return self._engine

        # Try to resolve artifact_path
        path = None
        if info and "artifact_path" in info:
            meta_path = info["artifact_path"]
            # Clean trailing slash if present
            clean_meta_path = meta_path.rstrip("/\\")
            if os.path.exists(clean_meta_path):
                path = clean_meta_path
            else:
                # Try relative from current work directory
                cwd_path = os.path.join(os.getcwd(), clean_meta_path)
                if os.path.exists(cwd_path):
                    path = cwd_path

        if not path:
            path = os.path.join(self.models_dir, version)

        # Robust test fallback: if models directory is completely empty, try parent models
        if not os.path.exists(path):
            parent_models_path = os.path.join("..", self.models_dir, version)
            if os.path.exists(parent_models_path):
                path = parent_models_path

        logger.info(f"Loading active model version '{version}' from directory: {path}")

        extractor = FeatureExtractor()
        extractor.load(path)

        model_file = os.path.join(path, "xgboost_model.pkl")
        xgb_model = joblib.load(model_file)

        self._engine = PredictionEngine(xgb_model, extractor, threshold)
        self._cached_version = version
        logger.info(f"Successfully instantiated PredictionEngine for model version: {version}")
        return self._engine

# Singleton Instance
model_service = ModelServiceClass()
