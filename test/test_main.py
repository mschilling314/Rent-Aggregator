import pytest
from main import main


def test_main():
    """
    Only tests to make sure main actually runs without errors, DOES NOT GUARANTEE DESIRED FUNCTIONALITY.
    """
    try:
        main()
    except Exception as e:
        pytest.fail(f"main() raised exception: {e}")