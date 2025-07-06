import shutil
from pathlib import Path

# Arquivo fonte que será copiado para cada subpasta
SOURCE_FILE = Path("test_main.py")

# Diretório raiz onde estão as pastas dos alunos (exemplo: respostas/ebape-prog-aplic-barra-2025/prog1-tarefa-scrap-yahoo-submissions)
TARGET_ROOT_DIR = Path("../respostas/ebape-prog-aplic-barra-2025/prog1-tarefa-scrap-yahoo-submissions")

def main():
    if not SOURCE_FILE.is_file():
        print(f"Arquivo fonte '{SOURCE_FILE}' não encontrado na raiz. Abortando.")
        return

    if not TARGET_ROOT_DIR.is_dir():
        print(f"Pasta alvo '{TARGET_ROOT_DIR}' não encontrada. Abortando.")
        return

    folders_updated = 0

    # Itera apenas pelas subpastas imediatas do diretório alvo
    for subfolder in TARGET_ROOT_DIR.iterdir():
        if subfolder.is_dir():
            destination_file = subfolder / "test_main.py"
            try:
                shutil.copy2(SOURCE_FILE, destination_file)
                print(f"Arquivo copiado para: {destination_file}")
                folders_updated += 1
            except Exception as e:
                print(f"Erro copiando para {destination_file}: {e}")

    print(f"\nTotal de pastas atualizadas: {folders_updated}")

if __name__ == "__main__":
    main()
