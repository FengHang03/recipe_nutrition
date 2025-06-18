from sqlalchemy import (
    create_engine, Column, Integer, String, Float, DateTime, Enum,
    ForeignKey, Text, Boolean, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID, JSON, ARRAY
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union
from app.db.database import Base
import uuid
from enum import Enum as PyEnum
from datetime import datetime

# 枚举定义
class Species(str, PyEnum):
    DOG = "dog"
    CAT = "cat"
    
class LifeStage(str, PyEnum):
    DOG_PUPPY = "dog_puppy"
    DOG_ADULT = "dog_adult" 
    CAT_KITTEN = "cat_kitten"
    CAT_ADULT = "cat_adult"
    
class ActivityLevel(str, PyEnum):
    SEDENTARY_ACTIVE = "sedentary_active"
    LOW_ACTIVE = "low_active"
    MODERATE_ACTIVE = "moderate_active"
    HIGH_ACTIVE = "high_active"
    EXTREME_ACTIVE = "extreme_active"

# 生理状态枚举
class PhysiologicalStatus(str, PyEnum):
    INTACT = "intact"         # 未绝育
    NEUTERED = "neutered"     # 已绝育
    PREGNANT = "pregnant"     # 怀孕
    LACTATING = "lactating"   # 哺乳

Base = declarative_base()

class IngredientCategory(Base):
    """食物分类表"""
    __tablename__ = 'ingredient_categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)  # protein, fat, etc.
    
    # 配方约束参数
    min_percentage = Column(Float, default=0)    # 在配方中的最小比例
    max_percentage = Column(Float, default=100)  # 在配方中的最大比例
    recommended_percentage = Column(Float)        # 推荐比例

    created_at = Column(DateTime, default=datetime.now())
    
    # 关系
    ingredients = relationship("Ingredient", back_populates="category")
    
    def __repr__(self):
        return f"<FoodCategory(name='{self.name}')>"

class Ingredient(Base):
    """食物基础信息表"""
    __tablename__ = 'ingredients'
    
    fdc_id = Column(Integer, primary_key=True)
    description = Column(String(500), nullable=False)
    common_name = Column(String(100), nullable=True)
    food_category_id = Column(Integer, ForeignKey('ingredient_categories.id'))

    # 基础营养信息 (冗余存储，优化查询性能)
    energy_kcal_100g = Column(Float)  # 每100g卡路里
    protein_g_100g = Column(Float)    # 每100g蛋白质
    fat_g_100g = Column(Float)        # 每100g脂肪
    carb_g_100g = Column(Float)       # 每100g碳水化合物
    
    # 成本和可获得性信息
    cost_per_100g = Column(Float, nullable=True, default=1.0)  # 成本/100g (单位: 元)
    
    # 安全性信息
    safe_for_dogs = Column(Boolean, default=True)
    safe_for_cats = Column(Boolean, default=True)
    
    # 物理特性
    water_content = Column(Float)  # 水分含量 %
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())
    
    # 关系
    category = relationship("IngredientCategory", back_populates="ingredients")
    nutrients = relationship("IngredientNutrient", back_populates="ingredient")

    __table_args__ = (
        Index('idx_ingredient_category', 'food_category_id'),
        Index('idx_ingredient_name', 'common_name'),
    )
    
    def __repr__(self):
        return f"<Ingredient(fdc_id='{self.fdc_id}')>"

class Nutrient(Base):
    """营养素信息表"""
    __tablename__ = 'nutrients'
    
    nutrient_id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    unit_name = Column(String(20), nullable=False) # g, mg, IU, etc.

    # AAFCO标准 (干物质基础, %)
    aafco_dog_adult_min = Column(Float)
    aafco_dog_adult_max = Column(Float)
    aafco_dog_puppy_min = Column(Float)
    aafco_dog_puppy_max = Column(Float)
    aafco_cat_adult_min = Column(Float)
    aafco_cat_adult_max = Column(Float)
    aafco_cat_kitten_min = Column(Float)
    aafco_cat_kitten_max = Column(Float)

    # # 生物利用度和交互作用
    # bioavailability_factor = Column(Float, default=1.0)
    # synergistic_nutrients = Column(ARRAY(Integer))  # 协同作用的营养素ID
    # antagonistic_nutrients = Column(ARRAY(Integer)) # 拮抗作用的营养素ID

    # 关系
    ingredient_nutrients = relationship("IngredientNutrient", back_populates="nutrient")

    __table_args__ = (
        Index('idx_nutrient_name', 'name'),
    )
    
    def __repr__(self):
        return f"<Nutrient(name='{self.name}')>"

class IngredientNutrient(Base):
    """食物-营养素含量关联表"""
    __tablename__ = 'ingredient_nutrients'
    
    id = Column(Integer, primary_key=True)
    fdc_id = Column(Integer, ForeignKey('ingredients.fdc_id'), nullable=False)
    nutrient_id = Column(Integer, ForeignKey('nutrients.nutrient_id'), nullable=False)
    amount = Column(Float, nullable=False)  # 营养素含量
    
    # 关系
    ingredient = relationship("Ingredient", back_populates="nutrients")
    nutrient = relationship("Nutrient", back_populates="ingredient_nutrients")

    __table_args__ = (
        UniqueConstraint('fdc_id', 'nutrient_id', name='uix_fdc_nutrient'),
        Index('idx_nutrient_ingredient', 'nutrient_id'),
        CheckConstraint('amount >= 0', name='check_amount_non_negative'),
    )

