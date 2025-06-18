import os
import sys
import logging

# 添加 backend 目录到 Python 路径，使 app 模块可以被导入
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
import unittest
import pytest
from app.services.energy_calculate import EnergyCalculator
from app.db.models import ActivityLevel, PhysiologicalStatus, Species, LifeStage

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestEnergyCalculator(unittest.TestCase):
    """能量计算器测试类"""
    
    def setUp(self):
        """测试前准备"""
        self.calculator = EnergyCalculator()
        print(f"\n{'='*50}")
        print(f"开始测试: {self._testMethodName}")
        print(f"{'='*50}")
    
    def tearDown(self):
        """测试后清理"""
        print(f"{'='*50}")
        print(f"测试结束: {self._testMethodName}")
        print(f"{'='*50}\n")
    
    def test_calculate_resting_energy_requirement(self):
        """测试静息能量需求计算 (RER)"""
        print("测试静息能量需求计算 (RER)")
        
        test_weights = [5.0, 10.0, 30.0]
        for weight in test_weights:
            expected_rer = 70 * (weight ** 0.75)
            actual_rer = self.calculator.calculate_resting_energy_requirement(weight)
            
            print(f"  体重: {weight}kg")
            print(f"  期望RER: {expected_rer:.1f} kcal")
            print(f"  实际RER: {actual_rer:.1f} kcal")
            print(f"  差异: {abs(expected_rer - actual_rer):.1f} kcal")
            print("-" * 30)
            
            self.assertAlmostEqual(actual_rer, expected_rer, places=1)
        
        # 边界测试
        print("测试边界情况:")
        try:
            self.calculator.calculate_resting_energy_requirement(0)
            print("  零体重应该抛出异常但没有")
        except ValueError as e:
            print(f"  零体重正确抛出异常: {e}")
        
        try:
            self.calculator.calculate_resting_energy_requirement(-5)
            print("  负体重应该抛出异常但没有")
        except ValueError as e:
            print(f"  负体重正确抛出异常: {e}")
    
    def test_get_activity_factor(self):
        """测试活动系数获取"""
        print("测试活动系数获取")
        
        test_cases = [
            (12, ActivityLevel.SEDENTARY_ACTIVE, 1.4, "久坐"),
            (24, ActivityLevel.LOW_ACTIVE, 1.6, "低活动"),
            (36, ActivityLevel.MODERATE_ACTIVE, 1.8, "中等活动"),
            (48, ActivityLevel.HIGH_ACTIVE, 2.0, "高活动"),
            (60, ActivityLevel.EXTREME_ACTIVE, 2.2, "极高活动")
        ]
        
        for age, activity_level, expected_factor, desc in test_cases:
            actual_factor = self.calculator.get_activity_factor(age, activity_level)
            print(f"  年龄: {age}个月, 活动水平: {desc}")
            print(f"  期望系数: {expected_factor}, 实际系数: {actual_factor}")
            print("-" * 30)
            self.assertEqual(actual_factor, expected_factor)
    
    def test_get_life_stage_factor_dog(self):
        """测试狗的生命阶段系数"""
        print("测试狗的生命阶段系数")
        
        test_cases = [
            (3, 3.0, LifeStage.DOG_PUPPY, "幼犬(0-4个月)"),
            (8, 2.5, LifeStage.DOG_PUPPY, "幼犬(4-12个月)"),
            (24, 1.0, LifeStage.DOG_ADULT, "成犬")
        ]
        
        for age, expected_factor, expected_stage, desc in test_cases:
            factor, stage = self.calculator.get_life_stage_factor(Species.DOG, age)
            print(f"  年龄: {age}个月 ({desc})")
            print(f"  期望系数: {expected_factor}, 实际系数: {factor}")
            print(f"  期望阶段: {expected_stage.value}, 实际阶段: {stage.value}")
            print("-" * 30)
            
            self.assertEqual(factor, expected_factor)
            self.assertEqual(stage, expected_stage)
    
    def test_get_life_stage_factor_cat(self):
        """测试猫的生命阶段系数"""
        print("测试猫的生命阶段系数")
        
        test_cases = [
            (6, 2.5, LifeStage.CAT_KITTEN, "幼猫"),
            (18, 1.0, LifeStage.CAT_ADULT, "成猫")
        ]
        
        for age, expected_factor, expected_stage, desc in test_cases:
            factor, stage = self.calculator.get_life_stage_factor(Species.CAT, age)
            print(f"  年龄: {age}个月 ({desc})")
            print(f"  期望系数: {expected_factor}, 实际系数: {factor}")
            print(f"  期望阶段: {expected_stage.value}, 实际阶段: {stage.value}")
            print("-" * 30)
            
            self.assertEqual(factor, expected_factor)
            self.assertEqual(stage, expected_stage)
    
    def test_calculate_daily_energy_requirement_normal_adult_dog(self):
        """测试正常成年狗的每日能量需求"""
        print("测试正常成年狗的每日能量需求")
        
        weight = 20.0
        age = 24
        activity_level = ActivityLevel.MODERATE_ACTIVE
        status = PhysiologicalStatus.INTACT
        
        result = self.calculator.calculate_daily_energy_requirement(
            weight_kg=weight,
            species=Species.DOG,
            age_months=age,
            activity_level=activity_level,
            physiological_status=status
        )
        
        expected_rer = 70 * (weight ** 0.75)
        life_stage_factor = 1.0  # 成犬
        activity_factor = 1.8    # 中等活动
        expected_der = expected_rer * life_stage_factor * activity_factor
        
        print(f"  输入参数:")
        print(f"    体重: {weight}kg")
        print(f"    年龄: {age}个月")
        print(f"    活动水平: {activity_level.value}")
        print(f"    生理状态: {status.value}")
        print(f"  计算过程:")
        print(f"    RER = 70 × {weight}^0.75 = {expected_rer:.1f} kcal")
        print(f"    生命阶段系数 = {life_stage_factor}")
        print(f"    活动系数 = {activity_factor}")
        print(f"    DER = {expected_rer:.1f} × {life_stage_factor} × {activity_factor} = {expected_der:.1f} kcal")
        print(f"  结果对比:")
        print(f"    期望RER: {expected_rer:.1f} kcal, 实际RER: {result['resting_energy_kcal']} kcal")
        print(f"    期望DER: {expected_der:.1f} kcal, 实际DER: {result['daily_energy_kcal']} kcal")
        print(f"    生命阶段: {result['life_stage']}")
        
        self.assertAlmostEqual(result["resting_energy_kcal"], expected_rer, places=1)
        self.assertAlmostEqual(result["daily_energy_kcal"], expected_der, places=1)
        self.assertEqual(result["life_stage"], LifeStage.DOG_ADULT.value)
    
    def test_calculate_daily_energy_requirement_puppy(self):
        """测试幼犬的每日能量需求"""
        print("测试幼犬的每日能量需求")
        
        weight = 3.0
        age = 3
        activity_level = ActivityLevel.MODERATE_ACTIVE
        status = PhysiologicalStatus.INTACT
        
        result = self.calculator.calculate_daily_energy_requirement(
            weight_kg=weight,
            species=Species.DOG,
            age_months=age,
            activity_level=activity_level,
            physiological_status=status
        )
        
        expected_rer = 70 * (weight ** 0.75)
        life_stage_factor = 3.0  # 幼犬0-4个月
        activity_factor = 1.8    # 中等活动
        expected_der = expected_rer * life_stage_factor * activity_factor
        
        print(f"  输入参数:")
        print(f"    体重: {weight}kg")
        print(f"    年龄: {age}个月 (幼犬)")
        print(f"    活动水平: {activity_level.value}")
        print(f"    生理状态: {status.value}")
        print(f"  计算过程:")
        print(f"    RER = 70 × {weight}^0.75 = {expected_rer:.1f} kcal")
        print(f"    生命阶段系数 = {life_stage_factor} (幼犬需要更多能量)")
        print(f"    活动系数 = {activity_factor}")
        print(f"    DER = {expected_rer:.1f} × {life_stage_factor} × {activity_factor} = {expected_der:.1f} kcal")
        print(f"  结果对比:")
        print(f"    期望RER: {expected_rer:.1f} kcal, 实际RER: {result['resting_energy_kcal']} kcal")
        print(f"    期望DER: {expected_der:.1f} kcal, 实际DER: {result['daily_energy_kcal']} kcal")
        print(f"    生命阶段: {result['life_stage']}")
        
        self.assertAlmostEqual(result["resting_energy_kcal"], expected_rer, places=1)
        self.assertAlmostEqual(result["daily_energy_kcal"], expected_der, places=1)
        self.assertEqual(result["life_stage"], LifeStage.DOG_PUPPY.value)
    
    def test_calculate_daily_energy_requirement_neutered(self):
        """测试绝育狗的每日能量需求"""
        print("测试绝育狗的每日能量需求")
        
        weight = 10.0
        age = 36
        activity_level = ActivityLevel.MODERATE_ACTIVE
        status = PhysiologicalStatus.NEUTERED
        
        result = self.calculator.calculate_daily_energy_requirement(
            weight_kg=weight,
            species=Species.DOG,
            age_months=age,
            activity_level=activity_level,
            physiological_status=status
        )
        
        expected_rer = 70 * (weight ** 0.75)
        life_stage_factor = 1.0
        base_activity_factor = 1.8
        adjusted_activity_factor = max(base_activity_factor - 0.2, 1.0)  # 绝育减少0.2
        expected_der = expected_rer * life_stage_factor * adjusted_activity_factor
        
        print(f"  输入参数:")
        print(f"    体重: {weight}kg")
        print(f"    年龄: {age}个月")
        print(f"    活动水平: {activity_level.value}")
        print(f"    生理状态: {status.value} (绝育)")
        print(f"  计算过程:")
        print(f"    RER = 70 × {weight}^0.75 = {expected_rer:.1f} kcal")
        print(f"    生命阶段系数 = {life_stage_factor}")
        print(f"    基础活动系数 = {base_activity_factor}")
        print(f"    绝育调整后活动系数 = max({base_activity_factor} - 0.2, 1.0) = {adjusted_activity_factor}")
        print(f"    DER = {expected_rer:.1f} × {life_stage_factor} × {adjusted_activity_factor} = {expected_der:.1f} kcal")
        print(f"  结果对比:")
        print(f"    实际DER: {result['daily_energy_kcal']} kcal")
        print(f"    期望DER: {expected_der:.1f} kcal")
        
        self.assertAlmostEqual(result["daily_energy_kcal"], expected_der, places=1)
    
    def test_calculate_daily_energy_requirement_pregnant(self):
        """测试怀孕狗的每日能量需求"""
        print("测试怀孕狗的每日能量需求")
        
        weight = 15.0
        age = 36
        activity_level = ActivityLevel.MODERATE_ACTIVE
        status = PhysiologicalStatus.PREGNANT
        
        result = self.calculator.calculate_daily_energy_requirement(
            weight_kg=weight,
            species=Species.DOG,
            age_months=age,
            activity_level=activity_level,
            physiological_status=status
        )
        
        expected_rer = 70 * (weight ** 0.75)
        # 新的怀孕期计算公式: (130/70) * RER + 26 * 体重
        expected_der = (130 / 70) * expected_rer + 26 * weight
        
        print(f"  输入参数:")
        print(f"    体重: {weight}kg")
        print(f"    年龄: {age}个月")
        print(f"    活动水平: {activity_level.value}")
        print(f"    生理状态: {status.value} (怀孕)")
        print(f"  计算过程:")
        print(f"    RER = 70 × {weight}^0.75 = {expected_rer:.1f} kcal")
        print(f"    怀孕期DER = (130/70) × RER + 26 × 体重")
        print(f"    DER = (130/70) × {expected_rer:.1f} + 26 × {weight} = {expected_der:.1f} kcal")
        print(f"  结果对比:")
        print(f"    实际DER: {result['daily_energy_kcal']} kcal")
        print(f"    期望DER: {expected_der:.1f} kcal")
        
        self.assertAlmostEqual(result["daily_energy_kcal"], expected_der, places=1)
    
    def test_calculate_daily_energy_requirement_lactating(self):
        """测试哺乳狗的每日能量需求"""
        print("测试哺乳狗的每日能量需求")
        
        test_cases = [
            (2, 3, 0.95, "第2周，3只幼犬"),
            (3, 4, 1.1, "第3周，4只幼犬"),
            (4, 2, 1.2, "第4周，2只幼犬"),
            (1, 1, 0.75, "第1周，1只幼犬")
        ]
        
        weight = 12.0
        age = 36
        activity_level = ActivityLevel.MODERATE_ACTIVE
        status = PhysiologicalStatus.LACTATING
        
        for week, count, lactation_factor, desc in test_cases:
            print(f"\n  测试场景: {desc}")
            
            result = self.calculator.calculate_daily_energy_requirement(
                weight_kg=weight,
                species=Species.DOG,
                age_months=age,
                activity_level=activity_level,
                physiological_status=status,
                lactation_week=week,
                nursing_count=count
            )
            
            expected_rer = 70 * (weight ** 0.75)
            # 新的哺乳期计算公式: (145/70) * RER + 体重 × 幼犬系数 × 哺乳系数
            if count <= 4:
                expected_der = (145 / 70) * expected_rer + weight * (24 * count) * lactation_factor
            else:
                expected_der = (145 / 70) * expected_rer + weight * (96 + 12 * (count - 4)) * lactation_factor
            
            print(f"    输入参数:")
            print(f"      体重: {weight}kg")
            print(f"      哺乳周数: {week}周")
            print(f"      幼犬数量: {count}只")
            print(f"      哺乳系数: {lactation_factor}")
            print(f"    计算过程:")
            print(f"      RER = 70 × {weight}^0.75 = {expected_rer:.1f} kcal")
            if count <= 4:
                print(f"      DER = (145/70) × RER + 体重 × (24 × 幼犬数) × 哺乳系数")
                print(f"      DER = (145/70) × {expected_rer:.1f} + {weight} × (24 × {count}) × {lactation_factor}")
            else:
                print(f"      DER = (145/70) × RER + 体重 × (96 + 12 × (幼犬数-4)) × 哺乳系数")
                print(f"      DER = (145/70) × {expected_rer:.1f} + {weight} × (96 + 12 × ({count}-4)) × {lactation_factor}")
            print(f"      DER = {expected_der:.1f} kcal")
            print(f"    结果对比:")
            print(f"      实际DER: {result['daily_energy_kcal']} kcal")
            print(f"      期望DER: {expected_der:.1f} kcal")
            
            self.assertAlmostEqual(result["daily_energy_kcal"], expected_der, places=1)
    
    def test_calculate_daily_energy_requirement_cat(self):
        """测试猫的每日能量需求"""
        print("测试猫的每日能量需求")
        
        # 成年猫
        print("\n  成年猫:")
        result = self.calculator.calculate_daily_energy_requirement(
            weight_kg=4.0,
            species=Species.CAT,
            age_months=24,
            activity_level=ActivityLevel.MODERATE_ACTIVE,
            physiological_status=PhysiologicalStatus.INTACT
        )
        
        expected_rer = 70 * (4.0 ** 0.75)
        expected_der = expected_rer * 1.0 * 1.8
        
        print(f"    DER = {expected_rer:.1f} × 1.0 × 1.8 = {expected_der:.1f} kcal")
        print(f"    实际DER: {result['daily_energy_kcal']} kcal")
        print(f"    生命阶段: {result['life_stage']}")
        
        self.assertAlmostEqual(result["daily_energy_kcal"], expected_der, places=1)
        self.assertEqual(result["life_stage"], LifeStage.CAT_ADULT.value)
        
        # 幼猫
        print("\n  幼猫:")
        result_kitten = self.calculator.calculate_daily_energy_requirement(
            weight_kg=1.5,
            species=Species.CAT,
            age_months=6,
            activity_level=ActivityLevel.HIGH_ACTIVE,
            physiological_status=PhysiologicalStatus.INTACT
        )
        
        expected_rer_kitten = 70 * (1.5 ** 0.75)
        expected_der_kitten = expected_rer_kitten * 2.5 * 2.0
        
        print(f"    DER = {expected_rer_kitten:.1f} × 2.5 × 2.0 = {expected_der_kitten:.1f} kcal")
        print(f"    实际DER: {result_kitten['daily_energy_kcal']} kcal")
        print(f"    生命阶段: {result_kitten['life_stage']}")
        
        self.assertAlmostEqual(result_kitten["daily_energy_kcal"], expected_der_kitten, places=1)
        self.assertEqual(result_kitten["life_stage"], LifeStage.CAT_KITTEN.value)
    
    def test_edge_cases_and_validation(self):
        """测试边界情况和输入验证"""
        print("测试边界情况和输入验证")
        
        # 测试负体重
        print("\n  测试负体重:")
        try:
            self.calculator.calculate_daily_energy_requirement(
                weight_kg=-1.0,
                species=Species.DOG,
                age_months=24,
                activity_level=ActivityLevel.MODERATE_ACTIVE,
                physiological_status=PhysiologicalStatus.INTACT
            )
            print("  负体重应该抛出异常但没有")
        except ValueError as e:
            print(f"  负体重正确抛出异常: {e}")
        
        # 测试零体重
        print("\n  测试零体重:")
        try:
            self.calculator.calculate_daily_energy_requirement(
                weight_kg=0.0,
                species=Species.DOG,
                age_months=24,
                activity_level=ActivityLevel.MODERATE_ACTIVE,
                physiological_status=PhysiologicalStatus.INTACT
            )
            print("  零体重应该抛出异常但没有")
        except ValueError as e:
            print(f"  零体重正确抛出异常: {e}")
        
        # 测试负年龄
        print("\n  测试负年龄:")
        try:
            self.calculator.calculate_daily_energy_requirement(
                weight_kg=10.0,
                species=Species.DOG,
                age_months=-1,
                activity_level=ActivityLevel.MODERATE_ACTIVE,
                physiological_status=PhysiologicalStatus.INTACT
            )
            print("  负年龄应该抛出异常但没有")
        except ValueError as e:
            print(f"  负年龄正确抛出异常: {e}")
        
        # 极小体重测试
        print("\n  测试极小体重 (0.5kg):")
        result = self.calculator.calculate_daily_energy_requirement(
            weight_kg=0.5,
            species=Species.CAT,
            age_months=2,
            activity_level=ActivityLevel.LOW_ACTIVE,
            physiological_status=PhysiologicalStatus.INTACT
        )
        print(f"    计算结果: {result['daily_energy_kcal']} kcal")
        self.assertGreater(result["daily_energy_kcal"], 0)
        
        # 极大体重测试
        print("\n  测试极大体重 (80kg):")
        result = self.calculator.calculate_daily_energy_requirement(
            weight_kg=80.0,
            species=Species.DOG,
            age_months=60,
            activity_level=ActivityLevel.HIGH_ACTIVE,
            physiological_status=PhysiologicalStatus.INTACT
        )
        print(f"    计算结果: {result['daily_energy_kcal']} kcal")
        self.assertGreater(result["daily_energy_kcal"], 0)
    
    def test_return_format(self):
        """测试返回值格式"""
        print("测试返回值格式")
        
        result = self.calculator.calculate_daily_energy_requirement(
            weight_kg=10.0,
            species=Species.DOG,
            age_months=24,
            activity_level=ActivityLevel.MODERATE_ACTIVE,
            physiological_status=PhysiologicalStatus.INTACT
        )
        
        print(f"  返回值: {result}")
        print(f"  包含的键: {list(result.keys())}")
        
        # 检查返回值包含所有必需的键
        required_keys = ["resting_energy_kcal", "daily_energy_kcal", "life_stage"]
        for key in required_keys:
            self.assertIn(key, result)
            print(f"  包含必需键: {key}")
        
        # 检查数值类型
        self.assertIsInstance(result["resting_energy_kcal"], (int, float))
        self.assertIsInstance(result["daily_energy_kcal"], (int, float))
        self.assertIsInstance(result["life_stage"], str)
        print("  数据类型正确")
        
        # 检查数值为正
        self.assertGreater(result["resting_energy_kcal"], 0)
        self.assertGreater(result["daily_energy_kcal"], 0)
        print("  能量值均为正数")

    def test_activity_factor_edge_case(self):
        """测试活动系数的极端情况"""
        print("测试活动系数的极端情况")
        
        # 测试老年绝育狗，确保活动系数不会低于1.0
        print("\n  测试老年绝育狗:")
        result = self.calculator.calculate_daily_energy_requirement(
            weight_kg=10.0,
            species=Species.DOG,
            age_months=96,  # 老年
            activity_level=ActivityLevel.SEDENTARY_ACTIVE,  # 最低活动水平1.4
            physiological_status=PhysiologicalStatus.NEUTERED  # 绝育
        )
        
        expected_rer = 70 * (10.0 ** 0.75)
        base_activity_factor = 1.4
        adjusted_activity_factor = max(base_activity_factor - 0.2, 1.0)  # 1.2
        expected_der = expected_rer * 1.0 * adjusted_activity_factor
        
        print(f"    输入: 老年(96个月) + 绝育 + 久坐活动水平")
        print(f"    基础活动系数: {base_activity_factor}")
        print(f"    调整后活动系数: max({base_activity_factor} - 0.2, 1.0) = {adjusted_activity_factor}")
        print(f"    期望DER: {expected_der:.1f} kcal")
        print(f"    实际DER: {result['daily_energy_kcal']} kcal")
        
        self.assertAlmostEqual(result["daily_energy_kcal"], expected_der, places=1)


if __name__ == '__main__':
    # 设置详细输出
    unittest.main(verbosity=2) 