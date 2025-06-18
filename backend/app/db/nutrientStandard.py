from dataclasses import dataclass
from enum import Enum
from typing import List
from app.db.models import LifeStage

@dataclass
class NutrientInfo:
    """营养素信息数据类"""
    id: int
    name: str
    amount: float
    unit: str

class NutrientID:
    """营养素ID常量定义"""
    ENERGY = 1008      # 能量 (kcal)
    PROTEIN = 1003     # 蛋白质 (g)
    CALCIUM = 1087     # 钙 (mg)
    PHOSPHORUS = 1091  # 磷 (mg)
    FAT = 1004         # 脂肪 (g)
    CARBOHYDRATE = 1005 # 碳水化合物 (g)
    WATER = 1051       # 水分 (g)
    FIBER = 1079       # 纤维 (g)
    IRON = 1089        # 铁 (mg)
    ZINC = 1095        # 锌 (mg)
    COPPER = 1098      # 铜 (mg)
    MAGNESIUM = 1090   # 镁 (mg)
    POTASSIUM = 1092   # 钾 (mg)
    SODIUM = 1093      # 钠 (mg)
    SELENIUM = 1103    # 硒 (μg)
    VITAMIN_A = 1104   # 维生素A (IU)
    VITAMIN_D = 1110   # 维生素D (IU)
    VITAMIN_E = 1109   # 维生素E (mg)
    VITAMIN_B1 = 1165  # 维生素B1 (mg)
    VITAMIN_B12 = 1178 # 维生素B12 (μg)
    RIBOFLAVIN = 1166  # 核黄素 (mg)
    OMEGA_6 = 1316     # ω-6脂肪酸 (g)
    OMEGA_3 = 1404     # ω-3脂肪酸 (g)

    @classmethod
    def get_all_ids(cls) -> List[int]:
        """获取所有营养素ID"""
        return [getattr(cls, attr) for attr in dir(cls) 
                if not attr.startswith('__') and not callable(getattr(cls, attr))]

    @classmethod
    def get_name(cls, nutrient_id: int) -> str:
        """根据ID获取营养素名称"""
        for attr in dir(cls):
            if not attr.startswith('__') and not callable(getattr(cls, attr)):
                if getattr(cls, attr) == nutrient_id:
                    return attr.lower().replace('_', ' ')
        return f"营养素 {nutrient_id}"

