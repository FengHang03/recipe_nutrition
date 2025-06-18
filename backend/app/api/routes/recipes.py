from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.db.database import get_db
from app.schemas.recipe import RecipeGenerateRequest, RecipeResponse
from app.services.recipe_service import RecipeService
from app.core.response import create_response

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/generate")
async def generate_recipe(
    request: RecipeGenerateRequest,
    db: AsyncSession = Depends(get_db)
):
    """生成配方"""
    try:
        service = RecipeService(db)
        result = await service.generate_recipe(
            pet_id=request.pet_id,
            target_calories=request.target_calories,
            preferred_weight_g=request.preferred_weight_g
        )
        
        return result
    
    except Exception as e:
        logger.error(f"生成配方失败: {e}")
        return {
            "status": "Error",
            "error": str(e),
            "recipe": {},
            "analysis": {}
        }

@router.get("/{recipe_id}")
async def get_recipe(
    recipe_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取配方详情"""
    try:
        service = RecipeService(db)
        recipe = await service.get_recipe(recipe_id)
        
        if not recipe:
            raise HTTPException(status_code=404, detail="配方不存在")
        
        return recipe
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取配方失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))