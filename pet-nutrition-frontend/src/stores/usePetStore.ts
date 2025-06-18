import { create } from 'zustand';
import { devtools } from 'zustand/middleware';
import { petAPI, recipeAPI } from '../services/api';
import type { 
  Pet, 
  PetFormData, 
  RecipeGenerationRequest, 
  RecipeResult,
  LoadingState,
  ErrorState,
  CurrentStep
} from '../types';

// State
interface PetStore {
  // State
  pet: Pet | null;
  recipe: RecipeResult | null;
  isLoading: LoadingState;
  isGenerating: LoadingState;
  error: ErrorState;
  currentStep: CurrentStep;

  // Pet-related operations
  createPet: (data: PetFormData) => Promise<void>;
  updatePet: (id: number, data: Partial<PetFormData>) => Promise<void>;
  clearPet: () => void;

  // Recipe-related operations
  generateRecipe: (request: RecipeGenerationRequest) => Promise<void>;
  clearRecipe: () => void;

  // UI state operations
  setCurrentStep: (step: CurrentStep) => void;
  setLoading: (loading: LoadingState) => void;
  setGenerating: (generating: LoadingState) => void;
  setError: (error: ErrorState) => void;
  reset: () => void;
}

const initialState = {
  pet: null,
  recipe: null,
  isLoading: false,
  isGenerating: false,
  error: null,
  currentStep: 0 as CurrentStep,
};

export const usePetStore = create<PetStore>()(
  devtools(
    (set, get) => ({
      ...initialState,

      // Pet-related operations
      createPet: async (data: PetFormData) => {
        console.log('🐕 Creating pet with data:', data);
        
        set((state) => ({ 
          ...state, 
          isLoading: true, 
          error: null 
        }), false, 'createPet/start');

        try {
          const response = await petAPI.createPet(data);
          console.log('✅ Pet created successfully:', response);
          
          // Convert response to Pet object
          const pet: Pet = {
            ...data,
            id: response.data.pet_id,
            daily_calories_kcal: response.data.daily_calories_kcal
          };
          
          set((state) => ({ 
            ...state, 
            pet, 
            isLoading: false,
            currentStep: 1,
            error: null 
          }), false, 'createPet/success');

        } catch (error) {
          console.error('❌ Failed to create pet:', error);
          const errorMessage = error instanceof Error ? error.message : 'Failed to create pet';
          
          set((state) => ({ 
            ...state, 
            isLoading: false, 
            error: errorMessage 
          }), false, 'createPet/error');
          
          throw error;
        }
      },

      updatePet: async (id: number, data: Partial<PetFormData>) => {
        try {
          const pet = await petAPI.updatePet(id, data);
          set({ pet });
        } catch (error) {
          console.error('Failed to update pet:', error);
          throw error;
        }
      },

      clearPet: () => {
        set({ pet: null });
      },

      // Recipe-related operations
      generateRecipe: async (request: RecipeGenerationRequest) => {
        console.log('🍽️ Generating recipe with request:', request);
        
        set((state) => ({ 
          ...state, 
          isGenerating: true, 
          error: null 
        }), false, 'generateRecipe/start');

        try {
          const recipe = await recipeAPI.generateRecipe(request);
          console.log('✅ Recipe generated successfully:', recipe);
          
          // 🔧 Fix: Set all related states at once
          set((state) => ({ 
            ...state, 
            recipe, 
            isGenerating: false,
            error: recipe.status !== 'Success' ? (recipe.error || 'Recipe generation failed') : null
          }), false, 'generateRecipe/success');

        } catch (error) {
          console.error('❌ Failed to generate recipe:', error);
          const errorMessage = error instanceof Error ? error.message : 'Recipe generation failed';
          
          set((state) => ({ 
            ...state, 
            isGenerating: false, 
            error: errorMessage 
          }), false, 'generateRecipe/error');
          
          throw error;
        }
      },

      clearRecipe: () => {
        set({ recipe: null });
      },

      // UI state operations
      setCurrentStep: (step: CurrentStep) => {
        console.log(`📍 Setting current step to: ${step}`);
        set({ currentStep: step });
      },

      setLoading: (loading: LoadingState) => {
        set({ isLoading: loading });
      },

      setGenerating: (generating: LoadingState) => {
        set({ isGenerating: generating });
      },

      setError: (error: ErrorState) => {
        set({ error });
      },

      reset: () => {
        console.log('🔄 Resetting store to initial state');
        set(initialState, false, 'reset');
      },
    }),
    {
      name: 'pet-store',
      enabled: process.env.NODE_ENV === 'development',
    }
  )
);

// ✅ Simple selector functions (these are safe)
export const usePet = () => usePetStore((state) => state.pet);
export const useRecipe = () => usePetStore((state) => state.recipe);
export const useIsLoading = () => usePetStore((state) => state.isLoading);
export const useIsGenerating = () => usePetStore((state) => state.isGenerating);
export const useError = () => usePetStore((state) => state.error);
export const useCurrentStep = () => usePetStore((state) => state.currentStep);

// 🚨 Remove compound selectors! These are the root cause of infinite loops
// Don't use these:
// export const useHasPet = () => usePetStore((state) => !!state.pet);
// export const useHasRecipe = () => usePetStore((state) => !!state.recipe);
// export const useIsReady = () => usePetStore((state) => !state.isLoading && !state.isGenerating);