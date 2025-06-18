from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Dict, Any, Optional
import logging

from app.db.models import Pet, Species, ActivityLevel, PhysiologicalStatus
from app.services.energy_calculate import EnergyCalculator

logger = logging.getLogger(__name__)

class PetService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_pet(self, pet_data: Dict[str, Any]) -> Dict[str, Any]:
        """创建宠物"""
        try:
            # 计算能量需求
            species = Species(pet_data["species"])
            activity_level = ActivityLevel(pet_data["activity_level"])
            physio_status = PhysiologicalStatus(pet_data["physiological_status"])
            
            energy_info = EnergyCalculator.calculate_daily_energy_requirement(
                weight_kg=pet_data["weight_kg"],
                species=species,
                age_months=pet_data["age_months"],
                activity_level=activity_level,
                physiological_status=physio_status,
                lactation_week=pet_data.get("lactation_week", 4),
                nursing_count=pet_data.get("nursing_count", 1)
            )
            
            # 创建宠物记录
            pet = Pet(
                name=pet_data["name"],
                species=pet_data["species"],
                breed=pet_data.get("breed"),
                age_months=pet_data["age_months"],
                weight_kg=pet_data["weight_kg"],
                activity_level=pet_data["activity_level"],
                physiological_status=physio_status,
                life_stage=energy_info["life_stage"],
                daily_calories_kcal=energy_info["daily_energy_kcal"],
                health_conditions=pet_data.get("health_conditions", []),
                allergies=pet_data.get("allergies", []),
                lactation_week=pet_data.get("lactation_week"),
                nursing_count=pet_data.get("nursing_count")
            )

            self.db.add(pet)
            await self.db.commit()
            await self.db.refresh(pet)
            
            return {
                "pet_id": pet.id,
                "daily_calories_kcal": pet.daily_calories_kcal,
                "life_stage": pet.life_stage.value
            }
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"创建宠物失败: {e}")
            raise

    async def get_pet(self, pet_id: int) -> Optional[Dict[str, Any]]:
        """获取宠物信息"""
        try:
            result = await self.db.execute(select(Pet).where(Pet.id == pet_id))
            pet = result.scalar_one_or_none()
            
            if not pet:
                return None
            
            return {
                "id": pet.id,
                "name": pet.name,
                "species": pet.species,
                "breed": pet.breed,
                "age_months": pet.age_months,
                "weight_kg": pet.weight_kg,
                "activity_level": pet.activity_level,
                "physiological_status": pet.physiological_status.value,
                "daily_calories_kcal": pet.daily_calories_kcal,
                "health_conditions": pet.health_conditions or [],
                "allergies": pet.allergies or []
            }
            
        except Exception as e:
            logger.error(f"获取宠物信息失败: {e}")
            raise

    async def update_pet(self, pet_id: int, update_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """更新宠物信息"""
        try:
            result = await self.db.execute(select(Pet).where(Pet.id == pet_id))
            pet = result.scalar_one_or_none()
            
            if not pet:
                return None
            
            # 更新字段
            for field, value in update_data.items():
                if hasattr(pet, field) and value is not None:
                    setattr(pet, field, value)
            
            await self.db.commit()
            await self.db.refresh(pet)
            
            return await self.get_pet(pet_id)
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"更新宠物信息失败: {e}")
            raise