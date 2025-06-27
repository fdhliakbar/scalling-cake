from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import tempfile
import os

from core.analyzer.ast_parser import ASTAnalyzer
from core.ml.models.classifier import CodeSmellClassifier
from core.rules.engine import RuleEngine
from services.file_service import FileService

router = APIRouter()

class CodeAnalysisRequest(BaseModel):
    code: str
    language: str = "python"
    analysis_type: str = "full"

class CodeAnalysisResponse(BaseModel):
    issues: List[Dict[str, Any]]
    suggestions: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    summary: Dict[str, Any]

@router.post("/code", response_model=CodeAnalysisResponse)
async def analyze_code(request: CodeAnalysisRequest):
    """Analyze code string and return issues/suggestions"""
    try:
        # Initialize analyzers
        ast_analyzer = ASTAnalyzer()
        rule_engine = RuleEngine()
        
        # Parse and analyze code
        ast_tree, features = ast_analyzer.parse_code(request.code, request.language)
        
        # Rule-based analysis
        rule_issues = rule_engine.analyze(ast_tree, request.language)
        
        # ML-based analysis (if models are loaded)
        ml_issues = []
        if "classifier" in models:
            classifier = models["classifier"]
            ml_issues = await classifier.predict_issues(request.code)
        
        # Generate suggestions
        suggestions = generate_suggestions(rule_issues + ml_issues, request.code)
        
        # Calculate metrics
        metrics = calculate_metrics(features, rule_issues, ml_issues)
        
        # Create summary
        summary = create_summary(rule_issues, ml_issues, metrics)
        
        return CodeAnalysisResponse(
            issues=rule_issues + ml_issues,
            suggestions=suggestions,
            metrics=metrics,
            summary=summary
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/file")
async def analyze_file(file: UploadFile = File(...)):
    """Upload and analyze a code file"""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Read file content
        file_service = FileService()
        code_content = file_service.read_file(temp_file_path)
        
        # Detect language from file extension
        language = detect_language(file.filename)
        
        # Analyze code
        request = CodeAnalysisRequest(
            code=code_content,
            language=language,
            analysis_type="full"
        )
        
        result = await analyze_code(request)
        
        # Cleanup
        os.unlink(temp_file_path)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch")
async def analyze_multiple_files(files: List[UploadFile] = File(...)):
    """Analyze multiple files at once"""
    results = []
    
    for file in files:
        try:
            result = await analyze_file(file)
            results.append({
                "filename": file.filename,
                "analysis": result,
                "status": "success"
            })
        except Exception as e:
            results.append({
                "filename": file.filename,
                "error": str(e),
                "status": "error"
            })
    
    return {"results": results}

# Helper functions
def generate_suggestions(issues, code):
    """Generate refactoring suggestions based on issues"""
    suggestions = []
    
    for issue in issues:
        if issue["type"] == "long_method":
            suggestions.append({
                "type": "extract_method",
                "description": "Extract part of this method into smaller methods",
                "priority": "medium",
                "effort": "medium"
            })
        elif issue["type"] == "duplicate_code":
            suggestions.append({
                "type": "extract_common_method",
                "description": "Extract duplicate code into a common method",
                "priority": "high",
                "effort": "low"
            })
    
    return suggestions

def calculate_metrics(features, rule_issues, ml_issues):
    """Calculate code quality metrics"""
    return {
        "lines_of_code": features.get("lines_of_code", 0),
        "cyclomatic_complexity": features.get("complexity", 0),
        "maintainability_index": calculate_maintainability_index(features),
        "technical_debt_minutes": len(rule_issues + ml_issues) * 15,
        "issue_count": len(rule_issues + ml_issues),
        "severity_breakdown": {
            "high": len([i for i in rule_issues + ml_issues if i.get("severity") == "high"]),
            "medium": len([i for i in rule_issues + ml_issues if i.get("severity") == "medium"]),
            "low": len([i for i in rule_issues + ml_issues if i.get("severity") == "low"])
        }
    }

def create_summary(rule_issues, ml_issues, metrics):
    """Create analysis summary"""
    total_issues = len(rule_issues + ml_issues)
    
    return {
        "overall_score": max(0, 100 - (total_issues * 10)),
        "grade": get_grade(metrics["maintainability_index"]),
        "top_issues": get_top_issues(rule_issues + ml_issues),
        "recommendations": get_recommendations(rule_issues + ml_issues)
    }

def detect_language(filename):
    """Detect programming language from file extension"""
    extensions = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".java": "java",
        ".cpp": "cpp",
        ".c": "c",
        ".cs": "csharp",
        ".php": "php",
        ".rb": "ruby",
        ".go": "go"
    }
    
    ext = os.path.splitext(filename)[1].lower()
    return extensions.get(ext, "unknown")