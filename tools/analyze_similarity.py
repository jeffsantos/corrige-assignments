#!/usr/bin/env python3
"""
Script para analisar similaridade entre implementações da tarefa 2 (main.py)
"""
import os
from pathlib import Path
from difflib import SequenceMatcher
from typing import List, Tuple

def read_file(path: Path) -> str:
    """Lê arquivo e retorna conteúdo"""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return ""

def similarity_ratio(text1: str, text2: str) -> float:
    """Calcula similaridade entre dois textos (0-1)"""
    return SequenceMatcher(None, text1, text2).ratio()

def normalize_code(code: str) -> str:
    """Normaliza código removendo comentários e espaços extras"""
    lines = []
    for line in code.split('\n'):
        # Remove comentários no início da linha
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            lines.append(stripped)
    return '\n'.join(lines)

def main():
    turma = input("Informe a turma para verificação de similaridade (turma-ano): ")

    base_dir = Path(f"respostas/ebape-prog-aplic-{turma}/prog2-prova-submissions")

    if not base_dir.exists():
        print("Turma inexistente")
        return
    
    # Encontra todos os main.py
    main_files = list(base_dir.glob("*/main.py"))

    print(f"Encontrados {len(main_files)} arquivos main.py\n")

    # Lê todos os arquivos
    submissions = {}
    for file_path in main_files:
        student = file_path.parent.name.replace("prog2-prova-", "")
        content = read_file(file_path)
        normalized = normalize_code(content)

        # Ignora submissões vazias ou muito pequenas
        if len(normalized) > 50:
            submissions[student] = {
                'path': file_path,
                'content': content,
                'normalized': normalized,
                'lines': len(content.split('\n'))
            }

    print(f"Analisando {len(submissions)} submissões válidas...\n")

    # Compara todos os pares
    similarities = []
    students = list(submissions.keys())

    for i in range(len(students)):
        for j in range(i + 1, len(students)):
            student1 = students[i]
            student2 = students[j]

            # Similaridade do código normalizado
            sim = similarity_ratio(
                submissions[student1]['normalized'],
                submissions[student2]['normalized']
            )

            if sim > 0.70:  # Threshold de 70% de similaridade
                similarities.append({
                    'student1': student1,
                    'student2': student2,
                    'similarity': sim,
                    'lines1': submissions[student1]['lines'],
                    'lines2': submissions[student2]['lines']
                })

    # Ordena por similaridade (maior primeiro)
    similarities.sort(key=lambda x: x['similarity'], reverse=True)

    # Exibe resultados
    print("=" * 80)
    print("PARES COM ALTA SIMILARIDADE (>70%)")
    print("=" * 80)

    if not similarities:
        print("\nNenhum par com alta similaridade encontrado.")
    else:
        for idx, match in enumerate(similarities, 1):
            print(f"\n{idx}. {match['student1']} <-> {match['student2']}")
            print(f"   Similaridade: {match['similarity']*100:.1f}%")
            print(f"   Linhas: {match['lines1']} vs {match['lines2']}")

    print("\n" + "=" * 80)
    print(f"Total de pares suspeitos: {len(similarities)}")
    print("=" * 80)

    # Agrupa por clusters (submissões muito similares entre si)
    if similarities:
        print("\n\nANÁLISE DE CLUSTERS:")
        print("=" * 80)

        # Identifica grupos de submissões similares
        clusters = []
        processed = set()

        for match in similarities:
            if match['similarity'] > 0.85:  # Muito similares
                s1, s2 = match['student1'], match['student2']

                # Verifica se já está em algum cluster
                found_cluster = None
                for cluster in clusters:
                    if s1 in cluster or s2 in cluster:
                        found_cluster = cluster
                        break

                if found_cluster:
                    found_cluster.add(s1)
                    found_cluster.add(s2)
                else:
                    clusters.append({s1, s2})

        for idx, cluster in enumerate(clusters, 1):
            print(f"\nCluster {idx} ({len(cluster)} alunos):")
            for student in sorted(cluster):
                print(f"  - {student}")

if __name__ == "__main__":
    main()
