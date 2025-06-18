import { useMemo, useState, useEffect } from 'react';
import { LifeStage } from '../types';
import type { RecipeResult } from '../types';
import { petAPI } from '../services/api';

// AAFCO标准数据 - 移动到独立文件
import { AAFCO_STANDARDS, NutrientID } from '../constants/aafcoStandards';

// 颜色常量
const MACRO_COLORS = {
  protein: '#DC2626',
  fat: '#D97706', 
  carbs: '#059669'
};

const COLORS = ['#2563EB', '#DC2626', '#059669', '#D97706', '#7C3AED', '#DB2777', '#0891B2', '#EA580C'];

export const useRecipeData = (recipe: RecipeResult) => {
  const [petDetails, setPetDetails] = useState<any>(null);
  const [loadingPetDetails, setLoadingPetDetails] = useState(false);

  const { recipe: recipeData, analysis } = recipe;

  // 获取宠物详细信息
  useEffect(() => {
    const fetchPetDetails = async () => {
      if (recipeData.pet_id && !petDetails && !loadingPetDetails) {
        setLoadingPetDetails(true);
        try {
          // TODO: 启用当后端支持完整宠物信息API时
          console.log('🐕 Pet details fetch would happen here for pet ID:', recipeData.pet_id);
        } catch (error) {
          console.warn('获取宠物详细信息失败:', error);
        } finally {
          setLoadingPetDetails(false);
        }
      }
    };
    
    fetchPetDetails();
  }, [recipeData.pet_id, petDetails, loadingPetDetails]);

  // 宠物信息推断
  const petInfo = useMemo(() => {
    const optimization = analysis.optimization_strategy;
    const weightAnalysis = analysis.weight_analysis;
    const petId = recipeData.pet_id;
    
    if (petDetails) {
      return {
        pet_id: petId,
        species: petDetails.species || 'dog',
        life_stage: petDetails.life_stage || LifeStage.DOG_ADULT,
        name: petDetails.name || `Pet #${petId}`,
        age: petDetails.age_months ? (
          petDetails.age_months < 12 ? 'Puppy/Kitten' : 'Adult'
        ) : 'Adult',
        weight: petDetails.weight_kg ? 
          `${petDetails.weight_kg}kg` : 
          (weightAnalysis?.target_weight_g ? 
            `${(weightAnalysis.target_weight_g / 1000).toFixed(1)}kg` : 
            `${(recipeData.total_weight_g / 1000).toFixed(1)}kg (recipe)`)
      };
    }
    
    return {
      pet_id: petId,
      species: 'dog',
      life_stage: LifeStage.DOG_ADULT,
      name: `Pet #${petId}`,
      age: 'Adult',
      weight: weightAnalysis?.target_weight_g ? 
        `${(weightAnalysis.target_weight_g / 1000).toFixed(1)}kg` : 
        `${(recipeData.total_weight_g / 1000).toFixed(1)}kg (recipe)`
    };
  }, [analysis, recipeData, petDetails]);

  // 营养素密度计算
  const nutrientDensity = useMemo(() => {
    const factor = 1000 / recipeData.actual_calories;
    return {
      protein: analysis.nutrition.protein_g * factor,
      fat: analysis.nutrition.fat_g * factor,
      carbohydrate: analysis.nutrition.carbohydrate_g * factor,
      fiber: (analysis.nutrition.fiber_g || 0) * factor
    };
  }, [analysis.nutrition, recipeData.actual_calories]);

  // 宏量营养素数据
  const macroData = useMemo(() => {
    const { protein_g, fat_g, carbohydrate_g } = analysis.nutrition;
    const total = protein_g + fat_g + carbohydrate_g;
    
    return [
      {
        name: 'Protein',
        value: protein_g,
        percentage: ((protein_g / total) * 100).toFixed(1),
        color: MACRO_COLORS.protein,
        calories: protein_g * 4
      },
      {
        name: 'Fat',
        value: fat_g,
        percentage: ((fat_g / total) * 100).toFixed(1),
        color: MACRO_COLORS.fat,
        calories: fat_g * 9
      },
      {
        name: 'Carbohydrate',
        value: carbohydrate_g,
        percentage: ((carbohydrate_g / total) * 100).toFixed(1),
        color: MACRO_COLORS.carbs,
        calories: carbohydrate_g * 4
      }
    ];
  }, [analysis.nutrition]);

  // 食材分布数据
  const ingredientData = useMemo(() => {
    return recipeData.ingredients.map((item, index) => ({
      name: item.description.length > 12 ? item.description.substring(0, 12) + '...' : item.description,
      value: item.amount_g,
      percentage: item.percentage,
      color: COLORS[index % COLORS.length]
    }));
  }, [recipeData.ingredients]);

  // AAFCO合规性数据
  const complianceData = useMemo(() => {
    const currentStandards = AAFCO_STANDARDS[petInfo.life_stage as keyof typeof AAFCO_STANDARDS];
    const complianceArray: any[] = [];
    
    const mainNutrients = [
      {
        id: NutrientID.PROTEIN,
        name: 'Protein',
        actual: nutrientDensity.protein,
      },
      {
        id: NutrientID.FAT,
        name: 'Fat', 
        actual: nutrientDensity.fat,
      },
      {
        id: NutrientID.CALCIUM,
        name: 'Calcium',
        actual: 1250, // 模拟值
      },
      {
        id: NutrientID.PHOSPHORUS,
        name: 'Phosphorus',
        actual: 1200, // 模拟值
      },
      {
        id: NutrientID.IRON,
        name: 'Iron',
        actual: 12, // 模拟值
      }
    ];
    
    mainNutrients.forEach(nutrient => {
      const standard = currentStandards[nutrient.id];
      if (!standard) return;
      
      let status = 'ADEQUATE';
      if (standard.min && nutrient.actual < standard.min) {
        status = 'DEFICIENT';
      } else if (standard.max && nutrient.actual > standard.max) {
        status = 'EXCESSIVE';
      }
      
      complianceArray.push({
        nutrient: nutrient.name,
        actual: nutrient.actual,
        required_min: standard.min,
        required_max: standard.max,
        unit: standard.unit,
        status: status
      });
    });
    
    return complianceArray;
  }, [nutrientDensity, petInfo.life_stage]);

  // 雷达图数据
  const radarData = useMemo(() => {
    return complianceData.map(item => ({
      nutrient: item.nutrient,
      value: item.required_min ? Math.min((item.actual / item.required_min * 100), 150) : 100,
      fullMark: 150,
      status: item.status
    }));
  }, [complianceData]);

  return {
    petInfo,
    nutrientDensity,
    macroData,
    ingredientData,
    complianceData,
    radarData,
    loadingPetDetails,
    MACRO_COLORS,
    COLORS
  };
}; 