from pydantic import BaseModel
from typing import Optional, Dict, Any, List

class RecipeGenerateRequest(BaseModel):
    """配方生成请求"""
    pet_id: int
    target_calories: Optional[float] = None
    preferred_weight_g: Optional[float] = None

class RecipeIngredient(BaseModel):
    """配方成分"""
    fdc_id: int
    description: str
    common_name: str
    amount_g: float
    percentage: float
    cost: float
    calories: float
    category: str

class RecipeData(BaseModel):
    """配方数据"""
    pet_id: int
    total_weight_g: float
    target_calories: float
    actual_calories: float
    energy_accuracy: float
    ingredients: List[RecipeIngredient]

class NutritionAnalysis(BaseModel):
    """营养分析 - 包含基础营养素和详细营养素分析"""
    total_calories_kcal: float
    protein_g: float
    fat_g: float
    carbohydrate_g: float
    fiber_g: Optional[float] = 0
    # 详细营养素分析（动态键值）
    class Config:
        extra = "allow"  # 允许额外字段

class EfficiencyMetrics(BaseModel):
    """效率指标"""
    caloric_density_kcal_per_g: float
    cost_efficiency_cost_per_kcal: float
    ingredient_count: int
    weight_category: str

class AAFCOCompliance(BaseModel):
    """AAFCO合规性分析"""
    compliant: bool
    violations: List[Dict[str, Any]]
    score: float

class CostAnalysis(BaseModel):
    """成本分析"""
    total_cost: float
    cost_per_kg: float

class WeightAnalysis(BaseModel):
    """重量分析"""
    optimization_mode: str
    weight_category: str
    weight_reasonable: bool
    suggested_adjustments: Optional[List[str]] = None
    
    # 营养导向模式字段
    weight_preference_g: Optional[float] = None
    adjustment_needed: Optional[bool] = None
    
    # 重量引导模式字段
    baseline_weight_g: Optional[float] = None
    target_weight_g: Optional[float] = None
    final_weight_g: Optional[float] = None
    baseline_deviation_g: Optional[float] = None
    final_deviation_g: Optional[float] = None
    adjustment_success: Optional[bool] = None
    improvement_percent: Optional[float] = None
    
    # 营养妥协评估
    nutrition_compromise: Optional[Dict[str, Any]] = None
    recommendation: Optional[str] = None
    fallback_reason: Optional[str] = None
    
    class Config:
        extra = "allow"  # 允许额外字段

class OptimizationStrategy(BaseModel):
    """优化策略信息"""
    optimization_strategy: str
    primary_mode: str
    weight_preference_provided: bool
    strategy_description: str

class UserGuidance(BaseModel):
    """用户指导信息"""
    weight_achievement: float
    weight_achievement_category: str
    next_steps: List[str]

class AnalysisData(BaseModel):
    """分析数据"""
    nutrition: NutritionAnalysis
    efficiency: EfficiencyMetrics
    aafco_compliance: AAFCOCompliance
    cost_analysis: CostAnalysis
    weight_analysis: Optional[WeightAnalysis] = None
    optimization_strategy: Optional[OptimizationStrategy] = None
    user_guidance: Optional[UserGuidance] = None

class RecipeResponse(BaseModel):
    """配方响应"""
    status: str
    recipe: Optional[RecipeData] = None
    analysis: Optional[AnalysisData] = None
    error: Optional[str] = None
