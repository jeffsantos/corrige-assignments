#!/bin/bash

# Script para configurar commit hooks e template
# Execute este script uma vez para configurar o ambiente

echo "🔧 Configurando commit hooks e template..."

# Tornar o hook executável
chmod +x ../.git/hooks/commit-msg

# Configurar template de commit
git config --local commit.template ../.gitmessage

echo "✅ Configuração concluída!"
echo ""
echo "📝 Agora quando você fizer 'git commit', será mostrado o template."
echo "🔍 O hook validará automaticamente se a mensagem segue os padrões."
echo ""
echo "💡 Para testar, tente fazer um commit com mensagem inválida:"
echo "   git commit -m 'mensagem invalida'"
echo ""
echo "✅ Ou uma mensagem válida:"
echo "   git commit -m 'feat(ai): adiciona nova funcionalidade'" 