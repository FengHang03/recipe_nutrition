import React from 'react';
import { motion } from 'framer-motion';
import { Loader2, Heart, BarChart3, Calculator } from 'lucide-react';

interface LoadingScreenProps {
  message?: string;
  submessage?: string;
}

const LoadingScreen: React.FC<LoadingScreenProps> = ({ 
    message = "加载中...", 
    submessage 
  }) => {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-green-50">
        <div className="text-center">
          {/* 主加载动画 */}
          <motion.div
            animate={{ rotate: 360 }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "linear"
            }}
            className="w-16 h-16 mx-auto mb-6"
          >
            <Loader2 className="w-16 h-16 text-green-600" />
          </motion.div>
          
          {/* 消息文本 */}
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-2xl font-bold text-gray-900 mb-2"
          >
            {message}
          </motion.h2>
          
          {submessage && (
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="text-gray-600 mb-8"
            >
              {submessage}
            </motion.p>
          )}
          
          {/* 功能图标动画 */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.6 }}
            className="flex justify-center space-x-8"
          >
            <motion.div
              animate={{ y: [0, -5, 0] }}
              transition={{
                duration: 2,
                repeat: Infinity,
                delay: 0
              }}
              className="flex flex-col items-center"
            >
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-2">
                <Heart className="w-6 h-6 text-green-600" />
              </div>
              <span className="text-xs text-gray-500">Nutritional Analysis</span>
            </motion.div>
            
            <motion.div
              animate={{ y: [0, -5, 0] }}
              transition={{
                duration: 2,
                repeat: Infinity,
                delay: 0.3
              }}
              className="flex flex-col items-center"
            >
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-2">
                <Calculator className="w-6 h-6 text-blue-600" />
              </div>
              <span className="text-xs text-gray-500">Recipe Optimization</span>
            </motion.div>
            
            <motion.div
              animate={{ y: [0, -5, 0] }}
              transition={{
                duration: 2,
                repeat: Infinity,
                delay: 0.6
              }}
              className="flex flex-col items-center"
            >
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-2">
                <BarChart3 className="w-6 h-6 text-purple-600" />
              </div>
              <span className="text-xs text-gray-500">Result Presentation</span>
            </motion.div>
          </motion.div>
          
          {/* 进度条 */}
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: "100%" }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: "easeInOut"
            }}
            className="mt-8 mx-auto h-1 bg-green-600 rounded-full"
            style={{ maxWidth: "200px" }}
          />
        </div>
      </div>
    );
  };

export default LoadingScreen;