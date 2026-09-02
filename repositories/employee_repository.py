from abc import ABC, abstractmethod
import json
import os
from typing import List
from models.employee import Employee
from models.exceptions import CorruptDataError, StorageError


class EmployeeRepository(ABC):
    """Abstract base repository defining the persistence interface for Employee records."""

    @abstractmethod
    def load_all(self) -> List[Employee]:
        """Loads and returns all employees from persistent storage."""
        pass

    @abstractmethod
    def save_all(self, employees: List[Employee]) -> None:
        """Persists the provided list of employees to storage."""
        pass


class JSONEmployeeRepository(EmployeeRepository):
    """JSON file implementation of EmployeeRepository with strict error differentiation."""

    def __init__(self, file_path: str = "employees.json") -> None:
        self.file_path = file_path

    def load_all(self) -> List[Employee]:
        """Loads employees from a JSON file.

        - If the file does not exist, returns an empty list without error.
        - If the file exists but contains invalid JSON or non-list root, raises CorruptDataError.
        - If an I/O error occurs, raises StorageError.
        """
        if not os.path.exists(self.file_path):
            return []

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return []
                data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise CorruptDataError(
                f"Data file '{self.file_path}' contains malformed JSON: {exc.msg} (line {exc.lineno})"
            ) from exc
        except OSError as exc:
            raise StorageError(
                f"Failed to read data file '{self.file_path}': {exc.strerror or str(exc)}"
            ) from exc

        if not isinstance(data, list):
            raise CorruptDataError(
                f"Data file '{self.file_path}' must contain a JSON array of employee records, got {type(data).__name__}."
            )

        employees: List[Employee] = []
        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                raise CorruptDataError(
                    f"Record at index {idx} in '{self.file_path}' is not a valid JSON object."
                )
            employees.append(Employee.from_dict(item))

        return employees

    def save_all(self, employees: List[Employee]) -> None:
        """Saves all employees to the JSON file atomically using a temporary file.

        Raises:
            StorageError: If writing to the file fails due to an I/O error.
        """
        data = [emp.to_dict() for emp in employees]
        temp_path = f"{self.file_path}.tmp"

        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
                f.flush()
                os.fsync(f.fileno())

            # Atomic file replacement
            os.replace(temp_path, self.file_path)
        except OSError as exc:
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            raise StorageError(
                f"Failed to save data to '{self.file_path}': {exc.strerror or str(exc)}"
            ) from exc
