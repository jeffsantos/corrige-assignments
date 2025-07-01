import ast
import os
import sys
from pathlib import Path
from collections import defaultdict

SRC_DIR = Path(__file__).parent / "src"

class ClassInfo:
    def __init__(self, name, bases, module):
        self.name = name
        self.bases = bases  # list of base class names
        self.module = module
        self.attrs = set()  # attribute types (composition)


def find_py_files(base_dir):
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py"):
                yield Path(root) / file


def parse_classes(py_file):
    with open(py_file, encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(py_file))
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            bases = [b.id if isinstance(b, ast.Name) else getattr(b, 'attr', None) for b in node.bases]
            ci = ClassInfo(node.name, bases, module=py_file.relative_to(SRC_DIR.parent).as_posix())
            # Find attributes that are instances of other classes (composition)
            for stmt in node.body:
                if isinstance(stmt, ast.AnnAssign) and isinstance(stmt.annotation, ast.Name):
                    ci.attrs.add(stmt.annotation.id)
                elif isinstance(stmt, ast.Assign):
                    # Try to detect: self.x = ClassName(...)
                    for target in stmt.targets:
                        if isinstance(target, ast.Attribute) and isinstance(stmt.value, ast.Call):
                            if isinstance(stmt.value.func, ast.Name):
                                ci.attrs.add(stmt.value.func.id)
            classes.append(ci)
    return classes


def build_class_map():
    class_map = {}
    module_map = defaultdict(list)
    for py_file in find_py_files(SRC_DIR):
        for ci in parse_classes(py_file):
            class_map[ci.name] = ci
            module_map[ci.module].append(ci.name)
    return class_map, module_map


def generate_mermaid(class_map, module_map):
    lines = ["classDiagram"]
    # Classes and inheritance
    for cname, ci in class_map.items():
        lines.append(f"    class {cname}")
        for base in ci.bases:
            if base and base != "object":
                lines.append(f"    {base} <|-- {cname}")
    # Composition (attribute references)
    for cname, ci in class_map.items():
        for attr in ci.attrs:
            if attr in class_map:
                lines.append(f"    {cname} --> {attr} : has-a")
    # Optionally, group by module (as comments)
    lines.append("")
    for module, classes in module_map.items():
        lines.append(f"%% Module: {module}")
        for cname in classes:
            lines.append(f"%%   - {cname}")
    return "\n".join(lines)


def main():
    class_map, module_map = build_class_map()
    mermaid = generate_mermaid(class_map, module_map)
    if len(sys.argv) > 1:
        out_path = sys.argv[1]
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(mermaid)
        print(f"Diagrama Mermaid salvo em {out_path}")
    else:
        print(mermaid)

if __name__ == "__main__":
    main() 