"""
数据库功能检验脚本
逐步测试数据库创建、数据导入、查询等功能
"""

import os
import sys
import pandas as pd

# 添加 backend 目录到 Python 路径，使 app 模块可以被导入
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.db.database import Base, engine
from app.db.models import Base, Pet, Ingredient, IngredientCategory, IngredientNutrient, Nutrient, Species, ActivityLevel, PhysiologicalStatus
from app.services.energy_calculate import EnergyCalculator
from app.services.recipe_service import NutritionOptimizer
from app.db.databaseManager import SimplePetNutritionSystem
from app.db.nutrientStandard import AAFCO_STANDARDS, LifeStage, NutrientID

class DatabaseTester:
    """数据库功能测试器"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = None
        self.session = None
        self.system = None
    
    def run_all_tests(self, csv_file_path: str = None):
        """运行所有测试"""
        print("🧪 开始数据库功能检验")
        print("=" * 50)
    
        tests = [
            ("1. 数据库连接测试", self.test_database_connection),
            ("2. 表结构创建测试", self.test_table_creation), 
            ("3. 基础数据插入测试", self.test_basic_data_insertion),
            ("4. 数据导入测试", lambda: self.test_data_import(csv_file_path) if csv_file_path else self.skip_test("需要CSV文件")),
            ("5. 数据查询测试", self.test_data_queries),
            ("6. 宠物创建测试", self.test_pet_creation),
            ("7. 能量计算测试", self.test_energy_calculation),
            ("8. 数据完整性检查", self.test_data_integrity),
            ("9. 数据库性能测试", self.test_database_performance),
            ("10. 宠物AAFCO标准需求量转换测试", self.test_pet_aafco_requirements),
            ("11. 详细AAFCO需求对比分析", self.test_detailed_aafco_comparison)
        ]
    
        results = {}
        for test_name, test_func in tests:
            print(f"\n{test_name}")
            print("-" * 30)
            try:
                result = test_func()
                results[test_name] = "✅ PASS" if result else "❌ FAIL"
                print(f"结果: {results[test_name]}")
            except Exception as e:
                results[test_name] = f"❌ ERROR: {str(e)}"
                print(f"结果: {results[test_name]}")
        
        # 打印总结
        self.print_test_summary(results)
    
        return results
    
    def test_database_connection(self):
        """测试数据库连接"""
        try:
            self.engine = create_engine(self.database_url, echo=False)
            
            # 测试连接
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                assert result.fetchone()[0] == 1
            
            print("✅ 数据库连接成功")
            
            # 创建会话
            SessionLocal = sessionmaker(bind=self.engine)
            self.session = SessionLocal()
            
            print("✅ 数据库会话创建成功")
            return True
            
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            return False
    
    def test_table_creation(self):
        """测试表结构创建"""
        try:
            # 创建所有表
            Base.metadata.create_all(bind=self.engine)
            print("✅ 数据库表创建成功")
            
            # 检查表是否存在
            with self.engine.connect() as conn:
                tables = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)).fetchall()
            
            table_names = [table[0] for table in tables]
            expected_tables = ['ingredient_categories', 'ingredients', 'nutrients', 'ingredient_nutrients', 'pets']
            
            for table in expected_tables:
                if table in table_names:
                    print(f"✅ 表 {table} 创建成功")
                else:
                    print(f"❌ 表 {table} 未找到")
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ 表创建失败: {e}")
            return False
    
    def test_basic_data_insertion(self):
        """测试基础数据插入"""
        try:
            # 创建食物分类
            categories = [
                IngredientCategory(name="protein", min_percentage=40, max_percentage=70),
                IngredientCategory(name="vegetable", min_percentage=5, max_percentage=20),
                IngredientCategory(name="fat", min_percentage=2, max_percentage=8)
            ]
            
            for category in categories:
                if self.session.query(IngredientCategory).filter_by(name=category.name).first():
                    print(f"❌ 食物分类 {category.name} 已存在")
                    continue
                self.session.add(category)
            self.session.commit()
            print("✅ 食物分类插入成功")
            
            # 创建营养素 - 使用不冲突的ID
            nutrients = [
                Nutrient(nutrient_id=1001, name="Test Protein", unit_name="G"),
                Nutrient(nutrient_id=1002, name="Test Fat", unit_name="G"),
                Nutrient(nutrient_id=1007, name="Test Energy", unit_name="KCAL")
            ]
            
            for nutrient in nutrients:
                # 检查name和nutrient_id是否都不冲突
                existing_by_name = self.session.query(Nutrient).filter_by(name=nutrient.name).first()
                existing_by_id = self.session.query(Nutrient).filter_by(nutrient_id=nutrient.nutrient_id).first()
                
                if existing_by_name:
                    print(f"❌ 营养素名称 {nutrient.name} 已存在")
                    continue
                if existing_by_id:
                    print(f"❌ 营养素ID {nutrient.nutrient_id} 已存在")
                    continue
                    
                self.session.add(nutrient)
            self.session.commit()
            print("✅ 营养素插入成功")
            
            # 创建测试食物
            protein_category = self.session.query(IngredientCategory).filter_by(name="protein").first()
            test_food = Ingredient(
                fdc_id=999999,
                description="Test Chicken Breast",
                food_category_id=protein_category.id,
                energy_kcal_100g=165,
                protein_g_100g=25.0,
                fat_g_100g=3.6,
                carb_g_100g=0.0,
                cost_per_100g=5.0
            )

            if self.session.query(Ingredient).filter_by(fdc_id=999999).first():
                print(f"❌ 食物 {test_food.description} 已存在")
            else:
                self.session.add(test_food)
                self.session.commit()
                print("✅ 测试食物插入成功")
            
            # 创建营养素含量数据
            food_nutrients = [
                IngredientNutrient(fdc_id=999999, nutrient_id=1001, amount=25.0),  # Test Protein
                IngredientNutrient(fdc_id=999999, nutrient_id=1002, amount=3.6),   # Test Fat
                IngredientNutrient(fdc_id=999999, nutrient_id=1007, amount=165.0)  # Test Energy
            ]
            
            for fn in food_nutrients:
                if self.session.query(IngredientNutrient).filter_by(fdc_id=999999, nutrient_id=fn.nutrient_id).first():
                    print(f"❌ 营养素含量数据 {fn.nutrient_id} 已存在")
                    continue
                self.session.add(fn)
            self.session.commit()
            print("✅ 营养素含量数据插入成功")    
            
            return True
            
        except Exception as e:
            print(f"❌ 基础数据插入失败: {e}")
            self.session.rollback()
            return False

    def test_data_import(self, csv_file_path: str):
        """测试USDA数据导入"""
        if not csv_file_path or not os.path.exists(csv_file_path):
            print("❌ CSV文件不存在或路径错误")
            return False
        
        try:
            # 检查CSV文件结构
            print(f"✅ 开始检查CSV文件结构: {csv_file_path}")
            df = pd.read_csv(csv_file_path)
            required_columns = ['fdc_id', 'description', 'food_category_label', 
                              'nutrient_id', 'name', 'amount', 'unit_name']
            
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                print(f"❌ CSV文件缺少必要列: {missing_columns}")
                return False
            
            print(f"✅ CSV文件结构正确，包含 {len(df)} 条记录")
            
            # 创建系统并导入数据
            self.system = SimplePetNutritionSystem(self.database_url)
            
            print("开始导入USDA数据...")
            self.system.import_usda_data(csv_file_path)
            print("✅ USDA数据导入成功")
            
            return True
            
        except Exception as e:
            print(f"❌ 数据导入失败: {e}")
            return False

    def test_data_queries(self):
        """测试数据查询功能"""
        try:
            # 查询食物分类数量
            category_count = self.session.query(IngredientCategory).count()
            print(f"✅ 食物分类数量: {category_count}")
            
            # 查询食物数量
            food_count = self.session.query(Ingredient).count()
            print(f"✅ 食物数量: {food_count}")
            
            # 查询营养素数量
            nutrient_count = self.session.query(Nutrient).count()
            print(f"✅ 营养素数量: {nutrient_count}")
            
            # 查询营养含量数据数量
            food_nutrient_count = self.session.query(IngredientNutrient).count()
            print(f"✅ 营养含量数据数量: {food_nutrient_count}")
            
            # 测试复杂查询：查找蛋白质含量最高的食物
            if food_count > 0:
                high_protein_food = self.session.query(Ingredient).filter(
                    Ingredient.protein_g_100g.isnot(None)
                ).order_by(Ingredient.protein_g_100g.desc()).first()
                
                if high_protein_food:
                    print(f"✅ 蛋白质含量最高的食物: {high_protein_food.description} ({high_protein_food.protein_g_100g}g/100g)")
                else:
                    print("⚠️ 未找到含蛋白质信息的食物")
                    
                    # 诊断：检查是否有Protein营养素
                    protein_nutrient = self.session.query(Nutrient).filter(Nutrient.name == 'Protein').first()
                    if protein_nutrient:
                        print(f"🔍 找到Protein营养素: ID={protein_nutrient.nutrient_id}")
                        
                        # 检查是否有食物含有Protein数据
                        protein_count = self.session.query(IngredientNutrient).filter(
                            IngredientNutrient.nutrient_id == protein_nutrient.nutrient_id
                        ).count()
                        print(f"🔍 含Protein数据的记录数: {protein_count}")
                        
                        # 检查一个具体例子
                        example = self.session.query(IngredientNutrient, Ingredient).join(Ingredient).filter(
                            IngredientNutrient.nutrient_id == protein_nutrient.nutrient_id
                        ).first()
                        
                        if example:
                            nut_data, food = example
                            print(f"🔍 示例: {food.description} 蛋白质={nut_data.amount}g/100g")
                            print(f"🔍 但该食物的protein_g_100g字段值为: {food.protein_g_100g}")
                        
                    else:
                        print("❌ 数据库中未找到名为'Protein'的营养素")
                        
                        # 查找所有包含protein的营养素
                        protein_like = self.session.query(Nutrient).filter(
                            Nutrient.name.ilike('%protein%')
                        ).all()
                        
                        if protein_like:
                            print("🔍 包含'protein'的营养素:")
                            for n in protein_like[:5]:
                                print(f"   - ID:{n.nutrient_id}, 名称:'{n.name}'")
                        else:
                            print("❌ 未找到任何包含'protein'的营养素")
            
            # 测试JOIN查询：查找蛋白质类食物
            protein_foods = self.session.query(Ingredient).join(IngredientCategory).filter(
                IngredientCategory.name == "protein"
            ).limit(3).all()
            
            print(f"✅ 蛋白质类食物示例:")
            for food in protein_foods:
                print(f"   - {food.description}")
            
            return True
            
        except Exception as e:
            print(f"❌ 数据查询失败: {e}")
            return False
    
    def test_pet_creation(self):
        """测试宠物创建功能"""
        try:
            if not self.system:
                self.system = SimplePetNutritionSystem(self.database_url)
            
            # 创建测试宠物
            test_pets = [
                {
                    "name": "测试狗狗",
                    "species": "dog",
                    "age_months": 36,
                    "weight_kg": 25.0,
                    "activity_level": "moderate_active",
                    "physiological_status": "neutered"
                },
                {
                    "name": "测试猫咪",
                    "species": "cat",
                    "age_months": 24,
                    "weight_kg": 4.0,
                    "activity_level": "low_active",
                    "physiological_status": "pregnant"
                }
            ]
            
            created_pets = []
            for pet_data in test_pets:
                try:
                    pet_id = self.system.create_pet(pet_data)
                    created_pets.append(pet_id)
                    print(f"✅ 创建宠物 '{pet_data['name']}' 成功，ID: {pet_id}")
                except Exception as e:
                    print(f"❌ 创建宠物 '{pet_data['name']}' 失败: {e}")
                    return False
            
            # 验证宠物数据
            for pet_id in created_pets:
                pet = self.session.query(Pet).filter_by(id=pet_id).first()
                if pet:
                    print(f"✅ 宠物 {pet.name} 验证成功")
                    print(f"   生命阶段: {pet.physiological_status}")
                    print(f"   日能量需求: {pet.daily_calories_kcal} kcal")
                else:
                    print(f"❌ 宠物ID {pet_id} 验证失败")
                    return False
            
            return True
            
        except Exception as e:
            print(f"❌ 宠物创建测试失败: {e}")
            return False
    
    def test_energy_calculation(self):
        """测试能量计算功能"""
        try:
            # 测试不同类型宠物的能量计算
            test_cases = [
                {
                    "name": "成年中型犬(已绝育)",
                    "weight_kg": 20.0,
                    "species": Species.DOG,
                    "age_months": 36,
                    "activity_level": ActivityLevel.MODERATE_ACTIVE,
                    "physiological_status": PhysiologicalStatus.NEUTERED,
                    "expected_range": (900, 1400)
                },
                {
                    "name": "怀孕期母猫",
                    "weight_kg": 4.0,
                    "species": Species.CAT,
                    "age_months": 24,
                    "activity_level": ActivityLevel.LOW_ACTIVE,
                    "physiological_status": PhysiologicalStatus.PREGNANT,
                    "expected_range": (500, 900)
                },
                {
                    "name": "活跃幼犬",
                    "weight_kg": 8.0,
                    "species": Species.DOG,
                    "age_months": 6,
                    "activity_level": ActivityLevel.HIGH_ACTIVE,
                    "physiological_status": PhysiologicalStatus.INTACT,
                    "expected_range": (1000, 1800)
                }
            ]
            
            for case in test_cases:
                energy_info = EnergyCalculator.calculate_daily_energy_requirement(
                    weight_kg=case["weight_kg"],
                    species=case["species"],
                    age_months=case["age_months"],
                    activity_level=case["activity_level"],
                    physiological_status=case["physiological_status"]
                )
                
                daily_energy = energy_info["daily_energy_kcal"]
                expected_min, expected_max = case["expected_range"]
                 
                if expected_min <= daily_energy <= expected_max:
                    print(f"✅ {case['name']}: {daily_energy} kcal/天 (合理范围)")
                else:
                    print(f"⚠️ {case['name']}: {daily_energy} kcal/天 (超出预期范围 {expected_min}-{expected_max})")
                
                print(f"   详细信息: RER={energy_info['resting_energy_kcal']}, "
                      f"每日所需能量={energy_info['daily_energy_kcal']}, "
                      f"生命阶段={energy_info['life_stage']}")
            
            return True
            
        except Exception as e:
            print(f"❌ 能量计算测试失败: {e}")
            return False
    
    def test_data_integrity(self):
        """测试数据完整性"""
        try:
            # 检查孤立的营养数据（没有对应食物的营养数据）
            orphaned_nutrients = self.session.query(IngredientNutrient).outerjoin(Ingredient).filter(
                Ingredient.fdc_id.is_(None)
            ).count()
            
            if orphaned_nutrients > 0:
                print(f"⚠️ 发现 {orphaned_nutrients} 条孤立的营养数据")
            else:
                print("✅ 营养数据完整性检查通过")
            
            # 检查没有营养数据的食物
            foods_without_nutrition = self.session.query(Ingredient).outerjoin(IngredientNutrient).filter(
                IngredientNutrient.fdc_id.is_(None)
            ).count()
            
            if foods_without_nutrition > 0:
                print(f"⚠️ 发现 {foods_without_nutrition} 种没有营养数据的食物")
            else:
                print("✅ 食物营养数据完整性检查通过")
            
            # 检查基础营养信息是否更新
            foods_with_energy = self.session.query(Ingredient).filter(
                Ingredient.energy_kcal_100g.isnot(None)
            ).count()
            
            total_foods = self.session.query(Ingredient).count()
            
            if total_foods > 0:
                energy_coverage = foods_with_energy / total_foods * 100
                print(f"✅ 食物能量信息覆盖率: {energy_coverage:.1f}%")
                
                if energy_coverage < 80:
                    print("⚠️ 能量信息覆盖率较低，可能影响配方生成")
            
            return True
            
        except Exception as e:
            print(f"❌ 数据完整性检查失败: {e}")
            return False
    
    def test_database_performance(self):
        """测试数据库性能"""
        try:
            import time
            
            # 测试复杂查询性能
            start_time = time.time()
            
            # 查询：获取所有蛋白质类食物及其营养信息
            result = self.session.query(Ingredient).join(IngredientCategory).join(IngredientNutrient).join(Nutrient).filter(
                IngredientCategory.name == "protein",
                Nutrient.name == "Protein"
            ).limit(10).all()
            
            query_time = time.time() - start_time
            
            print(f"✅ 复杂查询性能: {query_time:.3f}秒 (查询{len(result)}条记录)")
            
            if query_time > 1.0:
                print("⚠️ 查询速度较慢，建议添加数据库索引")
            
            # 测试批量插入性能（如果数据量大）
            food_count = self.session.query(Ingredient).count()
            nutrient_count = self.session.query(Nutrient).count()
            
            print(f"✅ 数据库规模: {food_count}种食物, {nutrient_count}种营养素")
            
            if food_count > 100 and query_time < 0.1:
                print("✅ 数据库性能良好")
            elif food_count > 100:
                print("⚠️ 数据库性能需要优化")
            
            return True
            
        except Exception as e:
            print(f"❌ 性能测试失败: {e}")
            return False
    
    def test_pet_aafco_requirements(self):
        """测试宠物AAFCO标准需求量转换"""
        try:
            if not self.system:
                self.system = SimplePetNutritionSystem(self.database_url)
            
            # 创建营养优化器实例用于测试
            optimizer = NutritionOptimizer(self.session)
            
            # 测试不同类型的宠物
            test_pets = [
                {
                    "name": "测试成年犬",
                    "species": "dog",
                    "age_months": 36,
                    "weight_kg": 20.0,
                    "activity_level": "moderate_active",
                    "physiological_status": "neutered",
                    "expected_aafco": LifeStage.DOG_ADULT
                },
                {
                    "name": "测试幼犬",
                    "species": "dog", 
                    "age_months": 6,
                    "weight_kg": 8.0,
                    "activity_level": "high_active",
                    "physiological_status": "intact",
                    "expected_aafco": LifeStage.DOG_PUPPY
                }
                # 注意：暂时跳过猫的测试，因为AAFCO_STANDARDS中还没有猫的标准
                # {
                #     "name": "测试成年猫",
                #     "species": "cat",
                #     "age_months": 24,
                #     "weight_kg": 4.5,
                #     "activity_level": "low_active", 
                #     "physiological_status": "neutered",
                #     "expected_aafco": LifeStage.CAT_ADULT
                # }
            ]
            
            for pet_data in test_pets:
                print(f"\n🔍 测试宠物: {pet_data['name']}")
                
                # 创建宠物
                pet_id = self.system.create_pet(pet_data)
                pet = self.session.query(Pet).filter_by(id=pet_id).first()
                
                # 获取宠物的每日能量需求
                daily_energy = pet.daily_calories_kcal
                print(f"   每日能量需求: {daily_energy} kcal")
                
                # 确定AAFCO标准
                if pet.species == "dog" and pet.age_months <= 12:
                    aafco_key = LifeStage.DOG_PUPPY
                elif pet.species == "dog" and pet.age_months > 12:
                    aafco_key = LifeStage.DOG_ADULT
                elif pet.species == "cat" and pet.age_months <= 12:
                    aafco_key = LifeStage.CAT_KITTEN
                elif pet.species == "cat" and pet.age_months > 12:
                    aafco_key = LifeStage.CAT_ADULT
                
                # 检查AAFCO标准是否存在
                if aafco_key not in AAFCO_STANDARDS:
                    print(f"   ⚠️ 跳过测试：{aafco_key.value} 的AAFCO标准尚未定义")
                    continue
                
                assert aafco_key == pet_data["expected_aafco"], f"AAFCO标准选择错误: 期望{pet_data['expected_aafco']}, 实际{aafco_key}"
                print(f"   使用AAFCO标准: {aafco_key.value}")
                
                # 获取AAFCO标准
                standards = AAFCO_STANDARDS[aafco_key]
                
                # 测试关键营养素需求转换
                key_nutrients = [
                    ("Protein", NutrientID.PROTEIN),
                    ("Total lipid (fat)", NutrientID.FAT),
                    ("Calcium, Ca", NutrientID.CALCIUM),
                    ("Phosphorus, P", NutrientID.PHOSPHORUS)
                ]
                
                print(f"   转换后的营养需求:")
                for nutrient_name, nutrient_id in key_nutrients:
                    if nutrient_id in standards:
                        standard = standards[nutrient_id]
                        
                        # 测试最小值转换
                        min_required = optimizer._calculate_nutrient_requirement(
                            standard, 400.0, nutrient_id, "min", daily_energy
                        )
                        
                        # 测试最大值转换（如果存在）
                        max_allowed = optimizer._calculate_nutrient_requirement(
                            standard, 400.0, nutrient_id, "max", daily_energy
                        )
                        
                        if min_required is not None:
                            print(f"     {nutrient_name}: 最小需求 {min_required:.2f}")
                            
                            # 验证计算逻辑：检查是否基于每1000kcal标准正确转换
                            aafco_min_per_1000kcal = standard.get("min")
                            if aafco_min_per_1000kcal:
                                expected_min = aafco_min_per_1000kcal * daily_energy / 1000
                                tolerance = abs(expected_min * 0.01)  # 1%容差
                                
                                if abs(min_required - expected_min) <= tolerance:
                                    print(f"       ✅ 最小值转换正确")
                                else:
                                    print(f"       ❌ 最小值转换错误: 期望{expected_min:.2f}, 实际{min_required:.2f}")
                                    return False
                        
                        if max_allowed is not None:
                            print(f"     {nutrient_name}: 最大允许 {max_allowed:.2f}")
                            
                            # 验证最大值转换
                            aafco_max_per_1000kcal = standard.get("max")
                            if aafco_max_per_1000kcal:
                                expected_max = aafco_max_per_1000kcal * daily_energy / 1000
                                tolerance = abs(expected_max * 0.01)
                                
                                if abs(max_allowed - expected_max) <= tolerance:
                                    print(f"       ✅ 最大值转换正确")
                                else:
                                    print(f"       ❌ 最大值转换错误: 期望{expected_max:.2f}, 实际{max_allowed:.2f}")
                                    return False
                    else:
                        print(f"     {nutrient_name}: 无AAFCO标准")
                
                print(f"   ✅ {pet_data['name']} AAFCO需求转换验证通过")
            
            return True
            
        except Exception as e:
            print(f"❌ 宠物AAFCO需求转换测试失败: {e}")
            return False
    
    def test_detailed_aafco_comparison(self):
        """详细AAFCO需求对比分析"""
        try:
            if not self.system:
                self.system = SimplePetNutritionSystem(self.database_url)
            
            optimizer = NutritionOptimizer(self.session)
            
            # 创建一个标准测试宠物
            test_pet_data = {
                "name": "标准测试犬",
                "species": "dog",
                "age_months": 36,
                "weight_kg": 15.0,
                "activity_level": "moderate_active", 
                "physiological_status": "neutered"
            }
            
            pet_id = self.system.create_pet(test_pet_data)
            pet = self.session.query(Pet).filter_by(id=pet_id).first()
            
            print(f"\n📊 详细AAFCO需求分析 - {pet.name}")
            print(f"体重: {pet.weight_kg}kg, 年龄: {pet.age_months}个月")
            print(f"每日能量需求: {pet.daily_calories_kcal} kcal")
            print(f"生理状态: {pet.physiological_status}")
            
            # 使用成年犬标准
            aafco_key = LifeStage.DOG_ADULT
            standards = AAFCO_STANDARDS[aafco_key]
            
            print(f"\n使用AAFCO标准: {aafco_key.value}")
            print("-" * 60)
            print(f"{'营养素':<20} {'AAFCO/1000kcal':<15} {'实际需求':<15} {'单位':<10}")
            print("-" * 60)
            
            # 分析所有营养素需求
            nutrient_mapping = {
                NutrientID.PROTEIN: "Protein",
                NutrientID.FAT: "Total lipid (fat)",
                NutrientID.CALCIUM: "Calcium, Ca", 
                NutrientID.PHOSPHORUS: "Phosphorus, P",
                NutrientID.POTASSIUM: "Potassium, K",
                NutrientID.SODIUM: "Sodium, Na",
                NutrientID.MAGNESIUM: "Magnesium, Mg",
                NutrientID.IRON: "Iron, Fe",
                NutrientID.ZINC: "Zinc, Zn",
                NutrientID.COPPER: "Copper, Cu"
            }
            
            conversion_success_count = 0
            total_nutrients = 0
            
            for nutrient_id, nutrient_name in nutrient_mapping.items():
                if nutrient_id in standards:
                    total_nutrients += 1
                    standard = standards[nutrient_id]
                    
                    # 计算实际需求
                    min_required = optimizer._calculate_nutrient_requirement(
                        standard, 400.0, nutrient_id, "min", pet.daily_calories_kcal
                    )
                    
                    max_allowed = optimizer._calculate_nutrient_requirement(
                        standard, 400.0, nutrient_id, "max", pet.daily_calories_kcal
                    )
                    
                    aafco_min = standard.get("min", "N/A")
                    aafco_max = standard.get("max", "N/A")
                    unit = standard.get("unit", "")
                    
                    # 格式化输出
                    aafco_range = f"{aafco_min}"
                    if aafco_max and aafco_max != "N/A":
                        aafco_range += f"-{aafco_max}"
                    
                    actual_range = f"{min_required:.2f}" if min_required else "N/A"
                    if max_allowed:
                        actual_range += f"-{max_allowed:.2f}"
                    
                    print(f"{nutrient_name:<20} {aafco_range:<15} {actual_range:<15} {unit:<10}")
                    
                    if min_required is not None:
                        conversion_success_count += 1
                        
                        # 检查转换的合理性
                        if aafco_min != "N/A":
                            # 验证转换是否合理（基于宠物的能量需求）
                            expected_proportion = pet.daily_calories_kcal / 1000.0
                            if 0.5 <= expected_proportion <= 3.0:  # 合理的能量需求范围
                                print(f"  ✅ 转换比例合理: {expected_proportion:.2f}")
                            else:
                                print(f"  ⚠️ 转换比例异常: {expected_proportion:.2f}")
            
            conversion_rate = conversion_success_count / total_nutrients * 100 if total_nutrients > 0 else 0
            print("-" * 60)
            print(f"营养素转换成功率: {conversion_rate:.1f}% ({conversion_success_count}/{total_nutrients})")
            
            # 验证能量需求的合理性
            expected_daily_energy_range = (800, 1500)  # 15kg中型犬的合理能量范围
            if expected_daily_energy_range[0] <= pet.daily_calories_kcal <= expected_daily_energy_range[1]:
                print("✅ 宠物能量需求在合理范围内")
            else:
                print(f"⚠️ 宠物能量需求可能异常: {pet.daily_calories_kcal} kcal")
            
            # 检查关键营养素比例是否符合AAFCO建议
            if conversion_success_count >= total_nutrients * 0.8:  # 80%转换成功
                print("✅ AAFCO标准转换功能正常")
                return True
            else:
                print("❌ AAFCO标准转换存在问题")
                return False
            
        except Exception as e:
            print(f"❌ 详细AAFCO对比分析失败: {e}")
            return False
    
    def skip_test(self, reason: str):
        """跳过测试"""
        print(f"⏭️ 测试跳过: {reason}")
        return True
    
    def print_test_summary(self, results: dict):
        """打印测试总结"""
        print("\n" + "=" * 50)
        print("🧪 数据库功能检验总结")
        print("=" * 50)
        
        passed = sum(1 for result in results.values() if result.startswith("✅"))
        failed = sum(1 for result in results.values() if result.startswith("❌"))
        total = len(results)
        
        for test_name, result in results.items():
            print(f"{test_name}: {result}")
        
        print(f"\n📊 总结: {passed}/{total} 项测试通过")
        
        if passed == total:
            print("🎉 所有测试通过！数据库功能正常")
        elif passed >= total * 0.8:
            print("⚠️ 大部分测试通过，有少量问题需要关注")
        else:
            print("❌ 多项测试失败，需要检查系统配置")
    
    def reset_database(self):
        """重置数据库"""
        try:
            if not self.engine:
                self.engine = create_engine(self.database_url, echo=False)
            
            print("正在删除现有表...")
            Base.metadata.drop_all(bind=self.engine)
            print("正在创建新表...")
            Base.metadata.create_all(bind=self.engine)
            print("✅ 数据库重置完成！")
            return True
        except Exception as e:
            print(f"❌ 数据库重置失败: {e}")
            return False

    def cleanup(self):
        """清理资源"""
        if self.session:
            self.session.close()
        if self.engine:
            self.engine.dispose()

def main():
    """主函数"""
    print("🗃️ 数据库功能检验工具")
    print("请确保已经:")
    print("1. 安装了PostgreSQL")
    print("2. 创建了数据库")
    print("3. 准备了USDA CSV文件")
    print()
    
    # 数据库配置
    database_url = input("请输入数据库URL (默认: postgresql://postgres:1997@localhost:5433/pet_diet_db): ").strip()
    if not database_url:
        database_url = "postgresql://postgres:1997@localhost:5433/pet_diet_db"
    
    # CSV文件路径（可选）
    csv_path = input("请输入CSV文件路径 (可选，按回车跳过，默认：D:/Programs/AI_pet_fresh_diet/backend/data/food_data.csv): ").strip()
    if not csv_path:
        csv_path = "D:/Programs/AI_pet_fresh_diet/backend/data/food_data.csv"
        
    if csv_path and not os.path.exists(csv_path):
        print(f"⚠️ 文件 {csv_path} 不存在，将跳过数据导入测试")
        csv_path = None
    
    # 运行测试
    tester = DatabaseTester(database_url)
    
    try:
        tester.reset_database()
        results = tester.run_all_tests(csv_path)
        return results
    finally:
        tester.cleanup()

if __name__ == "__main__":
    main()