#!/bin/bash
# Web服务启动脚本

echo "🌐 启动股票分析Web服务"
echo "=================================="

# 检查Flask是否安装
echo ""
echo "检查依赖..."
python3 -c "import flask" 2>/dev/null

if [ $? -ne 0 ]; then
    echo "❌ Flask未安装"
    echo ""
    echo "正在安装Flask..."
    pip3 install flask
    echo ""
    echo "✅ Flask安装完成"
fi

# 检查.env文件
if [ ! -f ".env" ]; then
    echo "⚠️  未找到.env文件"
    echo ""
    echo "创建示例.env文件..."
    cat > .env << 'EOF'
# 智谱AI配置
ZHIPU_API_KEY=your_api_key_here
ZHIPU_MODEL=glm-4-plus

# 默认AIGC模型
DEFAULT_AIGC_MODEL=zhipu
EOF
    echo ""
    echo "✅ .env文件已创建"
    echo "   请编辑.env文件，填入你的智谱AI API密钥"
    echo ""
fi

# 启动服务
echo ""
echo "🚀 启动Web服务..."
echo ""
echo "📱 访问地址: http://127.0.0.1:5000"
echo "⏹️  按 Ctrl+C 停止服务"
echo ""
echo "=================================="
echo ""

python3 app.py
