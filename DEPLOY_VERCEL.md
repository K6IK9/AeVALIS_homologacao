# 🚀 Deploy no Vercel - Guia Completo

## 📋 Pré-requisitos

1. **Conta no Vercel** - [vercel.com](https://vercel.com)
2. **Banco PostgreSQL** - Neon, Railway, ou outro provedor
3. **Repositório Git** - GitHub, GitLab, ou Bitbucket

## 🛠️ Configuração Passo a Passo

### 1. Preparar o Banco de Dados

Crie um banco PostgreSQL em um dos provedores:
- **Neon** (recomendado) - [neon.tech](https://neon.tech)
- **Railway** - [railway.app](https://railway.app)
- **Supabase** - [supabase.com](https://supabase.com)

### 2. Configurar Variáveis de Ambiente no Vercel

No dashboard do Vercel, vá em:
**Project Settings → Environment Variables**

Adicione as seguintes variáveis:

```
SECRET_KEY=sua-chave-secreta-super-segura-aqui-minimo-50-caracteres
DEBUG=False
DB_NAME=nome_do_seu_banco
DB_USER=usuario_do_banco
DB_PASSWORD=senha_do_banco
DB_HOST=host_do_banco
DB_PORT=5432
```

### 3. Deploy Automático

1. Conecte seu repositório ao Vercel
2. O Vercel detectará automaticamente que é um projeto Python
3. As configurações do `vercel.json` serão aplicadas
4. O script `build.sh` executará as migrações

### 4. Pós-Deploy

Após o primeiro deploy:

1. **Criar superusuário**:
   ```bash
   vercel env pull
   python manage.py createsuperuser
   ```

2. **Verificar funcionamento**:
   - Acesse `/admin/` 
   - Teste login e funcionalidades

## 🔧 Configurações Importantes

### Arquivos de Configuração

- `vercel.json` - Configuração principal do Vercel
- `build.sh` - Script de build (migrações e static files)
- `requirements.txt` - Dependências Python
- `.vercelignore` - Arquivos ignorados no deploy

### Limitações do Vercel (Hobby Plan)

- **Timeout**: 10 segundos por request
- **Memória**: 1024 MB
- **Tamanho**: 250 MB por deploy
- **Bandwidth**: 100 GB/mês

## 🐛 Troubleshooting

### Erro de Timeout
```
Add to settings.py:
DATABASES['default']['CONN_MAX_AGE'] = 0
```

### Arquivos Estáticos não Carregam
```
Verify STATIC_URL = "/static/"
Check WhiteNoise middleware order
```

### Erro de Migrações
```
Check database connection
Verify environment variables
```

## 📚 Recursos Úteis

- [Vercel Python Runtime](https://vercel.com/docs/runtimes/python)
- [Django on Vercel](https://vercel.com/guides/deploying-django-with-vercel)
- [Environment Variables](https://vercel.com/docs/projects/environment-variables)

## 🆘 Comandos Úteis

```bash
# Deploy manual
vercel --prod

# Ver logs
vercel logs

# Baixar variáveis de ambiente
vercel env pull

# Executar migrações local com env do Vercel
vercel env pull
python manage.py migrate
```
