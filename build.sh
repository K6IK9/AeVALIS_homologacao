#!/bin/bash

# Build script para Vercel - Django
echo "🚀 Iniciando build do Django para Vercel..."

# Verificar estrutura de diretórios
echo "📂 Verificando estrutura..."
ls -la static/ || echo "❌ Pasta static não encontrada"
ls -la staticfiles/ || echo "📁 Pasta staticfiles será criada"

# Executar migrações
echo "🗄️ Executando migrações..."
python manage.py migrate --noinput

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

# Verificar se os arquivos foram coletados
echo "🔍 Verificando arquivos estáticos coletados..."
ls -la staticfiles/
ls -la staticfiles/assets/ || echo "❌ Assets não encontrados em staticfiles"

echo "✅ Build concluído!"
