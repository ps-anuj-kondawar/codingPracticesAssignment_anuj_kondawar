import unittest
import os
import sys

# Ensure project root is in the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.employee import Employee
from models.exceptions import CorruptDataError, StorageError
from repositories.employee_repository import JSONEmployeeRepository
from services.employee_service import EmployeeService


class FailingEmployeeRepository(JSONEmployeeRepository):
    """Test stub simulating persistent disk I/O failure on save."""

    def save_all(self, employees):
        raise StorageError("Disk write simulated failure.")


class TestEmployeeService(unittest.TestCase):
    """Unit tests for EmployeeService business logic and state consistency."""

    def setUp(self) -> None:
        """Sets up a clean test database file before each test."""
        self.db_path = "test_employees.json"
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        self.service = EmployeeService(self.db_path)

    def tearDown(self) -> None:
        """Cleans up the test database file after each test."""
        if os.path.exists(self.db_path):
            os.remove(self.db_path)

    def test_add_valid_employee(self) -> None:
        emp = Employee("EMP001", "John Doe", "john.doe@example.com", "Engineering", "Software Engineer", "2026-07-13")
        success, msg = self.service.add_employee(emp)
        self.assertTrue(success)
        self.assertEqual(len(self.service.get_all_employees()), 1)
        self.assertEqual(self.service.get_all_employees()[0].name, "John Doe")

    def test_add_duplicate_employee_id(self) -> None:
        emp1 = Employee("EMP001", "John Doe", "john.doe@example.com", "Engineering", "Software Engineer", "2026-07-13")
        self.service.add_employee(emp1)
        emp2 = Employee("EMP001", "Jane Doe", "jane.doe@example.com", "HR", "Recruiter", "2026-07-13")
        success, msg = self.service.add_employee(emp2)
        self.assertFalse(success)
        self.assertIn("already exists", msg)

    def test_add_invalid_email(self) -> None:
        emp = Employee("EMP001", "John Doe", "john.doe-invalid", "Engineering", "Software Engineer", "2026-07-13")
        success, msg = self.service.add_employee(emp)
        self.assertFalse(success)
        self.assertIn("Email is invalid", msg)

    def test_add_invalid_date(self) -> None:
        emp = Employee("EMP001", "John Doe", "john.doe@example.com", "Engineering", "Software Engineer", "13-07-2026")
        success, msg = self.service.add_employee(emp)
        self.assertFalse(success)
        self.assertIn("YYYY-MM-DD", msg)

    def test_search_by_id(self) -> None:
        emp = Employee("EMP001", "John Doe", "john.doe@example.com", "Engineering", "Software Engineer", "2026-07-13")
        self.service.add_employee(emp)
        found = self.service.search_by_id("EMP001")
        self.assertIsNotNone(found)
        self.assertEqual(found.name, "John Doe")
        found_lower = self.service.search_by_id("emp001")
        self.assertIsNotNone(found_lower)

    def test_update_employee(self) -> None:
        emp = Employee("EMP001", "John Doe", "john.doe@example.com", "Engineering", "Software Engineer", "2026-07-13")
        self.service.add_employee(emp)

        success, msg = self.service.update_employee("EMP001", name="Johnathan Doe", department="R&D")
        self.assertTrue(success)
        updated_emp = self.service.search_by_id("EMP001")
        self.assertIsNotNone(updated_emp)
        self.assertEqual(updated_emp.name, "Johnathan Doe")
        self.assertEqual(updated_emp.department, "R&D")
        self.assertEqual(updated_emp.email, "john.doe@example.com")

    def test_delete_employee(self) -> None:
        emp = Employee("EMP001", "John Doe", "john.doe@example.com", "Engineering", "Software Engineer", "2026-07-13")
        self.service.add_employee(emp)
        success, msg = self.service.delete_employee("EMP001")
        self.assertTrue(success)
        self.assertIsNone(self.service.search_by_id("EMP001"))

    def test_sorting_by_name(self) -> None:
        emp1 = Employee("EMP001", "Zachary Smith", "zach@example.com", "HR", "Recruiter", "2026-07-13")
        emp2 = Employee("EMP002", "Alice Johnson", "alice@example.com", "Engineering", "Developer", "2026-07-13")
        emp3 = Employee("EMP003", "Bob Miller", "bob@example.com", "Engineering", "Manager", "2026-07-13")

        self.service.add_employee(emp1)
        self.service.add_employee(emp2)
        self.service.add_employee(emp3)

        sorted_list = self.service.get_employees_sorted_by_name()
        self.assertEqual(sorted_list[0].name, "Alice Johnson")
        self.assertEqual(sorted_list[1].name, "Bob Miller")
        self.assertEqual(sorted_list[2].name, "Zachary Smith")

    def test_filtering_by_department(self) -> None:
        emp1 = Employee("EMP001", "Alice Johnson", "alice@example.com", "Engineering", "Developer", "2026-07-13")
        emp2 = Employee("EMP002", "Bob Miller", "bob@example.com", "Engineering", "Manager", "2026-07-13")
        emp3 = Employee("EMP003", "Zachary Smith", "zach@example.com", "HR", "Recruiter", "2026-07-13")

        self.service.add_employee(emp1)
        self.service.add_employee(emp2)
        self.service.add_employee(emp3)

        filtered = self.service.filter_employees_by_department("Engineering")
        self.assertEqual(len(filtered), 2)

        filtered_hr = self.service.filter_employees_by_department("hr")
        self.assertEqual(len(filtered_hr), 1)
        self.assertEqual(filtered_hr[0].name, "Zachary Smith")

    # --- Error Handling & Persistence Tests ---

    def test_missing_file_treated_as_empty_database(self) -> None:
        """Verifies that a missing database file starts with an empty list without error."""
        non_existent_file = "non_existent_database.json"
        if os.path.exists(non_existent_file):
            os.remove(non_existent_file)

        service = EmployeeService(non_existent_file)
        self.assertEqual(service.get_all_employees(), [])

    def test_corrupt_json_raises_corrupt_data_error(self) -> None:
        """Verifies that invalid JSON syntax raises CorruptDataError rather than treating as empty."""
        corrupt_file = "corrupt_data.json"
        with open(corrupt_file, "w", encoding="utf-8") as f:
            f.write("{ invalid json formatting")

        try:
            with self.assertRaises(CorruptDataError):
                EmployeeService(corrupt_file)
        finally:
            if os.path.exists(corrupt_file):
                os.remove(corrupt_file)

    def test_non_list_json_raises_corrupt_data_error(self) -> None:
        """Verifies that a valid JSON file that is not a list raises CorruptDataError."""
        invalid_type_file = "invalid_type.json"
        with open(invalid_type_file, "w", encoding="utf-8") as f:
            f.write('{"key": "value"}')

        try:
            with self.assertRaises(CorruptDataError):
                EmployeeService(invalid_type_file)
        finally:
            if os.path.exists(invalid_type_file):
                os.remove(invalid_type_file)

    # --- State Consistency & Rollback Tests ---

    def test_add_employee_rollback_on_io_failure(self) -> None:
        """Verifies that in-memory employee list is rolled back if saving fails."""
        failing_repo = FailingEmployeeRepository(self.db_path)
        service = EmployeeService(failing_repo)

        emp = Employee("EMP100", "State Tester", "tester@example.com", "QA", "Tester", "2026-07-13")
        success, msg = service.add_employee(emp)

        self.assertFalse(success)
        self.assertIn("Failed to save data", msg)
        self.assertEqual(len(service.get_all_employees()), 0)
        self.assertIsNone(service.search_by_id("EMP100"))

    def test_update_employee_rollback_on_io_failure(self) -> None:
        """Verifies that employee fields are rolled back to original state if saving fails."""
        emp = Employee("EMP200", "Original Name", "original@example.com", "Sales", "Rep", "2026-07-13")
        self.service.add_employee(emp)

        # Switch repository to failing repository
        self.service.repository = FailingEmployeeRepository(self.db_path)

        success, msg = self.service.update_employee("EMP200", name="New Name", department="Marketing")
        self.assertFalse(success)
        self.assertIn("Failed to save data", msg)

        # Verify in-memory state reverted
        stored_emp = self.service.search_by_id("EMP200")
        self.assertIsNotNone(stored_emp)
        self.assertEqual(stored_emp.name, "Original Name")
        self.assertEqual(stored_emp.department, "Sales")

    def test_delete_employee_rollback_on_io_failure(self) -> None:
        """Verifies that deleted employee is restored in-memory if saving fails."""
        emp = Employee("EMP300", "Delete Candidate", "delete@example.com", "Operations", "Lead", "2026-07-13")
        self.service.add_employee(emp)

        # Switch repository to failing repository
        self.service.repository = FailingEmployeeRepository(self.db_path)

        success, msg = self.service.delete_employee("EMP300")
        self.assertFalse(success)
        self.assertIn("Failed to save data", msg)

        # Verify employee is still present in memory
        self.assertEqual(len(self.service.get_all_employees()), 1)
        self.assertIsNotNone(self.service.search_by_id("EMP300"))


if __name__ == "__main__":
    unittest.main()
