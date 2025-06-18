# 🐾 AI Pet Fresh Diet - 宠物营养优化系统

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/React-18.2+-blue.svg)](https://reactjs.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8+-blue.svg)](https://typescriptlang.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Tuanty Nutrition 是一个基于 AAFCO（美国饲料管理协会）营养标准的专业宠物鲜食配方生成系统。通过先进的线性规划算法，为您的爱宠量身定制营养均衡、成本优化的科学配方。

## ✨ 功能特色

### 🎯 智能配方优化
- **多目标优化**: 营养需求 + 成本控制 + 食材多样性
- **AAFCO标准合规**: 严格遵循美国饲料控制协会营养标准
- **混合优化策略**: 营养导向 + 重量偏好引导
- **实时分析报告**: 学术级营养分析报告

### 🐕 宠物管理
- **多物种支持**: 犬类、猫类不同生命阶段
- **个性化参数**: 年龄、体重、活动水平、生理状态
- **健康状况考虑**: 过敏原、健康条件定制化

### 📊 专业分析
- **营养密度计算**: 每1000kcal营养素含量分析
- **宏量营养素分布**: 蛋白质、脂肪、碳水化合物平衡
- **成本效益分析**: 每餐成本、每千卡成本优化
- **可视化图表**: 饼图、雷达图、趋势分析

## 🏗️ 技术架构

### 前端技术栈
```typescript
React 18.2+ (TypeScript)
├── 状态管理: Zustand 5.0+
├── 路由: React Router 7.6+
├── 表单: React Hook Form + Zod
├── 数据获取: TanStack Query 5.0+
├── 动画: Framer Motion 12.0+
├── 图表: Recharts 2.15+
├── 样式: Tailwind CSS 3.4+
└── 构建工具: Vite 6.3+
```

### 后端技术栈
```python
FastAPI 0.104+ (Python 3.10+)
├── 数据库: SQLAlchemy 2.0+ + PostgreSQL/AsyncPG
├── 数据处理: Pandas + NumPy
├── 优化算法: SciPy + PuLP (线性规划)
├── 数据验证: Pydantic 2.5+
├── 异步支持: AsyncIO + HTTPX
└── 测试框架: Pytest + Pytest-AsyncIO
```

## 🚀 快速开始

### 环境要求
- **Node.js**: >= 18.0.0
- **Python**: >= 3.10.0
- **PostgreSQL**: >= 13.0 (可选，开发环境可用SQLite)

### 一键安装
```bash
# 克隆项目
git clone https://github.com/your-username/ai-pet-fresh-diet.git
cd ai-pet-fresh-diet

# 安装所有依赖
npm run setup

# 启动开发环境（前后端同时运行）
npm run dev
```

### 分步安装

#### 1. 后端设置
```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 启动后端服务
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. 前端设置
```bash
cd pet-nutrition-frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 环境配置
创建 `backend/.env` 文件：
```env
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost/pet_nutrition
# 或使用SQLite（开发环境）
# DATABASE_URL=sqlite:///./pet_nutrition.db

# API配置
API_V1_STR=/api/v1
PROJECT_NAME="Pet Nutrition API"
DEBUG=True

# CORS配置
BACKEND_CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
```

## 📱 使用指南

### 1. 创建宠物档案
- 输入宠物基本信息（姓名、物种、品种）
- 设置生理参数（年龄、体重、活动水平）
- 配置健康状况（过敏原、特殊需求）

### 2. 生成营养配方
- 设置目标热量（系统可自动计算）
- 可选设置偏好重量
- 选择优化策略（营养优先/重量引导）

### 3. 分析配方报告
- 查看学术级营养分析报告
- 检查AAFCO标准合规性
- 评估成本效益和食材多样性
- 导出PDF报告或保存配方

## 🔧 重构亮点

### 代码架构优化
我们最近完成了大规模重构，将原本1066行的巨型组件拆分为模块化架构：

#### 📊 重构成果
- **代码减少65%**: 1066行 → 400行
- **组件模块化**: 单一职责原则
- **可维护性提升**: 便于测试和协作
- **性能优化**: 减少重渲染

#### 🏗️ 新架构
```
src/
├── components/
│   ├── RecipeResult.tsx (主组件，400行)
│   └── recipe/
│       ├── ReportHeader.tsx (报告头部)
│       └── NutritionCharts.tsx (图表组件)
├── hooks/
│   └── useRecipeData.ts (数据处理逻辑)
└── constants/
    └── aafcoStandards.ts (AAFCO标准数据)
```

#### ✨ 架构优势
- **关注点分离**: 数据逻辑与UI渲染分离
- **代码复用**: 组件和钩子可在多处使用
- **类型安全**: 完整的TypeScript类型定义
- **测试友好**: 每个模块都可独立测试

## 🧪 开发工具

### 代码质量
```bash
# 前端代码检查
cd pet-nutrition-frontend
npm run lint

# 后端代码格式化
cd backend
black app/
isort app/
ruff check app/

# 类型检查
mypy app/
```

### 测试
```bash
# 后端测试
cd backend
pytest

# 前端测试（如果配置）
cd pet-nutrition-frontend
npm test
```

## 📊 API 文档

启动后端服务后，访问：
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 主要端点
```
POST /api/v1/pets/          # 创建宠物
GET  /api/v1/pets/{id}/     # 获取宠物信息
POST /api/v1/recipes/generate  # 生成配方
GET  /api/v1/health/        # 健康检查
```

## 🔬 算法原理

### 线性规划优化
系统使用多目标线性规划算法：

```python
# 目标函数
minimize: Σ(营养素缺乏惩罚) + Σ(成本) + Σ(多样性惩罚)

# 约束条件
subject to:
- 能量约束: |实际热量 - 目标热量| ≤ 7%
- AAFCO标准: 各营养素 ≥ 最低要求
- 食材限制: 单一食材 ≤ 35%
- 分类平衡: 蛋白质40-70%, 蔬菜≥15%
```

### 混合优化策略
1. **营养导向优化**: 优先满足营养需求
2. **重量引导优化**: 在营养合规前提下调整重量
3. **平衡策略**: 营养质量与用户偏好的智能平衡

## 🌟 贡献指南

### 开发流程
1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 代码规范
- **前端**: 遵循 ESLint + Prettier 配置
- **后端**: 遵循 Black + isort + Ruff 配置
- **提交**: 使用 Conventional Commits 格式

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [AAFCO](https://www.aafco.org/) - 营养标准参考
- [USDA FoodData Central](https://fdc.nal.usda.gov/) - 食材营养数据
- [FastAPI](https://fastapi.tiangolo.com/) - 高性能API框架
- [React](https://reactjs.org/) - 用户界面库

## 📞 支持

如有问题或建议，请：
- 创建 [Issue](https://github.com/your-username/ai-pet-fresh-diet/issues)
- 发送邮件至 support@petnutrition.ai
- 查看 [Wiki](https://github.com/your-username/ai-pet-fresh-diet/wiki) 文档

---

<div align="center">
  <p>用❤️为宠物健康而构建</p>
  <p>Built with ❤️ for Pet Health</p>
</div>