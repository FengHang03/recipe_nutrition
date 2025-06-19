import axios, { type AxiosResponse } from 'axios';
import type{ 
  Pet, 
  PetFormData, 
  RecipeResult, 
  RecipeGenerationRequest,
  ApiResponse,
  CreatePetResponse,
} from '../types';

import { LifeStage, ActivityLevel, PhysiologicalStatus } from '../types/index';

// Configure base URL - dynamically use current host
const getApiBaseUrl = () => {
  // 在开发环境中，如果有环境变量则使用环境变量
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL;
  }
  
  const currentHost = window.location.hostname;
  
  // 检查是否是ngrok域名访问
  if (currentHost.includes('ngrok-free.app')) {
    // 如果是通过ngrok的前端域名访问，使用ngrok的后端域名
    return 'https://a92e-113-87-81-162.ngrok-free.app';
  }
  
  // 本地开发环境或局域网访问
  if (currentHost === 'localhost' || currentHost === '127.0.0.1') {
    return 'http://localhost:8000';
  }
  
  // 局域网IP访问
  return `http://${currentHost}:8000`;
};

const API_BASE_URL = getApiBaseUrl();

// 调试信息
console.log('🔧 API Configuration:', {
  currentHost: window.location.hostname,
  currentOrigin: window.location.origin,
  apiBaseUrl: API_BASE_URL,
  envApiUrl: import.meta.env.VITE_API_BASE_URL
});

// Create axios instance
const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// 🔧 Add life stage calculation function
const calculateLifeStage = (species: string, age_months: number): LifeStage => {
  if (species === 'dog') {
    return age_months < 12 ? LifeStage.DOG_PUPPY : LifeStage.DOG_ADULT;
  } else if (species === 'cat') {
    return age_months < 12 ? LifeStage.CAT_KITTEN : LifeStage.CAT_ADULT;
  }
  return LifeStage.DOG_ADULT; // Default value
};

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    console.log('📤 API Request:', {
      method: config.method?.toUpperCase(),
      url: config.url,
      data: config.data
    });
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 🔧 Enhanced response interceptor with detailed error information
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    console.log('📥 API Response:', {
      status: response.status,
      url: response.config.url,
      data: response.data
    });
    return response;
  },
  (error) => {
    // Detailed error handling
    if (axios.isAxiosError(error)) {
      console.error('🚨 API Error Details:', {
        status: error.response?.status,
        statusText: error.response?.statusText,
        data: error.response?.data,
        url: error.config?.url,
        method: error.config?.method
      });
      
      // 🔧 Specifically handle 422 validation errors
      if (error.response?.status === 422) {
        console.error('📋 Detailed validation error:', error.response.data);
        
        let detailedMessage = 'Data validation failed';
        if (error.response.data?.detail) {
          const details = Array.isArray(error.response.data.detail) 
            ? error.response.data.detail 
            : [error.response.data.detail];
          
          const fieldErrors = details.map((d: any) => {
            const field = d.loc ? d.loc.join('.') : 'unknown';
            return `${field}: ${d.msg}`;
          }).join('; ');
          
          detailedMessage = `Validation failed: ${fieldErrors}`;
        }
        
        return Promise.reject(new Error(detailedMessage));
      }
    }
    
    const errorMessage = error.response?.data?.message || 
                        error.response?.data?.detail || 
                        error.message || 
                        'Network error';
    console.error('API Error:', errorMessage);
    return Promise.reject(new Error(errorMessage));
  }
);

// API method definitions
export const petAPI = {
  // 🔧 Fix create pet method
  async createPet(petData: PetFormData): Promise<CreatePetResponse> {
    console.log('📤 Creating pet with data:', petData);

    try {
      // 🔧 Data mapping and transformation to match backend model
      const apiData = {
        // Basic information
        name: petData.name || null,
        species: petData.species,
        breed: petData.breed || null,
        
        // Numeric information - ensure correct type
        age_months: Number(petData.age_months),
        weight_kg: Number(petData.weight_kg),
        
        // Enum values - should now match backend enums
        activity_level: petData.activity_level,
        physiological_status: petData.physiological_status,
        
        // 🔧 Calculate life stage
        life_stage: calculateLifeStage(petData.species, petData.age_months),
        
        // Array fields
        health_conditions: petData.health_conditions || [],
        allergies: null, // Temporarily empty
        
        // 🔧 Lactation-related fields (only send during lactation)
        ...(petData.physiological_status === 'lactating' && {
          lactation_week: petData.lactation_week || 4,
          nursing_count: petData.nursing_count || 1
        })
      };

      console.log('🔄 Transformed API data:', apiData);

      // 🔧 Fix: Use correct URL path (/pets/ instead of /pets)
      const response = await apiClient.post<CreatePetResponse>('/pets/', apiData);
      
      console.log('✅ Pet creation response:', response.data);
      
      // 🔧 Return response data directly, no need to check wrapped ApiResponse
      // Because from error messages, backend returns data directly rather than wrapped in success/data structure
      return response.data;
      
    } catch (error) {
      console.error('❌ Create pet failed:', error);
      throw error;
    }
  },

  // Get pet information
  async getPet(petId: number): Promise<Pet> {
    try {
      const response = await apiClient.get<Pet>(`/pets/${petId}/`);
      return response.data;
    } catch (error) {
      console.error('Get pet error:', error);
      throw error;
    }
  },

  // Update pet information
  async updatePet(petId: number, petData: Partial<PetFormData>): Promise<Pet> {
    try {
      const response = await apiClient.put<Pet>(`/pets/${petId}/`, petData);
      return response.data;
    } catch (error) {
      console.error('Update pet error:', error);
      throw error;
    }
  }
};

