"""Dataset management for agent evaluation and testing."""

import json
from pathlib import Path
from typing import Any

import mlflow
import pandas as pd
from pydantic import BaseModel

from shared.logging_utils import get_logger

logger = get_logger(__name__)


class EvaluationDataset(BaseModel):
    """Model for evaluation dataset metadata."""

    name: str
    version: str
    description: str
    data_path: str
    schema_version: str = "1.0"
    total_samples: int = 0
    tags: dict[str, str] = {}


class DatasetManager:
    """Manage evaluation datasets for agents."""

    def __init__(self, base_path: str | Path = "data/evaluation"):
        """
        Initialize dataset manager.

        Args:
            base_path: Base directory for storing datasets
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def load_dataset(
        self, dataset_name: str, as_dataframe: bool = False
    ) -> list[dict[str, Any]] | pd.DataFrame:
        """
        Load a dataset from disk.

        Args:
            dataset_name: Name of the dataset file (without .json extension)
            as_dataframe: Return as pandas DataFrame instead of list

        Returns:
            Dataset as list of dicts or DataFrame
        """
        dataset_path = self.base_path / f"{dataset_name}.json"

        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found: {dataset_path}")

        with open(dataset_path, "r") as f:
            data = json.load(f)

        logger.info(f"Loaded dataset '{dataset_name}' with {len(data)} samples")

        if as_dataframe:
            return pd.DataFrame(data)

        return data

    def save_dataset(
        self,
        dataset: list[dict[str, Any]] | pd.DataFrame,
        dataset_name: str,
        description: str = "",
        version: str = "1.0",
        tags: dict[str, str] | None = None,
    ) -> Path:
        """
        Save a dataset to disk.

        Args:
            dataset: Dataset to save (list of dicts or DataFrame)
            dataset_name: Name for the dataset
            description: Description of the dataset
            version: Version string
            tags: Optional metadata tags

        Returns:
            Path to saved dataset
        """
        dataset_path = self.base_path / f"{dataset_name}.json"

        # Convert DataFrame to list of dicts
        if isinstance(dataset, pd.DataFrame):
            data = dataset.to_dict(orient="records")
        else:
            data = dataset

        # Save data
        with open(dataset_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

        # Save metadata
        metadata = EvaluationDataset(
            name=dataset_name,
            version=version,
            description=description,
            data_path=str(dataset_path),
            total_samples=len(data),
            tags=tags or {},
        )

        metadata_path = self.base_path / f"{dataset_name}_metadata.json"
        with open(metadata_path, "w") as f:
            f.write(metadata.model_dump_json(indent=2))

        logger.info(f"Saved dataset '{dataset_name}' with {len(data)} samples to {dataset_path}")
        return dataset_path

    def log_dataset_to_mlflow(
        self, dataset_name: str, context: str = "evaluation", targets: str | None = None
    ) -> mlflow.data.dataset.Dataset:
        """
        Log a dataset to MLFlow for tracking.

        Args:
            dataset_name: Name of the dataset to load and log
            context: Context for the dataset (training, evaluation, testing)
            targets: Column name for target values (for supervised learning)

        Returns:
            MLFlow Dataset object
        """
        # Load dataset as DataFrame
        df = self.load_dataset(dataset_name, as_dataframe=True)

        # Create MLFlow dataset
        mlflow_dataset = mlflow.data.from_pandas(df, name=dataset_name, targets=targets)

        # Log to current run
        mlflow.log_input(mlflow_dataset, context=context)

        logger.info(f"Logged dataset '{dataset_name}' to MLFlow with context '{context}'")
        return mlflow_dataset

    def get_dataset_info(self, dataset_name: str) -> EvaluationDataset:
        """
        Get metadata about a dataset.

        Args:
            dataset_name: Name of the dataset

        Returns:
            Dataset metadata
        """
        metadata_path = self.base_path / f"{dataset_name}_metadata.json"

        if not metadata_path.exists():
            # Try to reconstruct from data file
            dataset_path = self.base_path / f"{dataset_name}.json"
            if dataset_path.exists():
                with open(dataset_path, "r") as f:
                    data = json.load(f)
                return EvaluationDataset(
                    name=dataset_name,
                    version="unknown",
                    description="No metadata available",
                    data_path=str(dataset_path),
                    total_samples=len(data),
                )
            raise FileNotFoundError(f"Dataset metadata not found: {metadata_path}")

        with open(metadata_path, "r") as f:
            return EvaluationDataset.model_validate_json(f.read())

    def list_datasets(self) -> list[str]:
        """
        List all available datasets.

        Returns:
            List of dataset names
        """
        datasets = [
            p.stem for p in self.base_path.glob("*.json") if not p.stem.endswith("_metadata")
        ]
        return sorted(datasets)

    def split_dataset(
        self,
        dataset_name: str,
        train_ratio: float = 0.8,
        random_state: int = 42,
        save: bool = True,
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Split a dataset into train/test sets.

        Args:
            dataset_name: Name of the dataset to split
            train_ratio: Ratio of data for training (0-1)
            random_state: Random seed for reproducibility
            save: Whether to save the splits as new datasets

        Returns:
            Tuple of (train_df, test_df)
        """
        df = self.load_dataset(dataset_name, as_dataframe=True)

        # Shuffle and split
        df_shuffled = df.sample(frac=1, random_state=random_state).reset_index(drop=True)
        split_idx = int(len(df_shuffled) * train_ratio)

        train_df = df_shuffled[:split_idx]
        test_df = df_shuffled[split_idx:]

        if save:
            self.save_dataset(
                train_df,
                f"{dataset_name}_train",
                description=f"Training split of {dataset_name}",
                tags={"split": "train", "parent": dataset_name},
            )
            self.save_dataset(
                test_df,
                f"{dataset_name}_test",
                description=f"Test split of {dataset_name}",
                tags={"split": "test", "parent": dataset_name},
            )

        logger.info(
            f"Split dataset '{dataset_name}' into train ({len(train_df)}) and test ({len(test_df)})"
        )

        return train_df, test_df

    def validate_dataset_schema(
        self, dataset_name: str, required_fields: list[str]
    ) -> tuple[bool, list[str]]:
        """
        Validate that a dataset has required fields.

        Args:
            dataset_name: Name of the dataset
            required_fields: List of required field names

        Returns:
            Tuple of (is_valid, missing_fields)
        """
        data = self.load_dataset(dataset_name)

        if not data:
            return False, required_fields

        # Check first record for required fields
        first_record = data[0]
        missing_fields = [field for field in required_fields if field not in first_record]

        is_valid = len(missing_fields) == 0
        return is_valid, missing_fields


def get_dataset_manager(base_path: str | Path = "data/evaluation") -> DatasetManager:
    """Get a dataset manager instance."""
    return DatasetManager(base_path=base_path)
