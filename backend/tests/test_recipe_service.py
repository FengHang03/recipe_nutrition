import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.recipe_service import RecipeService, NutritionOptimizer, OptimizationConfig
from app.db.models import Pet, Ingredient, IngredientNutrient, Nutrient
from app.db.nutrientStandard import LifeStage, NutrientID

# Mock data
MOCK_PET = Pet(
    id=1,
    name="Test Pet",
    species="dog",
    age_months=24,
    daily_calories_kcal=1000.0
)

MOCK_INGREDIENTS = [
    Ingredient(
        fdc_id=1,
        description="Chicken Breast",
        energy_kcal_100g=165.0,
        cost_per_100g=2.0,
        safe_for_dogs=True,
        safe_for_cats=True,
        category=MagicMock(name="Protein")
    ),
    Ingredient(
        fdc_id=2,
        description="Brown Rice",
        energy_kcal_100g=112.0,
        cost_per_100g=0.5,
        safe_for_dogs=True,
        safe_for_cats=True,
        category=MagicMock(name="Grain")
    ),
    Ingredient(
        fdc_id=3,
        description="Carrot",
        energy_kcal_100g=41.0,
        cost_per_100g=0.3,
        safe_for_dogs=True,
        safe_for_cats=True,
        category=MagicMock(name="Vegetable")
    )
]

MOCK_NUTRIENTS = {
    NutrientID.PROTEIN: Nutrient(
        nutrient_id=NutrientID.PROTEIN,
        name="Protein",
        unit_name="G"
    ),
    NutrientID.FAT: Nutrient(
        nutrient_id=NutrientID.FAT,
        name="Fat",
        unit_name="G"
    )
}

MOCK_INGREDIENT_NUTRIENTS = [
    IngredientNutrient(
        fdc_id=1,
        nutrient_id=NutrientID.PROTEIN,
        amount=31.0
    ),
    IngredientNutrient(
        fdc_id=1,
        nutrient_id=NutrientID.FAT,
        amount=3.6
    ),
    IngredientNutrient(
        fdc_id=2,
        nutrient_id=NutrientID.PROTEIN,
        amount=2.6
    ),
    IngredientNutrient(
        fdc_id=2,
        nutrient_id=NutrientID.FAT,
        amount=0.9
    )
]

@pytest.fixture
def mock_session():
    """Create a mock database session"""
    session = AsyncMock(spec=AsyncSession)
    
    # Mock the execute method to return different results based on the query
    async def mock_execute(query):
        mock_result = AsyncMock()
        
        # Handle different query types
        if query._select_from_entity == Pet:
            mock_result.scalar_one_or_none.return_value = MOCK_PET
        elif query._select_from_entity == Ingredient:
            mock_result.scalars.return_value = MOCK_INGREDIENTS
        elif query._select_from_entity == Nutrient:
            mock_result.scalar_one_or_none.return_value = MOCK_NUTRIENTS.get(
                query.whereclause.right.value
            )
        elif query._select_from_entity == IngredientNutrient:
            mock_result.scalar_one_or_none.return_value = next(
                (n for n in MOCK_INGREDIENT_NUTRIENTS 
                 if n.fdc_id == query.whereclause.left.left.left.value 
                 and n.nutrient_id == query.whereclause.right.value),
                None
            )
        
        return mock_result
    
    session.execute = mock_execute
    return session

@pytest.mark.asyncio
async def test_recipe_service_initialization(mock_session):
    """Test RecipeService initialization"""
    service = RecipeService(mock_session)
    assert service.db == mock_session

@pytest.mark.asyncio
async def test_generate_recipe_success(mock_session):
    """Test successful recipe generation"""
    service = RecipeService(mock_session)
    
    result = await service.generate_recipe(
        pet_id=1,
        target_calories=1000.0,
        recipe_weight_g=400.0
    )
    
    assert result["status"] == "Success"
    assert "recipe" in result
    assert "analysis" in result
    assert result["analysis"]["target_calories"] == 1000.0
    assert result["analysis"]["total_cost"] > 0

@pytest.mark.asyncio
async def test_generate_recipe_pet_not_found(mock_session):
    """Test recipe generation with non-existent pet"""
    service = RecipeService(mock_session)
    
    # Override the mock to return None for pet
    async def mock_execute(query):
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = None
        return mock_result
    
    mock_session.execute = mock_execute
    
    result = await service.generate_recipe(
        pet_id=999,
        target_calories=1000.0,
        recipe_weight_g=400.0
    )
    
    assert result["status"] == "Error"
    assert "error" in result
    assert result["error"] == "宠物不存在"

@pytest.mark.asyncio
async def test_optimization_config_validation():
    """Test OptimizationConfig validation"""
    # Test valid configuration
    config = OptimizationConfig()
    assert config.energy_weight == 1000.0
    assert config.nutrient_weight == 100.0
    assert config.max_single_food_percent == 35.0
    assert config.recipe_weight_g == 400.0
    
    # Test invalid configurations
    with pytest.raises(ValueError):
        OptimizationConfig(energy_weight=-1)
    
    with pytest.raises(ValueError):
        OptimizationConfig(nutrient_weight=0)
    
    with pytest.raises(ValueError):
        OptimizationConfig(max_single_food_percent=101)
    
    with pytest.raises(ValueError):
        OptimizationConfig(recipe_weight_g=-1)

@pytest.mark.asyncio
async def test_nutrition_optimizer_initialization(mock_session):
    """Test NutritionOptimizer initialization"""
    config = OptimizationConfig()
    optimizer = NutritionOptimizer(mock_session, config)
    
    assert optimizer.session == mock_session
    assert optimizer.config == config
    assert optimizer.problem is None
    assert optimizer.food_vars == {}
    assert optimizer.optimization_result == {}

@pytest.mark.asyncio
async def test_get_available_foods(mock_session):
    """Test getting available foods for a pet"""
    optimizer = NutritionOptimizer(mock_session)
    
    # Test for dog
    foods = await optimizer._get_available_foods(MOCK_PET)
    assert len(foods) > 0
    assert all(food.safe_for_dogs for food in foods)
    
    # Test for cat
    cat_pet = Pet(
        id=2,
        name="Test Cat",
        species="cat",
        age_months=24,
        daily_calories_kcal=800.0
    )
    foods = await optimizer._get_available_foods(cat_pet)
    assert len(foods) > 0
    assert all(food.safe_for_cats for food in foods) 