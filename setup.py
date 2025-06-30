"""
Script de setup para o sistema de correção automática.
"""
#!/usr/bin/env python3

import os
import sys
import subprocess
from pathlib import Path


def check_python_version():
    """Verifica se a versão do Python é compatível."""
    if sys.version_info < (3, 9):
        print("❌ Erro: Python 3.9+ é necessário")
        print(f"   Versão atual: {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detectado")
    return True


def check_pipenv():
    """Verifica se o pipenv está instalado."""
    try:
        result = subprocess.run(['pipenv', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ pipenv detectado")
            return True
    except FileNotFoundError:
        pass
    
    print("❌ pipenv não encontrado")
    return False


def install_pipenv():
    """Instala o pipenv."""
    print("📦 Instalando pipenv...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pipenv'], 
                      check=True)
        print("✅ pipenv instalado com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar pipenv: {e}")
        return False


def install_dependencies():
    """Instala as dependências do projeto."""
    print("📦 Instalando dependências...")
    try:
        subprocess.run(['pipenv', 'install'], check=True)
        print("✅ Dependências instaladas com sucesso")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao instalar dependências: {e}")
        return False


def check_directories():
    """Verifica se os diretórios necessários existem."""
    base_path = Path(__file__).parent
    
    required_dirs = [
        base_path / "enunciados",
        base_path / "respostas"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not dir_path.exists():
            missing_dirs.append(dir_path.name)
        else:
            print(f"✅ Diretório {dir_path.name} encontrado")
    
    if missing_dirs:
        print(f"⚠️  Diretórios ausentes: {', '.join(missing_dirs)}")
        print("   Certifique-se de que os diretórios 'enunciados' e 'respostas' existem")
        return False
    
    return True


def create_reports_directory():
    """Cria o diretório de relatórios."""
    reports_dir = Path(__file__).parent / "reports"
    reports_dir.mkdir(exist_ok=True)
    print("✅ Diretório 'reports' criado")


def check_openai_key():
    """Verifica se a chave da API OpenAI está configurada."""
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print("✅ OPENAI_API_KEY configurada")
        return True
    else:
        print("⚠️  OPENAI_API_KEY não configurada")
        print("   Configure a variável de ambiente:")
        print("   export OPENAI_API_KEY='sua-chave-api-aqui'")
        return False


def run_tests():
    """Executa os testes básicos."""
    print("🧪 Executando testes...")
    try:
        result = subprocess.run(['pipenv', 'run', 'pytest', 'tests/', '-v'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Testes passaram")
            return True
        else:
            print("❌ Alguns testes falharam")
            print(result.stdout)
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar testes: {e}")
        return False


def test_cli():
    """Testa se a CLI está funcionando."""
    print("🔧 Testando CLI...")
    try:
        result = subprocess.run(['pipenv', 'run', 'python', '-m', 'src.main', '--help'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ CLI funcionando corretamente")
            return True
        else:
            print("❌ Erro na CLI")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao testar CLI: {e}")
        return False


def main():
    """Função principal do setup."""
    print("🚀 Setup do Sistema de Correção Automática")
    print("=" * 50)
    
    # Verificações básicas
    if not check_python_version():
        sys.exit(1)
    
    if not check_pipenv():
        if not install_pipenv():
            sys.exit(1)
    
    # Instalação de dependências
    if not install_dependencies():
        sys.exit(1)
    
    # Verificação de diretórios
    if not check_directories():
        print("\n⚠️  Certifique-se de que os diretórios necessários existem")
        print("   O sistema pode não funcionar corretamente")
    
    # Criação de diretórios
    create_reports_directory()
    
    # Verificação da API key
    check_openai_key()
    
    # Testes
    print("\n" + "=" * 50)
    print("🧪 Executando verificações finais...")
    
    if run_tests():
        print("✅ Testes básicos passaram")
    else:
        print("⚠️  Alguns testes falharam, mas o sistema pode funcionar")
    
    if test_cli():
        print("✅ Interface de linha de comando funcionando")
    else:
        print("❌ Problema com a interface de linha de comando")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 Setup concluído com sucesso!")
    print("\n📖 Próximos passos:")
    print("1. Configure sua OPENAI_API_KEY se ainda não fez")
    print("2. Ative o ambiente virtual: pipenv shell")
    print("3. Teste o sistema:")
    print("   python -m src.main list-assignments")
    print("   python -m src.main list-turmas")
    print("\n📚 Para mais informações, consulte o README.md")


if __name__ == "__main__":
    main() 