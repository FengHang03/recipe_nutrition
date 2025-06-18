#!/usr/bin/env python3
"""
简单脚本：检查protein_g_100g字段问题
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

def check_protein_issue():
    """检查protein_g_100g问题"""
    try:
        # 直接连接数据库
        engine = create_engine("postgresql://postgres:1997@localhost:5433/pet_diet_db", echo=False)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        print("🔍 检查 protein_g_100g 字段问题")
        print("=" * 50)
        
        # 1. 检查数据库中是否有数据
        table_check = session.execute(text("""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name IN ('ingredients', 'nutrients', 'ingredient_nutrients')
        """)).fetchall()
        
        print(f"数据库表: {[t[0] for t in table_check]}")
        
        if not table_check:
            print("❌ 数据库表不存在")
            return False
        
        # 2. 检查营养素表
        nutrient_count = session.execute(text("SELECT COUNT(*) FROM nutrients")).fetchone()[0]
        print(f"营养素总数: {nutrient_count}")
        
        # 3. 查找Protein营养素
        protein_nutrient = session.execute(text("""
            SELECT nutrient_id, name FROM nutrients WHERE name = 'Protein'
        """)).fetchone()
        
        if protein_nutrient:
            nutrient_id, name = protein_nutrient
            print(f"✅ 找到Protein营养素: ID={nutrient_id}, Name='{name}'")
            
            # 4. 检查ingredient_nutrients表中的Protein数据
            protein_data_count = session.execute(text(f"""
                SELECT COUNT(*) FROM ingredient_nutrients WHERE nutrient_id = {nutrient_id}
            """)).fetchone()[0]
            
            print(f"Protein营养数据条数: {protein_data_count}")
            
            if protein_data_count > 0:
                # 5. 检查ingredients表中protein_g_100g字段
                ingredients_with_protein = session.execute(text("""
                    SELECT COUNT(*) FROM ingredients WHERE protein_g_100g IS NOT NULL
                """)).fetchone()[0]
                
                print(f"有protein_g_100g数据的食物数量: {ingredients_with_protein}")
                
                # 6. 查看一个具体例子
                example = session.execute(text(f"""
                    SELECT i.fdc_id, i.description, i.protein_g_100g, fn.amount
                    FROM ingredients i
                    JOIN ingredient_nutrients fn ON i.fdc_id = fn.fdc_id
                    WHERE fn.nutrient_id = {nutrient_id}
                    LIMIT 1
                """)).fetchone()
                
                if example:
                    fdc_id, description, protein_g_100g, raw_amount = example
                    print(f"示例食物: {description}")
                    print(f"  FDC ID: {fdc_id}")
                    print(f"  protein_g_100g字段: {protein_g_100g}")
                    print(f"  原始营养数据: {raw_amount}")
                    
                    if protein_g_100g is None and raw_amount is not None:
                        print("❌ 问题确认：protein_g_100g字段未更新，但原始数据存在")
                        return "update_needed"
                    elif protein_g_100g is not None:
                        print("✅ protein_g_100g字段正常")
                        return "normal"
                
        else:
            print("❌ 未找到名为'Protein'的营养素")
            
            # 查找相似的营养素
            similar_nutrients = session.execute(text("""
                SELECT nutrient_id, name FROM nutrients WHERE LOWER(name) LIKE '%protein%'
            """)).fetchall()
            
            if similar_nutrients:
                print("包含'protein'的营养素:")
                for nid, nname in similar_nutrients:
                    print(f"  - ID:{nid}, Name:'{nname}'")
            
            return False
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ 检查失败: {e}")
        return False

def fix_protein_update():
    """修复protein_g_100g字段更新"""
    try:
        engine = create_engine("postgresql://postgres:1997@localhost:5433/pet_diet_db", echo=False)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        print("🔧 开始修复protein_g_100g字段...")
        
        # 执行更新操作
        update_sql = """
        UPDATE ingredients 
        SET protein_g_100g = (
            SELECT fn.amount 
            FROM ingredient_nutrients fn 
            JOIN nutrients n ON fn.nutrient_id = n.nutrient_id 
            WHERE fn.fdc_id = ingredients.fdc_id AND n.name = 'Protein'
        )
        WHERE EXISTS (
            SELECT 1 
            FROM ingredient_nutrients fn 
            JOIN nutrients n ON fn.nutrient_id = n.nutrient_id 
            WHERE fn.fdc_id = ingredients.fdc_id AND n.name = 'Protein'
        )
        """
        
        result = session.execute(text(update_sql))
        session.commit()
        
        print(f"✅ 更新了 {result.rowcount} 条记录的protein_g_100g字段")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ 修复失败: {e}")
        return False

if __name__ == "__main__":
    result = check_protein_issue()
    
    if result == "update_needed":
        print("\n是否要修复protein_g_100g字段? (y/n): ", end="")
        if input().lower() == 'y':
            fix_protein_update()
            print("\n再次检查:")
            check_protein_issue() 