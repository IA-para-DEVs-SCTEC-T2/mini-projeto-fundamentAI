#!/usr/bin/env python3
"""
Script para criar labels e issues do FundamentAI no GitHub
Repositório: IA-para-DEVs-SCTEC-T2/mini-projeto-equipe08
"""

import subprocess
import sys

REPO = "IA-para-DEVs-SCTEC-T2/mini-projeto-equipe08"

# Labels necessárias
LABELS = [
    {"name": "setup", "color": "0e8a16", "description": "Configuração inicial do projeto"},
    {"name": "backend", "color": "1d76db", "description": "Backend Python"},
    {"name": "frontend", "color": "5319e7", "description": "Frontend React"},
    {"name": "database", "color": "fbca04", "description": "Banco de dados"},
    {"name": "collectors", "color": "c5def5", "description": "Coletores de dados"},
    {"name": "data", "color": "bfdadc", "description": "Dados e processamento"},
    {"name": "processors", "color": "d4c5f9", "description": "Processadores de dados"},
    {"name": "business-logic", "color": "f9d0c4", "description": "Lógica de negócio"},
    {"name": "prompts", "color": "c2e0c6", "description": "Prompts e LLM"},
    {"name": "llm", "color": "bfd4f2", "description": "Integração com LLM"},
    {"name": "api", "color": "0052cc", "description": "API REST"},
    {"name": "rest", "color": "006b75", "description": "REST API"},
    {"name": "etl", "color": "e99695", "description": "ETL e pipelines"},
    {"name": "automation", "color": "fef2c0", "description": "Automação"},
    {"name": "ui", "color": "d876e3", "description": "Interface do usuário"},
    {"name": "components", "color": "c5def5", "description": "Componentes React"},
    {"name": "services", "color": "bfdadc", "description": "Serviços"},
    {"name": "integration", "color": "ededed", "description": "Integração"},
    {"name": "security", "color": "ee0701", "description": "Segurança"},
    {"name": "config", "color": "fbca04", "description": "Configuração"},
    {"name": "test", "color": "0e8a16", "description": "Testes"},
    {"name": "docs", "color": "0075ca", "description": "Documentação"},
    {"name": "ci", "color": "1d76db", "description": "CI/CD"},
    {"name": "release", "color": "5319e7", "description": "Release"},
]

def create_label(label_data):
    """Cria uma label no GitHub"""
    cmd = [
        "gh", "label", "create",
        label_data["name"],
        "--repo", REPO,
        "--color", label_data["color"],
        "--description", label_data["description"],
        "--force"  # Sobrescreve se já existir
    ]
    
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        return {"success": True}
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": str(e), "stderr": e.stderr}

def create_labels():
    """Cria todas as labels necessárias"""
    print("🏷️  Criando labels no repositório...")
    print()
    
    for label in LABELS:
        print(f"  Criando label: {label['name']}")
        result = create_label(label)
        if result["success"]:
            print(f"    ✅ Criada")
        else:
            print(f"    ⚠️  Erro (pode já existir)")
    
    print()
    print("✅ Labels criadas/atualizadas com sucesso!")
    print()

def main():
    print("="*80)
    print("🚀 SETUP: Criando labels necessárias")
    print("="*80)
    print()
    
    create_labels()
    
    print("="*80)
    print("✅ Setup concluído!")
    print("="*80)
    print()
    print("Agora você pode executar o script de criação de issues.")

if __name__ == "__main__":
    main()
