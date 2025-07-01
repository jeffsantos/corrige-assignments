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
        self.attrs = set()  # attribute types (composição)
        self.dependencies = set()  # classes que esta classe depende (dependência)


def find_py_files(base_dir):
    """Encontra todos os arquivos Python no diretório."""
    py_files = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py"):
                py_files.append(Path(root) / file)
    return py_files


def extract_type_name(type_annotation):
    """Extrai o nome do tipo de uma anotação de tipo."""
    if isinstance(type_annotation, ast.Name):
        return type_annotation.id
    elif isinstance(type_annotation, ast.Attribute):
        return type_annotation.attr
    elif isinstance(type_annotation, ast.Subscript):
        # Para tipos como List[ClassName], Optional[ClassName], etc.
        if isinstance(type_annotation.value, ast.Name):
            return type_annotation.value.id
        elif isinstance(type_annotation.value, ast.Attribute):
            return type_annotation.value.attr
    elif isinstance(type_annotation, ast.Constant):
        # Para strings de tipo (type hints como strings)
        if isinstance(type_annotation.value, str):
            return type_annotation.value
    return None


def parse_classes(py_file):
    """Parse classes de um arquivo Python."""
    try:
        with open(py_file, encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(py_file))
    except Exception as e:
        print(f"Erro ao parsear {py_file}: {e}")
        return []
    
    classes = []
    imports = {}  # Mapeia imports para nomes locais
    
    # Primeiro, coletar imports
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.asname:
                    imports[alias.asname] = alias.name
                else:
                    imports[alias.name] = alias.name
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                if alias.asname:
                    imports[alias.asname] = f"{module}.{alias.name}"
                else:
                    imports[alias.name] = f"{module}.{alias.name}"
    
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
            
            # Encontrar atributos e dependências
            for stmt in node.body:
                # Anotações de tipo (type hints)
                if isinstance(stmt, ast.AnnAssign):
                    if isinstance(stmt.annotation, ast.Name):
                        ci.attrs.add(stmt.annotation.id)
                        ci.dependencies.add(stmt.annotation.id)
                    elif isinstance(stmt.annotation, ast.Attribute):
                        ci.attrs.add(stmt.annotation.attr)
                        ci.dependencies.add(stmt.annotation.attr)
                    else:
                        type_name = extract_type_name(stmt.annotation)
                        if type_name:
                            ci.dependencies.add(type_name)
                
                # Atribuições (composição)
                elif isinstance(stmt, ast.Assign):
                    for target in stmt.targets:
                        if isinstance(target, ast.Attribute) and isinstance(stmt.value, ast.Call):
                            if isinstance(stmt.value.func, ast.Name):
                                ci.attrs.add(stmt.value.func.id)
                                ci.dependencies.add(stmt.value.func.id)
                            elif isinstance(stmt.value.func, ast.Attribute):
                                ci.attrs.add(stmt.value.func.attr)
                                ci.dependencies.add(stmt.value.func.attr)
                
                # Funções com type hints
                elif isinstance(stmt, ast.FunctionDef):
                    # Parâmetros com type hints
                    for arg in stmt.args.args:
                        if arg.annotation:
                            type_name = extract_type_name(arg.annotation)
                            if type_name:
                                ci.dependencies.add(type_name)
                    
                    # Retorno com type hint
                    if stmt.returns:
                        type_name = extract_type_name(stmt.returns)
                        if type_name:
                            ci.dependencies.add(type_name)
                    
                    # Corpo da função - procurar por referências de tipo
                    for func_node in ast.walk(stmt):
                        if isinstance(func_node, ast.Name):
                            if func_node.id in imports:
                                # É um import
                                imported_name = imports[func_node.id]
                                if '.' in imported_name:
                                    class_name = imported_name.split('.')[-1]
                                    ci.dependencies.add(class_name)
                                else:
                                    ci.dependencies.add(imported_name)
            
            # Procurar por referências de tipo no corpo da classe
            for class_node in ast.walk(node):
                if isinstance(class_node, ast.Name):
                    if class_node.id in imports:
                        imported_name = imports[class_node.id]
                        if '.' in imported_name:
                            class_name = imported_name.split('.')[-1]
                            ci.dependencies.add(class_name)
                        else:
                            ci.dependencies.add(imported_name)
            
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
            if ci.dependencies:
                print(f"      Dependências: {ci.dependencies}")
    
    print(f"Total de classes encontradas: {len(class_map)}")
    return class_map, module_map


def get_package_name(module_path):
    """Extrai o nome do pacote a partir do caminho do módulo."""
    # Remove 'src/' do início
    if module_path.startswith('src/'):
        module_path = module_path[4:]
    
    # Se tem subdiretórios, pega o primeiro (ex: domain/models.py -> domain)
    if '/' in module_path:
        return module_path.split('/')[0]
    else:
        return 'root'


