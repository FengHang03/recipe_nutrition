from app.db.models import ActivityLevel, PhysiologicalStatus, Species, LifeStage, Pet

class EnergyCalculator:
    """宠物能量需求计算器"""
    
    @staticmethod
    def calculate_resting_energy_requirement(weight_kg: float) -> float:
        """计算静息能量需求 (RER)"""
        if weight_kg <= 0:
            raise ValueError("体重必须大于0")
        # RER = 70 × (体重kg)^0.75
        return 70 * (weight_kg ** 0.75)
    
    @staticmethod
    def get_activity_factor(age_months: int, activity_level: ActivityLevel) -> float:
        """获取活动系数"""
        base_factors = {
            ActivityLevel.SEDENTARY_ACTIVE: 1.4,
            ActivityLevel.LOW_ACTIVE: 1.6,
            ActivityLevel.MODERATE_ACTIVE: 1.8,
            ActivityLevel.HIGH_ACTIVE: 2.0,
            ActivityLevel.EXTREME_ACTIVE: 2.2
        }

        return base_factors[activity_level]
    
    @staticmethod
    def get_life_stage_factor(species: Species, age_months: int) -> tuple:
        """获取生命阶段系数和阶段名称"""
        
        if species == Species.DOG:
            if age_months <= 4:
                return 3.0, LifeStage.DOG_PUPPY  # 幼犬需要更多能量
            elif age_months <= 12:
                return 2.5, LifeStage.DOG_PUPPY  # 幼犬需要更多能量
            else:
                return 1.0, LifeStage.DOG_ADULT
        
        else:  # CAT
            if age_months <= 12:
                return 2.5, LifeStage.CAT_KITTEN  # 幼猫需要最多能量
            else:
                return 1.0, LifeStage.CAT_ADULT
    
    @classmethod
    def calculate_daily_energy_requirement(cls, 
                                         weight_kg: float,
                                         species: Species,
                                         age_months: int,
                                         activity_level: ActivityLevel,
                                         physiological_status: PhysiologicalStatus,
                                         lactation_week: int = 4,
                                         nursing_count: int = 1) -> dict:
        """计算每日能量需求"""
        try:
            # 输入验证
            if weight_kg <= 0:
                raise ValueError("体重必须大于0")
            if age_months < 0:
                raise ValueError("年龄不能为负数")
        
            # 1. 计算RER
            rer = cls.calculate_resting_energy_requirement(weight_kg)

            # 2. 获取生命阶段系数
            life_stage_factor, life_stage = cls.get_life_stage_factor(species, age_months)

            # 3. 计算基础DER
            der = life_stage_factor * rer

            # 4. 根据生理状态调整
            if physiological_status == PhysiologicalStatus.PREGNANT:
                # 怀孕期能量需求：1.8 × RER + 26 × 体重
                der = 139 * weight_kg ** 0.75 + 26 * weight_kg
            
            elif physiological_status == PhysiologicalStatus.LACTATING:
                # 哺乳期能量需求计算
                if lactation_week == 2:
                    lactation_factor = 0.95
                elif lactation_week == 3:
                    lactation_factor = 1.1
                elif lactation_week == 4:
                    lactation_factor = 1.2
                else:
                    lactation_factor = 0.75
                
                if nursing_count <= 4:
                    der = 145 * weight_kg ** 0.75 + weight_kg * (24 * nursing_count) * lactation_factor
                else:
                    der = 145 * weight_kg ** 0.75 + weight_kg * (96 + 12 * (nursing_count - 4)) * lactation_factor
            
            else:
                # 对于非特殊生理状态（正常、绝育），应用活动系数
                if age_months < 12:
                    activity_factor = 1.0
                else:
                    activity_factor = cls.get_activity_factor(age_months, activity_level)
                
                # 绝育或老年宠物需要较少能量
                if physiological_status == PhysiologicalStatus.NEUTERED or age_months > 84:
                    activity_factor = (activity_factor - 0.2) 
                    
                der = der * activity_factor
        
        except Exception as e:
            raise e
        
        return {
            "resting_energy_kcal": round(rer, 1),
            "daily_energy_kcal": round(der, 1),
            "life_stage": life_stage.value
        }
    
    