# class BreedCharacteristic(Base):
#     __tablename__ = "breed_characteristics"
    
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
#     species = Column(String, nullable=False)  # 物种（狗/猫等）
#     breed = Column(String, nullable=False)
#     size_category = Column(String(20), nullable=True)   # toy, small, medium, large, giant
#     typical_weight_range = Column(String, nullable=True)
#     typical_lifespan = Column(String, nullable=True)
#     activity_level = Column(String, nullable=True)
#     temperament = Column(JSON, nullable=True)  # 性格特点列表
#     common_health_issues = Column(JSON, nullable=True)  # 常见健康问题
#     dietary_needs = Column(JSON, nullable=True)  # 特殊饮食需求
#     recommended_nutrients = Column(ARRAY(Integer))  # 推荐加强的营养素
#     nutrients_to_limit = Column(ARRAY(Integer))     # 需要限制的营养素
#     metabolic_rate_factor = Column(Float, default=1.0)    # 代谢率修正因子

#     llm_analysis_date = Column(DateTime, nullable=True)  # LLM分析日期
    
#     __table_args__ = (
#         UniqueConstraint('species', 'breed', name='uidx_species_breed'),
#         Index('idx_breed_characteristic_species', 'species'),
#     )

class Pet(Base):
    """宠物信息表"""
    __tablename__ = 'pets'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=True)
    species = Column(String(20), nullable=False)  # 'dog' or 'cat'
    breed = Column(String(100), nullable=True)
    
    # 基本信息
    age_months = Column(Integer, nullable=False)
    weight_kg = Column(Float, nullable=False)
    
    # 活动和健康
    activity_level = Column(String(20), default='moderate')  # low, moderate, high
    # 生理状态
    physiological_status = Column(Enum(PhysiologicalStatus), 
                                 nullable=False, 
                                 default=PhysiologicalStatus.INTACT)
    
    life_stage = Column(Enum(LifeStage), nullable=False, default=LifeStage.DOG_ADULT)

    lactation_week = Column(Integer, nullable=True, default=4)  # 哺乳周数(1-4)
    nursing_count = Column(Integer, nullable=True, default=1)   # 哺乳幼崽数量
    
    # 健康状况 (JSON格式)
    health_conditions = Column(JSON, nullable=True)  # 存储JSON字符串
    allergies = Column(JSON, nullable=True)  # 食物过敏信息
    
    # 代谢率
    daily_calories_kcal = Column(Float, nullable=True)
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.now())
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())

    __table_args__ = (
        Index('idx_pet_name', 'name'),
        Index('idx_pet_species_breed', 'species', 'breed'),
        Index('idx_pet_physiological_status', 'physiological_status'),
    )

# class Recipe(Base):
#     """生成的配方记录表"""
#     __tablename__ = 'recipes'
    
#     id = Column(Integer, primary_key=True)
#     pet_id = Column(Integer, ForeignKey('pets.id'))
    
#     # 配方基本信息
#     name = Column(String(200))
#     total_weight_g = Column(Float, nullable=False)
#     total_cost = Column(Float)
    
#     # 优化参数
#     optimization_objective = Column(String(50))  # cost, palatability, nutrition
    
#     # 营养分析结果 (JSON格式)
#     nutrition_analysis = Column(Text)
#     aafco_compliance = Column(Text)  # AAFCO符合性分析

#     # 配方数据 (JSON存储)
#     ingredients = Column(JSON, nullable=False)  # {fdc_id: {amount_g, percentage, cost}}
#     dietary_focus = Column(String, nullable=True)  # 食谱重点，如"weight-management", "joint-health"

#     # 配方状态
#     is_approved = Column(Boolean, default=False)
#     approval_notes = Column(Text)
    
#     # 时间戳
#     created_at = Column(DateTime, default=datetime.utcnow)
    
#     # 关系
#     ingredients = relationship("RecipeIngredient", back_populates="recipe")
#     pet = relationship("Pet", back_populates="recipes")
#     standard = relationship("NutritionStandard", back_populates="recipes")
#     analyses = relationship("RecipeAnalysis", back_populates="recipe")

#     __table_args__ = (
#         Index('idx_recipe_pet_id', 'pet_id'),
#         Index("idx_recipes_dietary_focus", "dietary_focus"),
#     )

# class RecipeIngredient(Base):
#     """配方成分表"""
#     __tablename__ = 'recipe_ingredients'
    
#     id = Column(Integer, primary_key=True)
#     recipe_id = Column(Integer, ForeignKey('recipes.id'), nullable=False)
#     fdc_id = Column(Integer, ForeignKey('ingredients.fdc_id'), nullable=False)
    
#     amount_g = Column(Float, nullable=False)  # 用量(克)
#     percentage = Column(Float, nullable=False)  # 占比(%)
    
#     # 关系
#     recipe = relationship("Recipe", back_populates="ingredients")
#     ingredient = relationship("Ingredient")
