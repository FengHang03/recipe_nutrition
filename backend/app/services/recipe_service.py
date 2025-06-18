import logging
from typing import List, Dict, Any, Optional, Union
from enum import Enum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from contextlib import asynccontextmanager
import asyncio
from functools import lru_cache
import traceback
from sqlalchemy.orm import selectinload

from dataclasses import dataclass
from app.db.models import Pet, Ingredient, IngredientNutrient, Nutrient
from app.db.nutrientStandard import AAFCO_STANDARDS, LifeStage, CATEGORY_CONSTRAINTS, NutrientID

from pulp import LpProblem, LpMinimize, LpVariable, LpStatus, PULP_CBC_CMD, lpSum, value

logger = logging.getLogger(__name__)

@dataclass
class OptimizationConfig:
    """优化配置类 - 管理优化过程中的各种权重和约束参数"""
    
    # 目标函数权重
    nutrient_deficiency_weight: float = 1000.0     # 营养素缺乏惩罚权重
    nutrient_excess_weight: float = 100.0          # 营养素过量惩罚权重

    # 重量引导权重（辅助）
    weight_preference_weight: float = 2.0

    cost_weight: float = 1.0                       # 成本权重
    diversity_weight: float = 10.0                 # 食材多样性权重
    
    # 能量约束容差
    energy_tolerance: float = 0.07                 # 能量偏差容差(10%)
    
    # 重量调整相关参数
    weight_adjustment_threshold: float = 0.3      # 重量偏差阈值（40%）
    
    # 食材多样性约束
    max_single_ingredient_percent: float = 35.0    # 单一食材最大占比(%)
    min_ingredient_count: int = 3                  # 最少食材种类
    min_ingredient_amount_g: float = 5.0           # 单一食材最小用量(g)
    
    # 合理性检查
    max_reasonable_weight_g: float = 2000.0        # 最大合理重量(g) - 仅用于检查
    min_reasonable_weight_g: float = 50.0          # 最小合理重量(g) - 仅用于检查
    
    def __post_init__(self):
        """验证配置参数"""
        if self.nutrient_deficiency_weight <= 0:
            raise ValueError("nutrient_deficiency_weight must be positive")
        if self.energy_tolerance <= 0 or self.energy_tolerance > 0.5:
            raise ValueError("energy_tolerance must be between 0 and 0.5")
        if not 0 < self.max_single_ingredient_percent <= 100:
            raise ValueError("max_single_ingredient_percent must be between 0 and 100")


