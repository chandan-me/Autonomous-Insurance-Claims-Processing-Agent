"""
Defines the exact data structure used throughout the project. This file acts as the foundation of the application. It specifies what information must be extracted from every FNOL document and validates the extracted data before it moves to the routing engine.
"""

from typing import Optional, List
from pydantic import BaseModel, Field


class PolicyInfo(BaseModel):
    policy_number: Optional[str] = None
    policyholder_name: Optional[str] = None
    effective_dates: Optional[str] = None


class IncidentInfo(BaseModel):
    date: Optional[str] = None
    time: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None


class InvolvedParties(BaseModel):
    claimant: Optional[str] = None
    third_parties: Optional[str] = None
    contact_details: Optional[str] = None


class AssetDetails(BaseModel):
    asset_type: Optional[str] = None
    asset_id: Optional[str] = None
    estimated_damage: Optional[str] = None


class OtherFields(BaseModel):
    claim_type: Optional[str] = None
    attachments: Optional[str] = None
    initial_estimate: Optional[str] = None


class FNOLExtraction(BaseModel):
    """Top-level container matching the full field list from the spec."""
    policy_info: PolicyInfo = Field(default_factory=PolicyInfo)
    incident_info: IncidentInfo = Field(default_factory=IncidentInfo)
    involved_parties: InvolvedParties = Field(default_factory=InvolvedParties)
    asset_details: AssetDetails = Field(default_factory=AssetDetails)
    other_fields: OtherFields = Field(default_factory=OtherFields)

    def flatten(self) -> dict:
        """Flatten nested structure into a single dict for the final JSON output."""
        flat = {}
        for section in [self.policy_info, self.incident_info,
                         self.involved_parties, self.asset_details, self.other_fields]:
            flat.update(section.model_dump())
        return flat


#  used for missing-field detection.
# "Instead of writing these field names repeatedly in different files, I created one master list here."
MANDATORY_FIELDS = [
    "policy_number", "policyholder_name", "effective_dates",
    "date", "time", "location", "description",
    "claimant", "third_parties", "contact_details",
    "asset_type", "asset_id", "estimated_damage",
    "claim_type", "attachments", "initial_estimate",
]
