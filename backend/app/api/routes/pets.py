from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
import logging

from app.db.database import get_db
from app.schemas.pet import PetCreate, PetResponse, PetUpdate
from app.services.pet_service import PetService
from app.core.response import create_response

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=dict)
async def create_pet(
    pet_data: PetCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建宠物"""
    try:
        service = PetService(db)
        result = await service.create_pet(pet_data.dict())
        
        return create_response(
            success=True,
            data={
                "pet_id": result["pet_id"],
                "daily_calories_kcal": result["daily_calories_kcal"],
                "life_stage": result["life_stage"]
            },
            message="宠物创建成功"
        )
    except Exception as e:
        logger.error(f"创建宠物失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{pet_id}", response_model=dict)
async def get_pet(
    pet_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取宠物信息"""
    try:
        service = PetService(db)
        pet = await service.get_pet(pet_id)
        
        if not pet:
            raise HTTPException(status_code=404, detail="宠物不存在")
        
        return create_response(
            success=True,
            data=pet,
            message="获取宠物信息成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取宠物信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/{pet_id}", response_model=dict)
async def update_pet(
    pet_id: int,
    pet_data: PetUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新宠物信息"""
    try:
        service = PetService(db)
        updated_pet = await service.update_pet(pet_id, pet_data.dict(exclude_unset=True))
        
        if not updated_pet:
            raise HTTPException(status_code=404, detail="宠物不存在")
        
        return create_response(
            success=True,
            data=updated_pet,
            message="宠物信息更新成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新宠物信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))