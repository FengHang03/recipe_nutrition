import React, { useEffect, useRef, useCallback } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2, AlertCircle, Heart } from 'lucide-react';

// 导入 logo 图片
import logoImage from './image/logo20.jpg';

import Homepage from './components/Homepage';
import PetForm from './components/forms/PetForm';
import RecipeResult from './components/RecipeResult';
import LoadingScreen from './components/ui/LoadingScreen';
import ErrorBoundary from './components/ui/ErrorBoundary';

import { 
  usePetStore, 
  usePet, 
  useRecipe, 
  useIsLoading, 
  useIsGenerating, 
  useError,
  useCurrentStep
} from './stores/usePetStore';
import { PetFormData, RecipeGenerationRequest } from './types';

// 创建 React Query 客户端
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5分钟
      refetchOnWindowFocus: false,
    },
  },
});

// 主应用组件
const MainApp: React.FC = () => {
  const pet = usePet();
  const recipe = useRecipe();
  const isLoading = useIsLoading();
  const isGenerating = useIsGenerating();
  const error = useError();
  const currentStep = useCurrentStep();
  
  // 移动端菜单状态
  const [isMobileMenuOpen, setIsMobileMenuOpen] = React.useState(false);
  
  // 🔧 修复：直接从 store 获取操作函数，避免复合选择器
  const createPet = usePetStore((state) => state.createPet);
  const generateRecipe = usePetStore((state) => state.generateRecipe);
  const setCurrentStep = usePetStore((state) => state.setCurrentStep);
  const reset = usePetStore((state) => state.reset);
  const setError = usePetStore((state) => state.setError);

  // 🔧 使用 ref 防止重复触发
  const hasTriggeredGeneration = useRef(false);
  const mobileMenuRef = useRef<HTMLDivElement>(null);

  // 页面切换动画配置
  const pageVariants = {
    initial: { opacity: 0, y: 20 },
    in: { opacity: 1, y: 0 },
    out: { opacity: 0, y: -20 }
  };

  const pageTransition = {
    type: 'tween' as const,
    ease: 'anticipate' as const,
    duration: 0.5
  };

  // 🔧 修复：使用 useCallback 稳定函数引用
  const handleGenerateRecipe = useCallback(async () => {
    if (!pet?.id || isGenerating || hasTriggeredGeneration.current) {
      return;
    }

    hasTriggeredGeneration.current = true; // 设置标志，防止重复调用

    const request: RecipeGenerationRequest = {
      pet_id: pet.id,
      target_calories: pet.daily_calories_kcal
    };

    console.log('🚀 Generating recipe with request:', request);

    try {
      await generateRecipe(request);
      setCurrentStep(2);
      console.log('✅ Recipe generation initiated successfully');
    } catch (error) {
      console.error('❌ Recipe generation failed:', error);
      hasTriggeredGeneration.current = false; // 失败时重置
    }
  }, [pet?.id, pet?.daily_calories_kcal, isGenerating, generateRecipe, setCurrentStep]);

  useEffect(() => {
    if (recipe && currentStep === 1 && !isGenerating) {
      console.log('📋 Recipe generated, checking status:', recipe.status);

      if (recipe.status === 'Success') {
        setCurrentStep(2);
        console.log('✅ Moving to recipe result page');
      } else if (recipe.status === 'Error') {
        console.error('❌ Recipe generation failed:', recipe.error);
        setError(recipe.error || '配方生成失败');
        hasTriggeredGeneration.current = false; // 重置，允许重试
      }
    } 
  }, [currentStep, recipe, isGenerating, setCurrentStep, setError]);

  // 🔧 修复：处理宠物表单提交
  const handlePetFormSubmit = useCallback(async (data: PetFormData) => {
    try {
      await createPet(data);
      console.log('✅ Pet created successfully');
    } catch (error) {
      console.error('❌ Failed to create pet:', error);
    }
  }, [createPet]);

  // 🔧 修复：处理重新生成配方
  const handleNewRecipe = useCallback(() => {
    hasTriggeredGeneration.current = false; // 重置标志
    setCurrentStep(0);
    reset();
  }, [setCurrentStep, reset]);

  // 🔧 修复：监听宠物创建完成，自动跳转
  useEffect(() => {
    if (pet && !recipe && currentStep === 0 && !isLoading && !isGenerating) {
      setCurrentStep(1);
    }
  }, [pet, recipe, currentStep, isLoading, isGenerating, setCurrentStep]);

  // 🔧 修复：监听步骤变化，在步骤1时自动生成配方
  useEffect(() => {
    if (pet && !recipe && currentStep === 1 && !isGenerating && !hasTriggeredGeneration.current) {
      handleGenerateRecipe();
    }
  }, [pet, recipe, currentStep, isGenerating, handleGenerateRecipe]);

  // 🔧 修复：监听配方生成完成，自动跳转到结果页
  useEffect(() => {
    if (recipe && currentStep === 1 && !isGenerating) {
      setCurrentStep(2);
    }
  }, [recipe, currentStep, isGenerating, setCurrentStep]);

  // 点击外部关闭移动端菜单
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (mobileMenuRef.current && !mobileMenuRef.current.contains(event.target as Node)) {
        setIsMobileMenuOpen(false);
      }
    };

    if (isMobileMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isMobileMenuOpen]);

  // 处理保存配方
  const handleSaveRecipe = useCallback(() => {
    console.log('保存配方功能待实现');
  }, []);

  // 处理分享配方
  const handleShareRecipe = useCallback(() => {
    console.log('分享配方功能待实现');
  }, []);

  // 渲染加载屏幕
  if (isLoading || isGenerating) {
    return (
      <LoadingScreen 
        message={isLoading ? 'Creating pet profile...' : 'Generating nutrition recipe...'}
        submessage={isGenerating ? 'This may take a few seconds, please wait' : undefined}
      />
    );
  }

  // 根据当前步骤渲染不同页面
  const renderCurrentStep = () => {
    switch (currentStep) {
      case 0:
        return (
          <motion.div
            key="homepage"
            initial="initial"
            animate="in"
            exit="out"
            variants={pageVariants}
            transition={pageTransition}
          >
            <Homepage onGetStarted={() => setCurrentStep(1)} />
          </motion.div>
        );

      case 1:
        if (!pet) {
          return (
            <motion.div
              key="pet-form"
              initial="initial"
              animate="in"
              exit="out"
              variants={pageVariants}
              transition={pageTransition}
            >
              <PetForm 
                onSubmit={handlePetFormSubmit}
                onNext={() => setCurrentStep(2)}
              />
            </motion.div>
          );
        } else {
          // 如果已有宠物信息，显示生成中状态
          return (
            <LoadingScreen 
              message="Generating an exclusive recipe for your pet..."
              submessage="AI and Linear Programming Algorithm Optimization Based on AAFCO Nutrition Standard"
            />
          );
        }

      case 2:
        // 🔧 检查配方状态，只在成功时显示结果
        if (recipe && recipe.status === 'Success') {
          return (
            <motion.div
              key="recipe-result"
              initial="initial"
              animate="in"
              exit="out"
              variants={pageVariants}
              transition={pageTransition}
            >
              <RecipeResult 
                recipe={recipe}
                onSave={handleSaveRecipe}
                onShare={handleShareRecipe}
                onNewRecipe={handleNewRecipe}
              />
            </motion.div>
          );
        } else if (recipe && recipe.status === 'Error') {
          // 配方生成失败，显示错误页面
          return (
            <motion.div
              key="recipe-error"
              initial="initial"
              animate="in"
              exit="out"
              variants={pageVariants}
              transition={pageTransition}
              className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 to-orange-50"
            >
              <div className="max-w-md mx-auto bg-white rounded-lg shadow-md p-6 text-center">
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <AlertCircle className="w-8 h-8 text-red-600" />
                </div>
                <h2 className="text-xl font-semibold text-gray-900 mb-2">Recipe Generation Failed</h2>
                <p className="text-gray-600 mb-4">{recipe.error}</p>
                <button
                  onClick={handleNewRecipe}
                  className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 transition-colors"
                >
                  Generate New Recipe
                </button>
              </div>
            </motion.div>
          );
        } else {
          // 没有配方数据，返回首页
          return (
            <motion.div
              key="homepage"
              initial="initial"
              animate="in"
              exit="out"
              variants={pageVariants}
              transition={pageTransition}
            >
              <Homepage onGetStarted={() => setCurrentStep(1)} />
            </motion.div>
          );
        }

      default:
        return (
          <motion.div
            key="homepage"
            initial="initial"
            animate="in"
            exit="out"
            variants={pageVariants}
            transition={pageTransition}
          >
            <Homepage onGetStarted={() => setCurrentStep(1)} />
          </motion.div>
        );
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-green-50">
      {/* 全局错误提示 */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -50 }}
            className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50"
          >
            <div className="bg-red-50 border border-red-200 rounded-lg shadow-lg p-4 max-w-md">
              <div className="flex items-center">
                <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
                <p className="text-red-800 font-medium">Error Occurred</p>
                <button
                  onClick={() => setError(null)}
                  className="ml-auto text-red-600 hover:text-red-800"
                >
                  ×
                </button>
              </div>
              <p className="text-red-600 text-sm mt-1">{error}</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 导航栏 */}
      <nav className="bg-white shadow-sm border-b border-gray-200" ref={mobileMenuRef}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo 区域 */}
            <div 
              className="flex items-center space-x-3 cursor-pointer"
              onClick={handleNewRecipe}
            >
              <img 
                src={logoImage} 
                alt="Tuanty Nutrition Logo" 
                className="w-10 h-10 rounded-lg object-cover shadow-sm"
              />
              <span className="text-xl font-semibold text-gray-900">Tuanty Nutrition</span>
            </div>
            
            {/* 中央菜单 */}
            <div className="hidden md:flex items-center space-x-8">
              <button
                onClick={() => {
                  // 如果当前没有宠物信息，跳转到宠物表单页面
                  if (!pet) {
                    setCurrentStep(1);
                  } else {
                    // 如果已有宠物信息，重新开始制作配方流程
                    handleNewRecipe();
                  }
                }}
                className="text-gray-700 hover:text-green-600 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 hover:bg-green-50"
              >
                Recipes
              </button>
              <button
                className="text-gray-700 hover:text-green-600 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 hover:bg-green-50"
                onClick={() => console.log('Products clicked')}
              >
                Products
              </button>
              <button
                className="text-gray-700 hover:text-green-600 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 hover:bg-green-50"
                onClick={() => console.log('Support clicked')}
              >
                Support
              </button>
              <button
                className="text-gray-700 hover:text-green-600 px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 hover:bg-green-50"
                onClick={() => console.log('About Us clicked')}
              >
                About Us
              </button>
            </div>
            
            {/* 步骤指示器 */}
            {currentStep > 0 && (
              <div className="hidden lg:flex items-center space-x-4">
                <div className={`flex items-center space-x-2 ${
                  currentStep >= 1 ? 'text-green-600' : 'text-gray-400'
                }`}>
                  <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center text-xs font-bold ${
                    currentStep >= 1 ? 'border-green-600 bg-green-600 text-white' : 'border-gray-300'
                  }`}>
                    1
                  </div>
                  <span className="text-sm font-medium">Pet Information</span>
                </div>
                
                <div className={`w-8 h-0.5 ${
                  currentStep >= 2 ? 'bg-green-600' : 'bg-gray-300'
                }`} />
                
                <div className={`flex items-center space-x-2 ${
                  currentStep >= 2 ? 'text-green-600' : 'text-gray-400'
                }`}>
                  <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center text-xs font-bold ${
                    currentStep >= 2 ? 'border-green-600 bg-green-600 text-white' : 'border-gray-300'
                  }`}>
                    2
                  </div>
                  <span className="text-sm font-medium">Nutrition Recipe</span>
                </div>
              </div>
            )}
            
            {/* 移动端菜单按钮 */}
            <div className="md:hidden">
              <button
                className="text-gray-700 hover:text-green-600 p-2"
                onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={isMobileMenuOpen ? "M6 18L18 6M6 6l12 12" : "M4 6h16M4 12h16M4 18h16"} />
                </svg>
              </button>
            </div>
          </div>
          
          {/* 移动端下拉菜单 */}
          <AnimatePresence>
            {isMobileMenuOpen && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="md:hidden bg-white border-t border-gray-200"
              >
                <div className="px-4 py-2 space-y-1">
                  <button
                    onClick={() => {
                      if (!pet) {
                        setCurrentStep(1);
                      } else {
                        handleNewRecipe();
                      }
                      setIsMobileMenuOpen(false);
                    }}
                    className="block w-full text-left px-3 py-2 text-gray-700 hover:text-green-600 hover:bg-green-50 rounded-md transition-colors duration-200"
                  >
                    Recipes
                  </button>
                  <button
                    onClick={() => {
                      console.log('Products clicked');
                      setIsMobileMenuOpen(false);
                    }}
                    className="block w-full text-left px-3 py-2 text-gray-700 hover:text-green-600 hover:bg-green-50 rounded-md transition-colors duration-200"
                  >
                    Products
                  </button>
                  <button
                    onClick={() => {
                      console.log('Support clicked');
                      setIsMobileMenuOpen(false);
                    }}
                    className="block w-full text-left px-3 py-2 text-gray-700 hover:text-green-600 hover:bg-green-50 rounded-md transition-colors duration-200"
                  >
                    Support
                  </button>
                  <button
                    onClick={() => {
                      console.log('About Us clicked');
                      setIsMobileMenuOpen(false);
                    }}
                    className="block w-full text-left px-3 py-2 text-gray-700 hover:text-green-600 hover:bg-green-50 rounded-md transition-colors duration-200"
                  >
                    About Us
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </nav>

      {/* 主内容区域 */}
      <main className="min-h-screen">
        <AnimatePresence mode="wait">
          {renderCurrentStep()}
        </AnimatePresence>
      </main>

      {/* 页脚 */}
      <footer className="bg-white border-t border-gray-200 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <div className="flex items-center justify-center space-x-3 mb-4">
              <img 
                src={logoImage} 
                alt="Tuanty Nutrition Logo" 
                className="w-8 h-8 rounded-lg object-cover"
              />
              <span className="text-lg font-semibold text-gray-900">Tuanty Nutrition</span>
            </div>
            <p className="text-gray-600 mb-4">
              Science-based Pet Nutrition Recipe Generation System
            </p>
            <p className="text-sm text-gray-500">
              © 2025 Tuanty Nutrition. This system is for reference only. Please consult a professional veterinarian for special cases.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

// 主App组件，包含Router和QueryClient
const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <ErrorBoundary>
        <Router>
          <Routes>
            <Route path="/*" element={<MainApp />} />
          </Routes>
        </Router>
      </ErrorBoundary>
    </QueryClientProvider>
  );
};

export default App;