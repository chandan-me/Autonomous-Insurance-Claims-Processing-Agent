"""
Deterministic logic for:
  1. Detecting missing mandatory fields.
  2. Deciding the routing decision.

This is the decision-making engine of the application.
     where this validates whether required information is present, checks for fraud indicators, evaluates injury claims, compares the estimated damage against the business threshold, and finally returns both the recommended claim route and a clear explanation. By using deterministic rules instead of AI for routing, the application remains consistent, transparent, and production-ready
"""

import re
from schema import MANDATORY_FIELDS

DAMAGE_THRESHOLD = 25000
FRAUD_KEYWORDS = ["fraud", "inconsistent", "staged"]


def find_missing_fields(flat_fields: dict) -> list[str]:
    """Returns a list of mandatory field names that are empty, null, or blank."""
    missing = []
    for field in MANDATORY_FIELDS:
        value = flat_fields.get(field)
        if value is None or str(value).strip() == "":
            missing.append(field)
    return missing


def _parse_damage_amount(value: str | None) -> float | None:
    """
    Converts a damage value like '₹18,500' or '18500.00' into a float.
    Returns None if it can't be parsed -- callers must treat that as
    "unknown", not "zero", to avoid silently mis-routing a claim.
    """
    if not value:
        return None
    cleaned = re.sub(r"[^\d.]", "", value)  # strip currency symbols/commas
    try:
        return float(cleaned)
    except ValueError:
        return None


def _contains_fraud_keywords(description: str | None) -> list[str]:
    """Returns which fraud-related keywords were found in the description (case-insensitive)."""
    if not description:
        return []
    lowered = description.lower()
    return [kw for kw in FRAUD_KEYWORDS if kw in lowered]


def determine_route(flat_fields: dict, missing_fields: list[str]) -> tuple[str, str]:
    """
    Applies routing rules IN PRIORITY ORDER (first match wins).
    Returns (route_name, reason_string).

    Priority order and justification:
      1. Manual Review     -- can't trust any downstream decision if data is incomplete.
      2. Investigation Flag-- fraud risk outweighs speed/queue considerations.
      3. Specialist Queue  -- injury claims need specialist handling regardless of amount.
      4. Fast-track        -- only for clean, low-value, non-flagged claims.
      5. Standard Review   -- fallback bucket, nothing else applied.
    """

    # Rule 1: Manual Review -- any mandatory field missing
    if missing_fields:
        reason = (
            f"Routed to Manual Review because {len(missing_fields)} mandatory "
            f"field(s) are missing: {', '.join(missing_fields)}."
        )
        return "Manual Review", reason

    # Rule 2: Investigation Flag -- fraud-related keywords in description
    description = flat_fields.get("description")
    found_keywords = _contains_fraud_keywords(description)
    if found_keywords:
        reason = (
            f"Routed to Investigation Flag because the incident description "
            f"contains flagged keyword(s): {', '.join(found_keywords)}."
        )
        return "Investigation Flag", reason

    # Rule 3: Specialist Queue -- claim type is injury
    claim_type = (flat_fields.get("claim_type") or "").strip().lower()
    if claim_type == "injury":
        reason = "Routed to Specialist Queue because the claim type is 'injury'."
        return "Specialist Queue", reason

    # Rule 4: Fast-track -- estimated damage below threshold
    damage = _parse_damage_amount(flat_fields.get("estimated_damage"))
    if damage is not None and damage < DAMAGE_THRESHOLD:
        reason = (
            f"Routed to Fast-track because estimated damage (₹{damage:,.2f}) "
            f"is below the ₹{DAMAGE_THRESHOLD:,} threshold and no other flags were triggered."
        )
        return "Fast-track", reason

    # Rule 5: Fallback -- nothing else matched
    if damage is None:
        reason = "Routed to Standard Review because estimated damage could not be determined."
    else:
        reason = (
            f"Routed to Standard Review because estimated damage (₹{damage:,.2f}) "
            f"is at or above the ₹{DAMAGE_THRESHOLD:,} threshold and no other flags were triggered."
        )
    return "Standard Review", reason