# AAFCO标准数据 (每 1000 kcal 代谢能)
AAFCO_STANDARDS = {
    LifeStage.DOG_ADULT: {
        NutrientID.PROTEIN: {"min": 45.0, "max": None, 'unit': 'G', 'nutrient_id': NutrientID.PROTEIN},
        NutrientID.FAT: {"min": 13.8, "max": None, 'unit': 'G', 'nutrient_id': NutrientID.FAT},
        NutrientID.ENERGY: {"min": 2000, "max": None, 'unit': 'KCAL', 'nutrient_id': NutrientID.ENERGY},
        NutrientID.CALCIUM: {"min": 1.25*1000, "max": 6.25*1000, 'unit': 'MG', 'nutrient_id': NutrientID.CALCIUM},
        NutrientID.PHOSPHORUS: {"min": 1.0*1000, "max": 4.0*1000, 'unit': 'MG', 'nutrient_id': NutrientID.PHOSPHORUS},
        NutrientID.POTASSIUM: {"min": 1.5*1000, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.POTASSIUM},
        NutrientID.SODIUM: {"min": 0.2*1000, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.SODIUM},
        NutrientID.MAGNESIUM: {"min": 0.15*1000, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.MAGNESIUM},
        NutrientID.IRON: {"min": 10, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.IRON},
        NutrientID.ZINC: {"min": 20, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.ZINC},
        NutrientID.COPPER: {"min": 1.83, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.COPPER},
        NutrientID.SELENIUM: {"min": 0.08*1000, "max": 0.5*1000, 'unit': 'UG', 'nutrient_id': NutrientID.SELENIUM},
        NutrientID.VITAMIN_A: {"min": 1250, "max": 62500, 'unit': 'IU', 'nutrient_id': NutrientID.VITAMIN_A},
        NutrientID.VITAMIN_E: {"min": 12.5 * 0.6774, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.VITAMIN_E}, # 转换系数: 1IU = 0.6774 mg
        NutrientID.VITAMIN_D: {"min": 125, "max": 750, 'unit': 'IU', 'nutrient_id': NutrientID.VITAMIN_D},
        NutrientID.VITAMIN_B1: {"min": 0.56, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.VITAMIN_B1},
        NutrientID.VITAMIN_B12: {"min": 0.007*1000, "max": None, 'unit': 'UG', 'nutrient_id': NutrientID.VITAMIN_B12},
        NutrientID.RIBOFLAVIN: {"min": 1.3, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.RIBOFLAVIN},
        NutrientID.OMEGA_6: {"min": 3.3, "max": None, 'unit': 'G', 'nutrient_id': NutrientID.OMEGA_6}, # LA
        NutrientID.OMEGA_3: {"min": 0.2, "max": None, 'unit': 'G', 'nutrient_id': NutrientID.OMEGA_3}  # ALA
    },
    LifeStage.DOG_PUPPY: {
        NutrientID.PROTEIN: {"min": 30, "max": None, 'unit': 'G', 'nutrient_id': NutrientID.PROTEIN},
        NutrientID.FAT: {"min": 21.3, "max": None, 'unit': 'G', 'nutrient_id': NutrientID.FAT},
        NutrientID.CALCIUM: {"min": 3.0*1000, "max": 6.25*1000, 'unit': 'MG', 'nutrient_id': NutrientID.CALCIUM},
        NutrientID.PHOSPHORUS: {"min": 2.5*1000, "max": 4.0*1000, 'unit': 'MG', 'nutrient_id': NutrientID.PHOSPHORUS},
        NutrientID.POTASSIUM: {"min": 1.5*1000, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.POTASSIUM},
        NutrientID.SODIUM: {"min": 0.8*1000, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.SODIUM},
        NutrientID.MAGNESIUM: {"min": 0.14*1000, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.MAGNESIUM},
        NutrientID.IRON: {"min": 22, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.IRON},
        NutrientID.ZINC: {"min": 25, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.ZINC},
        NutrientID.COPPER: {"min": 3.1, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.COPPER},
        NutrientID.SELENIUM: {"min": 0.5*1000, "max": None, 'unit': 'UG', 'nutrient_id': NutrientID.SELENIUM},
        NutrientID.VITAMIN_A: {"min": 1250, "max": 62500, 'unit': 'IU', 'nutrient_id': NutrientID.VITAMIN_A},
        NutrientID.VITAMIN_D: {"min": 125, "max": 750, 'unit': 'IU', 'nutrient_id': NutrientID.VITAMIN_D},
        NutrientID.VITAMIN_E: {"min": 12.5, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.VITAMIN_E},
        NutrientID.VITAMIN_B1: {"min": 0.56, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.VITAMIN_B1},
        NutrientID.VITAMIN_B12: {"min": 0.007*1000, "max": None, 'unit': 'UG', 'nutrient_id': NutrientID.VITAMIN_B12},
        NutrientID.RIBOFLAVIN: {"min": 1.3, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.RIBOFLAVIN},
        NutrientID.OMEGA_6: {"min": 3.3, "max": None, 'unit': 'G', 'nutrient_id': NutrientID.OMEGA_6},
        NutrientID.OMEGA_3: {"min": 0.2, "max": None, 'unit': 'G', 'nutrient_id': NutrientID.OMEGA_3}
    },
    LifeStage.CAT_ADULT: {
        NutrientID.PROTEIN: {"min": 63.0, "max": None, 'unit': 'G', 'nutrient_id': NutrientID.PROTEIN},
        NutrientID.FAT: {"min": 22.5, "max": None, 'unit': 'G', 'nutrient_id': NutrientID.FAT},
        NutrientID.ENERGY: {"min": 2000, "max": None, 'unit': 'KCAL', 'nutrient_id': NutrientID.ENERGY},
        NutrientID.CALCIUM: {"min": 1.44*1000, "max": 6.25*1000, 'unit': 'MG', 'nutrient_id': NutrientID.CALCIUM},
        NutrientID.PHOSPHORUS: {"min": 1.25*1000, "max": 4.0*1000, 'unit': 'MG', 'nutrient_id': NutrientID.PHOSPHORUS},
        NutrientID.POTASSIUM: {"min": 1.67*1000, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.POTASSIUM},
        NutrientID.SODIUM: {"min": 0.21*1000, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.SODIUM},
        NutrientID.MAGNESIUM: {"min": 0.1*1000, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.MAGNESIUM},
        NutrientID.IRON: {"min": 20, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.IRON},
        NutrientID.ZINC: {"min": 18.75, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.ZINC},
        NutrientID.COPPER: {"min": 1.25, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.COPPER},
        NutrientID.SELENIUM: {"min": 0.067*1000, "max": 0.5*1000, 'unit': 'UG', 'nutrient_id': NutrientID.SELENIUM},
        NutrientID.VITAMIN_A: {"min": 2083, "max": 333333, 'unit': 'IU', 'nutrient_id': NutrientID.VITAMIN_A},
        NutrientID.VITAMIN_E: {"min": 9.58, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.VITAMIN_E},
        NutrientID.VITAMIN_D: {"min": 62.5, "max": 1667, 'unit': 'IU', 'nutrient_id': NutrientID.VITAMIN_D},
        NutrientID.VITAMIN_B1: {"min": 1.4, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.VITAMIN_B1},
        NutrientID.VITAMIN_B12: {"min": 0.0056*1000, "max": None, 'unit': 'UG', 'nutrient_id': NutrientID.VITAMIN_B12},
        NutrientID.RIBOFLAVIN: {"min": 1.0, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.RIBOFLAVIN},
        NutrientID.OMEGA_6: {"min": 1.4, "max": None, 'unit': 'G', 'nutrient_id': NutrientID.OMEGA_6},
        NutrientID.OMEGA_3: {"min": 0.06, "max": None, 'unit': 'G', 'nutrient_id': NutrientID.OMEGA_3}
    },
    LifeStage.CAT_KITTEN: {
        NutrientID.PROTEIN: {"min": 75.0, "max": None, 'unit': 'G', 'nutrient_id': NutrientID.PROTEIN},
        NutrientID.FAT: {"min": 22.5, "max": None, 'unit': 'G', 'nutrient_id': NutrientID.FAT},
        NutrientID.CALCIUM: {"min": 2.4*1000, "max": 6.25*1000, 'unit': 'MG', 'nutrient_id': NutrientID.CALCIUM},
        NutrientID.PHOSPHORUS: {"min": 2.0*1000, "max": 4.0*1000, 'unit': 'MG', 'nutrient_id': NutrientID.PHOSPHORUS},
        NutrientID.POTASSIUM: {"min": 1.67*1000, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.POTASSIUM},
        NutrientID.SODIUM: {"min": 0.67*1000, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.SODIUM},
        NutrientID.MAGNESIUM: {"min": 0.1*1000, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.MAGNESIUM},
        NutrientID.IRON: {"min": 20, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.IRON},
        NutrientID.ZINC: {"min": 18.75, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.ZINC},
        NutrientID.COPPER: {"min": 1.67, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.COPPER},
        NutrientID.SELENIUM: {"min": 0.083*1000, "max": None, 'unit': 'UG', 'nutrient_id': NutrientID.SELENIUM},
        NutrientID.VITAMIN_A: {"min": 2083, "max": 333333, 'unit': 'IU', 'nutrient_id': NutrientID.VITAMIN_A},
        NutrientID.VITAMIN_E: {"min": 9.58, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.VITAMIN_E},
        NutrientID.VITAMIN_D: {"min": 62.5, "max": 1667, 'unit': 'IU', 'nutrient_id': NutrientID.VITAMIN_D},
        NutrientID.VITAMIN_B1: {"min": 1.4, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.VITAMIN_B1},
        NutrientID.VITAMIN_B12: {"min": 0.0056*1000, "max": None, 'unit': 'UG', 'nutrient_id': NutrientID.VITAMIN_B12},
        NutrientID.RIBOFLAVIN: {"min": 1.0, "max": None, 'unit': 'MG', 'nutrient_id': NutrientID.RIBOFLAVIN},
        NutrientID.OMEGA_6: {"min": 1.4, "max": None, 'unit': 'G', 'nutrient_id': NutrientID.OMEGA_6},
        NutrientID.OMEGA_3: {"min": 0.06, "max": None, 'unit': 'G', 'nutrient_id': NutrientID.OMEGA_3}
    }
}

# 食物分类约束配置
CATEGORY_CONSTRAINTS = {
    "protein": {"min_percent": 40, "max_percent": 70},      # 蛋白质类食物40-70%
    "carbohydrate": {"min_percent": 10, "max_percent": 30}, # 碳水化合物10-30%
    "vegetable": {"min_percent": 5, "max_percent": 20},     # 蔬菜5-20%
    "fruit": {"min_percent": 0, "max_percent": 10},         # 水果0-10%
    "fat": {"min_percent": 2, "max_percent": 8},            # 脂肪类2-8%
    "supplement": {"min_percent": 0, "max_percent": 5}     # 补充剂0-5%
}
 