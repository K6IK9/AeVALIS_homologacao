#!/bin/bash

# Build script para Vercel - Django
echo "🚀 Iniciando build do Django para Vercel..."

# Executar migrações
echo "🗄️ Executando migrações..."
python manage.py migrate --noinput

# Coletar arquivos estáticos
echo "📁 Coletando arquivos estáticos..."
python manage.py collectstatic --noinput --clear

echo "✅ Build concluído!"
