#!/usr/bin/env python3
"""
能量计算器测试运行脚本
提供不同的运行选项：单元测试、演示程序、交互式测试
"""

import os
import sys
import subprocess
import argparse

def run_unit_tests():
    """运行单元测试"""
    print("运行能量计算器单元测试...")
    try:
        # 设置环境变量确保UTF-8编码
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        result = subprocess.run([
            sys.executable, "-m", "unittest", 
            "app.test.test_energy_calculator", 
            "-v"
        ], cwd=os.path.dirname(__file__), 
           capture_output=True, 
           text=True, 
           encoding='utf-8',
           errors='replace',
           env=env)
        
        print(result.stdout)
        if result.stderr:
            print("错误信息:")
            print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"运行测试时出错: {e}")
        return False

def run_demo():
    """运行演示程序"""
    print("运行能量计算器演示程序...")
    try:
        # 设置环境变量确保UTF-8编码
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        result = subprocess.run([
            sys.executable, "app/test/demo_energy_calculator.py"
        ], cwd=os.path.dirname(__file__), encoding='utf-8', env=env)
        
        return result.returncode == 0
    except Exception as e:
        print(f"运行演示时出错: {e}")
        return False

def run_simple_test():
    """运行简单测试"""
    print("运行简单功能测试...")
    
    # 添加路径
    sys.path.append(os.path.dirname(__file__))
    
    try:
        from app.services.energy_calculate import EnergyCalculator
        from app.db.models import ActivityLevel, PhysiologicalStatus, Species, LifeStage
        
        calculator = EnergyCalculator()
        
        print("\n快速测试结果:")
        print("-" * 50)
        
        # 测试几个常见案例
        test_cases = [
            ("小型犬", 5.0, Species.DOG, 24, ActivityLevel.MODERATE_ACTIVE, PhysiologicalStatus.INTACT),
            ("中型犬", 15.0, Species.DOG, 36, ActivityLevel.HIGH_ACTIVE, PhysiologicalStatus.INTACT),
            ("大型犬", 30.0, Species.DOG, 48, ActivityLevel.MODERATE_ACTIVE, PhysiologicalStatus.NEUTERED),
            ("成年猫", 4.0, Species.CAT, 24, ActivityLevel.MODERATE_ACTIVE, PhysiologicalStatus.INTACT),
        ]
        
        for desc, weight, species, age, activity, status in test_cases:
            result = calculator.calculate_daily_energy_requirement(
                weight_kg=weight,
                species=species,
                age_months=age,
                activity_level=activity,
                physiological_status=status
            )
            
            print(f"{desc:<8} ({weight:4.1f}kg): RER={result['resting_energy_kcal']:6.1f}, DER={result['daily_energy_kcal']:6.1f} kcal/day")
        
        print("-" * 50)
        print("简单测试完成，所有计算正常!")
        return True
        
    except Exception as e:
        print(f"简单测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def interactive_test():
    """交互式测试"""
    print("交互式能量计算器测试")
    print("你可以输入宠物参数来计算能量需求")
    
    # 添加路径
    sys.path.append(os.path.dirname(__file__))
    
    try:
        from app.services.energy_calculate import EnergyCalculator
        from app.db.models import ActivityLevel, PhysiologicalStatus, Species, LifeStage
        
        calculator = EnergyCalculator()
        
        while True:
            print("\n" + "="*50)
            print("请输入宠物信息 (输入 'quit' 退出):")
            
            # 获取物种
            species_input = input("物种 (dog/cat): ").strip().lower()
            if species_input == 'quit':
                break
            
            if species_input == 'dog':
                species = Species.DOG
            elif species_input == 'cat':
                species = Species.CAT
            else:
                print("请输入 'dog' 或 'cat'")
                continue
            
            # 获取体重
            try:
                weight = float(input("体重 (kg): "))
                if weight <= 0:
                    print("体重必须大于0")
                    continue
            except ValueError:
                print("请输入有效的数字")
                continue
            
            # 获取年龄
            try:
                age = int(input("年龄 (月): "))
                if age < 0:
                    print("年龄不能为负数")
                    continue
            except ValueError:
                print("请输入有效的整数")
                continue
            
            # 获取活动水平
            print("活动水平:")
            print("1 - 久坐 (sedentary)")
            print("2 - 低活动 (low)")
            print("3 - 中等活动 (moderate)")
            print("4 - 高活动 (high)")
            print("5 - 极高活动 (extreme)")
            
            try:
                activity_choice = int(input("选择活动水平 (1-5): "))
                activity_map = {
                    1: ActivityLevel.SEDENTARY_ACTIVE,
                    2: ActivityLevel.LOW_ACTIVE,
                    3: ActivityLevel.MODERATE_ACTIVE,
                    4: ActivityLevel.HIGH_ACTIVE,
                    5: ActivityLevel.EXTREME_ACTIVE
                }
                if activity_choice not in activity_map:
                    print("请选择1-5之间的数字")
                    continue
                activity = activity_map[activity_choice]
            except ValueError:
                print("请输入有效的数字")
                continue
            
            # 获取生理状态
            print("生理状态:")
            print("1 - 正常 (intact)")
            print("2 - 绝育 (neutered)")
            print("3 - 怀孕 (pregnant)")
            print("4 - 哺乳 (lactating)")
            
            try:
                status_choice = int(input("选择生理状态 (1-4): "))
                status_map = {
                    1: PhysiologicalStatus.INTACT,
                    2: PhysiologicalStatus.NEUTERED,
                    3: PhysiologicalStatus.PREGNANT,
                    4: PhysiologicalStatus.LACTATING
                }
                if status_choice not in status_map:
                    print("请选择1-4之间的数字")
                    continue
                status = status_map[status_choice]
            except ValueError:
                print("请输入有效的数字")
                continue
            
            # 如果是哺乳期，获取额外参数
            lactation_week = 4
            nursing_count = 1
            if status == PhysiologicalStatus.LACTATING:
                try:
                    lactation_week = int(input("哺乳周数 (1-4, 默认4): ") or "4")
                    nursing_count = int(input("幼崽数量 (默认1): ") or "1")
                except ValueError:
                    print("使用默认值：哺乳4周，1只幼崽")
            
            # 计算结果
            try:
                result = calculator.calculate_daily_energy_requirement(
                    weight_kg=weight,
                    species=species,
                    age_months=age,
                    activity_level=activity,
                    physiological_status=status,
                    lactation_week=lactation_week,
                    nursing_count=nursing_count
                )
                
                print(f"\n计算结果:")
                print(f"静息能量需求 (RER): {result['resting_energy_kcal']} kcal/day")
                print(f"每日能量需求 (DER): {result['daily_energy_kcal']} kcal/day")
                print(f"每公斤需求: {result['daily_energy_kcal']/weight:.1f} kcal/kg/day")
                print(f"生命阶段: {result['life_stage']}")
                
            except Exception as e:
                print(f"计算出错: {e}")
        
        print("\n感谢使用交互式测试!")
        return True
        
    except Exception as e:
        print(f"交互式测试启动失败: {e}")
        return False

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="能量计算器测试工具")
    parser.add_argument('mode', nargs='?', default='menu', 
                       choices=['test', 'demo', 'simple', 'interactive', 'menu'],
                       help='运行模式: test(单元测试), demo(演示), simple(简单测试), interactive(交互式), menu(显示菜单)')
    
    args = parser.parse_args()
    
    if args.mode == 'menu':
        print("能量计算器测试工具")
        print("="*40)
        print("请选择运行模式:")
        print("1. 单元测试 (test)")
        print("2. 演示程序 (demo)")
        print("3. 简单测试 (simple)")
        print("4. 交互式测试 (interactive)")
        print("5. 退出")
        
        while True:
            choice = input("\n请选择 (1-5): ").strip()
            if choice == '1':
                run_unit_tests()
                break
            elif choice == '2':
                run_demo()
                break
            elif choice == '3':
                run_simple_test()
                break
            elif choice == '4':
                interactive_test()
                break
            elif choice == '5':
                print("再见!")
                break
            else:
                print("请选择1-5之间的数字")
    
    elif args.mode == 'test':
        success = run_unit_tests()
        sys.exit(0 if success else 1)
    
    elif args.mode == 'demo':
        success = run_demo()
        sys.exit(0 if success else 1)
    
    elif args.mode == 'simple':
        success = run_simple_test()
        sys.exit(0 if success else 1)
    
    elif args.mode == 'interactive':
        success = interactive_test()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 