class NutritionOptimizer:
    """营养配方优化器 - 基于线性规划"""
    
    def __init__(self, session: AsyncSession, config: Optional[OptimizationConfig] = None):
        self.session = session
        self.config = config or OptimizationConfig()
        self.problem: Optional[LpProblem] = None
        self.ingredient_vars: Dict[int, LpVariable] = {}
        self.binary_vars: Dict[int, LpVariable] = {}  # 用于表示是否使用某种食材
        self._food_cache: Dict[str, List[Ingredient]] = {}

    def _solve_optimization_problem(self) -> str:
        """在同步上下文中解决优化问题"""
        try:
            if not self.problem:
                raise ValueError("Optimization problem not initialized")
            
            logger.info("Solving optimization problem...")
            solver = PULP_CBC_CMD(msg=1, timeLimit=120)
            self.problem.solve(solver)

            status = LpStatus[self.problem.status]
            logger.info(f"Optimization problem solved with status: {status}")

            return status
        except Exception as e:
            logger.error(f"优化求解器错误: {e}")
            logger.error(f"detail of falut massages: {traceback.format_exc()}")
            return "Failed"
    
    async def optimize_recipe(self, 
                       pet: Pet,
                       target_calories: float,
                       preferred_weight_g: Optional[float] = None,
                       log_level: str = "INFO") -> Dict[str, Any]:
        """
        为宠物优化营养配方

        Args:
            pet: 宠物信息
            target_calories: 目标配方总热量(千卡)
            preferred_weight_g: 用户偏好重量(g)，可选
            log_level: 日志级别
            
        Returns:
            Dict[str, Any]: 优化结果，包含状态、配方和分析信息
        """
        try:
            # 输入验证
            if not isinstance(pet, Pet) or not hasattr(pet, "id") or pet.id is None:
                raise ValueError("Invalid pet object")
            
            if target_calories <= 0:
                raise ValueError(f"target_calories must be positive, but got {target_calories}")
            
            logger.info(f"Starting recipe optimization for pet {pet.id} with target calories {target_calories}")

            # 1. acquire available foods
            available_foods = await self._get_available_foods(pet)
            if not available_foods:
                return self._create_error_result("No suitable foods found for this pet species")

            # 2. verify the integrity of the available foods
            valid_foods = await self._validate_food_nutrition_data(available_foods)
            if not valid_foods:
                return self._create_error_result("No foods with complete nutrition data")
            
            logger.info(f"Found {len(valid_foods)} foods with complete nutrition data")

            # 3. acquire nutrient standard
            try:
                aafco_key = self._get_aafco_key(pet)
                standards = AAFCO_STANDARDS[aafco_key]
                logger.info(f"Using AAFCO {aafco_key} nutrient standards")
            except (KeyError, ValueError) as e:
                return self._create_error_result(f"could not get AAFCO standard {e}")
            
            # 4. 执行混合优化策略
            if preferred_weight_g:
                logger.info(f"Performing hybrid optimization with weight preference: {preferred_weight_g}")
                return await self._hybrid_optimization_with_weight_preference(
                    valid_foods, standards, target_calories, preferred_weight_g, pet
                )
            else:
                return await self._nutrition_focused_optimization(
                    valid_foods, standards, target_calories, pet
                )
        except Exception as e:
            error_msg = f"Hybrid optimization failed: {str(e)}"
            logger.error(error_msg)
            logger.error(f"Detailed error: {traceback.format_exc()}")
            return self._create_error_result(error_msg)
        
    async def _nutrition_focused_optimization(self, 
                                            foods: List[Ingredient], 
                                            standards: Dict[str, Any],
                                            target_calories: float,
                                            pet: Pet) -> Dict[str, Any]:
        """纯营养导向优化"""
        try:
            logger.info("Performing nutrition-focused optimization")
            
            # 创建优化问题
            self.problem = LpProblem("Nutrition_Focused_Optimization", LpMinimize)
            
            # 创建决策变量
            self._create_decision_variables(foods)
            
            # 硬约束：能量
            self._add_energy_constraints(foods, target_calories)
            
            # 目标函数：营养 + 成本 + 多样性
            objective_components = await self._create_nutrition_objective(foods, standards, target_calories)
            objective_components.extend([
                self._create_cost_objective(foods),
                self._create_diversity_objective(foods)
            ])
            
            # 多样性和分类约束
            self._add_diversity_constraints(foods)
            await self._add_category_constraints(foods)
            
            # 设置目标函数
            self.problem += sum(objective_components)
            
            # 求解
            status = await self._solve_problem()
            
            if status == "Optimal":
                result = await self._process_nutrition_results(foods, target_calories, standards)
                
                # 检查重量合理性
                if result["status"] == "Success":
                    weight = result["recipe"]["total_weight_g"]
                    result["analysis"]["weight_analysis"] = {
                        "optimization_mode": "nutrition_focused",
                        "weight_category": self._categorize_weight(weight, target_calories),
                        "weight_reasonable": self._is_weight_reasonable(weight, target_calories),
                        "suggested_adjustments": self._get_weight_suggestions(weight, target_calories)
                    }
                
                return result
            else:
                return self._create_error_result(f"Nutrition optimization failed: {status}")
                
        except Exception as e:
            logger.error(f"Nutrition-focused optimization error: {e}")
            return self._create_error_result(f"Optimization error: {e}")
        
    async def _hybrid_optimization_with_weight_preference(self,
                                                        foods: List[Ingredient],
                                                        standards: Dict[str, Any],
                                                        target_calories: float,
                                                        preferred_weight_g: float,
                                                        pet: Pet) -> Dict[str, Any]:
        """带重量偏好的混合优化"""
        try:
            # 首先进行纯营养优化，获得基准
            logger.info("Step 1: Getting nutrition-optimal baseline")
            baseline_result = await self._nutrition_focused_optimization(foods, standards, target_calories, pet)
            
            if baseline_result["status"] != "Success":
                return baseline_result
            
            baseline_weight = baseline_result["recipe"]["total_weight_g"]
            
            # 计算重量偏差
            weight_difference_ratio = abs(baseline_weight - preferred_weight_g) / baseline_weight
            
            logger.info(f"Baseline weight: {baseline_weight:.1f}g, Preferred: {preferred_weight_g:.1f}g, "
                       f"Difference: {weight_difference_ratio:.1%}")
            
            # 如果偏差在可接受范围内，使用营养最优解
            if weight_difference_ratio <= self.config.weight_adjustment_threshold:
                logger.info(f"Weight difference {weight_difference_ratio:.1%} is acceptable, using nutrition-optimal result")
                baseline_result["analysis"]["weight_analysis"]["optimization_mode"] = "nutrition_optimal_accepted"
                baseline_result["analysis"]["weight_analysis"]["weight_preference_g"] = preferred_weight_g
                baseline_result["analysis"]["weight_analysis"]["adjustment_needed"] = False
                return baseline_result
            
            # 如果偏差较大，进行重量引导优化
            logger.info(f"Step 2: Applying weight-guided optimization (difference: {weight_difference_ratio:.1%})")
            return await self._weight_guided_optimization(
                foods, standards, target_calories, preferred_weight_g, baseline_weight, baseline_result
            )
            
        except Exception as e:
            logger.error(f"Hybrid optimization error: {e}")
            return self._create_error_result(f"Hybrid optimization error: {e}")
        
    async def _weight_guided_optimization(self,
                                        foods: List[Ingredient],
                                        standards: Dict[str, Any],
                                        target_calories: float,
                                        target_weight_g: float,
                                        baseline_weight_g: float,
                                        baseline_result: Dict[str, Any]) -> Dict[str, Any]:
        """改进的重量引导优化"""
        try:
            # 1. 分类食材并确保各类食材的代表性
            categorized_foods = self._categorize_foods_for_balance(foods, target_calories, target_weight_g)
            
            if not self._validate_food_categories(categorized_foods):
                logger.warning("食材分类不完整，无法生成平衡配方")
                return self._add_failure_analysis(baseline_result, "缺乏必要的食材类别")
            
            # 2. 计算平衡的能量密度目标
            target_density = target_calories / target_weight_g
            
            # 3. 创建优化问题
            self.problem = LpProblem("Balanced_Weight_Guided_Optimization", LpMinimize)
            
            # 使用所有食材，而不是只选择高密度食材
            self._create_decision_variables(foods)
            
            # 4. 营养平衡硬约束
            await self._add_nutritional_balance_constraints(foods, target_weight_g)
            
            # 5. 重量约束（适度放宽）
            weight_tolerance = min(0.35, 200 / target_weight_g)  # 最大35%或200g容差
            min_weight = target_weight_g * (1 - weight_tolerance)
            max_weight = target_weight_g * (1 + weight_tolerance)
            
            total_weight = lpSum([self.ingredient_vars[food.fdc_id] for food in foods])
            self.problem += total_weight >= min_weight, "Min_Weight_Balanced"
            self.problem += total_weight <= max_weight, "Max_Weight_Balanced"
            
            logger.info(f"平衡重量约束: {min_weight:.1f}g - {max_weight:.1f}g")
            
            # 6. 能量约束
            total_energy = lpSum([
                self.ingredient_vars[food.fdc_id] * (food.energy_kcal_100g or 0) / 100
                for food in foods if food.energy_kcal_100g is not None
            ])
            
            energy_tolerance = 0.06  # 6%容差
            min_energy = target_calories * (1 - energy_tolerance)
            max_energy = target_calories * (1 + energy_tolerance)
            
            self.problem += total_energy >= min_energy, "Min_Energy_Balanced"
            self.problem += total_energy <= max_energy, "Max_Energy_Balanced"
            
            # 7. 创建平衡的目标函数
            objective_components = await self._create_balanced_objective(
                foods, standards, target_calories, target_weight_g, categorized_foods
            )
            
            # 8. 设置目标函数
            self.problem += sum(objective_components)
            
            # 9. 求解
            status = await self._solve_problem()
            
            if status == "Optimal":
                result = await self._process_nutrition_results(foods, target_calories, standards)
                
                if result["status"] == "Success":
                    # 添加营养平衡分析
                    await self._add_nutritional_balance_analysis(result, categorized_foods)
                    
                    # 添加重量调整分析
                    final_weight = result["recipe"]["total_weight_g"]
                    result["analysis"]["weight_analysis"] = self._create_balanced_success_analysis(
                        baseline_weight_g, target_weight_g, final_weight, baseline_result, result
                    )
                
                return result
            else:
                logger.warning(f"平衡优化失败: {status}")
                return self._add_failure_analysis(baseline_result, f"平衡优化求解失败: {status}")
                
        except Exception as e:
            logger.error(f"平衡优化错误: {e}")
            return self._add_failure_analysis(baseline_result, f"平衡优化错误: {e}")
        
    def _categorize_foods_for_balance(self, foods: List[Ingredient], 
                                    target_calories: float, 
                                    target_weight_g: float) -> Dict[str, List[Ingredient]]:
        """为平衡配方分类食材"""
        target_density = target_calories / target_weight_g
        
        categorized = {
            "high_density_protein": [],    # 高密度蛋白质(肉类、鱼类)
            "moderate_density_foods": [],  # 中等密度食材
            "low_density_vegetables": [],  # 低密度蔬菜(必需的)
            "healthy_fats": [],           # 健康脂肪
            "supplements": []             # 补充类食材(肝脏等)
        }
        
        for food in foods:
            if not food.energy_kcal_100g:
                continue
                
            density = food.energy_kcal_100g / 100
            category = getattr(food.category, 'name', 'other') if food.category else 'other'
            
            # 分类逻辑
            if category == "protein" and density >= 1.5:
                categorized["high_density_protein"].append(food)
            elif category in ["fat", "nuts"] or "seed" in food.description.lower():
                categorized["healthy_fats"].append(food)
            elif category in ["vegetable", "fruit"] or density < 0.8:
                categorized["low_density_vegetables"].append(food)
            elif "liver" in food.description.lower() or "organ" in food.description.lower():
                categorized["supplements"].append(food)
            else:
                categorized["moderate_density_foods"].append(food)
        
        # 按能量密度排序
        for cat_foods in categorized.values():
            cat_foods.sort(key=lambda f: f.energy_kcal_100g or 0, reverse=True)
        
        logger.info(f"食材分类: 高密度蛋白{len(categorized['high_density_protein'])}种, "
                   f"蔬菜{len(categorized['low_density_vegetables'])}种, "
                   f"健康脂肪{len(categorized['healthy_fats'])}种")
        
        return categorized
    
    def _validate_food_categories(self, categorized_foods: Dict[str, List[Ingredient]]) -> bool:
        """验证食材分类是否完整"""
        required_minimums = {
            "high_density_protein": 2,      # 至少2种高密度蛋白质
            "low_density_vegetables": 1,    # 至少1种蔬菜
            "healthy_fats": 1,             # 至少1种健康脂肪
        }
        
        for category, min_count in required_minimums.items():
            if len(categorized_foods[category]) < min_count:
                logger.error(f"分类 {category} 食材不足: {len(categorized_foods[category])} < {min_count}")
                return False
        
        return True
    
    async def _add_nutritional_balance_constraints(self, foods: List[Ingredient], target_weight_g: float):
        """添加营养平衡硬约束"""
        total_weight = lpSum([self.ingredient_vars[food.fdc_id] for food in foods])
        
        # 1. 分类总重量计算
        protein_foods = [f for f in foods if f.category and f.category.name == "protein"]
        vegetable_foods = [f for f in foods if f.category and f.category.name in ["vegetable", "fruit"]]
        fat_foods = [f for f in foods if f.category and f.category.name in ["fat", "nuts"] or "seed" in f.description.lower()]
        
        protein_weight = lpSum([self.ingredient_vars[f.fdc_id] for f in protein_foods])
        vegetable_weight = lpSum([self.ingredient_vars[f.fdc_id] for f in vegetable_foods])
        fat_weight = lpSum([self.ingredient_vars[f.fdc_id] for f in fat_foods])
        
        # 2. 营养平衡比例约束
        # 蛋白质类食材：40-70%
        self.problem += protein_weight >= 0.40 * total_weight, "Min_Protein_Foods_Ratio"
        self.problem += protein_weight <= 0.70 * total_weight, "Max_Protein_Foods_Ratio"
        
        # 蔬菜类食材：至少15%（确保纤维和维生素）
        if vegetable_foods:
            self.problem += vegetable_weight >= 0.15 * total_weight, "Min_Vegetable_Foods_Ratio"
            self.problem += vegetable_weight <= 0.40 * total_weight, "Max_Vegetable_Foods_Ratio"
        
        # 脂肪类食材：不超过25%（防止过量脂肪）
        if fat_foods:
            self.problem += fat_weight <= 0.25 * total_weight, "Max_Fat_Foods_Ratio"
        
        # 3. 纤维最低要求（通过蔬菜保证）
        if vegetable_foods:
            # 确保有足够的低密度蔬菜提供纤维
            low_density_vegetables = [f for f in vegetable_foods if f.energy_kcal_100g and f.energy_kcal_100g < 80]
            if low_density_vegetables:
                low_density_veg_weight = lpSum([self.ingredient_vars[f.fdc_id] for f in low_density_vegetables])
                min_fiber_providing_weight = max(20.0, target_weight_g * 0.08)  # 至少8%的重量来自低密度蔬菜
                self.problem += low_density_veg_weight >= min_fiber_providing_weight, "Min_Fiber_Foods"
        
        logger.info("添加营养平衡约束: 蛋白质40-70%, 蔬菜≥15%, 脂肪≤25%")

    async def _create_balanced_objective(self, foods: List[Ingredient], 
                                       standards: Dict[str, Any],
                                       target_calories: float,
                                       target_weight_g: float,
                                       categorized_foods: Dict[str, List[Ingredient]]) -> List[Any]:
        """创建平衡的目标函数"""
        objective_components = []
        
        # 1. 营养目标（权重适中）
        nutrition_objectives = await self._create_moderate_nutrition_objective(foods, standards, target_calories)
        objective_components.extend(nutrition_objectives)
        
        # 2. 重量精确度目标（高权重）
        total_weight = lpSum([self.ingredient_vars[food.fdc_id] for food in foods])
        weight_precision_var = LpVariable("weight_precision", lowBound=0)
        self.problem += weight_precision_var >= total_weight - target_weight_g
        self.problem += weight_precision_var >= target_weight_g - total_weight
        
        weight_precision_objective = 15.0 * weight_precision_var
        objective_components.append(weight_precision_objective)
        
        # 3. 营养平衡奖励目标
        balance_objective = self._create_nutritional_balance_objective(foods, categorized_foods)
        objective_components.append(balance_objective)
        
        # 4. 成本和多样性目标
        cost_objective = self._create_cost_objective(foods)
        diversity_objective = self._create_enhanced_diversity_objective(foods, categorized_foods)
        
        objective_components.extend([cost_objective, diversity_objective])
        
        return objective_components
    
    async def _create_moderate_nutrition_objective(self, foods: List[Ingredient], 
                                                 standards: Dict[str, Any], 
                                                 target_calories: float) -> List[Any]:
        """创建适中的营养目标函数"""
        objective_components = []
        
        # 中等营养约束权重
        moderate_deficiency_weight = self.config.nutrient_deficiency_weight * 0.5  # 降到50%
        moderate_excess_weight = self.config.nutrient_excess_weight * 0.7          # 降到70%
        
        # 关键营养素仍保持较高权重
        critical_nutrients = {1003, 1004, 1087, 1091, 1092}  # 蛋白质、脂肪、钙、磷、钾
        
        for nutrient_id, standard in standards.items():
            try:
                nutrient_amount = await self._get_nutrient_expression(foods, nutrient_id)
                
                if nutrient_amount is not None:
                    min_required = await self._calculate_nutrient_requirement(
                        standard, target_calories, nutrient_id, "min"
                    )
                    max_allowed = await self._calculate_nutrient_requirement(
                        standard, target_calories, nutrient_id, "max"
                    )
                    
                    importance_weight = self._get_nutrient_importance(nutrient_id)
                    
                    # 区分关键和非关键营养素
                    if nutrient_id in critical_nutrients:
                        deficiency_weight = moderate_deficiency_weight
                        excess_weight = moderate_excess_weight
                    else:
                        deficiency_weight = moderate_deficiency_weight * 0.6
                        excess_weight = moderate_excess_weight * 0.6
                    
                    # 处理缺乏
                    if min_required and min_required > 0:
                        deficiency_var = LpVariable(f"deficiency_{nutrient_id}", lowBound=0)
                        self.problem += (
                            nutrient_amount + deficiency_var >= min_required,
                            f"Min_{nutrient_id}"
                        )
                        
                        penalty = deficiency_weight * importance_weight * deficiency_var
                        objective_components.append(penalty)
                    
                    # 处理过量
                    if max_allowed and max_allowed > 0:
                        excess_var = LpVariable(f"excess_{nutrient_id}", lowBound=0)
                        self.problem += (
                            nutrient_amount - excess_var <= max_allowed,
                            f"Max_{nutrient_id}"
                        )
                        
                        penalty = excess_weight * importance_weight * excess_var
                        objective_components.append(penalty)
                
            except Exception as e:
                logger.error(f"Error processing moderate nutrient {nutrient_id}: {e}")
                continue
        
        return objective_components
    
    def _create_nutritional_balance_objective(self, foods: List[Ingredient], 
                                            categorized_foods: Dict[str, List[Ingredient]]) -> Any:
        """创建营养平衡奖励目标"""
        balance_components = []
        
        # 1. 食材类别多样性奖励
        for category, cat_foods in categorized_foods.items():
            if cat_foods:
                category_usage = lpSum([self.binary_vars[f.fdc_id] for f in cat_foods if f.fdc_id in self.binary_vars])
                # 奖励使用每个类别的食材
                balance_components.append(-5.0 * category_usage)  # 负数表示奖励
        
        # 2. 特殊营养平衡奖励
        # 鼓励使用蔬菜（纤维来源）
        vegetable_foods = categorized_foods.get("low_density_vegetables", [])
        if vegetable_foods:
            vegetable_usage = lpSum([
                self.ingredient_vars[f.fdc_id] for f in vegetable_foods 
                if f.fdc_id in self.ingredient_vars
            ])
            balance_components.append(-10.0 * vegetable_usage / 100)  # 每100g蔬菜奖励10分
        
        return lpSum(balance_components) if balance_components else 0

    def _create_enhanced_diversity_objective(self, foods: List[Ingredient], 
                                           categorized_foods: Dict[str, List[Ingredient]]) -> Any:
        """创建增强的多样性目标"""
        diversity_components = []
        
        # 1. 基础多样性
        basic_diversity = lpSum([
            (1 - self.binary_vars[food.fdc_id]) for food in foods
            if food.fdc_id in self.binary_vars
        ])
        diversity_components.append(self.config.diversity_weight * basic_diversity)
        
        # 2. 类别内多样性奖励
        for category, cat_foods in categorized_foods.items():
            if len(cat_foods) > 1:
                # 奖励在同一类别中使用多种食材
                category_diversity = lpSum([
                    self.binary_vars[f.fdc_id] for f in cat_foods
                    if f.fdc_id in self.binary_vars
                ])
                diversity_components.append(-3.0 * category_diversity)  # 奖励类别内多样性
        
        return lpSum(diversity_components)

    async def _add_nutritional_balance_analysis(self, result: Dict[str, Any], 
                                              categorized_foods: Dict[str, List[Ingredient]]):
        """添加营养平衡分析"""
        if "recipe" not in result or "ingredients" not in result["recipe"]:
            return
        
        ingredients = result["recipe"]["ingredients"]
        total_weight = result["recipe"]["total_weight_g"]
        
        # 计算各类别占比
        category_analysis = {}
        for category, cat_foods in categorized_foods.items():
            cat_fdc_ids = {f.fdc_id for f in cat_foods}
            category_weight = sum(
                ing["amount_g"] for ing in ingredients 
                if ing["fdc_id"] in cat_fdc_ids
            )
            category_analysis[category] = {
                "weight_g": round(category_weight, 1),
                "percentage": round(category_weight / total_weight * 100, 1),
                "ingredient_count": len([ing for ing in ingredients if ing["fdc_id"] in cat_fdc_ids])
            }
        
        # 计算营养平衡评分
        balance_score = self._calculate_balance_score(category_analysis, total_weight)
        
        # 添加到分析结果
        if "analysis" not in result:
            result["analysis"] = {}
        
        result["analysis"]["nutritional_balance"] = {
            "category_breakdown": category_analysis,
            "balance_score": balance_score,
            # "fiber_adequacy": self._assess_fiber_adequacy(ingredients),
            # "protein_quality": self._assess_protein_quality(ingredients),
            "overall_assessment": self._get_balance_assessment(balance_score, category_analysis)
        }

    def _calculate_balance_score(self, category_analysis: Dict, total_weight: float) -> float:
        """计算营养平衡评分 (0-100)"""
        score = 100
        
        # 检查各类别比例是否合理
        protein_percent = sum(
            data["percentage"] for key, data in category_analysis.items()
            if "protein" in key
        )
        vegetable_percent = sum(
            data["percentage"] for key, data in category_analysis.items()
            if "vegetable" in key
        )
        fat_percent = sum(
            data["percentage"] for key, data in category_analysis.items()
            if "fat" in key or "nuts" in key
        )
        
        # 评分逻辑
        if protein_percent < 30:
            score -= (30 - protein_percent) * 2
        elif protein_percent > 80:
            score -= (protein_percent - 80) * 1.5
        
        if vegetable_percent < 10:
            score -= (10 - vegetable_percent) * 3
        
        if fat_percent > 30:
            score -= (fat_percent - 30) * 2
        
        return max(0, round(score, 1))

    def _get_balance_assessment(self, balance_score: float, category_analysis: Dict) -> str:
        """获取平衡评估结论"""
        if balance_score >= 85:
            return "营养平衡良好，各类食材搭配合理"
        elif balance_score >= 70:
            return "营养平衡基本合理，建议适当调整食材比例"
        else:
            return "营养平衡需要改善，建议增加蔬菜类食材或调整配方结构"

    def _create_balanced_success_analysis(self, baseline_weight_g: float, target_weight_g: float, 
                                        final_weight_g: float, baseline_result: Dict, 
                                        final_result: Dict) -> Dict[str, Any]:
        """创建平衡成功分析"""
        weight_deviation = abs(final_weight_g - target_weight_g) / target_weight_g * 100
        
        baseline_score = baseline_result["analysis"]["aafco_compliance"]["score"]
        final_score = final_result["analysis"]["aafco_compliance"]["score"]
        
        return {
            "optimization_mode": "balanced_weight_guided",
            "baseline_weight_g": baseline_weight_g,
            "target_weight_g": target_weight_g,
            "final_weight_g": final_weight_g,
            "weight_deviation_percent": round(weight_deviation, 1),
            "adjustment_success": weight_deviation <= 35,  # 35%以内算成功
            "nutrition_compromise": {
                "baseline_score": baseline_score,
                "final_score": final_score,
                "score_difference": round(baseline_score - final_score, 1),
                "acceptable": (baseline_score - final_score) <= 8.0
            },
            "balance_achievement": "已确保营养平衡和食材多样性",
            "recommendation": self._get_balanced_recommendation(weight_deviation, final_score),
            "energy_density_achieved": round(final_result["recipe"]["actual_calories"] / final_weight_g, 2)
        }

    def _get_balanced_recommendation(self, weight_deviation: float, nutrition_score: float) -> str:
        """获取平衡优化建议"""
        if weight_deviation <= 20 and nutrition_score >= 80:
            return "配方已达到重量目标且营养平衡良好，可直接使用"
        elif weight_deviation <= 35 and nutrition_score >= 75:
            return "配方基本达到重量目标，营养平衡合理，推荐使用"
        elif weight_deviation > 35:
            return "重量偏差较大但营养平衡良好，可考虑调整目标重量或分次制作"
        else:
            return "需要进一步优化营养配比，建议咨询宠物营养师"

    def _add_failure_analysis(self, baseline_result: Dict, reason: str) -> Dict[str, Any]:
        """添加失败分析信息"""
        baseline_result["analysis"]["weight_analysis"] = {
            "optimization_mode": "weight_guided_failed",
            "adjustment_success": False,
            "failure_reason": reason,
            "recommendation": "重量调整失败，建议使用营养优先方案或调整目标重量",
            "fallback_used": True
        }
        return baseline_result
        
    async def _solve_problem(self) -> str:
        """异步求解问题"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._solve_optimization_problem)

    def _create_decision_variables(self, foods: List[Ingredient]):
        """创建决策变量"""
        self.ingredient_vars = {}
        self.binary_vars = {}
        
        for food in foods:
            # 连续变量：食材用量(g)
            self.ingredient_vars[food.fdc_id] = LpVariable(
                f"amount_{food.fdc_id}", 
                lowBound=0, 
                cat="Continuous"
            )
            
            # 二进制变量：是否使用该食材
            self.binary_vars[food.fdc_id] = LpVariable(
                f"use_{food.fdc_id}", 
                cat="Binary"
            )

    def _add_energy_constraints(self, foods: List[Ingredient], target_calories: float):
        """添加能量约束 - 硬约束"""
        total_energy = lpSum([
            self.ingredient_vars[food.fdc_id] * (food.energy_kcal_100g or 0) / 100
            for food in foods 
            if food.energy_kcal_100g is not None
        ])
        
        # 严格的能量约束
        min_energy = target_calories * (1 - self.config.energy_tolerance)
        max_energy = target_calories * (1 + self.config.energy_tolerance)
        
        self.problem += total_energy >= min_energy, "Min_Energy_Required"
        self.problem += total_energy <= max_energy, "Max_Energy_Allowed"
        
        logger.info(f"Energy constraints: {min_energy:.1f} - {max_energy:.1f} kcal")

    async def _create_nutrition_objective(self, foods: List[Ingredient], 
                                        standards: Dict[str, Any], 
                                        target_calories: float) -> List[Any]:
        """创建营养素相关的目标函数组件"""
        objective_components = []
        processed_nutrients = 0
        
        for nutrient_id, standard in standards.items():
            try:
                # 计算总营养素含量
                nutrient_amount = await self._get_nutrient_expression(foods, nutrient_id)
                
                if nutrient_amount is not None:
                    # 计算营养素需求
                    min_required = await self._calculate_nutrient_requirement(
                        standard, target_calories, nutrient_id, "min"
                    )
                    max_allowed = await self._calculate_nutrient_requirement(
                        standard, target_calories, nutrient_id, "max"
                    )
                    
                    importance_weight = self._get_nutrient_importance(nutrient_id)
                    
                    # 处理最小需求
                    if min_required and min_required > 0:
                        # 营养素不足惩罚
                        deficiency_var = LpVariable(f"deficiency_{nutrient_id}", lowBound=0)
                        self.problem += (
                            nutrient_amount + deficiency_var >= min_required,
                            f"Min_{nutrient_id}"
                        )
                        
                        # 添加到目标函数
                        penalty = (self.config.nutrient_deficiency_weight * 
                                 importance_weight * deficiency_var)
                        objective_components.append(penalty)
                    
                    # 处理最大限制
                    if max_allowed and max_allowed > 0:
                        # 营养素过量惩罚（软约束）
                        excess_var = LpVariable(f"excess_{nutrient_id}", lowBound=0)
                        self.problem += (
                            nutrient_amount - excess_var <= max_allowed,
                            f"Max_{nutrient_id}"
                        )
                        
                        # 添加到目标函数
                        penalty = (self.config.nutrient_excess_weight * 
                                 importance_weight * excess_var)
                        objective_components.append(penalty)
                    
                    processed_nutrients += 1
                
            except Exception as e:
                logger.error(f"Error processing nutrient {nutrient_id}: {e}")
                continue
        
        logger.info(f"Successfully processed {processed_nutrients} nutrients")
        
        return objective_components
    
    def _create_cost_objective(self, foods: List[Ingredient]) -> Any:
        """创建成本目标函数组件"""
        total_cost = lpSum([
            self.ingredient_vars[food.fdc_id] * (food.cost_per_100g or 0) / 100
            for food in foods
        ])
        return self.config.cost_weight * total_cost

    def _create_diversity_objective(self, foods: List[Ingredient]) -> Any:
        """创建多样性目标函数组件 - 鼓励使用更多种类的食材"""
        # 惩罚未使用的食材（鼓励多样性）
        unused_penalty = lpSum([
            (1 - self.binary_vars[food.fdc_id]) for food in foods
        ])
        return self.config.diversity_weight * unused_penalty
    
    def _add_diversity_constraints(self, foods: List[Ingredient]):
        """添加食材多样性约束"""
        total_weight = lpSum([self.ingredient_vars[food.fdc_id] for food in foods])
        
        for food in foods:
            ingredient_var = self.ingredient_vars[food.fdc_id]
            binary_var = self.binary_vars[food.fdc_id]
            
            # 如果使用该食材，最小用量约束
            self.problem += (
                ingredient_var >= self.config.min_ingredient_amount_g * binary_var,
                f"Min_Use_{food.fdc_id}"
            )
            
            # 大M约束：如果不使用该食材，用量为0
            big_m = self.config.max_reasonable_weight_g
            self.problem += (
                ingredient_var <= big_m * binary_var,
                f"Max_Use_{food.fdc_id}"
            )
            
            # 单一食材最大占比约束（基于总重量）
            max_percent = self.config.max_single_ingredient_percent / 100
            self.problem += (
                ingredient_var <= max_percent * total_weight,
                f"Max_Percent_{food.fdc_id}"
            )
        
        # 最少食材种类约束
        self.problem += (
            lpSum([self.binary_vars[food.fdc_id] for food in foods]) >= self.config.min_ingredient_count,
            "Min_Ingredient_Count"
        )

    async def _add_category_constraints(self, foods: List[Ingredient]):
        """添加食材分类约束"""
        try:
            # 按分类分组
            foods_by_category: Dict[str, List[Ingredient]] = {}
            for food in foods:
                if food.category:
                    cat_name = food.category.name
                    if cat_name not in foods_by_category:
                        foods_by_category[cat_name] = []
                    foods_by_category[cat_name].append(food)

            total_weight = lpSum([self.ingredient_vars[food.fdc_id] for food in foods])
            
            # 添加分类比例约束
            for category_name, category_foods in foods_by_category.items():
                constraints = CATEGORY_CONSTRAINTS.get(category_name, {})
                
                if constraints and len(category_foods) > 0:
                    category_total = lpSum([
                        self.ingredient_vars[food.fdc_id] for food in category_foods
                    ])
                    
                    min_percent = constraints.get("min_percent", 0)
                    max_percent = constraints.get("max_percent", 100)
                    
                    if min_percent > 0:
                        self.problem += (
                            category_total >= (min_percent / 100) * total_weight,
                            f"Cat_Min_{category_name}"
                        )
                    
                    if max_percent < 100:
                        self.problem += (
                            category_total <= (max_percent / 100) * total_weight,
                            f"Cat_Max_{category_name}"
                        )

            logger.info(f"Added category constraints for {len(foods_by_category)} categories")

        except Exception as e:
            logger.error(f"Error adding category constraints: {e}")

    def _is_weight_reasonable(self, weight_g: float, target_calories: float) -> bool:
        """检查重量是否合理"""
        if weight_g < self.config.min_reasonable_weight_g or weight_g > self.config.max_reasonable_weight_g:
            return False
        
        density = target_calories / weight_g
        return 1.5 <= density <= 6.0

    def _categorize_weight(self, weight_g: float, target_calories: float) -> str:
        """重量分类"""
        density = target_calories / weight_g
        
        if density > 4.0:
            return "高密度配方"
        elif density > 3.0:
            return "中等密度配方"
        elif density > 2.0:
            return "低密度配方"
        else:
            return "超低密度配方"

    def _get_weight_suggestions(self, weight_g: float, target_calories: float) -> List[str]:
        """获取重量建议"""
        suggestions = []
        
        if weight_g < 150:
            suggestions.append("配方较轻，适合制作多份小量保存")
        elif weight_g > 1000:
            suggestions.append("配方较重，建议分装冷冻保存")
        
        density = target_calories / weight_g
        if density > 4.5:
            suggestions.append("高能量密度，注意控制喂食量")
        elif density < 2.5:
            suggestions.append("能量密度偏低，确保宠物能摄入足够分量")
        
        return suggestions
    
    def _get_adjustment_recommendation(self, adjustment_success: bool, 
                                     nutrition_compromise: float,
                                     final_deviation: float,
                                     target_weight: float) -> str:
        """获取调整建议"""
        if adjustment_success and nutrition_compromise <= 3.0:
            return "成功调整至目标重量，营养质量保持良好"
        elif adjustment_success and nutrition_compromise <= 5.0:
            return "成功调整至目标重量，营养质量轻微妥协但可接受"
        elif adjustment_success:
            return "已调整至目标重量，但营养质量有明显妥协，建议考虑营养优先方案"
        elif final_deviation / target_weight < 0.2:  # 20%以内
            return "接近目标重量，营养质量良好"
        else:
            return "无法有效调整至目标重量，建议采用营养优先方案"

    async def _validate_food_nutrition_data(self, foods: List[Ingredient]) -> List[Ingredient]:
        """验证食材营养数据的完整性"""
        valid_foods = []
        
        for food in foods:
            # 检查基本能量数据
            if not food.energy_kcal_100g or food.energy_kcal_100g <= 0:
                logger.warning(f"Food {food.fdc_id} lacks energy data")
                continue
            
            # 检查是否有足够的营养素数据
            stmt = select(IngredientNutrient).where(
                IngredientNutrient.fdc_id == food.fdc_id,
                IngredientNutrient.amount.isnot(None),
                IngredientNutrient.amount > 0
            )
            result = await self.session.execute(stmt)
            nutrient_count = len(result.scalars().all())
            
            if nutrient_count >= 3:  # 至少要有3种营养素数据
                valid_foods.append(food)
            else:
                logger.warning(f"Food {food.fdc_id} has insufficient nutrient data ({nutrient_count} nutrients)")
        
        return valid_foods

    async def _get_nutrient_expression(self, foods: List[Ingredient], nutrient_id: int) -> Optional[Any]:
        """获取营养素的线性表达式"""
        nutrient_expr = 0
        has_data = False

        for food in foods:
            stmt = select(IngredientNutrient).join(Nutrient).where(
                IngredientNutrient.fdc_id == food.fdc_id,
                Nutrient.nutrient_id == nutrient_id
            )
            result = await self.session.execute(stmt)
            nutrient_data = result.scalar_one_or_none()
            
            if nutrient_data and nutrient_data.amount is not None:
                amount_per_g = nutrient_data.amount / 100.0
                nutrient_expr += self.ingredient_vars[food.fdc_id] * amount_per_g
                has_data = True
        
        return nutrient_expr if has_data else None

    async def _calculate_nutrient_requirement(self, standard: Dict[str, Any], 
                                            target_calories: float, 
                                            nutrient_id: int, 
                                            req_type: str) -> Optional[float]:
        """计算营养素需求量"""
        try:
            requirement = standard.get(req_type)
            if not requirement:
                return None
            
            # 基于目标能量计算需求
            recipe_requirement = requirement * target_calories / 1000
            
            # 单位转换
            unit = standard.get("unit")
            if unit:
                stmt = select(Nutrient).where(Nutrient.nutrient_id == nutrient_id)
                result = await self.session.execute(stmt)
                nutrient = result.scalar_one_or_none()
                
                if nutrient and nutrient.unit_name:
                    recipe_requirement = self._convert_units(
                        recipe_requirement, unit, nutrient.unit_name
                    )
            
            return recipe_requirement
            
        except Exception as e:
            logger.error(f"Error calculating nutrient requirement for {nutrient_id}: {e}")
            return None

    async def _process_nutrition_results(self, foods: List[Ingredient], 
                                       target_calories: float, 
                                       standards: Dict[str, Any]) -> Dict[str, Any]:
        """处理优化结果"""
        try:
            # 提取配方
            recipe_ingredients = []
            total_weight = 0
            actual_calories = 0
            total_cost = 0
            
            for food in foods:
                amount = self.ingredient_vars[food.fdc_id].varValue
                if amount and amount > 0.1:  # 忽略极小用量
                    ingredient_info = {
                        "fdc_id": food.fdc_id,
                        "description": food.description,
                        "common_name": food.common_name or food.description,
                        "amount_g": round(amount, 1),
                        "cost": round(amount * (food.cost_per_100g or 0) / 100, 2),
                        "calories": round(amount * (food.energy_kcal_100g or 0) / 100, 1),
                        "category": food.category.name if food.category else "其他"
                    }
                    recipe_ingredients.append(ingredient_info)
                    total_weight += amount
                    actual_calories += ingredient_info["calories"]
                    total_cost += ingredient_info["cost"]
            
            # 检查结果合理性
            if total_weight < self.config.min_reasonable_weight_g or total_weight > self.config.max_reasonable_weight_g:
                logger.warning(f"Recipe weight {total_weight:.1f}g may be unreasonable")
            
            # 计算百分比
            for ingredient in recipe_ingredients:
                ingredient["percentage"] = round(ingredient["amount_g"] / total_weight * 100, 1)
            
            # 按用量排序
            recipe_ingredients.sort(key=lambda x: x["amount_g"], reverse=True)
            
            # 营养分析
            nutrition_analysis = await self._analyze_nutrition(
                foods, recipe_ingredients, standards, target_calories
            )
            
            # 提取基础营养信息以匹配前端期望的格式
            basic_nutrition = {
                "total_calories_kcal": round(actual_calories, 1),
                "protein_g": 0,
                "fat_g": 0,
                "carbohydrate_g": 0,
                "fiber_g": 0
            }
            
            # 从营养分析中提取基础营养素
            if NutrientID.PROTEIN in nutrition_analysis:
                basic_nutrition["protein_g"] = nutrition_analysis[NutrientID.PROTEIN]["amount_total"]
            if NutrientID.FAT in nutrition_analysis:
                basic_nutrition["fat_g"] = nutrition_analysis[NutrientID.FAT]["amount_total"]
            # 从营养分析中获取碳水化合物，如果没有则设为0
            if NutrientID.CARBOHYDRATE in nutrition_analysis:
                basic_nutrition["carbohydrate_g"] = nutrition_analysis[NutrientID.CARBOHYDRATE]["amount_total"]
            else:
                # 如果没有直接的碳水化合物数据，通过重量计算估算（但这不是最准确的方法）
                dry_matter = total_weight * 0.9  # 假设90%为干物质
                other_nutrients = basic_nutrition["protein_g"] + basic_nutrition["fat_g"]
                basic_nutrition["carbohydrate_g"] = max(0, dry_matter - other_nutrients)
            
            # 合并营养分析（包含详细的营养素分析和基础营养信息）
            combined_nutrition = {**nutrition_analysis, **basic_nutrition}
            
            # 计算营养密度和效率指标
            efficiency_metrics = {
                "caloric_density_kcal_per_g": round(actual_calories / total_weight, 2),
                "cost_efficiency_cost_per_kcal": round(total_cost / actual_calories, 4),
                "ingredient_count": len(recipe_ingredients),
                "weight_category": self._categorize_weight(total_weight, target_calories)
            }
            
            return {
                "status": "Success",
                "recipe": {
                    "total_weight_g": round(total_weight, 1),
                    "target_calories": target_calories,
                    "actual_calories": round(actual_calories, 1),
                    "energy_accuracy": round(abs(actual_calories - target_calories) / target_calories * 100, 2),
                    "ingredients": recipe_ingredients
                },
                "analysis": {
                    "nutrition": combined_nutrition,
                    "efficiency": efficiency_metrics,
                    "aafco_compliance": {
                        "compliant": self._check_overall_compliance(nutrition_analysis),
                        "violations": self._get_violations(nutrition_analysis),
                        "score": self._calculate_compliance_score(nutrition_analysis)
                    },
                    "cost_analysis": {
                        "total_cost": round(total_cost, 2),
                        "cost_per_kg": round(total_cost * 1000 / total_weight, 2)
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing nutrition results: {e}")
            return self._create_error_result(f"Error processing results: {e}")

    async def _analyze_nutrition(self, foods: List[Ingredient], recipe_ingredients: List[Dict[str, Any]], 
                               standards: Dict[str, Any], 
                               target_calories: float) -> Dict[str, Any]:
        """分析配方营养合规性"""
        analysis: Dict[str, Any] = {}
        
        try:
            for nutrient_id in standards.keys():
                total_amount = 0
                
                # 计算每种营养素的总含量
                for ingredient in recipe_ingredients:
                    fdc_id = ingredient["fdc_id"]
                    amount_g = ingredient["amount_g"]
                    
                    # 查询营养素含量
                    stmt = select(IngredientNutrient).join(Nutrient).where(
                        IngredientNutrient.fdc_id == fdc_id,
                        Nutrient.nutrient_id == nutrient_id
                    )
                    result = await self.session.execute(stmt)
                    nutrient_data = result.scalar_one_or_none()
                    
                    if nutrient_data and nutrient_data.amount is not None:
                        total_amount += nutrient_data.amount * amount_g / 100
            
                # 基于实际能量计算每1000kcal的营养素含量
                amount_per_1000kcal = total_amount * 1000 / target_calories
                
                standard = standards[nutrient_id]
                min_req = standard.get("min")
                max_req = standard.get("max")
            
                status = "OK"
                if min_req and amount_per_1000kcal < min_req:
                    status = "LOW"
                elif max_req and amount_per_1000kcal > max_req:
                    status = "HIGH"
                
                analysis[nutrient_id] = {
                    "amount_per_1000kcal": round(amount_per_1000kcal, 2),
                    "amount_total": round(total_amount, 2),
                    "requirement_min": min_req,
                    "requirement_max": max_req,
                    "status": status,
                    "unit": standard.get("unit")
                }
        
            return analysis
        except Exception as e:
            logger.error(f"Error analyzing nutrition: {e}")
            return {}

    # 以下方法与原版本相同，保持不变
    def _get_aafco_key(self, pet: Pet) -> LifeStage:
        """获取AAFCO标准键值"""
        if not hasattr(pet, "species") or not pet.species:
            raise ValueError("Pet species is required")
        if not hasattr(pet, "age_months") or pet.age_months is None:
            raise ValueError("Pet age is required")
        
        species = pet.species.lower()
        age_months = pet.age_months

        if species == "dog":
            return LifeStage.DOG_PUPPY if age_months <= 12 else LifeStage.DOG_ADULT
        elif species == "cat":
            return LifeStage.CAT_KITTEN if age_months <= 12 else LifeStage.CAT_ADULT
        else:
            raise ValueError(f"Unsupported pet species: {pet.species}")
    
    async def _get_available_foods(self, pet: Pet) -> List[Ingredient]:
        """获取对宠物安全的可用食材"""
        cache_key = f"{pet.species}_{pet.id}"

        if cache_key in self._food_cache:
            logger.info(f"Using cached foods for {cache_key}")
            return self._food_cache[cache_key]

        try:
            stmt = select(Ingredient).options(selectinload(Ingredient.category)).join(Ingredient.category, isouter=True)
            
            if pet.species.lower() == 'dog':
                stmt = stmt.where(Ingredient.safe_for_dogs == True)
            elif pet.species.lower() == 'cat':
                stmt = stmt.where(Ingredient.safe_for_cats == True)
            else:
                raise ValueError(f"Unsupported pet species: {pet.species}")

            stmt = stmt.where(Ingredient.energy_kcal_100g.isnot(None), Ingredient.energy_kcal_100g > 0)
            
            result = await self.session.execute(stmt)
            foods = result.scalars().all()

            if not foods:
                logger.warning(f"No foods found for {pet.species}")
                return []
            
            self._food_cache[cache_key] = foods
            logger.info(f"Retrieved {len(foods)} foods from database")
            return foods
        
        except Exception as e:
            logger.error(f"Error getting foods for {pet.species}: {e}")
            return []
    
    def _get_nutrient_importance(self, nutrient_id: int) -> float:
        """获取营养素重要性权重"""
        importance_map = {
            NutrientID.PROTEIN: 10.0,
            NutrientID.FAT: 8.0,
            NutrientID.CALCIUM: 7.0,
            NutrientID.PHOSPHORUS: 7.0,
            NutrientID.IRON: 5.0,
            NutrientID.ZINC: 5.0,
            NutrientID.SODIUM: 3.0
        }
        return importance_map.get(nutrient_id, 4.0)
    
    def _convert_units(self, value: float, from_unit: str, to_unit: str) -> float:
        """营养素单位转换"""
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError(f"Invalid value for unit conversion: {value}")
            
        from_unit = from_unit.upper().strip()
        to_unit = to_unit.upper().strip()

        if from_unit == to_unit:
            return value
        
        conversion_factors = {
            "G": 1000.0,
            "MG": 1.0,
            "IU": 0.6774,
            "UG": 0.001,
        }
        
        if from_unit not in conversion_factors or to_unit not in conversion_factors:
            logger.error(f"Unsupported unit conversion: {from_unit} -> {to_unit}")
            return value
        
        return value * conversion_factors[from_unit] / conversion_factors[to_unit]
    
    def _check_overall_compliance(self, nutrition_analysis: Dict[str, Any]) -> bool:
        """检查整体AAFCO合规性"""
        for nutrient_data in nutrition_analysis.values():
            if isinstance(nutrient_data, dict) and nutrient_data.get("status") == "LOW":
                return False
        return True
    
    def _get_violations(self, nutrition_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """获取营养素违规信息"""
        violations = []
        for nutrient_id, data in nutrition_analysis.items():
            if isinstance(data, dict) and data.get("status") in ["LOW", "HIGH"]:
                violation = {
                    "nutrient": str(nutrient_id),
                    "actual": data.get("amount_per_1000kcal", 0),
                    "unit": data.get("unit", ""),
                    "status": data.get("status")
                }
                if data.get("requirement_min"):
                    violation["required_min"] = data["requirement_min"]
                if data.get("requirement_max"):
                    violation["required_max"] = data["requirement_max"]
                violations.append(violation)
        return violations
    
    def _calculate_compliance_score(self, nutrition_analysis: Dict[str, Any]) -> float:
        """计算营养合规性评分 (0-100)"""
        if not nutrition_analysis:
            return 0.0
        
        total_score = 0
        total_weight = 0
        
        for nutrient_id, data in nutrition_analysis.items():
            if not isinstance(data, dict):
                continue
            
            importance = self._get_nutrient_importance(nutrient_id)
            
            if data.get("status") == "OK":
                score = 100
            elif data.get("status") == "LOW":
                min_req = data.get("requirement_min")
                actual = data.get("amount_per_1000kcal")
                if min_req and min_req > 0 and actual is not None:
                    ratio = actual / min_req
                    score = max(0, ratio * 100)
                else:
                    score = 50
            else:  # HIGH
                score = 80
            
            total_score += score * importance
            total_weight += importance
        
        # 返回加权平均分
        return round(total_score / total_weight if total_weight > 0 else 0.0, 1)
    
    def _create_error_result(self, error_message: str) -> Dict[str, Any]:
        """创建错误结果"""
        return {
            "status": "Error",
            "error": error_message,
            "recipe": {},
            "analysis": {}
        }

class RecipeService:
    def __init__(self, db: AsyncSession):
        self.db = db

    @asynccontextmanager
    async def get_optimizer(self):
        """创建一个异步上下文管理器来管理优化器的生命周期"""
        optimizer = NutritionOptimizer(self.db)
        try:
            yield optimizer
        finally:
            # 清理资源
            optimizer.problem = None
            optimizer.ingredient_vars = {}
            optimizer.binary_vars = {}
            optimizer._food_cache = {}

    async def generate_recipe(self, 
                              pet_id: int, 
                              target_calories: Optional[float],
                              preferred_weight_g: Optional[float] = None) -> Dict[str, Any]:
        """生成配方"""
        try:
            logger.info(f"Generating recipe for pet {pet_id} with target calories {target_calories}")
            
            # 🔧 输入验证
            if not isinstance(pet_id, int) or pet_id <= 0:
                return {
                    "status": "Error",
                    "error": "无效的宠物ID",
                    "recipe": {},
                    "analysis": {}
                }
            
            # 获取宠物信息
            try:
                result = await self.db.execute(select(Pet).where(Pet.id == pet_id))
                pet = result.scalar_one_or_none()

                if not pet:
                    return {
                        "status": "Error",
                        "error": f"宠物 {pet_id} 不存在",
                        "recipe": {},
                        "analysis": {}
                    }
                
                logger.info(f"找到宠物: {pet.name} ({pet.species}, {pet.age_months}个月, {pet.weight_kg}kg)")

            except Exception as e:
                logger.error(f"Error getting pet {pet_id}: {e}")
                return {
                    "status": "Error",
                    "error": "获取宠物信息失败",
                    "recipe": {},
                    "analysis": {}
                }

            
            # 🔧 使用宠物的每日卡路里需求作为默认值
            if not target_calories or target_calories <= 0:
                if pet.daily_calories_kcal and pet.daily_calories_kcal > 0:
                    target_calories = pet.daily_calories_kcal
                    logger.info(f"使用宠物每日卡路里需求: {target_calories} kcal")
                else:
                    # 🔧 如果没有存储的卡路里数据，计算一个基本估值
                    target_calories = self._estimate_daily_calories(pet)
                    logger.warning(f"宠物缺少卡路里数据，使用估算值: {target_calories} kcal")
            
            # 验证最终的目标卡路里
            if target_calories <= 0 or target_calories > 15000:  # 合理范围检查
                return {
                    "status": "Error",
                    "error": f"目标卡路里 {target_calories} 超出合理范围 (1-15000)",
                    "recipe": {},
                    "analysis": {}
                }
            
            # 使用异步上下文管理器创建和使用优化器
            async with self.get_optimizer() as optimizer:
                # 生成配方
                result = await optimizer.optimize_recipe(
                    pet=pet,
                    target_calories=target_calories,
                    preferred_weight_g=preferred_weight_g
                )

                 # 🔧 在结果中添加宠物ID
                if result.get("status") == "Success" and "recipe" in result:
                    result["recipe"]["pet_id"] = pet_id

                    # 添加混合优化的额外分析信息
                    self._add_hybrid_analysis_info(result, preferred_weight_g)
                
                logger.info(f"配方生成完成，状态: {result.get('status')}")
                return result
            
        except Exception as e:
            error_msg = f"生成配方失败: {str(e)}"
            logger.error(error_msg)
            logger.error(f"detail of falut massages: {traceback.format_exc()}")
            return {
                "status": "Error",
                "error": str(e),
                "recipe": {},
                "analysis": {}
            }

    def _add_hybrid_analysis_info(self, result: Dict[str, Any], preferred_weight_g: Optional[float]):
        """添加混合优化特有的分析信息"""
        if "analysis" not in result:
            return
        
        analysis = result["analysis"]
        
        # 添加优化策略说明
        weight_analysis = analysis.get("weight_analysis", {})
        optimization_mode = weight_analysis.get("optimization_mode", "nutrition_focused")
        
        strategy_info = {
            "optimization_strategy": "hybrid",
            "primary_mode": optimization_mode,
            "weight_preference_provided": preferred_weight_g is not None,
            "strategy_description": self._get_strategy_description(optimization_mode, preferred_weight_g)
        }
        
        analysis["optimization_strategy"] = strategy_info
        
        # 添加用户建议
        if preferred_weight_g:
            final_weight = result["recipe"]["total_weight_g"]
            deviation_percent = abs(final_weight - preferred_weight_g) / preferred_weight_g * 100
            
            user_guidance = {
                "weight_achievement": deviation_percent,
                "weight_achievement_category": self._categorize_weight_achievement(deviation_percent),
                "next_steps": self._get_next_step_suggestions(weight_analysis)
            }
            
            analysis["user_guidance"] = user_guidance

    def _get_strategy_description(self, mode: str, preferred_weight: Optional[float]) -> str:
        """获取策略描述"""
        if not preferred_weight:
            return "采用营养导向优化，重量由营养需求自然决定"
        
        if mode == "nutrition_optimal_accepted":
            return "营养最优解的重量在可接受范围内，未进行重量调整"
        elif mode == "weight_guided":
            return "在满足营养需求的前提下，向用户偏好重量进行引导调整"
        else:
            return "采用营养导向优化，重量由营养需求决定"

    def _categorize_weight_achievement(self, deviation_percent: float) -> str:
        """重量达成度分类"""
        if deviation_percent <= 5:
            return "完全达成"
        elif deviation_percent <= 15:
            return "基本达成"
        elif deviation_percent <= 30:
            return "部分达成"
        else:
            return "显著偏差"

    def _get_next_step_suggestions(self, weight_analysis: Dict[str, Any]) -> List[str]:
        """获取下一步建议"""
        suggestions = []
        
        if weight_analysis.get("adjustment_success"):
            suggestions.append("重量调整成功，可直接使用此配方")
        else:
            suggestions.append("如重视营养质量，建议使用当前方案")
            suggestions.append("如必须达到特定重量，可考虑分次制作或调整食材比例")
        
        nutrition_compromise = weight_analysis.get("nutrition_compromise", {})
        if nutrition_compromise.get("score_difference", 0) > 5:
            suggestions.append("当前方案存在一定营养妥协，建议权衡重量与营养需求")
        
        return suggestions
    
    async def get_recipe(self, recipe_id: int) -> Optional[Dict[str, Any]]:
        """获取配方（预留接口）"""
        # TODO: 实现配方存储和检索功能
        logger.info(f"获取配方 {recipe_id} - 功能待实现")
        return None
    
    async def save_recipe(self, recipe_data: Dict[str, Any]) -> Optional[int]:
        """保存配方到数据库（预留接口）"""
        # TODO: 实现配方保存功能
        logger.info("保存配方 - 功能待实现")
        return None
    
    async def list_recipes(self, pet_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """获取宠物的历史配方列表（预留接口）"""
        # TODO: 实现配方列表功能
        logger.info(f"获取宠物 {pet_id} 的配方列表 - 功能待实现")
        return []

    def _estimate_daily_calories(self, pet: Pet) -> float:
        """使用专业的能量计算器估算宠物每日卡路里需求"""
        try:
            from app.services.energy_calculate import EnergyCalculator
            from app.db.models import Species, ActivityLevel, PhysiologicalStatus
            
            # 转换宠物种类
            if pet.species.lower() == 'dog':
                species = Species.DOG
            elif pet.species.lower() == 'cat':
                species = Species.CAT
            else:
                raise ValueError(f"Unsupported species: {pet.species}")
            
            # 获取活动水平，如果没有设置则使用默认值
            activity_level = getattr(pet, 'activity_level', ActivityLevel.MODERATE_ACTIVE)
            if isinstance(activity_level, str):
                # 如果是字符串，转换为枚举
                activity_level = ActivityLevel(activity_level)
            
            # 获取生理状态，如果没有设置则使用默认值
            physiological_status = getattr(pet, 'physiological_status', PhysiologicalStatus.NEUTERED)
            if isinstance(physiological_status, str):
                # 如果是字符串，转换为枚举
                physiological_status = PhysiologicalStatus(physiological_status)
            
            # 获取哺乳期相关参数
            lactation_week = getattr(pet, 'lactation_week', 4)
            nursing_count = getattr(pet, 'nursing_count', 1)
            
            # 使用专业的能量计算器
            energy_result = EnergyCalculator.calculate_daily_energy_requirement(
                weight_kg=pet.weight_kg,
                species=species,
                age_months=pet.age_months,
                activity_level=activity_level,
                physiological_status=physiological_status,
                lactation_week=lactation_week,
                nursing_count=nursing_count
            )
            
            daily_calories = energy_result["daily_energy_kcal"]
            
            logger.info(f"Calculated daily calories for {pet.species} (weight: {pet.weight_kg}kg, age: {pet.age_months}mo, life_stage: {energy_result['life_stage']}): {daily_calories} kcal")
            
            return daily_calories
            
        except Exception as e:
            logger.error(f"Error calculating daily calories for pet: {e}")
            # 返回一个基于体重的简单估算作为备用
            default_calories = pet.weight_kg * 50  # 简单的每公斤50卡路里估算
            logger.warning(f"Using default calorie estimation: {default_calories} kcal")
            return default_calories       