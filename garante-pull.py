import subprocess
from pathlib import Path

ROOT_DIR = Path("respostas")

FIRST_LEVEL_FOLDERS = [
    "ebape-prog-aplic-barra-2025",
    "ebape-prog-aplic-botafogo1-2025",
    "ebape-prog-aplic-botafogo2-2025"
]

LOG_FILE = "git_pull_log.txt"

def git_pull(repo_path: Path):
    try:
        result = subprocess.run(
            ["git", "pull"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False
        )
        success = (result.returncode == 0)
        output = result.stdout + result.stderr
        return success, output
    except Exception as e:
        return False, f"Exception ao executar git pull: {e}"

def main():
    total_repos = 0
    success_count = 0
    fail_count = 0

    with open(LOG_FILE, "w", encoding="utf-8") as log:
        for first_level_name in FIRST_LEVEL_FOLDERS:
            first_level_path = ROOT_DIR / first_level_name
            if not first_level_path.is_dir():
                print(f"[AVISO] Pasta não encontrada: {first_level_path}")
                log.write(f"Pasta não encontrada: {first_level_path}\n")
                continue

            for second_level in first_level_path.iterdir():
                if second_level.is_dir():
                    for third_level in second_level.iterdir():
                        if third_level.is_dir():
                            repo_dir = third_level
                            total_repos += 1
                            print(f"[{total_repos}] Executando git pull em: {repo_dir}")

                            log.write(f"Executando git pull em: {repo_dir}\n")

                            if (repo_dir / ".git").is_dir():
                                success, output = git_pull(repo_dir)
                                if success:
                                    success_count += 1
                                    print(f"    git pull OK: {repo_dir}")
                                    log.write(f"git pull OK: {repo_dir}\n")
                                else:
                                    fail_count += 1
                                    print(f"    git pull FALHOU: {repo_dir}")
                                    log.write(f"git pull FALHOU: {repo_dir}\n")
                                log.write(output + "\n")
                            else:
                                print(f"    Não é um repositório Git: {repo_dir}")
                                log.write(f"Não é um repositório Git: {repo_dir}\n")

                            log.write("-" * 40 + "\n")

    print("\n=== Resumo da execução ===")
    print(f"Total de repositórios encontrados: {total_repos}")
    print(f"git pull bem-sucedidos: {success_count}")
    print(f"git pull com falha: {fail_count}")
    print(f"Veja detalhes no arquivo de log: {LOG_FILE}")

if __name__ == "__main__":
    main()
