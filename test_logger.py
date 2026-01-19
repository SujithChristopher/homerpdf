"""Test script for operation logger functionality."""

import tempfile
from pathlib import Path
from utils.operation_logger import OperationLogger


def test_operation_logger():
    """Test the operation logger functionality."""
    # Create a temporary database for testing
    temp_dir = Path(tempfile.gettempdir()) / "test_homerpdf"
    temp_dir.mkdir(exist_ok=True)
    db_path = temp_dir / "test_operations.db"

    # Clean up any existing test database
    if db_path.exists():
        db_path.unlink()

    print("Testing Operation Logger...")
    print("-" * 50)

    # Initialize logger
    logger = OperationLogger(db_path)
    print(f"[OK] Database created at: {db_path}")

    # Test 1: First operation (not a duplicate)
    print("\nTest 1: First operation")
    duplicate = logger.check_duplicate(
        time_point="A0",
        center_code="CMC",
        hospital_number="12345",
        pdf_files=["arat.pdf", "nhpt.pdf"],
        operation_type="download",
        merge_flag=False,
    )
    print(f"  Duplicate check: {duplicate}")
    assert duplicate is None, "First operation should not be a duplicate"
    print("  [OK]Not a duplicate (as expected)")

    # Log the first operation
    record_id = logger.log_operation(
        time_point="A0",
        center_code="CMC",
        hospital_number="12345",
        pdf_files=["arat.pdf", "nhpt.pdf"],
        operation_type="download",
        merge_flag=False,
        is_duplicate=False,
        reprint_reason=None,
        output_path="C:\\Users\\Test\\Downloads",
    )
    print(f"  [OK]Logged operation with ID: {record_id}")

    # Test 2: Exact duplicate
    print("\nTest 2: Exact duplicate operation")
    duplicate = logger.check_duplicate(
        time_point="A0",
        center_code="CMC",
        hospital_number="12345",
        pdf_files=["arat.pdf", "nhpt.pdf"],
        operation_type="download",
        merge_flag=False,
    )
    print(f"  Duplicate check: {duplicate is not None}")
    assert duplicate is not None, "Second identical operation should be a duplicate"
    print(f"  [OK]Duplicate detected!")
    print(f"    Previous operation timestamp: {duplicate['timestamp']}")
    print(f"    Previous operation type: {duplicate['operation_type']}")

    # Log the duplicate with reason
    record_id = logger.log_operation(
        time_point="A0",
        center_code="CMC",
        hospital_number="12345",
        pdf_files=["arat.pdf", "nhpt.pdf"],
        operation_type="download",
        merge_flag=False,
        is_duplicate=True,
        reprint_reason="Testing duplicate detection functionality",
        output_path="C:\\Users\\Test\\Downloads",
    )
    print(f"  [OK]Logged duplicate operation with reason")

    # Test 3: Different time point (not a duplicate)
    print("\nTest 3: Different time point")
    duplicate = logger.check_duplicate(
        time_point="A1",  # Changed from A0
        center_code="CMC",
        hospital_number="12345",
        pdf_files=["arat.pdf", "nhpt.pdf"],
        operation_type="download",
        merge_flag=False,
    )
    print(f"  Duplicate check: {duplicate}")
    assert duplicate is None, "Different time point should not be a duplicate"
    print("  [OK]Not a duplicate (different time point)")

    # Test 4: Different PDFs (not a duplicate)
    print("\nTest 4: Different PDF selection")
    duplicate = logger.check_duplicate(
        time_point="A0",
        center_code="CMC",
        hospital_number="12345",
        pdf_files=["arat.pdf"],  # Only one PDF instead of two
        operation_type="download",
        merge_flag=False,
    )
    print(f"  Duplicate check: {duplicate}")
    assert duplicate is None, "Different PDFs should not be a duplicate"
    print("  [OK]Not a duplicate (different PDF selection)")

    # Test 5: Order-independent duplicate detection
    print("\nTest 5: Order-independent duplicate detection")
    # Log operation with PDFs in one order
    logger.log_operation(
        time_point="A2",
        center_code="MNP",
        hospital_number="TEST001",
        pdf_files=["arat.pdf", "nhpt.pdf", "wmft.pdf"],
        operation_type="print",
        merge_flag=True,
        is_duplicate=False,
        reprint_reason=None,
        output_path=None,
    )

    # Check with same PDFs in different order
    duplicate = logger.check_duplicate(
        time_point="A2",
        center_code="MNP",
        hospital_number="TEST001",
        pdf_files=["wmft.pdf", "nhpt.pdf", "arat.pdf"],  # Different order
        operation_type="print",
        merge_flag=True,
    )
    print(f"  Duplicate check: {duplicate is not None}")
    assert duplicate is not None, "Same PDFs in different order should be detected as duplicate"
    print("  [OK]Duplicate detected (order-independent)")

    # Test 6: Different merge flag (not a duplicate)
    print("\nTest 6: Different merge flag")
    duplicate = logger.check_duplicate(
        time_point="A0",
        center_code="CMC",
        hospital_number="12345",
        pdf_files=["arat.pdf", "nhpt.pdf"],
        operation_type="download",
        merge_flag=True,  # Changed from False
    )
    print(f"  Duplicate check: {duplicate}")
    assert duplicate is None, "Different merge flag should not be a duplicate"
    print("  [OK]Not a duplicate (different merge flag)")

    # Clean up
    logger.close()
    print("\n" + "=" * 50)
    print("All tests passed!")
    print("=" * 50)
    print(f"\nTest database location: {db_path}")
    print("You can inspect the database with: sqlite3 <path>")


if __name__ == "__main__":
    test_operation_logger()
