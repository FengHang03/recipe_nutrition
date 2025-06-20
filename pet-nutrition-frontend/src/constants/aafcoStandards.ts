import { LifeStage } from '../types';

// 营养素ID常量定义 (对应后端NutrientID)
export const NutrientID = {
  ENERGY: 1008,
  PROTEIN: 1003,
  CALCIUM: 1087,
  PHOSPHORUS: 1091,
  FAT: 1004,
  CARBOHYDRATE: 1005,
  WATER: 1051,
  FIBER: 1079,
  IRON: 1089,
  ZINC: 1095,
  COPPER: 1098,
  MAGNESIUM: 1090,
  POTASSIUM: 1092,
  SODIUM: 1093,
  SELENIUM: 1103,
  VITAMIN_A: 1104,
  VITAMIN_D: 1110,
  VITAMIN_E: 1109,
  VITAMIN_B1: 1165,
  VITAMIN_B12: 1178,
  RIBOFLAVIN: 1166,
  OMEGA_6: 1316,
  OMEGA_3: 1404
} as const;

// AAFCO标准数据 (每 1000 kcal 代谢能) - 对应后端完整数据
export const AAFCO_STANDARDS = {
  [LifeStage.DOG_ADULT]: {
    [NutrientID.PROTEIN]: { min: 45.0, max: null, unit: 'G', nutrient_id: NutrientID.PROTEIN },
    [NutrientID.FAT]: { min: 13.8, max: null, unit: 'G', nutrient_id: NutrientID.FAT },
    [NutrientID.ENERGY]: { min: 2000, max: null, unit: 'KCAL', nutrient_id: NutrientID.ENERGY },
    [NutrientID.CALCIUM]: { min: 1.25 * 1000, max: 6.25 * 1000, unit: 'MG', nutrient_id: NutrientID.CALCIUM },
    [NutrientID.PHOSPHORUS]: { min: 1.0 * 1000, max: 4.0 * 1000, unit: 'MG', nutrient_id: NutrientID.PHOSPHORUS },
    [NutrientID.POTASSIUM]: { min: 1.5 * 1000, max: null, unit: 'MG', nutrient_id: NutrientID.POTASSIUM },
    [NutrientID.SODIUM]: { min: 0.2 * 1000, max: null, unit: 'MG', nutrient_id: NutrientID.SODIUM },
    [NutrientID.MAGNESIUM]: { min: 0.15 * 1000, max: null, unit: 'MG', nutrient_id: NutrientID.MAGNESIUM },
    [NutrientID.IRON]: { min: 10, max: null, unit: 'MG', nutrient_id: NutrientID.IRON },
    [NutrientID.ZINC]: { min: 20, max: null, unit: 'MG', nutrient_id: NutrientID.ZINC },
    [NutrientID.COPPER]: { min: 1.83, max: null, unit: 'MG', nutrient_id: NutrientID.COPPER },
    [NutrientID.SELENIUM]: { min: 0.08 * 1000, max: 0.5 * 1000, unit: 'UG', nutrient_id: NutrientID.SELENIUM },
    [NutrientID.VITAMIN_A]: { min: 1250, max: 62500, unit: 'IU', nutrient_id: NutrientID.VITAMIN_A },
    [NutrientID.VITAMIN_E]: { min: 12.5 * 0.6774, max: null, unit: 'MG', nutrient_id: NutrientID.VITAMIN_E },
    [NutrientID.VITAMIN_D]: { min: 125, max: 750, unit: 'IU', nutrient_id: NutrientID.VITAMIN_D },
    [NutrientID.VITAMIN_B1]: { min: 0.56, max: null, unit: 'MG', nutrient_id: NutrientID.VITAMIN_B1 },
    [NutrientID.VITAMIN_B12]: { min: 0.007 * 1000, max: null, unit: 'UG', nutrient_id: NutrientID.VITAMIN_B12 },
    [NutrientID.RIBOFLAVIN]: { min: 1.3, max: null, unit: 'MG', nutrient_id: NutrientID.RIBOFLAVIN },
    [NutrientID.OMEGA_6]: { min: 3.3, max: null, unit: 'G', nutrient_id: NutrientID.OMEGA_6 },
    [NutrientID.OMEGA_3]: { min: 0.2, max: null, unit: 'G', nutrient_id: NutrientID.OMEGA_3 }
  },
  [LifeStage.DOG_PUPPY]: {
    [NutrientID.PROTEIN]: { min: 30, max: null, unit: 'G', nutrient_id: NutrientID.PROTEIN },
    [NutrientID.FAT]: { min: 21.3, max: null, unit: 'G', nutrient_id: NutrientID.FAT },
    [NutrientID.CALCIUM]: { min: 3.0 * 1000, max: 6.25 * 1000, unit: 'MG', nutrient_id: NutrientID.CALCIUM },
    [NutrientID.PHOSPHORUS]: { min: 2.5 * 1000, max: 4.0 * 1000, unit: 'MG', nutrient_id: NutrientID.PHOSPHORUS },
    [NutrientID.POTASSIUM]: { min: 1.5 * 1000, max: null, unit: 'MG', nutrient_id: NutrientID.POTASSIUM },
    [NutrientID.SODIUM]: { min: 0.8 * 1000, max: null, unit: 'MG', nutrient_id: NutrientID.SODIUM },
    [NutrientID.MAGNESIUM]: { min: 0.14 * 1000, max: null, unit: 'MG', nutrient_id: NutrientID.MAGNESIUM },
    [NutrientID.IRON]: { min: 22, max: null, unit: 'MG', nutrient_id: NutrientID.IRON },
    [NutrientID.ZINC]: { min: 25, max: null, unit: 'MG', nutrient_id: NutrientID.ZINC },
    [NutrientID.COPPER]: { min: 3.1, max: null, unit: 'MG', nutrient_id: NutrientID.COPPER },
    [NutrientID.SELENIUM]: { min: 0.5 * 1000, max: null, unit: 'UG', nutrient_id: NutrientID.SELENIUM },
    [NutrientID.VITAMIN_A]: { min: 1250, max: 62500, unit: 'IU', nutrient_id: NutrientID.VITAMIN_A },
    [NutrientID.VITAMIN_D]: { min: 125, max: 750, unit: 'IU', nutrient_id: NutrientID.VITAMIN_D },
    [NutrientID.VITAMIN_E]: { min: 12.5, max: null, unit: 'MG', nutrient_id: NutrientID.VITAMIN_E },
    [NutrientID.VITAMIN_B1]: { min: 0.56, max: null, unit: 'MG', nutrient_id: NutrientID.VITAMIN_B1 },
    [NutrientID.VITAMIN_B12]: { min: 0.007 * 1000, max: null, unit: 'UG', nutrient_id: NutrientID.VITAMIN_B12 },
    [NutrientID.RIBOFLAVIN]: { min: 1.3, max: null, unit: 'MG', nutrient_id: NutrientID.RIBOFLAVIN },
    [NutrientID.OMEGA_6]: { min: 3.3, max: null, unit: 'G', nutrient_id: NutrientID.OMEGA_6 },
    [NutrientID.OMEGA_3]: { min: 0.2, max: null, unit: 'G', nutrient_id: NutrientID.OMEGA_3 }
  },
  [LifeStage.CAT_ADULT]: {
    [NutrientID.PROTEIN]: { min: 63.0, max: null, unit: 'G', nutrient_id: NutrientID.PROTEIN },
    [NutrientID.FAT]: { min: 22.5, max: null, unit: 'G', nutrient_id: NutrientID.FAT },
    [NutrientID.ENERGY]: { min: 2000, max: null, unit: 'KCAL', nutrient_id: NutrientID.ENERGY },
    [NutrientID.CALCIUM]: { min: 1.44 * 1000, max: 6.25 * 1000, unit: 'MG', nutrient_id: NutrientID.CALCIUM },
    [NutrientID.PHOSPHORUS]: { min: 1.25 * 1000, max: 4.0 * 1000, unit: 'MG', nutrient_id: NutrientID.PHOSPHORUS },
    [NutrientID.POTASSIUM]: { min: 1.67 * 1000, max: null, unit: 'MG', nutrient_id: NutrientID.POTASSIUM },
    [NutrientID.SODIUM]: { min: 0.21 * 1000, max: null, unit: 'MG', nutrient_id: NutrientID.SODIUM },
    [NutrientID.MAGNESIUM]: { min: 0.1 * 1000, max: null, unit: 'MG', nutrient_id: NutrientID.MAGNESIUM },
    [NutrientID.IRON]: { min: 20, max: null, unit: 'MG', nutrient_id: NutrientID.IRON },
    [NutrientID.ZINC]: { min: 18.75, max: null, unit: 'MG', nutrient_id: NutrientID.ZINC },
    [NutrientID.COPPER]: { min: 1.25, max: null, unit: 'MG', nutrient_id: NutrientID.COPPER },
    [NutrientID.SELENIUM]: { min: 0.067 * 1000, max: 0.5 * 1000, unit: 'UG', nutrient_id: NutrientID.SELENIUM },
    [NutrientID.VITAMIN_A]: { min: 2083, max: 333333, unit: 'IU', nutrient_id: NutrientID.VITAMIN_A },
    [NutrientID.VITAMIN_E]: { min: 9.58, max: null, unit: 'MG', nutrient_id: NutrientID.VITAMIN_E },
    [NutrientID.VITAMIN_D]: { min: 62.5, max: 1667, unit: 'IU', nutrient_id: NutrientID.VITAMIN_D },
    [NutrientID.VITAMIN_B1]: { min: 1.4, max: null, unit: 'MG', nutrient_id: NutrientID.VITAMIN_B1 },
    [NutrientID.VITAMIN_B12]: { min: 0.0056 * 1000, max: null, unit: 'UG', nutrient_id: NutrientID.VITAMIN_B12 },
    [NutrientID.RIBOFLAVIN]: { min: 1.0, max: null, unit: 'MG', nutrient_id: NutrientID.RIBOFLAVIN },
    [NutrientID.OMEGA_6]: { min: 1.4, max: null, unit: 'G', nutrient_id: NutrientID.OMEGA_6 },
    [NutrientID.OMEGA_3]: { min: 0.06, max: null, unit: 'G', nutrient_id: NutrientID.OMEGA_3 }
  },
  [LifeStage.CAT_KITTEN]: {
    [NutrientID.PROTEIN]: { min: 75.0, max: null, unit: 'G', nutrient_id: NutrientID.PROTEIN },
    [NutrientID.FAT]: { min: 22.5, max: null, unit: 'G', nutrient_id: NutrientID.FAT },
    [NutrientID.CALCIUM]: { min: 2.4 * 1000, max: 6.25 * 1000, unit: 'MG', nutrient_id: NutrientID.CALCIUM },
    [NutrientID.PHOSPHORUS]: { min: 2.0 * 1000, max: 4.0 * 1000, unit: 'MG', nutrient_id: NutrientID.PHOSPHORUS },
    [NutrientID.POTASSIUM]: { min: 1.67 * 1000, max: null, unit: 'MG', nutrient_id: NutrientID.POTASSIUM },
    [NutrientID.SODIUM]: { min: 0.67 * 1000, max: null, unit: 'MG', nutrient_id: NutrientID.SODIUM },
    [NutrientID.MAGNESIUM]: { min: 0.1 * 1000, max: null, unit: 'MG', nutrient_id: NutrientID.MAGNESIUM },
    [NutrientID.IRON]: { min: 20, max: null, unit: 'MG', nutrient_id: NutrientID.IRON },
    [NutrientID.ZINC]: { min: 18.75, max: null, unit: 'MG', nutrient_id: NutrientID.ZINC },
    [NutrientID.COPPER]: { min: 1.67, max: null, unit: 'MG', nutrient_id: NutrientID.COPPER },
    [NutrientID.SELENIUM]: { min: 0.083 * 1000, max: null, unit: 'UG', nutrient_id: NutrientID.SELENIUM },
    [NutrientID.VITAMIN_A]: { min: 2083, max: 333333, unit: 'IU', nutrient_id: NutrientID.VITAMIN_A },
    [NutrientID.VITAMIN_E]: { min: 9.58, max: null, unit: 'MG', nutrient_id: NutrientID.VITAMIN_E },
    [NutrientID.VITAMIN_D]: { min: 62.5, max: 1667, unit: 'IU', nutrient_id: NutrientID.VITAMIN_D },
    [NutrientID.VITAMIN_B1]: { min: 1.4, max: null, unit: 'MG', nutrient_id: NutrientID.VITAMIN_B1 },
    [NutrientID.VITAMIN_B12]: { min: 0.0056 * 1000, max: null, unit: 'UG', nutrient_id: NutrientID.VITAMIN_B12 },
    [NutrientID.RIBOFLAVIN]: { min: 1.0, max: null, unit: 'MG', nutrient_id: NutrientID.RIBOFLAVIN },
    [NutrientID.OMEGA_6]: { min: 1.4, max: null, unit: 'G', nutrient_id: NutrientID.OMEGA_6 },
    [NutrientID.OMEGA_3]: { min: 0.06, max: null, unit: 'G', nutrient_id: NutrientID.OMEGA_3 }
  }
}; 