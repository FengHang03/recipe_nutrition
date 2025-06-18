from app.services.recipe_service import NutritionOptimizer
from fastapi import FastAPI, HTTPException, Depends, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
# 创建优化器实例

# 创建FastAPI应用
app = FastAPI(
    title="智能宠物营养配方系统",
    description="基于AI技术的个性化宠物营养方案生成器",
    version="1.0.0"
)

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静态文件服务
app.mount("/static", StaticFiles(directory="static"), name="static")

optimizer = NutritionOptimizer()

#  API 路由
@app.get('/', response_class=HTMLResponse)
async def read_root():
    """返回前端界面"""
    return FileResponse("static/index.html")

@app.post("/api/generate-recipe", response_model=Recipe)
async def generate_recipe(pet_info: PetInfo):
    """生成营养配方"""
    try:
        recipe = optimizer.optimize_recipe(pet_info)
        return recipe
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"配方生成失败: {str(e)}")

@app.get("/api/ingredients")
async def get_ingredients():
    """获取食材数据库"""
    return NUTRITION_DATABASE

@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/api/analyze-nutrition")
async def analyze_custom_nutrition(ingredients: List[dict]):
    """分析自定义配方的营养成分"""
    # 这里可以实现自定义配方的营养分析
    pass

if __name__ == "__main__":
    import uvicorn

    # 创建static目录
    os.makedirs("static", exist_ok=True)

    print("🚀Starting pet nutrition diet server...")

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True, log_level="info")