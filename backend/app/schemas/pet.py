from pydantic import BaseModel, field_validator
from typing import Optional, List
from enum import Enum

class ActivityLevel(str, Enum):
    SEDENTARY_ACTIVE = "sedentary_active"
    LOW_ACTIVE = "low_active"
    MODERATE_ACTIVE = "moderate_active"
    HIGH_ACTIVE = "high_active"
    EXTREME_ACTIVE = "extreme_active"

class PhysiologicalStatus(str, Enum):
    INTACT = "intact"
    NEUTERED = "neutered"
    PREGNANT = "pregnant"
    LACTATING = "lactating"

class PetCreate(BaseModel):
    name: str
    species: str
    breed: Optional[str] = None
    age_months: int
    weight_kg: float
    activity_level: ActivityLevel
    physiological_status: PhysiologicalStatus
    health_conditions: Optional[List[str]] = []
    allergies: Optional[List[str]] = []
    lactation_week: Optional[int] = None
    nursing_count: Optional[int] = None

    @field_validator('species')
    def validate_species(cls, v):
        if v.lower() not in ['dog', 'cat']:
            raise ValueError('物种必须是 dog 或 cat')
        return v.lower()

    @field_validator('age_months')
    def validate_age(cls, v):
        if v <= 0 or v > 300:
            raise ValueError('年龄必须在 1-300 个月之间')
        return v

    @field_validator('weight_kg')
    def validate_weight(cls, v):
        if v <= 0 or v > 100:
            raise ValueError('体重必须在 0.1-100 kg之间')
        return v
    
class PetUpdate(BaseModel):
    name: Optional[str] = None
    breed: Optional[str] = None
    age_months: Optional[int] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[ActivityLevel] = None
    physiological_status: Optional[PhysiologicalStatus] = None
    health_conditions: Optional[List[str]] = None
    allergies: Optional[List[str]] = None

class PetResponse(BaseModel):
    id: int
    name: str
    species: str
    breed: Optional[str]
    age_months: int
    weight_kg: float
    activity_level: str
    physiological_status: str
    daily_calories_kcal: Optional[float]
    
    class Config:
        from_attributes = True