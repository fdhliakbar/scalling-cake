import ast
import astunparse
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass

@dataclass
class CodeFeatures:
    lines_of_code: int
    functions: List[Dict]
    classes: List[Dict]
    complexity: int
    imports: List[str]
    variables: List[str]

class ASTAnalyzer:
    def __init__(self):
        self.visitors = {
            "python": PythonASTVisitor(),
            "javascript": JavaScriptASTVisitor()
        }
    
    def parse_code(self, code: str, language: str = "python") -> Tuple[ast.AST, CodeFeatures]:
        """Parse code and extract features"""
        if language not in self.visitors:
            raise ValueError(f"Unsupported language: {language}")
        
        visitor = self.visitors[language]
        return visitor.parse_and_analyze(code)

class PythonASTVisitor(ast.NodeVisitor):
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.functions = []
        self.classes = []
        self.imports = []
        self.variables = []
        self.complexity = 0
        self.current_function = None
        self.current_class = None
    
    def parse_and_analyze(self, code: str) -> Tuple[ast.AST, CodeFeatures]:
        """Parse Python code and extract features"""
        try:
            tree = ast.parse(code)
            self.reset()
            self.visit(tree)
            
            features = CodeFeatures(
                lines_of_code=len(code.split('\n')),
                functions=self.functions,
                classes=self.classes,
                complexity=self.complexity,
                imports=self.imports,
                variables=self.variables
            )
            
            return tree, features
            
        except SyntaxError as e:
            raise ValueError(f"Syntax error in code: {e}")
    
    def visit_FunctionDef(self, node):
        """Visit function definitions"""
        func_info = {
            "name": node.name,
            "line_start": node.lineno,
            "line_end": node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
            "args_count": len(node.args.args),
            "decorators": [ast.unparse(d) for d in node.decorator_list],
            "complexity": self.calculate_function_complexity(node),
            "lines_of_code": (node.end_lineno or node.lineno) - node.lineno
        }
        
        self.functions.append(func_info)
        self.current_function = func_info
        
        # Add to total complexity
        self.complexity += func_info["complexity"]
        
        self.generic_visit(node)
        self.current_function = None
    
    def visit_ClassDef(self, node):
        """Visit class definitions"""
        class_info = {
            "name": node.name,
            "line_start": node.lineno,
            "line_end": node.end_lineno if hasattr(node, 'end_lineno') else node.lineno,
            "methods": [],
            "base_classes": [ast.unparse(base) for base in node.bases],
            "decorators": [ast.unparse(d) for d in node.decorator_list]
        }
        
        self.classes.append(class_info)
        self.current_class = class_info
        
        self.generic_visit(node)
        self.current_class = None
    
    def visit_Import(self, node):
        """Visit import statements"""
        for alias in node.names:
            self.imports.append(alias.name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Visit from-import statements"""
        module = node.module or ""
        for alias in node.names:
            self.imports.append(f"{module}.{alias.name}")
        self.generic_visit(node)
    
    def visit_If(self, node):
        """Visit if statements (adds to complexity)"""
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_For(self, node):
        """Visit for loops (adds to complexity)"""
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_While(self, node):
        """Visit while loops (adds to complexity)"""
        self.complexity += 1
        self.generic_visit(node)
    
    def visit_Try(self, node):
        """Visit try statements (adds to complexity)"""
        self.complexity += 1
        self.generic_visit(node)
    
    def calculate_function_complexity(self, node):
        """Calculate cyclomatic complexity for a function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity

class JavaScriptASTVisitor:
    """JavaScript AST visitor (placeholder - would need JS parser like esprima)"""
    def parse_and_analyze(self, code: str):
        # For now, return basic structure
        # In real implementation, use a JS parser
        return None, CodeFeatures(
            lines_of_code=len(code.split('\n')),
            functions=[],
            classes=[],
            complexity=1,
            imports=[],
            variables=[]
        )