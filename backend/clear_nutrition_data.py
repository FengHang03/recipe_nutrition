#!/usr/bin/env python3
"""
清理营养数据脚本 - 解决重复键问题
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.db.models import IngredientNutrient

def clear_nutrition_data():
    """清理营养含量数据表"""
    try:
        # 连接数据库
        engine = create_engine("postgresql://postgres:1997@localhost:5433/pet_diet_db", echo=False)
        SessionLocal = sessionmaker(bind=engine)
        session = SessionLocal()
        
        print("🧹 清理营养数据...")
        
        # 查看当前数据量
        current_count = session.query(IngredientNutrient).count()
        print(f"当前营养含量数据数量: {current_count}")
        
        if current_count > 0:
            # 删除所有营养含量数据
            session.query(IngredientNutrient).delete()
            session.commit()
            print(f"✅ 已清理 {current_count} 条营养含量数据")
        else:
            print("✅ 营养含量数据表已为空")
        
        session.close()
        return True
        
    except Exception as e:
        print(f"❌ 清理失败: {e}")
        return False

if __name__ == "__main__":
    print("🧹 营养数据清理工具")
    print("=" * 50)
    
    choice = input("确定要清理所有营养含量数据吗？(y/N): ").strip().lower()
    
    if choice == 'y':
        success = clear_nutrition_data()
        if success:
            print("\n✅ 清理完成！现在可以重新导入数据。")
        else:
            print("\n❌ 清理失败。")
    else:
        print("取消清理操作。") 