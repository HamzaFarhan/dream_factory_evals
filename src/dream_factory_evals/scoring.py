from enum import Enum
from typing import Any

from loguru import logger


class Penalty(Enum):
    MISSING_DATA = 5
    INVALID_JOIN = 10
    HALLUCINATION = 15
    RBAC_VIOLATION = 25
    # Add others as needed


def calculate_core_score(
    accuracy: float,  # 0-100%
    response_time: float,  # seconds
    penalties: int,
) -> float:
    """Core scoring formula used across all levels"""
    time_score = min(1.0, (5 - response_time) / 5) * 100  # 5s baseline
    return (2 * accuracy + time_score) - penalties


def calculate_penalties(error_counts: dict[Penalty, int]) -> int:
    """Calculate total penalties from error counts"""
    return sum(ptype.value * count for ptype, count in error_counts.items())


def level_adjustments(level: int, response: dict[str, Any]) -> int:
    """Apply level-specific scoring adjustments"""
    match level:
        case 1:
            # Double penalty for missing required fields
            if response.get("missing_fields"):
                return Penalty.MISSING_DATA.value * 2
        case 2:
            # Extra penalty for join errors
            if "join_errors" in response:
                return Penalty.INVALID_JOIN.value * response["join_errors"]
        case 3:
            # 50% bonus for hallucinations
            if response.get("hallucinations"):
                return int(Penalty.HALLUCINATION.value * 1.5 * response["hallucinations"])
        case 4:
            # Double RBAC violations
            if response.get("rbac_violations"):
                return Penalty.RBAC_VIOLATION.value * 2 * response["rbac_violations"]
    return 0


def get_time_score(response_time: float, level: int) -> float:
    """Level-specific time scoring"""
    thresholds = {1: 3, 2: 5, 3: 7, 4: 10}
    threshold = thresholds.get(level, 5)
    return min(1.0, (threshold - response_time) / threshold) * 100


# Example usage:
if __name__ == "__main__":
    # Test Level 4 response
    sample_response = {
        "accuracy": 85.0,
        "response_time": 8.2,
        "errors": {Penalty.HALLUCINATION: 1, Penalty.RBAC_VIOLATION: 2},
    }

    penalties = calculate_penalties(sample_response["errors"])
    adjustments = level_adjustments(4, sample_response)
    time_score = get_time_score(sample_response["response_time"], 4)

    final_score = (2 * sample_response["accuracy"] + time_score) - (penalties + adjustments)

    logger.info(f"Calculated score: {final_score:.1f}")