def generate_mermaid(class_map, module_map):
    """Gera diagrama Mermaid com pacotes."""
    lines = ["classDiagram"]
    
    # Agrupar classes por pacote
    packages = defaultdict(list)
    for module, classes in module_map.items():
        package = get_package_name(module)
        packages[package].extend(classes)
    
    # Definir pacotes
    for package_name, classes in packages.items():
        lines.append(f"    package {package_name} {{")
        for class_name in sorted(classes):
            lines.append(f"        class {class_name}")
        lines.append("    }")
    
    # Herança
    for cname, ci in class_map.items():
        for base in ci.bases:
            if base and base != "object" and base in class_map:
                lines.append(f"    {base} <|-- {cname}")
    
    # Composição (referências de atributos)
    for cname, ci in class_map.items():
        for attr in ci.attrs:
            if attr in class_map:
                lines.append(f"    {cname} --> {attr} : has-a")
    
    # Dependências (referências de tipo, imports, etc.)
    for cname, ci in class_map.items():
        for dep in ci.dependencies:
            if dep in class_map and dep not in ci.attrs:  # Não duplicar composições
                lines.append(f"    {cname} ..> {dep} : depends-on")
    
    return "\n".join(lines)


def generate_markdown(class_map, module_map):
    """Gera arquivo Markdown com diagrama Mermaid."""
    mermaid_diagram = generate_mermaid(class_map, module_map)
    
    # Estatísticas
    total_classes = len(class_map)
    modules_count = len(module_map)
    
    # Contar relacionamentos
    inheritances = 0
    compositions = 0
    dependencies = 0
    
    for ci in class_map.values():
        for base in ci.bases:
            if base and base != "object" and base in class_map:
                inheritances += 1
        compositions += len([attr for attr in ci.attrs if attr in class_map])
        dependencies += len([dep for dep in ci.dependencies if dep in class_map and dep not in ci.attrs])
    
    # Agrupar classes por módulo para a tabela
    module_details = []
    for module, classes in module_map.items():
        module_details.append({
            'module': module,
            'classes': sorted(classes),
            'count': len(classes)
        })
    module_details.sort(key=lambda x: x['module'])
    
    # Agrupar por pacotes para estatísticas
    packages = defaultdict(list)
    for module, classes in module_map.items():
        package = get_package_name(module)
        packages[package].extend(classes)
    
    packages_count = len(packages)
    
    markdown_content = f"""# Diagrama UML - Sistema de Correção Automática

> Gerado automaticamente em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}

## Visão Geral

Este diagrama representa a arquitetura e relacionamentos entre as classes do sistema de correção automática de assignments.

**Estatísticas:**
- **Total de classes:** {total_classes}
- **Módulos:** {modules_count}
- **Pacotes:** {packages_count}
- **Heranças:** {inheritances}
- **Composições:** {compositions}
- **Dependências:** {dependencies}

## Diagrama de Classes

```mermaid
{mermaid_diagram}
```

## Estrutura por Pacote

"""
    
    # Adicionar tabela de pacotes
    markdown_content += "| Pacote | Classes | Quantidade |\n"
    markdown_content += "|--------|---------|------------|\n"
    
    for package_name, classes in sorted(packages.items()):
        classes_list = ', '.join(sorted(classes))
        count = len(classes)
        markdown_content += f"| `{package_name}` | {classes_list} | {count} |\n"
    
    markdown_content += f"""

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
    inheritances_list = []
    for cname, ci in class_map.items():
        for base in ci.bases:
            if base and base != "object" and base in class_map:
                inheritances_list.append(f"- `{cname}` herda de `{base}`")
    
    if inheritances_list:
        markdown_content += "\n".join(inheritances_list)
    else:
        markdown_content += "- Nenhuma herança encontrada"
    
    markdown_content += "\n\n### Composição\n"
    
    # Listar composições
    compositions_list = []
    for cname, ci in class_map.items():
        for attr in ci.attrs:
            if attr in class_map:
                compositions_list.append(f"- `{cname}` contém `{attr}`")
    
    if compositions_list:
        markdown_content += "\n".join(compositions_list)
    else:
        markdown_content += "- Nenhuma composição encontrada"
    
    markdown_content += "\n\n### Dependências\n"
    
    # Listar dependências
    dependencies_list = []
    for cname, ci in class_map.items():
        for dep in ci.dependencies:
            if dep in class_map and dep not in ci.attrs:  # Não duplicar composições
                dependencies_list.append(f"- `{cname}` depende de `{dep}`")
    
    if dependencies_list:
        markdown_content += "\n".join(dependencies_list)
    else:
        markdown_content += "- Nenhuma dependência encontrada"
    
    markdown_content += f"""

## Legenda do Diagrama

- **<|--** : Herança (is-a)
- **-->** : Composição (has-a)
- **..>** : Dependência (depends-on)
- **package** : Agrupamento de classes por pacote/módulo

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