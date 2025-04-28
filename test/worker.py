import pytest
from worker import bin_magnitude

def test_bin_magnitude_valid():
    # Arrange
    magnitude = 4.5

    # Act
    bin_label = bin_magnitude(magnitude)

    # Assert
    assert bin_label == "4-4.9"

def test_bin_magnitude_none():
    # Arrange
    magnitude = None

    # Act
    bin_label = bin_magnitude(magnitude)

    # Assert
    assert bin_label == "unknown"

def test_bin_magnitude_invalid():
    # Arrange
    magnitude = "invalid"

    # Act
    bin_label = bin_magnitude(magnitude)

    # Assert
    assert bin_label == "invalid"

