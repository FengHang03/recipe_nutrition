import { create } from 'zustand';
import { subscribeWithSelector, devtools } from 'zustand/middleware';
import { 
  Pet, 
  PetFormData, 
  RecipeResult, 
  RecipeGenerationRequest,
  CreatePetResponse 
} from '../types';
import { petAPI, recipeAPI } from '../services/api';

interface PetStore {
  // 状态
  currentPet: Pet | null;
  petCreationResult: CreatePetResponse | null;
  currentRecipe: RecipeResult | null;
  isLoading: boolean;
  isGenerating: boolean;
  error: string | null;
  currentStep: number;

  // Pet相关操作
  createPet: (petData: PetFormData) => Promise<void>;
  setPet: (pet: Pet) => void;
  clearPet: () => void;

  // Recipe相关操作
  generateRecipe: (request: RecipeGenerationRequest) => Promise<void>;
  setRecipe: (recipe: RecipeResult) => void;
  clearRecipe: () => void;

  // UI状态操作
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  setCurrentStep: (step: number) => void;
  nextStep: () => void;
  prevStep: () => void;
  reset: () => void;
}

export const usePetStore = create<PetStore>()(
  subscribeWithSelector(
    devtools(
      (set, get) => ({
        // 初始状态
        currentPet: null,
        petCreationResult: null,
        currentRecipe: null,
        isLoading: false,
        isGenerating: false,
        error: null,
        currentStep: 0,

        // Pet相关操作
        createPet: async (petData: PetFormData) => {
          console.log('🔄 Creating pet with data:', petData);

          const { isLoading } = get();
          if (isLoading) {
            console.log('🏪 Store: Already loading, skipping');
            return;
          }
          console.log('🏪 Store: Setting loading state');
          set({ isLoading: true, error: null });
          
          try {
            console.log('🏪 Store: Calling petAPI.createPet...');
            const result = await petAPI.createPet(petData);
            console.log('🏪 Store: Pet API result:', result);
            
            const pet: Pet = {
              ...petData,
              id: result.data.pet_id,
              daily_calories_kcal: result.data.daily_calories_kcal
            };

            console.log('🏪 Store: Setting pet in state:', pet);
            set({ 
              currentPet: pet,
              petCreationResult: result,
              isLoading: false 
            });
            console.log('✅ Store: Pet created successfully');
          } catch (error) {
            console.error('❌ Store: Create pet failed:', error);
            const errorMessage = error instanceof Error ? error.message : '创建宠物失败';
            set({ 
              error: errorMessage, 
              isLoading: false 
            });
            throw error;
          }
        },

        setPet: (pet: Pet) => {
          set({ currentPet: pet, error: null });
        },

        clearPet: () => {
          set({ 
            currentPet: null, 
            petCreationResult: null,
            error: null 
          });
        },

        // Recipe相关操作
        generateRecipe: async (request: RecipeGenerationRequest) => {
          const { isGenerating } = get();
          if (isGenerating) return;

          set({ isGenerating: true, error: null });
          
          try {
            const recipe = await recipeAPI.generateRecipe(request);
            
            // 🔧 修复：一次性设置所有相关状态
            set({ 
              currentRecipe: recipe,
              isGenerating: false,
              error: recipe.status !== 'Success' ? (recipe.error || '配方生成失败') : null
            });
          } catch (error) {
            const errorMessage = error instanceof Error ? error.message : '配方生成失败';
            set({ 
              error: errorMessage, 
              isGenerating: false 
            });
            throw error;
          }
        },

        setRecipe: (recipe: RecipeResult) => {
          set({ currentRecipe: recipe, error: null });
        },

        clearRecipe: () => {
          set({ 
            currentRecipe: null, 
            error: null 
          });
        },

        // UI状态操作
        setLoading: (loading: boolean) => {
          set({ isLoading: loading });
        },

        setError: (error: string | null) => {
          set({ error });
        },

        setCurrentStep: (step: number) => {
          set({ currentStep: step });
        },

        nextStep: () => {
          const { currentStep } = get();
          set({ currentStep: currentStep + 1 });
        },

        prevStep: () => {
          const { currentStep } = get();
          if (currentStep > 0) {
            set({ currentStep: currentStep - 1 });
          }
        },

        reset: () => {
          set({
            currentPet: null,
            petCreationResult: null,
            currentRecipe: null,
            isLoading: false,
            isGenerating: false,
            error: null,
            currentStep: 0
          });
        }
      })
    )
  )
);

// ✅ 简单选择器函数（这些是安全的）
export const usePet = () => usePetStore((state) => state.currentPet);
export const useRecipe = () => usePetStore((state) => state.currentRecipe);
export const useIsLoading = () => usePetStore((state) => state.isLoading);
export const useIsGenerating = () => usePetStore((state) => state.isGenerating);
export const useError = () => usePetStore((state) => state.error);
export const useCurrentStep = () => usePetStore((state) => state.currentStep);

// 🚨 删除复合选择器！这些是导致无限循环的根本原因
// 不要使用这些：
// export const usePetActions = () => { ... }
// export const useRecipeActions = () => { ... }
// export const useUIActions = () => { ... }