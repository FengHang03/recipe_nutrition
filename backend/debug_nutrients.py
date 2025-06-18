#!/usr/bin/env python3
"""
诊断脚本：检查营养素数据和名称匹配情况
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db.models import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, text
from app.core.config import settings

def debug_nutrients():
    """诊断营养素数据"""
    # 创建同步引擎
    sync_engine = create_engine(settings.SQLALCHEMY_DATABASE_URI, echo=False)
    SessionLocal = sessionmaker(bind=sync_engine)
    session = SessionLocal()
    
    try:
        print("🔍 营养素诊断报告")
        print("=" * 50)
        
        # 1. 检查数据库中的营养素名称
        print("\n1. 数据库中的营养素列表:")
        nutrients = session.query(Nutrient).all()
        nutrient_names = [n.name for n in nutrients]
        
        target_names = ['Protein', 'Total lipid (fat)', 'Carbohydrate, by difference', 'Energy']
        
        for name in target_names:
            if name in nutrient_names:
                print(f"   ✅ {name}")
            else:
                print(f"   ❌ {name} - 未找到")
                # 寻找相似的名称
                similar = [n for n in nutrient_names if 'protein' in n.lower() or 'fat' in n.lower() or 'carb' in n.lower()]
                if similar:
                    print(f"      相似名称: {similar[:3]}")
        
        # 2. 检查一个具体食物的营养数据
        print("\n2. 检查具体食物的营养数据:")
        food = session.query(Ingredient).first()
        if food:
            print(f"   食物: {food.description}")
            print(f"   FDC ID: {food.fdc_id}")
            
            # 查询该食物的所有营养数据
            nutrition_data = session.query(IngredientNutrient, Nutrient).join(Nutrient).filter(
                IngredientNutrient.fdc_id == food.fdc_id
            ).all()
            
            print(f"   营养数据条数: {len(nutrition_data)}")
            
            for nut_data, nutrient in nutrition_data:
                if any(keyword in nutrient.name.lower() for keyword in ['protein', 'fat', 'carb', 'energy']):
                    print(f"   - {nutrient.name}: {nut_data.amount} {nutrient.unit_name}")
        
        # 3. 检查基础营养信息更新情况
        print("\n3. 基础营养信息统计:")
        total_foods = session.query(Ingredient).count()
        foods_with_protein = session.query(Ingredient).filter(Ingredient.protein_g_100g.isnot(None)).count()
        foods_with_fat = session.query(Ingredient).filter(Ingredient.fat_g_100g.isnot(None)).count()
        foods_with_carb = session.query(Ingredient).filter(Ingredient.carb_g_100g.isnot(None)).count()
        foods_with_energy = session.query(Ingredient).filter(Ingredient.energy_kcal_100g.isnot(None)).count()
        
        print(f"   总食物数: {total_foods}")
        print(f"   有蛋白质数据: {foods_with_protein} ({foods_with_protein/total_foods*100:.1f}%)")
        print(f"   有脂肪数据: {foods_with_fat} ({foods_with_fat/total_foods*100:.1f}%)")
        print(f"   有碳水数据: {foods_with_carb} ({foods_with_carb/total_foods*100:.1f}%)")
        print(f"   有能量数据: {foods_with_energy} ({foods_with_energy/total_foods*100:.1f}%)")
        
        # 4. 查找所有包含 "protein" 的营养素
        print("\n4. 所有包含 'protein' 的营养素:")
        protein_nutrients = session.query(Nutrient).filter(
            Nutrient.name.ilike('%protein%')
        ).all()
        
        for nutrient in protein_nutrients:
            print(f"   - ID: {nutrient.nutrient_id}, 名称: '{nutrient.name}', 单位: {nutrient.unit_name}")
        
        return True
        
    except Exception as e:
        print(f"❌ 诊断失败: {e}")
        return False
    finally:
        session.close()

if __name__ == "__main__":
    debug_nutrients() 