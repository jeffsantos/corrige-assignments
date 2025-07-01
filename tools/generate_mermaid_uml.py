import ast
import os
import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Corrigir caminho: tools/ está um nível acima de src/
SRC_DIR = Path(__file__).parent.parent / "src"

class ClassInfo:
    def __init__(self, name, bases, module):
        self.name = name
        self.bases = bases  # list of base class names
        self.module = module
        self.attrs = set()  # attribute types (composition)


def find_py_files(base_dir):
    """Encontra todos os arquivos Python no diretório."""
    py_files = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py"):
                py_files.append(Path(root) / file)
    return py_files


def parse_classes(py_file):
    """Parse classes de um arquivo Python."""
    try:
        with open(py_file, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(py_file))
    except Exception as e:
        print(f"Erro ao parsear {py_file}: {e}")
        return []
    
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Extrair bases (herança)
            bases = []
            for b in node.bases:
                if isinstance(b, ast.Name):
                    bases.append(b.id)
                elif isinstance(b, ast.Attribute):
                    bases.append(b.attr)
                else:
                    bases.append(str(b))
            
            # Calcular módulo relativo
            module_path = py_file.relative_to(SRC_DIR.parent).as_posix()
            
            ci = ClassInfo(node.name, bases, module=module_path)
            
            # Encontrar atributos que são instâncias de outras classes (composição)
            for stmt in node.body:
                if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.annotation, ast.Name):
                    ci.attrs.add(stmt.annotation.id)
                elif isinstance(stmt, ast.Assign):
                    # Tentar detectar: self.x = ClassName(...)
                    for target in stmt.targets:
                        if isinstance(target, ast.Attribute) and isinstance(stmt.value, ast.Call):
                            if isinstance(stmt.value.func, ast.Name):
                                ci.attrs.add(stmt.value.func.id)
                            elif isinstance(stmt.value.func, ast.Attribute):
                                ci.attrs.add(stmt.value.func.attr)
            
            classes.append(ci)
    return classes


def build_class_map():
    """Constrói mapa de classes e módulos."""
    if not SRC_DIR.exists():
        print(f"Erro: Diretório src não encontrado em {SRC_DIR}")
        return {}, {}
    
    print(f"Procurando arquivos Python em: {SRC_DIR}")
    
    class_map = {}
    module_map = defaultdict(list)
    
    py_files = find_py_files(SRC_DIR)
    print(f"Encontrados {len(py_files)} arquivos Python")
    
    for py_file in py_files:
        print(f"  Processando: {py_file.relative_to(SRC_DIR.parent)}")
        for ci in parse_classes(py_file):
            class_map[ci.name] = ci
            module_map[ci.module].append(ci.name)
            print(f"    Classe encontrada: {ci.name} (bases: {ci.bases})")
    
    print(f"Total de classes encontradas: {len(class_map)}")
    return class_map, module_map


def generate_mermaid(class_map, module_map):
    """Gera diagrama Mermaid."""
    lines = ["classDiagram"]
    
    # Classes e herança
    for cname, ci in class_map.items():
        lines.append(f"    class {cname}")
        for base in ci.bases:
            if base and base != "object" and base in class_map:
                lines.append(f"    {base} <|-- {cname}")
    
    # Composição (referências de atributos)
    for cname, ci in class_map.items():
        for attr in ci.attrs:
            if attr in class_map:
                lines.append(f"    {cname} --> {attr} : has-a")
    
    # Agrupar por módulo (como comentários)
    lines.append("")
    for module, classes in module_map.items():
        lines.append(f"%% Module: {module}")
        for cname in classes:
            lines.append(f"%%   - {cname}")
    
    return "\n".join(lines)


def generate_markdown(class_map, module_map):
    """Gera arquivo Markdown com diagrama Mermaid."""
    mermaid_diagram = generate_mermaid(class_map, module_map)
    
    # Estatísticas
    total_classes = len(class_map)
    modules_count = len(module_map)
    
    # Agrupar classes por módulo para a tabela
    module_details = []
    for module, classes in module_map.items():
        module_details.append({
            'module': module,
            'classes': sorted(classes),
            'count': len(classes)
        })
    module_details.sort(key=lambda x: x['module'])
    
    markdown_content = f"""# Diagrama UML - Sistema de Correção Automática

> Gerado automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}

## Visão Geral

Este diagrama representa a arquitetura e relacionamentos entre as classes do sistema de correção automática de assignments.

**Estatísticas:**
- **Total de classes:** {total_classes}
- **Módulos:** {modules_count}

## Diagrama de Classes

```mermaid
{mermaid_diagram}
```

## Estrutura por Módulo

"""
    
    # Adicionar tabela de módulos
    markdown_content += "| Módulo | Classes | Quantidade |\n"
    markdown_content += "|--------|---------|------------|\n"
    
    for module_detail in module_details:
        module_name = module_detail['module'].replace('src/', '')
        classes_list = ', '.join(module_detail['classes'])
        count = module_detail['count']
        markdown_content += f"| `{module_name}` | {classes_list} | {count} |\n"
    
    markdown_content += f"""

## Detalhes dos Relacionamentos

### Herança
"""
    
    # Listar heranças
    inheritances = []
    for cname, ci in class_map.items():
        for base in ci.bases:
            if base and base != "object" and base in class_map:
                inheritances.append(f"- `{cname}` herda de `{base}`")
    
    if inheritances:
        markdown_content += "\n".join(inheritances)
    else:
        markdown_content += "- Nenhuma herança encontrada"
    
    markdown_content += "\n\n### Composição\n"
    
    # Listar composições
    compositions = []
    for cname, ci in class_map.items():
        for attr in ci.attrs:
            if attr in class_map:
                compositions.append(f"- `{cname}` contém `{attr}`")
    
    if compositions:
        markdown_content += "\n".join(compositions)
    else:
        markdown_content += "- Nenhuma composição encontrada"
    
    markdown_content += f"""

## Como Visualizar

1. **GitHub**: Este arquivo Markdown será renderizado automaticamente com o diagrama Mermaid
2. **VS Code**: Use a extensão "Markdown Preview Mermaid Support"
3. **Online**: Cole o conteúdo do bloco Mermaid em https://mermaid.live/

## Gerado por

Script: `tools/generate_mermaid_uml.py`
"""
    
    return markdown_content


def main():
    class_map, module_map = build_class_map()
    
    if not class_map:
        print("Nenhuma classe encontrada!")
        return
    
    markdown_content = generate_markdown(class_map, module_map)
    
    if len(sys.argv) > 1:
        out_path = sys.argv[1]
        # Garantir que a extensão seja .md
        if not out_path.endswith('.md'):
            out_path += '.md'
    else:
        out_path = "diagrama_uml.md"
    
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    print(f"Diagrama Markdown salvo em {out_path}")
    print(f"Total de classes: {len(class_map)}")
    print(f"Total de módulos: {len(module_map)}")


if __name__ == "__main__":
    main() 