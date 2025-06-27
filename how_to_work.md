## Flow Penggunaan Utama

```
graph TD
    A[User Input] --> B{Input Type}
    B -->|Direct Code| C[Text Area Input]
    B -->|File Upload| D[File Upload]
    B -->|GitHub Repo| E[Repository URL]
    
    C --> F[Parse & Tokenize]
    D --> F
    E --> G[Clone Repository] --> F
    
    F --> H[AST Analysis]
    H --> I[Rule-based Check]
    H --> J[ML Pattern Detection]
    
    I --> K[Combine Results] 
    J --> K
    
    K --> L[Generate Suggestions]
    L --> M[Calculate Metrics]
    M --> N[Return Results]
    
    N --> O[Display in UI]
    O --> P[User Actions]
    P -->|Accept| Q[Apply Refactoring]
    P -->|Reject| R[Learn from Feedback]
```

## Cara Menggunakan

### Option A: Direct Code Input

```bash
# Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Test dengan curl
curl -X POST "http://localhost:8000/api/v1/analysis/code" \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def long_function():\n    # ... 50 lines of code\n    pass",
    "language": "python",
    "analysis_type": "full"
  }'
```

### Option B: File Upload
```bash
curl -X POST "http://localhost:8000/api/v1/analysis/file" \
  -F "file=@example.py"
```

### Option C: GitHub Repository

```bash
curl -X POST "http://localhost:8000/api/v1/github/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/username/repo",
    "branch": "main"
  }'
```

## Setup & Cara Menjalankan

```bash
# 1. Setup environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Download pre-trained models
python scripts/download_models.py

# 3. Run database migrations (if using database)
alembic upgrade head

# 4. Start Redis (for caching)
redis-server

# 5. Start the application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 6. Access web interface (if available)
# http://localhost:8000
```

## Docker Setup(Alternative)
```bash
docker-compose up --build
```

## Response Format

```json
{
  "issues": [
    {
      "type": "long_method",
      "severity": "medium", 
      "line": 15,
      "message": "Function has 25 lines (recommended: <20)",
      "suggestion": "Consider breaking into smaller functions"
    }
  ],
  "suggestions": [
    {
      "type": "extract_method",
      "description": "Extract lines 10-20 into separate method",
      "original_code": "...",
      "refactored_code": "...",
      "priority": "medium",
      "effort": "low"
    }
  ],
  "metrics": {
    "lines_of_code": 150,
    "cyclomatic_complexity": 12,
    "maintainability_index": 65,
    "technical_debt_minutes": 45
  },
  "summary": {
    "overall_score": 72,
    "grade": "B",
    "top_issues": ["long_method", "high_complexity"],
    "recommendations": ["Extract methods", "Reduce nesting"]
  }
}
```

## Sistem ini bekerja dengan cara:

- **Input**: User upload code/file/repo
- **Analysis**: AI analyze menggunakan AST + ML models
- **Detection**: Deteksi code smells dan anti-patterns
- **Suggestion**: Generate saran refactoring konkret
- **Output**: Return hasil analisis dengan metrics dan saran
- **Learning**: Belajar dari feedback user untuk improvement

## Thanks You All