import React from 'react';
import { motion } from 'framer-motion';
import { Target, Shield } from 'lucide-react';
import {
  PieChart, 
  Pie, 
  Cell, 
  ResponsiveContainer,
  RadarChart,
  Radar,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Tooltip
} from 'recharts';

interface MacroData {
  name: string;
  value: number;
  color: string;
}

interface RadarData {
  nutrient: string;
  value: number;
  status: string;
}

interface NutritionChartsProps {
  macroData: MacroData[];
  radarData: RadarData[];
}

const NutritionCharts: React.FC<NutritionChartsProps> = ({ 
  macroData, 
  radarData 
}) => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
      {/* 宏量营养素分布饼图 */}
      <motion.div 
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.5 }}
        className="bg-white rounded-lg shadow-sm border p-6"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Target className="w-5 h-5 mr-2" />
          Figure 1. Macronutrient Distribution
        </h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={macroData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                outerRadius={100}
                fill="#8884d8"
                dataKey="value"
              >
                {macroData.map((entry, index) => <Cell key={`cell-${index}`} fill={entry.color} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </motion.div>

      {/* AAFCO合规性雷达图 */}
      <motion.div 
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.5 }}
        className="bg-white rounded-lg shadow-sm border p-6"
      >
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
          <Shield className="w-5 h-5 mr-2" />
          Figure 2. AAFCO Compliance Radar
        </h3>
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="nutrient" />
              <PolarRadiusAxis angle={90} domain={[0, 150]} />
              <Radar
                name="Adequacy %"
                dataKey="value"
                stroke="#2563EB"
                fill="#2563EB"
                fillOpacity={0.3}
              />
              <Tooltip 
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const data = payload[0].payload;
                    return (
                      <div className="bg-white p-3 border border-gray-200 rounded-lg shadow-lg">
                        <p className="font-medium">{data.nutrient}</p>
                        <p style={{ color: payload[0].color }}>
                          Adequacy: {data.value.toFixed(1)}%
                        </p>
                        <p className={`text-sm ${
                          data.status === 'ADEQUATE' ? 'text-green-600' :
                          data.status === 'EXCESSIVE' ? 'text-yellow-600' : 'text-red-600'
                        }`}>
                          Status: {data.status}
                        </p>
                      </div>
                    );
                  }
                  return null;
                }}
              />
            </RadarChart>
          </ResponsiveContainer>
        </div>
        <div className="mt-2 text-center">
          <p className="text-xs text-gray-600">
            Values &gt;100% indicate adequacy relative to AAFCO minimum requirements
          </p>
        </div>
      </motion.div>
    </div>
  );
};

export default NutritionCharts; 