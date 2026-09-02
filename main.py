import sys
from models.exceptions import CorruptDataError, StorageError
from services.employee_service import EmployeeService
from ui.console_ui import EmployeeConsoleUI, COLOR_ERROR, COLOR_SUCCESS, COLOR_RESET


def main() -> None:
    """Main application entry point. Initializes services and starts the UI event loop."""
    try:
        service = EmployeeService("employees.json")
    except CorruptDataError as exc:
        print(f"\n{COLOR_ERROR}Data Integrity Error: {exc}{COLOR_RESET}")
        print("Please check or repair your 'employees.json' file before starting the application.\n")
        sys.exit(1)
    except StorageError as exc:
        print(f"\n{COLOR_ERROR}Storage Access Error: {exc}{COLOR_RESET}")
        sys.exit(1)

    ui = EmployeeConsoleUI(service)

    while True:
        ui.print_menu()
        choice = input("Enter your option (1-6): ").strip()

        if choice == "1":
            ui.add_employee_flow()
        elif choice == "2":
            ui.view_employees_flow()
        elif choice == "3":
            ui.search_employee_flow()
        elif choice == "4":
            ui.update_employee_flow()
        elif choice == "5":
            ui.delete_employee_flow()
        elif choice == "6":
            print(f"\n{COLOR_SUCCESS}Thank you for using the Employee Management System! Goodbye.{COLOR_RESET}\n")
            sys.exit(0)
        else:
            print(f"{COLOR_ERROR}Invalid selection. Please choose an option from 1 to 6.{COLOR_RESET}")


if __name__ == "__main__":
    main()
