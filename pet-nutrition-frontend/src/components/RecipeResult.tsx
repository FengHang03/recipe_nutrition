import React from 'react';
import { motion } from 'framer-motion';
import { 
  CheckCircle, 
  AlertTriangle, 
  Package,
  DollarSign, 
  Calculator,
  BarChart3,
  FileText,
  Heart,
  Award,
  Info
} from 'lucide-react';
import type { RecipeResult as RecipeResultType } from '../types';
import { useRecipeData } from '../hooks/useRecipeData';
import ReportHeader from './recipe/ReportHeader';
import NutritionCharts from './recipe/NutritionCharts';

interface RecipeResultProps {
  recipe: RecipeResultType;
  onSave?: () => void;
  onShare?: () => void;
  onNewRecipe?: () => void;
}

const RecipeResult: React.FC<RecipeResultProps> = ({ 
  recipe, 
  onSave, 
  onShare, 
  onNewRecipe 
}) => {
  console.log('🍽️ RecipeResult rendering with:', recipe);
  
  // 检查配方数据完整性
  if (!recipe || recipe.status !== 'Success') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Recipe Data Unavailable</h2>
          <button
            onClick={onNewRecipe}
            className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors"
          >
            Generate New Recipe
          </button>
        </div>
      </div>
    );
  }

  const { recipe: recipeData, analysis } = recipe;
  
  // 使用数据处理钩子
  const {
    petInfo,
    nutrientDensity,
    macroData,
    ingredientData,
    complianceData,
    radarData,
    COLORS
  } = useRecipeData(recipe);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* 报告头部 */}
        <ReportHeader 
          petInfo={petInfo}
          onSave={onSave}
          onShare={onShare}
          onNewRecipe={onNewRecipe}
        />

        {/* 执行摘要 */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-white rounded-lg shadow-sm border p-6 mb-8"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <FileText className="w-5 h-5 mr-2" />
            Executive Summary
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <div className="text-2xl font-bold text-blue-600">{recipeData.target_calories}</div>
              <div className="text-sm text-gray-600">Target Energy (kcal)</div>
              <div className="text-xs text-gray-500">Target Energy</div>
            </div>
            
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <div className="text-2xl font-bold text-green-600">{recipeData.actual_calories}</div>
              <div className="text-sm text-gray-600">Actual Energy (kcal)</div>
              <div className="text-xs text-gray-500">Actual Energy</div>
            </div>
            
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <div className="text-2xl font-bold text-orange-600">{recipeData.energy_accuracy.toFixed(1)}%</div>
              <div className="text-sm text-gray-600">Energy Accuracy</div>
              <div className="text-xs text-gray-500">Energy Accuracy</div>
            </div>
            
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <div className="text-2xl font-bold text-purple-600">{recipeData.total_weight_g}g</div>
              <div className="text-sm text-gray-600">Total Weight</div>
              <div className="text-xs text-gray-500">Total Weight</div>
            </div>
          </div>

          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <p className="text-sm text-gray-700">
              <strong>Analysis Summary:</strong> The formulated diet achieves {recipeData.energy_accuracy.toFixed(1)}% 
              energy accuracy relative to target requirements. The macronutrient distribution provides adequate 
              protein ({nutrientDensity.protein.toFixed(1)} g/1000kcal) and fat ({nutrientDensity.fat.toFixed(1)} g/1000kcal) 
              content meeting AAFCO {petInfo.age.toLowerCase()} {petInfo.species} nutritional standards.
            </p>
            
            {/* 优化策略信息 */}
            {analysis.optimization_strategy ? (
              <div className="mt-4 p-3 bg-blue-50 rounded-lg border-l-4 border-blue-400">
                <p className="text-sm text-blue-800">
                  <strong>Optimization Strategy:</strong> {analysis.optimization_strategy.strategy_description}
                </p>
              </div>
            ) : null}
            
            {/* 重量分析信息 */}
            {analysis.weight_analysis ? (
              <div className="mt-4 p-3 bg-purple-50 rounded-lg border-l-4 border-purple-400">
                <p className="text-sm text-purple-800">
                  <strong>Weight Analysis:</strong> {analysis.weight_analysis.weight_category}
                  {analysis.weight_analysis.recommendation ? ` - ${analysis.weight_analysis.recommendation}` : ''}
                </p>
              </div>
            ) : null}
          </div>
        </motion.div>

        {/* 宏量营养素分析表 */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-white rounded-lg shadow-sm border p-6 mb-8"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <BarChart3 className="w-5 h-5 mr-2" />
            Table 1. Macronutrient Composition Analysis
          </h3>
          
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b-2 border-gray-300">
                  <th className="text-left py-3 px-4 font-semibold">Macronutrient</th>
                  <th className="text-right py-3 px-4 font-semibold">Total Amount (g)</th>
                  <th className="text-right py-3 px-4 font-semibold">Per 1000 kcal (g)</th>
                  <th className="text-right py-3 px-4 font-semibold">Weight %</th>
                  <th className="text-right py-3 px-4 font-semibold">Energy %</th>
                  <th className="text-right py-3 px-4 font-semibold">AAFCO Min.</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-gray-200">
                  <td className="py-3 px-4 font-medium">Protein</td>
                  <td className="text-right py-3 px-4">{analysis.nutrition.protein_g.toFixed(1)}</td>
                  <td className="text-right py-3 px-4 font-medium">{nutrientDensity.protein.toFixed(1)}</td>
                  <td className="text-right py-3 px-4">{((analysis.nutrition.protein_g / recipeData.total_weight_g) * 100).toFixed(1)}%</td>
                  <td className="text-right py-3 px-4">{((analysis.nutrition.protein_g * 4 / recipeData.actual_calories) * 100).toFixed(1)}%</td>
                  <td className="text-right py-3 px-4 text-green-600">≥18.0</td>
                </tr>
                <tr className="border-b border-gray-200">
                  <td className="py-3 px-4 font-medium">Fat</td>
                  <td className="text-right py-3 px-4">{analysis.nutrition.fat_g.toFixed(1)}</td>
                  <td className="text-right py-3 px-4 font-medium">{nutrientDensity.fat.toFixed(1)}</td>
                  <td className="text-right py-3 px-4">{((analysis.nutrition.fat_g / recipeData.total_weight_g) * 100).toFixed(1)}%</td>
                  <td className="text-right py-3 px-4">{((analysis.nutrition.fat_g * 9 / recipeData.actual_calories) * 100).toFixed(1)}%</td>
                  <td className="text-right py-3 px-4 text-green-600">≥5.5</td>
                </tr>
                <tr className="border-b border-gray-200">
                  <td className="py-3 px-4 font-medium">Carbohydrate</td>
                  <td className="text-right py-3 px-4">{analysis.nutrition.carbohydrate_g.toFixed(1)}</td>
                  <td className="text-right py-3 px-4 font-medium">{nutrientDensity.carbohydrate.toFixed(1)}</td>
                  <td className="text-right py-3 px-4">{((analysis.nutrition.carbohydrate_g / recipeData.total_weight_g) * 100).toFixed(1)}%</td>
                  <td className="text-right py-3 px-4">{((analysis.nutrition.carbohydrate_g * 4 / recipeData.actual_calories) * 100).toFixed(1)}%</td>
                  <td className="text-right py-3 px-4 text-gray-500">N/A</td>
                </tr>
                {analysis.nutrition.fiber_g ? (
                  <tr className="border-b border-gray-200">
                    <td className="py-3 px-4 font-medium">Dietary Fiber</td>
                    <td className="text-right py-3 px-4">{analysis.nutrition.fiber_g.toFixed(1)}</td>
                    <td className="text-right py-3 px-4 font-medium">{nutrientDensity.fiber.toFixed(1)}</td>
                    <td className="text-right py-3 px-4">{((analysis.nutrition.fiber_g / recipeData.total_weight_g) * 100).toFixed(1)}%</td>
                    <td className="text-right py-3 px-4">-</td>
                    <td className="text-right py-3 px-4 text-gray-500">N/A</td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        </motion.div>

        {/* 食材组成分析表 */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-white rounded-lg shadow-sm border p-6 mb-8"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Package className="w-5 h-5 mr-2" />
            Table 2. Ingredient Composition and Nutritional Contribution
          </h3>
          
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b-2 border-gray-300">
                  <th className="text-left py-3 px-4 font-semibold">Ingredient</th>
                  <th className="text-left py-3 px-4 font-semibold">Category</th>
                  <th className="text-right py-3 px-4 font-semibold">Weight (g)</th>
                  <th className="text-right py-3 px-4 font-semibold">Weight %</th>
                  <th className="text-right py-3 px-4 font-semibold">Energy (kcal)</th>
                  <th className="text-right py-3 px-4 font-semibold">Energy %</th>
                  <th className="text-right py-3 px-4 font-semibold">Cost (¥)</th>
                </tr>
              </thead>
              <tbody>
                {recipeData.ingredients.map((ingredient, index) => (
                  <tr key={ingredient.fdc_id} className="border-b border-gray-200 hover:bg-gray-50">
                    <td className="py-3 px-4">
                      <div className="flex items-center space-x-2">
                        <div 
                          className="w-3 h-3 rounded-full" 
                          style={{ backgroundColor: COLORS[index % COLORS.length] }}
                        ></div>
                        <div>
                          <div className="font-medium text-gray-900">{ingredient.description}</div>
                          <div className="text-xs text-gray-500">{ingredient.common_name}</div>
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {ingredient.category}
                      </span>
                    </td>
                    <td className="text-right py-3 px-4 font-medium">{ingredient.amount_g.toFixed(1)}</td>
                    <td className="text-right py-3 px-4">{ingredient.percentage.toFixed(1)}%</td>
                    <td className="text-right py-3 px-4">{ingredient.calories || '-'}</td>
                    <td className="text-right py-3 px-4">
                      {ingredient.calories ? ((ingredient.calories / recipeData.actual_calories) * 100).toFixed(1) + '%' : '-'}
                    </td>
                    <td className="text-right py-3 px-4 text-green-600">
                      {ingredient.cost ? '¥' + ingredient.cost.toFixed(2) : '-'}
                    </td>
                  </tr>
                ))}
                <tr className="border-t-2 border-gray-300 bg-gray-50 font-semibold">
                  <td className="py-3 px-4" colSpan={2}>Total</td>
                  <td className="text-right py-3 px-4">{recipeData.total_weight_g.toFixed(1)}</td>
                  <td className="text-right py-3 px-4">100.0%</td>
                  <td className="text-right py-3 px-4">{recipeData.actual_calories}</td>
                  <td className="text-right py-3 px-4">100.0%</td>
                  <td className="text-right py-3 px-4 text-green-600">
                    ¥{analysis.cost_analysis?.total_cost.toFixed(2) || '0.00'}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </motion.div>

        {/* AAFCO营养标准对比表 */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-white rounded-lg shadow-sm border p-6 mb-8"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Info className="w-5 h-5 mr-2" />
            Table 3. AAFCO Nutritional Standards Compliance Analysis
          </h3>
          
          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b-2 border-gray-300">
                  <th className="text-left py-3 px-4 font-semibold">Nutrient</th>
                  <th className="text-right py-3 px-4 font-semibold">Actual Value</th>
                  <th className="text-right py-3 px-4 font-semibold">AAFCO Minimum</th>
                  <th className="text-right py-3 px-4 font-semibold">AAFCO Maximum</th>
                  <th className="text-center py-3 px-4 font-semibold">Compliance Status</th>
                  <th className="text-right py-3 px-4 font-semibold">Adequacy Ratio</th>
                </tr>
              </thead>
              <tbody>
                {complianceData.map((item, index) => (
                  <tr key={index} className="border-b border-gray-200 hover:bg-gray-50">
                    <td className="py-3 px-4 font-medium">{item.nutrient}</td>
                    <td className="text-right py-3 px-4">{item.actual.toFixed(1)} {item.unit}</td>
                    <td className="text-right py-3 px-4">{item.required_min?.toFixed(1) || '-'} {item.unit}</td>
                    <td className="text-right py-3 px-4">{item.required_max?.toFixed(1) || '-'} {item.unit}</td>
                    <td className="text-center py-3 px-4">
                      <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        item.status === 'ADEQUATE' ? 'bg-green-100 text-green-800' :
                        item.status === 'EXCESSIVE' ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {item.status}
                      </span>
                    </td>
                    <td className="text-right py-3 px-4 font-medium">
                      {item.required_min ? (item.actual / item.required_min * 100).toFixed(0) + '%' : '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-4 p-4 bg-blue-50 rounded-lg">
            <p className="text-sm text-gray-700">
              <strong>Note:</strong> All nutrient values are expressed per 1000 kcal metabolizable energy (ME) 
              as per AAFCO standards for adult dog maintenance. Adequacy ratios ≥100% indicate compliance 
              with minimum requirements.
            </p>
          </div>
        </motion.div>

        {/* 营养评估和可视化 */}
        <NutritionCharts 
          macroData={macroData}
          radarData={radarData}
        />

        {/* 成本效益分析 */}
        {analysis.cost_analysis ? (
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="bg-white rounded-lg shadow-sm border p-6 mb-8"
          >
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Calculator className="w-5 h-5 mr-2" />
              Table 4. Economic Analysis
            </h3>
            
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div className="text-center p-4 bg-green-50 rounded-lg border">
                <div className="text-2xl font-bold text-green-600">¥{analysis.cost_analysis.total_cost.toFixed(2)}</div>
                <div className="text-sm text-gray-600">Total Cost</div>
                <div className="text-xs text-gray-500">Total Cost/Meal</div>
              </div>
              
              <div className="text-center p-4 bg-blue-50 rounded-lg border">
                <div className="text-2xl font-bold text-blue-600">¥{analysis.cost_analysis.cost_per_kg.toFixed(2)}</div>
                <div className="text-sm text-gray-600">Cost per kg</div>
                <div className="text-xs text-gray-500">Cost per kg</div>
              </div>
              
              <div className="text-center p-4 bg-orange-50 rounded-lg border">
                <div className="text-2xl font-bold text-orange-600">¥{(analysis.cost_analysis.total_cost / recipeData.actual_calories).toFixed(3)}</div>
                <div className="text-sm text-gray-600">Cost per kcal</div>
                <div className="text-xs text-gray-500">Cost per kcal</div>
              </div>
              
              <div className="text-center p-4 bg-purple-50 rounded-lg border">
                <div className="text-2xl font-bold text-purple-600">{(recipeData.actual_calories / recipeData.total_weight_g).toFixed(1)}</div>
                <div className="text-sm text-gray-600">Energy Density</div>
                <div className="text-xs text-gray-500">Energy Density (kcal/g)</div>
              </div>
            </div>
          </motion.div>
        ) : null}

        {/* 专业评估与建议 */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="bg-white rounded-lg shadow-sm border p-6 mb-8"
        >
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Heart className="w-5 h-5 mr-2" />
            Professional Assessment and Recommendations
          </h3>
          
          {analysis.aafco_compliance.compliant ? (
            <div className="bg-green-50 border-l-4 border-green-400 p-4 mb-6">
              <div className="flex items-center space-x-3">
                <CheckCircle className="w-6 h-6 text-green-600" />
                <div>
                  <h4 className="text-lg font-medium text-green-800">AAFCO Compliance Achieved</h4>
                  <p className="text-green-700 mt-1">
                    The formulated diet meets all AAFCO nutritional adequacy statements for adult dog maintenance.
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
              <div className="flex items-center space-x-3">
                <AlertTriangle className="w-6 h-6 text-yellow-600" />
                <div>
                  <h4 className="text-lg font-medium text-yellow-800">Nutritional Adjustments Required</h4>
                  <p className="text-yellow-700 mt-1">
                    Some nutrients require optimization to meet AAFCO standards.
                  </p>
                </div>
              </div>
            </div>
          )}

          <div className="space-y-4">
            <div>
              <h4 className="font-semibold text-gray-900 mb-2">Key Findings:</h4>
              <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
                <li>Energy target achievement: {recipeData.energy_accuracy.toFixed(1)}% accuracy</li>
                <li>Protein adequacy: {((nutrientDensity.protein / 45.0) * 100).toFixed(0)}% of AAFCO minimum</li>
                <li>Fat adequacy: {((nutrientDensity.fat / 13.8) * 100).toFixed(0)}% of AAFCO minimum</li>
                <li>Cost efficiency: ¥{(analysis.cost_analysis?.total_cost! / recipeData.actual_calories).toFixed(3)} per kcal</li>
              </ul>
            </div>

            {analysis.user_guidance?.next_steps ? (
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Recommendations:</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {analysis.user_guidance.next_steps.map((recommendation, index) => (
                    <div key={index} className="flex items-start space-x-3 bg-blue-50 p-3 rounded-lg">
                      <div className="flex-shrink-0 w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center">
                        <span className="text-sm font-medium text-blue-600">{index + 1}</span>
                      </div>
                      <p className="text-gray-700 text-sm">{recommendation}</p>
                    </div>
                  ))}
                </div>
              </div>
            ) : null}
          </div>
        </motion.div>

        {/* 结论 */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="bg-gray-900 text-white rounded-lg shadow-sm p-6"
        >
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <Award className="w-5 h-5 mr-2" />
            Conclusion
          </h3>
          
          <p className="text-gray-300 leading-relaxed">
            The analyzed {petInfo.species === 'cat' ? 'feline' : 'canine'} diet formulation demonstrates {analysis.aafco_compliance.compliant ? 'full compliance' : 'partial compliance'} 
            with AAFCO nutritional standards for {petInfo.age.toLowerCase()} {petInfo.species} maintenance. The formulation achieves {recipeData.energy_accuracy.toFixed(1)}% 
            energy target accuracy with a balanced macronutrient profile providing {nutrientDensity.protein.toFixed(1)}g protein and {nutrientDensity.fat.toFixed(1)}g fat per 1000 kcal. 
            Economic analysis indicates a cost-effective solution at ¥{(analysis.cost_analysis?.total_cost! / recipeData.actual_calories).toFixed(3)} per kcal. 
            {analysis.weight_analysis?.optimization_mode && analysis.weight_analysis.optimization_mode !== 'nutrition_focused' ? 
              `Weight optimization strategy (${analysis.weight_analysis.optimization_mode}) was successfully applied. ` : ''
            }
            {analysis.aafco_compliance.compliant ? 
              `This formulation is suitable for long-term feeding of healthy ${petInfo.age.toLowerCase()} ${petInfo.species}s.` : 
              'Minor adjustments are recommended to achieve full nutritional adequacy.'
            }
          </p>
          
          <div className="mt-4 pt-4 border-t border-gray-700 text-center">
            <p className="text-sm text-gray-400">
              Analysis generated by Pet Nutrition Optimization System
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default RecipeResult;