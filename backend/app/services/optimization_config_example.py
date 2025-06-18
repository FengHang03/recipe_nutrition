"""
优化配置使用示例

演示如何使用 OptimizationConfig 来自定义营养配方优化参数
"""

from app.services.recipe_service import OptimizationConfig, NutritionOptimizer
from app.db.models import Pet

def example_basic_usage():
    """基本使用 - 使用默认配置"""
    
    # 使用默认配置
    config = OptimizationConfig()
    print(f"默认配置:")
    print(f"  能量权重: {config.energy_weight}")
    print(f"  营养素权重: {config.nutrient_weight}")
    print(f"  单一食材最大占比: {config.max_single_food_percent}%")
    print(f"  默认配方重量: {config.recipe_weight_g}g")
    
    # 创建优化器（需要数据库会话）
    # optimizer = NutritionOptimizer(session, config)

def example_custom_config():
    """自定义配置示例"""
    
    # 创建自定义配置 - 更保守的配方
    conservative_config = OptimizationConfig(
        energy_weight=2000.0,           # 更重视能量精确性
        nutrient_weight=50.0,           # 降低营养素惩罚权重
        max_single_food_percent=30.0,   # 限制单一食材最大占比为30%
        recipe_weight_g=500.0           # 增加配方重量
    )
    
    print(f"\n保守配置:")
    print(f"  能量权重: {conservative_config.energy_weight}")
    print(f"  营养素权重: {conservative_config.nutrient_weight}")
    print(f"  单一食材最大占比: {conservative_config.max_single_food_percent}%")
    print(f"  配方重量: {conservative_config.recipe_weight_g}g")

def example_high_nutrition_config():
    """高营养要求配置示例"""
    
    # 创建高营养要求配置
    high_nutrition_config = OptimizationConfig(
        energy_weight=500.0,            # 降低能量权重
        nutrient_weight=200.0,          # 大幅提高营养素权重
        max_single_food_percent=40.0,   # 允许更高的单一食材占比
        recipe_weight_g=400.0
    )
    
    print(f"\n高营养配置:")
    print(f"  能量权重: {high_nutrition_config.energy_weight}")
    print(f"  营养素权重: {high_nutrition_config.nutrient_weight}")
    print(f"  单一食材最大占比: {high_nutrition_config.max_single_food_percent}%")
    print(f"  配方重量: {high_nutrition_config.recipe_weight_g}g")

def example_validation():
    """配置验证示例"""
    
    print(f"\n配置验证示例:")
    
    try:
        # 这个配置会引发验证错误
        invalid_config = OptimizationConfig(
            energy_weight=-100,  # 负数权重无效
            max_single_food_percent=120  # 超过100%无效
        )
    except ValueError as e:
        print(f"配置验证错误: {e}")
    
    try:
        # 这个配置也会引发验证错误
        invalid_config2 = OptimizationConfig(
            max_single_food_percent=0  # 0%无效
        )
    except ValueError as e:
        print(f"配置验证错误: {e}")

def example_usage_with_optimizer():
    """在优化器中使用配置的示例"""
    
    # 示例：如何在实际应用中使用
    def optimize_pet_recipe(session, pet, target_calories, optimization_type="default"):
        """
        根据不同类型选择不同的优化配置
        
        Args:
            session: 数据库会话
            pet: 宠物对象
            target_calories: 目标热量
            optimization_type: 优化类型 ('default', 'conservative', 'high_nutrition')
        """
        
        if optimization_type == "conservative":
            config = OptimizationConfig(
                energy_weight=2000.0,
                nutrient_weight=50.0,
                max_single_food_percent=30.0
            )
        elif optimization_type == "high_nutrition":
            config = OptimizationConfig(
                energy_weight=500.0,
                nutrient_weight=200.0,
                max_single_food_percent=40.0
            )
        else:  # default
            config = OptimizationConfig()
        
        # 创建优化器并运行
        optimizer = NutritionOptimizer(session, config)
        
        # 注意：现在不需要传递recipe_weight_g参数，会使用配置中的默认值
        result = optimizer.optimize_recipe(
            pet=pet,
            target_calories=target_calories
        )
        
        return result
    
    print(f"\n使用示例:")
    print(f"- optimize_pet_recipe(session, pet, 500, 'default')")
    print(f"- optimize_pet_recipe(session, pet, 500, 'conservative')")
    print(f"- optimize_pet_recipe(session, pet, 500, 'high_nutrition')")

if __name__ == "__main__":
    example_basic_usage()
    example_custom_config()
    example_high_nutrition_config()
    example_validation()
    example_usage_with_optimizer() 