// 宠物相关类型
export interface Pet {
    id?: number;
    name: string;
    species: 'dog' | 'cat';
    breed?: string;
    age_months: number;
    weight_kg: number;
    activity_level: ActivityLevel;
    physiological_status: PhysiologicalStatus;
    health_conditions?: string[];
    allergies?: string[];
    daily_calories_kcal?: number;
    lactation_week?: number;
    nursing_count?: number;
  }
  
  export enum ActivityLevel {
    SEDENTARY_ACTIVE = 'sedentary_active',
    LOW_ACTIVE = 'low_active',
    MODERATE_ACTIVE = 'moderate_active',
    HIGH_ACTIVE = 'high_active',
    EXTREME_ACTIVE = 'extreme_active'
  }
  
  export enum PhysiologicalStatus {
    INTACT = 'intact',
    NEUTERED = 'neutered',
    PREGNANT = 'pregnant',
    LACTATING = 'lactating'
  }
  
  export enum LifeStage {
    DOG_PUPPY = 'dog_puppy',
    DOG_ADULT = 'dog_adult',
    CAT_KITTEN = 'cat_kitten',
    CAT_ADULT = 'cat_adult'
  }
  
  // 食材相关类型
  export interface Ingredient {
    fdc_id: number;
    description: string;
    common_name?: string;
    category?: string;
    energy_kcal_100g?: number;
    protein_g_100g?: number;
    fat_g_100g?: number;
    carb_g_100g?: number;
    cost_per_100g: number;
    safe_for_dogs: boolean;
    safe_for_cats: boolean;
  }
  
  // 配方相关类型
  export interface RecipeItem {
    name: string;
    category: string;
    amount_g: number;
    percentage: number;
    cost: number;
    calories: number;
  }
  
  export interface Recipe {
    [fdc_id: string]: RecipeItem;
  }
  
  export interface NutritionAnalysis {
    total_calories_kcal: number;
    protein_g: number;
    fat_g: number;
    carbohydrate_g: number;
    fiber_g?: number;
    calcium_mg?: number;
    phosphorus_mg?: number;
    // 可能还有其他营养素
    [key: string]: number | undefined;
  }

  // 🔧 AAFCO 符合性分析
  export interface AAFCOAnalysis {
    compliant: boolean;
    violations?: {
      nutrient: string;
      required_min?: number;
      required_max?: number;
      actual: number;
      unit: string;
      status?: string;
    }[];
    score: number;
    recommendations?: string[];
  }

  interface AAFCOCompliance {
    compliant: boolean;
    violations?: Array<{
      nutrient: string;
      actual: number;
      unit: string;
      required_min?: number;
      required_max?: number;
    }>;
    recommendations?: string[];
  }
  
  // 🔧 效率指标
  export interface EfficiencyMetrics {
    caloric_density_kcal_per_g: number;
    cost_efficiency_cost_per_kcal: number;
    ingredient_count: number;
    weight_category: string;
  }

  interface CostAnalysis {
    total_cost: number;
    cost_per_day: number;
    cost_per_kg: number;
  }
  
  interface RecipeResultType {
    status: string;
    recipe: {
      pet_id: number;
      total_weight_g: number;
      target_calories: number;
      actual_calories: number;
      energy_accuracy: number;
      ingredients: Ingredient[];
    };
    analysis: {
      nutrition: NutritionAnalysis;
      aafco_compliance: AAFCOCompliance;
      cost_analysis?: CostAnalysis;
    };
  }

  export interface RecipeAnalysis {
    target_calories: number;
    actual_calories: number;
    energy_deviation: number;
    energy_accuracy: number;
    total_cost: number;
    cost_per_kcal: number;
    nutrition_compliance_score: number;
    nutrition_compliance: NutritionAnalysis;
    objective_value: number;
  }
  
  export interface RecipeResult {
    status: 'Success' | 'Failed' | 'Error';
    error?: string;

    recipe: {
      pet_id: number;
      total_weight_g: number;
      target_calories: number;
      actual_calories: number;
      energy_accuracy: number;
      ingredients: RecipeIngredient[];
    };

    analysis: {
      nutrition: NutritionAnalysis;
      efficiency: EfficiencyMetrics;
      aafco_compliance: AAFCOAnalysis;
      cost_analysis: {
        total_cost: number;
        cost_per_kg: number;
      };
      weight_analysis?: WeightAnalysis;  // 添加重量分析
      optimization_strategy?: OptimizationStrategy;  // 优化策略
      user_guidance?: UserGuidance;  // 用户指导
    };
}
  
  // 表单数据类型
  export interface PetFormData {
    name: string;
    species: 'dog' | 'cat';
    breed: string;
    age_months: number;
    weight_kg: number;
    activity_level: ActivityLevel;
    physiological_status: PhysiologicalStatus;
    health_conditions: string[];
    allergies: string[];
    lactation_week?: number;
    nursing_count?: number;
  }
  
  export interface RecipeGenerationRequest {
    pet_id: number;
    target_calories?: number;
    preferred_weight_g?: number;
  }
  
  // 🔧 配方成分信息
  export interface RecipeIngredient {
    fdc_id: number;
    description: string;
    common_name?: string;
    amount_g: number;
    percentage: number;
    cost?: number;
    calories?: number;
    category?: string;
  }

  // API 响应类型
  export interface ApiResponse<T> {
    success: boolean;
    data?: T;
    message?: string;
    error?: string;
  }
  
  export interface CreatePetResponse {
    success: boolean;
    data: {
      pet_id: number;
      daily_calories_kcal: number;
      life_stage: string;
    };
    message: string;
    timestamp: string;
  }
  
  // 营养素信息
  export interface NutrientInfo {
    id: number;
    name: string;
    unit: string;
    importance: 'high' | 'medium' | 'low';
  }
  
  // 图表数据类型
  export interface ChartData {
    name: string;
    value: number;
    color?: string;
    percentage?: number;
  }
  
  export interface NutrientChartData {
    nutrient: string;
    actual: number;
    required: number;
    status: 'OK' | 'LOW' | 'HIGH';
    unit: string;
  }
  
  // 应用状态类型
  export interface AppState {
    // 宠物信息
    currentPet: Pet | null;
    
    // 配方生成
    isGenerating: boolean;
    currentRecipe: RecipeResult | null;
    
    // UI状态
    currentStep: number;
    errors: Record<string, string>;
  }

  // UI state types
  export type LoadingState = boolean;
  export type ErrorState = string | null;
  export type CurrentStep = 0 | 1 | 2;
  
  // 常量定义
  export const ACTIVITY_LEVEL_LABELS = {
    [ActivityLevel.SEDENTARY_ACTIVE]: 'Indoor/Sedentary',
    [ActivityLevel.LOW_ACTIVE]: 'Light Activity',
    [ActivityLevel.MODERATE_ACTIVE]: 'Moderate Activity',
    [ActivityLevel.HIGH_ACTIVE]: 'High Activity',
    [ActivityLevel.EXTREME_ACTIVE]: 'Extreme Activity'
  };
  
  export const PHYSIOLOGICAL_STATUS_LABELS = {
    [PhysiologicalStatus.INTACT]: 'Intact',
    [PhysiologicalStatus.NEUTERED]: 'Neutered',
    [PhysiologicalStatus.PREGNANT]: 'Pregnant',
    [PhysiologicalStatus.LACTATING]: 'Lactating'
  };
  
  export const DOG_BREEDS = [
    'Labrador', 'Golden Retriever', 'German Shepherd', 'Husky', 'Samoyed',
    'Border Collie', 'Poodle', 'Bichon Frise', 'Pomeranian', 'Corgi', 'Other'
  ];
  
  export const CAT_BREEDS = [
    'British Shorthair', 'American Shorthair', 'Scottish Fold', 'Persian', 'Siamese',
    'Ragdoll', 'Maine Coon', 'Russian Blue', 'Bengal', 'Other'
  ];

  // 🔧 重量分析接口
  export interface WeightAnalysis {
    optimization_mode: string;
    weight_category: string;
    weight_reasonable: boolean;
    suggested_adjustments?: string[];
    
    // 营养导向模式字段
    weight_preference_g?: number;
    adjustment_needed?: boolean;
    
    // 重量引导模式字段
    baseline_weight_g?: number;
    target_weight_g?: number;
    final_weight_g?: number;
    baseline_deviation_g?: number;
    final_deviation_g?: number;
    adjustment_success?: boolean;
    improvement_percent?: number;
    
    // 营养妥协评估
    nutrition_compromise?: {
      baseline_score: number;
      final_score: number;
      score_difference: number;
      acceptable: boolean;
    };
    recommendation?: string;
    fallback_reason?: string;
  }

  // 🔧 优化策略信息
  export interface OptimizationStrategy {
    optimization_strategy: string;
    primary_mode: string;
    weight_preference_provided: boolean;
    strategy_description: string;
  }

  // 🔧 用户指导信息
  export interface UserGuidance {
    weight_achievement: number;
    weight_achievement_category: string;
    next_steps: string[];
  }