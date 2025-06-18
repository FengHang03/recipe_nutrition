import React from 'react';
import { motion } from 'framer-motion';
import { Download, Share2, RefreshCcw } from 'lucide-react';

interface PetInfo {
  species: string;
  name: string;
  age: string;
  weight: string;
}

interface ReportHeaderProps {
  petInfo: PetInfo;
  onSave?: () => void;
  onShare?: () => void;
  onNewRecipe?: () => void;
}

const ReportHeader: React.FC<ReportHeaderProps> = ({ 
  petInfo, 
  onSave, 
  onShare, 
  onNewRecipe 
}) => {
  return (
    <motion.div 
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-lg shadow-sm border p-8 mb-8"
    >
      <div className="text-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          {petInfo.species === 'cat' ? 'Feline' : 'Canine'} Nutritional Formulation Analysis Report
        </h1>
        <h2 className="text-xl text-gray-700 mb-2">
          {petInfo.species === 'cat' ? 'Feline' : 'Canine'} Nutritional Formulation Analysis Report
        </h2>
        <div className="flex justify-center items-center space-x-6 text-gray-600 mb-3">
          <div className="flex items-center space-x-2">
            <span className="font-semibold">Pet:</span>
            <span>{petInfo.name}</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="font-semibold">Life Stage:</span>
            <span>{petInfo.age}</span>
          </div>
          <div className="flex items-center space-x-2">
            <span className="font-semibold">Weight:</span>
            <span>{petInfo.weight}</span>
          </div>
        </div>
        <p className="text-gray-600">
          Based on AAFCO Nutritional Standards for {petInfo.species === 'cat' ? 'Adult Cats' : 'Adult Dogs'}
        </p>
        <p className="text-sm text-gray-500 mt-4">
          Generated on: {new Date().toLocaleDateString('en-US', { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
          })}
        </p>
      </div>

      {/* 操作按钮 */}
      <div className="flex justify-center space-x-4 border-t pt-6">
        <button
          onClick={onSave}
          className="flex items-center space-x-2 bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 transition-colors"
        >
          <Download className="w-4 h-4" />
          <span>Save Report</span>
        </button>
        
        <button
          onClick={onShare}
          className="flex items-center space-x-2 bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700 transition-colors"
        >
          <Share2 className="w-4 h-4" />
          <span>Export PDF</span>
        </button>
        
        <button
          onClick={onNewRecipe}
          className="flex items-center space-x-2 bg-gray-600 text-white px-6 py-2 rounded hover:bg-gray-700 transition-colors"
        >
          <RefreshCcw className="w-4 h-4" />
          <span>New Analysis</span>
        </button>
      </div>
    </motion.div>
  );
};

export default ReportHeader; 