#!/usr/bin/env python3
"""
修复 protein_g_100g 字段的脚本
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.models import Ingredient, Nutrient, IngredientNutrient

def fix_protein_fields():
    """修复所有营养字段"""
    try:
        # 连接数据库
        engine = create_engine("postgresql://postgres:1997@localhost:5433/pet_diet_db", echo=False)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        print("🔧 开始修复营养字段...")
        print("=" * 50)
        
        # 1. 检查营养素表中的数据
        nutrients = session.query(Nutrient).all()
        print(f"营养素总数: {len(nutrients)}")
        
        # 查找关键营养素
        key_nutrients = {}
        for nutrient in nutrients:
            name_lower = nutrient.name.lower().strip()
            if 'protein' in name_lower and name_lower == 'protein':
                key_nutrients['protein'] = nutrient
            elif name_lower == 'total lipid (fat)':
                key_nutrients['fat'] = nutrient
            elif name_lower == 'carbohydrate, by difference':
                key_nutrients['carb'] = nutrient
            elif name_lower == 'energy':
                key_nutrients['energy'] = nutrient
        
        print("找到的关键营养素:")
        for key, nutrient in key_nutrients.items():
            print(f"  - {key}: ID={nutrient.nutrient_id}, Name='{nutrient.name}'")
        
        if 'protein' not in key_nutrients:
            print("❌ 未找到Protein营养素，尝试模糊匹配...")
            protein_candidates = [n for n in nutrients if 'protein' in n.name.lower()]
            if protein_candidates:
                print("可能的Protein营养素:")
                for i, n in enumerate(protein_candidates):
                    print(f"  {i+1}. ID={n.nutrient_id}, Name='{n.name}'")
                
                # 自动选择第一个完全匹配的
                exact_match = next((n for n in protein_candidates if n.name.lower().strip() == 'protein'), None)
                if exact_match:
                    key_nutrients['protein'] = exact_match
                    print(f"✅ 自动选择: {exact_match.name}")
                else:
                    key_nutrients['protein'] = protein_candidates[0]
                    print(f"⚠️ 自动选择第一个: {protein_candidates[0].name}")
        
        # 2. 更新所有食物的营养信息
        foods = session.query(Ingredient).all()
        updated_count = 0
        
        print(f"\n开始更新 {len(foods)} 种食物的营养信息...")
        
        for food in foods:
            updated = False
            
            # 更新protein_g_100g
            if 'protein' in key_nutrients:
                protein_data = session.query(IngredientNutrient).filter_by(
                    fdc_id=food.fdc_id,
                    nutrient_id=key_nutrients['protein'].nutrient_id
                ).first()
                
                if protein_data and food.protein_g_100g is None:
                    food.protein_g_100g = protein_data.amount
                    updated = True
            
            # 更新fat_g_100g
            if 'fat' in key_nutrients:
                fat_data = session.query(IngredientNutrient).filter_by(
                    fdc_id=food.fdc_id,
                    nutrient_id=key_nutrients['fat'].nutrient_id
                ).first()
                
                if fat_data and food.fat_g_100g is None:
                    food.fat_g_100g = fat_data.amount
                    updated = True
            
            # 更新carb_g_100g
            if 'carb' in key_nutrients:
                carb_data = session.query(IngredientNutrient).filter_by(
                    fdc_id=food.fdc_id,
                    nutrient_id=key_nutrients['carb'].nutrient_id
                ).first()
                
                if carb_data and food.carb_g_100g is None:
                    food.carb_g_100g = carb_data.amount
                    updated = True
            
            # 更新energy_kcal_100g
            if 'energy' in key_nutrients:
                energy_data = session.query(IngredientNutrient).filter_by(
                    fdc_id=food.fdc_id,
                    nutrient_id=key_nutrients['energy'].nutrient_id
                ).first()
                
                if energy_data and food.energy_kcal_100g is None:
                    food.energy_kcal_100g = energy_data.amount
                    updated = True
            
            if updated:
                updated_count += 1
        
        # 提交更改
        session.commit()
        print(f"✅ 成功更新了 {updated_count} 种食物的营养信息")
        
        # 3. 验证结果
        print("\n验证结果:")
        protein_count = session.query(Ingredient).filter(Ingredient.protein_g_100g.isnot(None)).count()
        fat_count = session.query(Ingredient).filter(Ingredient.fat_g_100g.isnot(None)).count()
        carb_count = session.query(Ingredient).filter(Ingredient.carb_g_100g.isnot(None)).count()
        energy_count = session.query(Ingredient).filter(Ingredient.energy_kcal_100g.isnot(None)).count()
        
        print(f"  - 有protein_g_100g数据的食物: {protein_count}")
        print(f"  - 有fat_g_100g数据的食物: {fat_count}")
        print(f"  - 有carb_g_100g数据的食物: {carb_count}")
        print(f"  - 有energy_kcal_100g数据的食物: {energy_count}")
        
        # 显示一个例子
        if protein_count > 0:
            example = session.query(Ingredient).filter(Ingredient.protein_g_100g.isnot(None)).first()
            print(f"\n示例食物: {example.description}")
            print(f"  - 蛋白质: {example.protein_g_100g}g/100g")
            print(f"  - 脂肪: {example.fat_g_100g}g/100g")
            print(f"  - 碳水化合物: {example.carb_g_100g}g/100g")
            print(f"  - 能量: {example.energy_kcal_100g}kcal/100g")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 营养字段修复工具")
    print("=" * 50)
    
    success = fix_protein_fields()
    
    if success:
        print("\n✅ 修复完成！现在可以重新运行测试。")
    else:
        print("\n❌ 修复失败，请检查错误信息。") 