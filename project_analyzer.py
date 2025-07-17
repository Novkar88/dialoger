import os
import re
import ast
from collections import defaultdict
from typing import Dict, Set, List
import logging

# Настройка логгера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('project_analysis.log'),
        logging.StreamHandler()
    ]
)

class ProjectAnalyzer:
    def __init__(self, project_root: str):
        self.project_root = project_root
        self.file_dependencies: Dict[str, Set[str]] = defaultdict(set)
        self.all_files: Set[str] = set()
        self.used_files: Set[str] = set()
        self.unused_files: Set[str] = set()

    def analyze_project(self):
        """Основной метод анализа проекта"""
        self._collect_all_files()
        self._analyze_imports()
        self._find_unused_files()
        self._log_results()

    def _collect_all_files(self):
        """Собираем все файлы проекта"""
        for root, _, files in os.walk(self.project_root):
            for file in files:
                if file.endswith(('.py', '.dart', '.kt', '.java', '.xml')):
                    full_path = os.path.join(root, file)
                    self.all_files.add(full_path)
        logging.info(f"Найдено файлов: {len(self.all_files)}")

    def _analyze_imports(self):
        """Анализируем зависимости между файлами"""
        for file_path in self.all_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                    if file_path.endswith('.py'):
                        self._analyze_python_imports(file_path, content)
                    elif file_path.endswith('.dart'):
                        self._analyze_dart_imports(file_path, content)
                    # Можно добавить обработку других языков

                    self.used_files.add(file_path)  # Файл считается используемым
            except Exception as e:
                logging.error(f"Ошибка при анализе {file_path}: {e}")

    def _analyze_python_imports(self, file_path: str, content: str):
        """Анализ импортов в Python-файлах"""
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        self._resolve_import(file_path, alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module
                    if module:
                        self._resolve_import(file_path, module)
        except Exception as e:
            logging.warning(f"Ошибка парсинга AST в {file_path}: {e}")

    def _analyze_dart_imports(self, file_path: str, content: str):
        """Анализ импортов в Dart-файлах"""
        import_pattern = r'import\s+[\'"](.+?)[\'"]'
        for match in re.finditer(import_pattern, content):
            import_path = match.group(1)
            self._resolve_import(file_path, import_path)

    def _resolve_import(self, source_file: str, import_path: str):
        """Разрешаем путь импорта в абсолютный путь к файлу"""
        try:
            # Для Python
            if import_path.endswith('.py'):
                target_path = os.path.normpath(os.path.join(
                    os.path.dirname(source_file),
                    import_path
                ))
            # Для Dart
            elif import_path.startswith('package:'):
                target_path = os.path.normpath(os.path.join(
                    self.project_root,
                    'lib',
                    import_path.replace('package:', '').replace('/', os.sep)
                ))
            else:
                target_path = os.path.normpath(os.path.join(
                    os.path.dirname(source_file),
                    f"{import_path.replace('.', os.sep)}.dart"
                ))

            if os.path.exists(target_path):
                self.file_dependencies[source_file].add(target_path)
        except Exception as e:
            logging.debug(f"Не удалось разрешить импорт {import_path} из {source_file}: {e}")

    def _find_unused_files(self):
        """Находим неиспользуемые файлы"""
        all_files_set = self.all_files
        used_files_set = self.used_files

        # Добавляем файлы, на которые есть ссылки из других файлов
        for deps in self.file_dependencies.values():
            used_files_set.update(deps)

        self.unused_files = all_files_set - used_files_set

    def _log_results(self):
        """Логируем результаты анализа"""
        logging.info("\n=== ИЕРАРХИЯ ПРОЕКТА ===")
        for file, deps in self.file_dependencies.items():
            rel_file = os.path.relpath(file, self.project_root)
            rel_deps = [os.path.relpath(d, self.project_root) for d in deps]
            logging.info(f"{rel_file} зависит от:")
            for dep in rel_deps:
                logging.info(f"  → {dep}")

        logging.info("\n=== НЕИСПОЛЬЗУЕМЫЕ ФАЙЛЫ ===")
        for file in sorted(self.unused_files):
            logging.info(os.path.relpath(file, self.project_root))

        logging.info(f"\nИтого: {len(self.all_files)} файлов, {len(self.unused_files)} неиспользуемых")

    def get_dependency_graph(self) -> Dict[str, List[str]]:
        """Возвращает граф зависимостей для визуализации"""
        return {
            os.path.relpath(k, self.project_root): [
                os.path.relpath(v, self.project_root) for v in vs
            ]
            for k, vs in self.file_dependencies.items()
        }

if __name__ == "__main__":
    project_path = input("Введите путь к корню проекта: ").strip()
    if not os.path.isdir(project_path):
        logging.error("Указанный путь не существует или не является директорией")
        exit(1)

    analyzer = ProjectAnalyzer(project_path)
    analyzer.analyze_project()

    # Дополнительно можно сохранить граф зависимостей в JSON
    import json
    with open('dependency_graph.json', 'w') as f:
        json.dump(analyzer.get_dependency_graph(), f, indent=2)
    logging.info("Граф зависимостей сохранен в dependency_graph.json")