export const recipeAPI = {
  // 🔧 Fix: Generate recipe method
  async generateRecipe(request: RecipeGenerationRequest): Promise<RecipeResult> {
    console.log('📤 Generating recipe with request:', request);

    try {
      const apiRequest = {
        pet_id: Number(request.pet_id),
        target_calories: request.target_calories ? Number(request.target_calories) : undefined,
        preferred_weight_g: request.preferred_weight_g ? Number(request.preferred_weight_g) : undefined  // Add preferred weight parameter
      };

      console.log('🔄 Transformed recipe request:', apiRequest);

      // 🔧 Use correct endpoint path, baseURL already includes /api/v1
      const response = await apiClient.post<RecipeResult>('/recipes/generate', apiRequest);
      
      console.log('✅ Recipe generation response:', response.data);

      // 🔧 Check response status
      if (response.data.status === 'Error') {
        throw new Error(response.data.error || 'Recipe generation failed');
      }

      // 🔧 Validate return data structure
      if (!response.data.recipe || !response.data.analysis) {
        throw new Error('Recipe data structure is incomplete');
      }

      return response.data;
    } catch (error) {
      console.error('Generate recipe error:', error);

      if (axios.isAxiosError(error)) {
        return {
          status: 'Error',
          error: error.response?.data?.detail || error.message || 'Network error',
          recipe: {
            pet_id: request.pet_id,
            total_weight_g: 0,
            target_calories: request.target_calories || 0,
            actual_calories: 0,
            energy_accuracy: 0,
            ingredients: []
          },
          analysis: {
            nutrition: {
              total_calories_kcal: 0,
              protein_g: 0,
              fat_g: 0,
              carbohydrate_g: 0,
              fiber_g: 0
            },
            efficiency: {
              caloric_density_kcal_per_g: 0,
              cost_efficiency_cost_per_kcal: 0,
              ingredient_count: 0,
              weight_category: "Unknown"
            },
            aafco_compliance: {
              compliant: false,
              violations: [],
              score: 0
            },
            cost_analysis: {
              total_cost: 0,
              cost_per_kg: 0
            },
            weight_analysis: {
              optimization_mode: "unknown",
              weight_category: "Unknown",
              weight_reasonable: false
            }
          }
        };
      }

      throw error;
    }
  },

  // Get recipe details
  async getRecipe(recipeId: number): Promise<RecipeResult> {
    try {
      console.log(`📤 Getting recipe ${recipeId}`);
      const response = await apiClient.get<RecipeResult>(`/recipes/${recipeId}/`);
      console.log('✅ Get recipe response:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Get recipe error:', error);
      throw error;
    }
  },

  // Save recipe
  async saveRecipe(recipeData: RecipeResult): Promise<{ recipe_id: number }> {
    try {
      console.log('📤 Saving recipe:', recipeData);
      const response = await apiClient.post<{ recipe_id: number }>('/recipes/', recipeData);
      console.log('✅ Save recipe response:', response.data);
      return response.data;
    } catch (error) {
      console.error('❌ Save recipe error:', error);
      throw error;
    }
  }
};

export const healthAPI = {
  // Health check
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    try {
      const response = await apiClient.get<{ status: string; timestamp: string }>('/health/');
      return response.data;
    } catch (error) {
      console.error('Health check error:', error);
      throw error;
    }
  }
};

// 🧪 Add debugging methods
export const debugAPI = {
  // Test pet creation with minimal data
  async testCreatePet(): Promise<void> {
    const testData = {
      name: "TestPet",
      species: "dog",
      breed: "test",
      age_months: 12,
      weight_kg: 10,
      activity_level: ActivityLevel.MODERATE_ACTIVE,
      physiological_status: PhysiologicalStatus.INTACT,
      life_stage: LifeStage.DOG_ADULT,
      health_conditions: []
    };
    
    console.log('🧪 Testing pet creation with minimal data:', testData);
    
    try {
      const response = await apiClient.post('/pets/', testData);
      console.log('✅ Test successful:', response.data);
    } catch (error) {
      console.error('❌ Test failed:', error);
    }
  }
};

// Export API instance
export default apiClient;