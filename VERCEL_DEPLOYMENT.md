# Vercel 部署指南

## 问题原因
原本的 Flask 服务器无法在 Vercel 上运行，因为 Vercel 是无服务器平台，不支持常规后端服务器。

## 解决方案
已转换为 **Vercel Serverless Functions** 架构：

1. **创建 `api/margin.py`** - Python Serverless Function
   - 替代了原来的 Flask `/api/margin` 路由
   - Vercel 自动将 `api/` 目录中的 Python 文件转换为无服务器函数

2. **更新 `vercel.json`** - Vercel 配置文件
   - 配置 Python 构建和路由规则
   - 映射 `/api/margin` 请求到函数

3. **更新 `margin.html`** - 前端配置
   - API_ENDPOINT 现在使用相对路径 `/api/margin`
   - 自动适配本地开发和 Vercel 部署环境

## 部署步骤

### 1. 推送到 GitHub
```bash
git add .
git commit -m "fix: Convert to Vercel Serverless Functions for Akshare API"
git push origin main
```

### 2. 部署到 Vercel
```bash
# 安装 Vercel CLI
npm install -g vercel

# 部署
vercel --prod
```

或者在 Vercel 网站直接连接 GitHub 仓库（推荐）

### 3. 验证部署
访问：`https://your-vercel-domain.vercel.app/margin.html`

## 可能遇到的问题

### ❌ Akshare 导入错误
**问题**：`ModuleNotFoundError: No module named 'akshare'`

**解决**：
1. 确保 `requirements.txt` 包含 akshare
2. Vercel 会自动安装 requirements.txt 中的依赖
3. 如果仍失败，可能是网络问题，重新部署即可

### ❌ 数据返回为空
**问题**：API 返回空数组

**可能原因**：
1. Akshare 数据源临时不可用
2. 请求的日期没有交易数据
3. 尝试其他交易日期

### ❌ CORS 错误
**问题**：浏览器报 CORS 错误

**原因**：已在 `api/margin.py` 中处理 CORS，但可能需要检查

## 技术栈
- **前端**：HTML + CSS + JavaScript（纯静态）
- **后端**：Python Serverless Functions (Vercel)
- **数据源**：AkShare
- **托管**：Vercel

## 本地测试

如要在本地测试 Flask 服务器：
```bash
pip install -r requirements.txt
python3 server.py
```
访问 `http://localhost:5000`

## 注意事项
- Vercel 的 Serverless Functions 有 **10 秒超时限制**，如果 Akshare 响应较慢可能超时
- 大数据量请求可能会受到内存限制
- 建议使用 Vercel 的缓存或 CDN 优化性能
