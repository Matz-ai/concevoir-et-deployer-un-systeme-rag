# Démo V2 : l'API FastAPI (port 8000) dans sa propre fenêtre, puis l'interface web (port 3000) ici.
# Ouvrir ensuite http://127.0.0.1:3000. Prérequis : venv installé, index construit, `npm install` dans web/.
Start-Process -FilePath "$PSScriptRoot\.venv\Scripts\python.exe" -WorkingDirectory $PSScriptRoot `
    -ArgumentList "-m", "uvicorn", "main:app", "--app-dir", "api", "--port", "8000"
npm --prefix "$PSScriptRoot\web" run dev
