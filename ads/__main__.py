from ads.core.manager import CoreManager

from ads.input.simulation import SimulationManager  # Test 1
from ads.input.csv import CSVManager  # Test 2


def main():
    user_input = input("Choose a test (1 or 2), based on work: ")
    if user_input == "1":
        core_manager = CoreManager(SimulationManager())
        core_manager.test_1()
    elif user_input == "2":
        core_manager = CoreManager(CSVManager())
        core_manager.test_2()
    else:
        print("Invalid input. Please enter 1 or 2.")
        exit(1)


if __name__ == "__main__":
    main()
