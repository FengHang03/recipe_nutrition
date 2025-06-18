import React, { useState, useRef } from 'react';
import { Home, User, Activity, Zap, Flame } from 'lucide-react';
import { PetFormData, ActivityLevel, PhysiologicalStatus } from '../../types';

interface PetFormProps {
  onSubmit: (data: PetFormData) => void;
  onNext: () => void;
}

const PetForm: React.FC<PetFormProps> = ({ onSubmit, onNext }) => {
  const renderCount = useRef(0);
  renderCount.current += 1;

  const [formData, setFormData] = useState<PetFormData>({
    name: 'Max',
    species: 'dog',
    breed: 'Golden Retriever',
    age_months: 12,
    weight_kg: 10,
    activity_level: ActivityLevel.MODERATE_ACTIVE,
    physiological_status: PhysiologicalStatus.INTACT,
    health_conditions: [],
    allergies: []
  });

  console.log(`🐾 PetForm render #${renderCount.current}`);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    console.log('🚀 PetForm submitting:', formData);
    onSubmit(formData);
  };

  const physiologicalStatusOptions = [
    { value: PhysiologicalStatus.INTACT, label: 'Intact' },
    { value: PhysiologicalStatus.NEUTERED, label: 'Neutered' },
    { value: PhysiologicalStatus.PREGNANT, label: 'Pregnant' },
    { value: PhysiologicalStatus.LACTATING, label: 'Lactating' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-green-50 p-8">
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">
          Pet Information Setup (Render #{renderCount.current})
        </h1>

        {/* Render count warning */}
        {renderCount.current > 3 && (
          <div className="mb-4 p-3 bg-yellow-100 border border-yellow-400 rounded">
            ⚠️ PetForm render count: {renderCount.current}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Pet Name */}
          <div>
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-2">
              Pet Name *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Enter pet name"
              required
            />
          </div>

          {/* Species */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Species *
            </label>
            <div className="grid grid-cols-2 gap-4">
              {/* Dog button */}
              <button
                type="button"
                onClick={() => setFormData(prev => ({ ...prev, species: 'dog', breed: 'Golden Retriever' }))}
                className={`p-4 border-2 rounded-lg transition-all duration-200 ${
                  formData.species === 'dog'
                    ? 'border-green-500 bg-green-50 text-green-700'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <div className="flex flex-col items-center space-y-2">
                  {/* Dog icon */}
                  <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M4.5 12.5C4.5 12.5 6.5 10.5 12 10.5S19.5 12.5 19.5 12.5V16.5C19.5 18.5 17.5 20.5 15.5 20.5H8.5C6.5 20.5 4.5 18.5 4.5 16.5V12.5Z"/>
                  </svg>
                  <span className="font-medium">Dog</span>
                </div>
              </button>

              {/* Cat button */}
              <button
                type="button"
                onClick={() => setFormData(prev => ({ ...prev, species: 'cat', breed: 'Ragdoll' }))}
                className={`p-4 border-2 rounded-lg transition-all duration-200 ${
                  formData.species === 'cat'
                    ? 'border-green-500 bg-green-50 text-green-700'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <div className="flex flex-col items-center space-y-2">
                  {/* Cat icon */}
                  <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2L13.5 7L18 7L14.5 10L16 15L12 12L8 15L9.5 10L6 7L10.5 7L12 2Z"/>
                  </svg>
                  <span className="font-medium">Cat</span>
                </div>
              </button>
            </div>
          </div>

          {/* Breed */}
          <div>
            <label htmlFor="breed" className="block text-sm font-medium text-gray-700 mb-2">
              Breed
            </label>
            <input
              type="text"
              value={formData.breed}
              onChange={(e) => setFormData(prev => ({ ...prev, breed: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
            />
          </div>

          {/* Age and Weight */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Age */}
            <div>
              <label htmlFor="age_months" className="block text-sm font-medium text-gray-700 mb-2">
                Age (months) *
              </label>
              <input
                type="number"
                value={formData.age_months}
                onChange={(e) => setFormData(prev => ({ ...prev, age_months: parseInt(e.target.value) || 0 }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                min="1"
                max="300"
                required
              />
            </div>

            {/* Weight */}
            <div>
              <label htmlFor="weight_kg" className="block text-sm font-medium text-gray-700 mb-2">
                Weight (kg) *
              </label>
              <input
                type="number"
                step="0.1"
                value={formData.weight_kg}
                onChange={(e) => setFormData(prev => ({ ...prev, weight_kg: parseFloat(e.target.value) || 0 }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                min="0.1"
                max="200"
                required
              />
            </div>
          </div>

          {/* Activity Level - Icon button selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Activity Level *
            </label>
            <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
              {/* Sedentary/Low Activity */}
              <button
                type="button"
                onClick={() => setFormData(prev => ({ ...prev, activity_level: ActivityLevel.SEDENTARY_ACTIVE }))}
                className={`p-3 border-2 rounded-lg transition-all duration-200 ${
                  formData.activity_level === ActivityLevel.SEDENTARY_ACTIVE
                    ? 'border-green-500 bg-green-50 text-green-700'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
                title="Sedentary/Low Activity - Mostly resting"
              >
                <div className="flex flex-col items-center space-y-1">
                  <Home className="w-5 h-5" />
                  <span className="text-xs">Indoor</span>
                </div>
              </button>

              {/* Low Activity */}
              <button
                type="button"
                onClick={() => setFormData(prev => ({ ...prev, activity_level: ActivityLevel.LOW_ACTIVE }))}
                className={`p-3 border-2 rounded-lg transition-all duration-200 ${
                  formData.activity_level === ActivityLevel.LOW_ACTIVE
                    ? 'border-green-500 bg-green-50 text-green-700'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
                title="Low Activity - Occasional walks or play"
              >
                <div className="flex flex-col items-center space-y-1">
                  <User className="w-5 h-5" />
                  <span className="text-xs">Light</span>
                </div>
              </button>

              {/* Moderate Activity */}
              <button
                type="button"
                onClick={() => setFormData(prev => ({ ...prev, activity_level: ActivityLevel.MODERATE_ACTIVE }))}
                className={`p-3 border-2 rounded-lg transition-all duration-200 ${
                  formData.activity_level === ActivityLevel.MODERATE_ACTIVE
                    ? 'border-green-500 bg-green-50 text-green-700'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
                title="Moderate Activity - Regular daily exercise"
              >
                <div className="flex flex-col items-center space-y-1">
                  <Activity className="w-5 h-5" />
                  <span className="text-xs">Moderate</span>
                </div>
              </button>

              {/* High Activity */}
              <button
                type="button"
                onClick={() => setFormData(prev => ({ ...prev, activity_level: ActivityLevel.HIGH_ACTIVE }))}
                className={`p-3 border-2 rounded-lg transition-all duration-200 ${
                  formData.activity_level === ActivityLevel.HIGH_ACTIVE
                    ? 'border-green-500 bg-green-50 text-green-700'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
                title="High Activity - Frequent exercise or working"
              >
                <div className="flex flex-col items-center space-y-1">
                  <Zap className="w-5 h-5" />
                  <span className="text-xs">High</span>
                </div>
              </button>

              {/* Extreme Activity */}
              <button
                type="button"
                onClick={() => setFormData(prev => ({ ...prev, activity_level: ActivityLevel.EXTREME_ACTIVE }))}
                className={`p-3 border-2 rounded-lg transition-all duration-200 ${
                  formData.activity_level === ActivityLevel.EXTREME_ACTIVE
                    ? 'border-green-500 bg-green-50 text-green-700'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
                title="Extreme Activity - Professional training or working dogs"
              >
                <div className="flex flex-col items-center space-y-1">
                  <Flame className="w-5 h-5" />
                  <span className="text-xs">Extreme</span>
                </div>
              </button>
            </div>
          </div>

          {/* 🔧 Fix: Physiological Status - Use correct enum values */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Physiological Status *
            </label>
            <select
              value={formData.physiological_status}
              onChange={(e) => setFormData(prev => ({ ...prev, physiological_status: e.target.value as PhysiologicalStatus }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500"
            >
              {physiologicalStatusOptions.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* 🔧 新增：哺乳期相关字段 */}
          {formData.physiological_status === 'lactating' && (
            <>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  哺乳周数 (1-4周)
                </label>
                <input
                  type="number"
                  value={formData.lactation_week || 4}
                  onChange={(e) => setFormData(prev => ({ ...prev, lactation_week: parseInt(e.target.value) || 4 }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500"
                  min="1"
                  max="4"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  哺乳幼崽数量
                </label>
                <input
                  type="number"
                  value={formData.nursing_count || 1}
                  onChange={(e) => setFormData(prev => ({ ...prev, nursing_count: parseInt(e.target.value) || 1 }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-green-500"
                  min="1"
                  max="12"
                />
              </div>
            </>
          )}

          {/* 提交按钮 */}
          <div className="flex gap-4">
            <button
              type="submit"
              className="flex-1 bg-green-600 text-white py-3 px-6 rounded-md hover:bg-green-700 transition-colors font-medium"
            >
              Generate nutritional recipe
            </button>
            
            <button
              type="button"
              onClick={() => {
                console.log('🔄 Reset form data');
                setFormData({
                  name: 'Max',
                  species: 'dog',
                  breed: 'Golden Retriever',
                  age_months: 12,
                  weight_kg: 10,
                  activity_level: ActivityLevel.MODERATE_ACTIVE,
                  physiological_status: PhysiologicalStatus.INTACT,
                  health_conditions: [],
                  allergies: []
                });
              }}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
            >
              Reset
            </button>
          </div>
        </form>

        {/* 调试信息 */}
        <div className="mt-6 p-4 bg-gray-100 rounded-lg">
          <h3 className="text-lg font-semibold mb-2">调试信息</h3>
          <div className="text-sm text-gray-600 space-y-1">
            <div>渲染次数: {renderCount.current}</div>
            <div>发送到API的数据格式:</div>
            <pre className="bg-white p-2 rounded border text-xs overflow-auto">
              {JSON.stringify(formData, null, 2)}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PetForm;