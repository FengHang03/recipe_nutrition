import os
import sys

# 添加 backend 目录到 Python 路径，使 app 模块可以被导入
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))    

from app.db.models import Base
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.dialects.postgresql import JSON
import pandas as pd
import logging
import numpy as np
from datetime import datetime

from app.db.models import Ingredient, Nutrient, IngredientNutrient, Pet, IngredientCategory, Species, ActivityLevel, PhysiologicalStatus
from app.db.nutrientStandard import NutrientID
from app.services.recipe_service import NutritionOptimizer
from app.services.energy_calculate import EnergyCalculator

logger = logging.getLogger(__name__)

class SimplePetNutritionSystem:
    """简化版宠物营养系统"""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)

    def create_pet(self, pet_data: dict) -> int:
        """创建宠物记录"""
        session = self.SessionLocal()
        
        try:
            # 计算生命阶段和能量需求
            species = Species(pet_data["species"])
            activity_level = ActivityLevel(pet_data["activity_level"])
            physio_status = PhysiologicalStatus(pet_data["physiological_status"])
            
            energy_info = EnergyCalculator.calculate_daily_energy_requirement(
                weight_kg=pet_data["weight_kg"],
                species=species,
                age_months=pet_data["age_months"],
                activity_level=activity_level,
                physiological_status=physio_status
            )
            
            pet = Pet(
                name=pet_data["name"],
                species=pet_data["species"],
                age_months=pet_data["age_months"],
                weight_kg=pet_data["weight_kg"],
                activity_level=pet_data["activity_level"],
                physiological_status=physio_status,  # 使用Enum对象
                life_stage=energy_info["life_stage"],
                daily_calories_kcal=energy_info["daily_energy_kcal"]  # 使用正确的字段名
            )

            session.add(pet)
            session.commit()
            
            print(f"成功创建宠物: {pet.name}")
            print(f"每日能量需求: {pet.daily_calories_kcal} kcal")
            
            return pet.id
            
        except Exception as e:
            session.rollback()
            print(f"创建宠物失败: {e}")
            raise
        finally:
            session.close()
    
    def generate_recipe(self, pet_id: int, recipe_weight_g: float = 1000.0) -> dict:
        """为宠物生成营养配方"""
        session = self.SessionLocal()
        
        try:
            # 获取宠物信息
            pet = session.query(Pet).filter_by(id=pet_id).first()
            if not pet:
                raise ValueError(f"未找到ID为{pet_id}的宠物")
            
            # 创建优化器
            optimizer = NutritionOptimizer(session)
            
            # 生成配方
            result = optimizer.optimize_recipe(
                pet=pet,
                target_calories=pet.daily_calories_kcal,
                recipe_weight_g=recipe_weight_g
            )
            
            return result
            
        except Exception as e:
            print(f"生成配方失败: {e}")
            raise
        finally:
            session.close()

    def import_usda_data(self, csv_file_path: str):
        """导入USDA数据"""
        if not csv_file_path or not os.path.exists(csv_file_path):
            print("❌ CSV文件不存在或路径错误")
            return False
        
        session = self.SessionLocal()
        
        try:
            # 导入食物分类
            categories = [
                {"name": "protein", "min_percentage": 40, "max_percentage": 70},
                {"name": "subprotein", "min_percentage": 0, "max_percentage": 15},
                {"name": "carbohydrate", "min_percentage": 10, "max_percentage": 30},
                {"name": "vegetable", "min_percentage": 5, "max_percentage": 20},
                {"name": "fruit", "min_percentage": 0, "max_percentage": 10},
                {"name": "fat", "min_percentage": 2, "max_percentage": 8}
            ]
            
            # 批量检查并插入食物分类
            existing_category_names = set(row[0] for row in session.query(IngredientCategory.name).all())
            new_categories = [cat for cat in categories if cat["name"] not in existing_category_names]
            
            if new_categories:
                session.bulk_insert_mappings(IngredientCategory, new_categories)
                session.commit()
                print(f"导入食物分类完成，新增 {len(new_categories)} 个分类")
            else:
                print("所有食物分类都已存在，跳过导入")

            # 读取CSV数据
            df = pd.read_csv(csv_file_path)
            print(f"读取到{len(df)}条记录")
            
            # 导入营养素
            nutrients_data = df[['nutrient_id', 'name', 'unit_name']].drop_duplicates()
            existing_nutrient_ids = set(row[0] for row in session.query(Nutrient.nutrient_id).all())
            
            # 转换为字典列表并过滤已存在的营养素
            new_nutrients_data = []
            for _, row in nutrients_data.iterrows():
                if row['nutrient_id'] not in existing_nutrient_ids:
                    new_nutrients_data.append({
                        'nutrient_id': row['nutrient_id'],
                        'name': row['name'],
                        'unit_name': row['unit_name']
                    })
            
            if new_nutrients_data:
                session.bulk_insert_mappings(Nutrient, new_nutrients_data)
                session.commit()
                print(f"导入营养素完成，新增 {len(new_nutrients_data)} 个营养素")
            else:
                print("所有营养素都已存在，跳过导入")

            # 导入食物
            foods_data = df[['fdc_id', 'description', 'food_category_label']].drop_duplicates()
            
            # 获取已存在的食物ID和分类映射
            existing_fdc_ids = set(row[0] for row in session.query(Ingredient.fdc_id).all())
            category_map = {cat.name: cat.id for cat in session.query(IngredientCategory).all()}
            
            # 准备新食物数据
            new_foods_data = []
            for _, row in foods_data.iterrows():
                if row['fdc_id'] not in existing_fdc_ids:
                    new_foods_data.append({
                        'fdc_id': row['fdc_id'],
                        'description': row['description'],
                        'food_category_id': category_map.get(row['food_category_label']),
                        'cost_per_100g': np.random.uniform(1.0, 8.0)  # 随机成本，实际应用中需要真实数据
                    })
            
            if new_foods_data:
                session.bulk_insert_mappings(Ingredient, new_foods_data)
                session.commit()
                print(f"导入食物完成，新增 {len(new_foods_data)} 种食物")
            else:
                print("所有食物都已存在，跳过导入")
            
            # 导入营养含量数据
            nutrition_data = df[['fdc_id', 'nutrient_id', 'amount']].drop_duplicates(subset=['fdc_id', 'nutrient_id'])
            
            print(f"开始导入营养含量数据，共 {len(nutrition_data)} 条记录...")
            
            batch_size = 1000
            # 优化：先获取所有已存在的(fdc_id, nutrient_id)组合
            existing_pairs = set()
            existing_records = session.query(IngredientNutrient.fdc_id, IngredientNutrient.nutrient_id).all()
            for fdc_id, nutrient_id in existing_records:
                existing_pairs.add((fdc_id, nutrient_id))
            
            print(f"数据库中已有 {len(existing_pairs)} 条营养含量记录")
            
            # 检查并筛选新记录
            new_records = []
            duplicate_count = 0
            
            for _, row in nutrition_data.iterrows():
                fdc_id = int(row['fdc_id'])
                nutrient_id = int(row['nutrient_id'])
                amount = float(row['amount'])
                
                # 在内存中检查是否已存在
                if (fdc_id, nutrient_id) in existing_pairs:
                    duplicate_count += 1
                else:
                    new_records.append({
                        'fdc_id': fdc_id,
                        'nutrient_id': nutrient_id,
                        'amount': amount
                    })
                    # 添加到集合中，避免同一批次内的重复
                    existing_pairs.add((fdc_id, nutrient_id))
            
            # 批量插入新记录
            if new_records:
                batch_size = 1000
                batch_count = 0
                for i in range(0, len(new_records), batch_size):
                    batch = new_records[i:i+batch_size]
                    session.bulk_insert_mappings(IngredientNutrient, batch)
                    session.commit()
                    batch_count += 1
                    print(f"插入营养含量数据批次 {batch_count} 完成")
                
                print(f"✅ 营养含量数据导入完成！")
                print(f"   - 总记录数: {len(nutrition_data)}")
                print(f"   - 新增记录: {len(new_records)}")
                print(f"   - 重复跳过: {duplicate_count}")
            else:
                print(f"⚠️ 所有 {len(nutrition_data)} 条营养含量数据都已存在，跳过导入")
            
            # 更新食物基础营养信息
            self._update_food_basic_nutrition(session)
            
            print("USDA数据导入完成！")
            
        except Exception as e:
            session.rollback()
            print(f"数据导入失败: {e}")
            raise
        finally:
            session.close()

    def _update_food_basic_nutrition(self, session):
        """更新食物基础营养信息"""
        print("更新食物基础营养信息...")
        
        foods = session.query(Ingredient).all()
        
        for food in foods:
            # 确保fdc_id是Python int类型
            fdc_id = int(food.fdc_id)
            
            # 查询主要营养素
            energy_data = session.query(IngredientNutrient).join(Nutrient).filter(
                IngredientNutrient.fdc_id == fdc_id,
                Nutrient.nutrient_id == NutrientID.ENERGY
            ).first()
            
            protein_data = session.query(IngredientNutrient).join(Nutrient).filter(
                IngredientNutrient.fdc_id == fdc_id,
                Nutrient.nutrient_id == NutrientID.PROTEIN
            ).first()
            
            fat_data = session.query(IngredientNutrient).join(Nutrient).filter(
                IngredientNutrient.fdc_id == fdc_id,
                Nutrient.nutrient_id == NutrientID.FAT
            ).first()
            
            carb_data = session.query(IngredientNutrient).join(Nutrient).filter(
                IngredientNutrient.fdc_id == fdc_id,
                Nutrient.nutrient_id == NutrientID.CARBOHYDRATE
            ).first()
            
            # 更新食物记录，确保数值是Python原生类型
            food.energy_kcal_100g = float(energy_data.amount) if energy_data else None
            food.protein_g_100g = float(protein_data.amount) if protein_data else None
            food.fat_g_100g = float(fat_data.amount) if fat_data else None
            food.carb_g_100g = float(carb_data.amount) if carb_data else None
        
        session.commit()
        print("基础营养信息更新完成")