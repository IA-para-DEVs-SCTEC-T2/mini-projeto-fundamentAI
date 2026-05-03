#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes para o script de logging de prompts.

Este arquivo contém testes manuais para validar as diferentes estratégias
de captura de conteúdo do prompt implementadas em log_prompt.py.

Uso:
    python3 .kiro/scripts/test_log_prompt.py
"""

import os
import sys
import subprocess


def test_strategy_1_env_variable():
    """
    Testa Estratégia 1: Captura via variável de ambiente KIRO_PROMPT.
    """
    print("=" * 60)
    print("Teste 1: Captura via variável de ambiente KIRO_PROMPT")
    print("=" * 60)
    
    # Define variável de ambiente
    test_prompt = "Este é um prompt de teste via variável de ambiente"
    env = os.environ.copy()
    env['KIRO_PROMPT'] = test_prompt
    
    # Executa script com variável de ambiente definida
    result = subprocess.run(
        ['python3', '-c', '''
import sys
sys.path.insert(0, ".kiro/scripts")
from log_prompt import get_prompt_content
print(get_prompt_content())
'''],
        env=env,
        capture_output=True,
        text=True
    )
    
    captured = result.stdout.strip()
    
    if captured == test_prompt:
        print("✅ PASSOU: Conteúdo capturado via variável de ambiente")
        print(f"   Esperado: {test_prompt}")
        print(f"   Obtido:   {captured}")
    else:
        print("❌ FALHOU: Conteúdo não foi capturado corretamente")
        print(f"   Esperado: {test_prompt}")
        print(f"   Obtido:   {captured}")
    
    print()


def test_strategy_2_stdin():
    """
    Testa Estratégia 2: Captura via stdin (quando não é TTY).
    """
    print("=" * 60)
    print("Teste 2: Captura via stdin (não-TTY)")
    print("=" * 60)
    
    test_prompt = "Este é um prompt de teste via stdin"
    
    # Executa script passando conteúdo via stdin
    result = subprocess.run(
        ['python3', '-c', '''
import sys
sys.path.insert(0, ".kiro/scripts")
from log_prompt import get_prompt_content
print(get_prompt_content())
'''],
        input=test_prompt,
        capture_output=True,
        text=True
    )
    
    captured = result.stdout.strip()
    
    if captured == test_prompt:
        print("✅ PASSOU: Conteúdo capturado via stdin")
        print(f"   Esperado: {test_prompt}")
        print(f"   Obtido:   {captured}")
    else:
        print("❌ FALHOU: Conteúdo não foi capturado corretamente")
        print(f"   Esperado: {test_prompt}")
        print(f"   Obtido:   {captured}")
    
    print()


def test_strategy_3_fallback():
    """
    Testa Estratégia 3: Fallback para placeholder quando nenhuma estratégia funciona.
    """
    print("=" * 60)
    print("Teste 3: Fallback para placeholder")
    print("=" * 60)
    
    expected_placeholder = "[Conteúdo do prompt não capturado automaticamente]"
    
    # Executa script sem variável de ambiente e sem stdin
    # (stdin será um TTY ou vazio)
    result = subprocess.run(
        ['python3', '-c', '''
import sys
sys.path.insert(0, ".kiro/scripts")
from log_prompt import get_prompt_content
print(get_prompt_content())
'''],
        capture_output=True,
        text=True
    )
    
    captured = result.stdout.strip()
    
    if captured == expected_placeholder:
        print("✅ PASSOU: Placeholder retornado quando nenhuma estratégia funciona")
        print(f"   Esperado: {expected_placeholder}")
        print(f"   Obtido:   {captured}")
    else:
        print("❌ FALHOU: Placeholder não foi retornado corretamente")
        print(f"   Esperado: {expected_placeholder}")
        print(f"   Obtido:   {captured}")
    
    print()


def test_priority_env_over_stdin():
    """
    Testa que variável de ambiente tem prioridade sobre stdin.
    """
    print("=" * 60)
    print("Teste 4: Prioridade - Env tem precedência sobre stdin")
    print("=" * 60)
    
    env_prompt = "Prompt via ENV (deve ter prioridade)"
    stdin_prompt = "Prompt via stdin (não deve ser usado)"
    
    env = os.environ.copy()
    env['KIRO_PROMPT'] = env_prompt
    
    # Executa script com AMBOS env e stdin definidos
    result = subprocess.run(
        ['python3', '-c', '''
import sys
sys.path.insert(0, ".kiro/scripts")
from log_prompt import get_prompt_content
print(get_prompt_content())
'''],
        env=env,
        input=stdin_prompt,
        capture_output=True,
        text=True
    )
    
    captured = result.stdout.strip()
    
    if captured == env_prompt:
        print("✅ PASSOU: Variável de ambiente tem prioridade sobre stdin")
        print(f"   Esperado: {env_prompt}")
        print(f"   Obtido:   {captured}")
    else:
        print("❌ FALHOU: Prioridade incorreta")
        print(f"   Esperado: {env_prompt}")
        print(f"   Obtido:   {captured}")
    
    print()


def test_empty_env_variable():
    """
    Testa que variável de ambiente vazia é ignorada e fallback é usado.
    """
    print("=" * 60)
    print("Teste 5: Variável de ambiente vazia deve ser ignorada")
    print("=" * 60)
    
    expected_placeholder = "[Conteúdo do prompt não capturado automaticamente]"
    
    env = os.environ.copy()
    env['KIRO_PROMPT'] = ""  # Vazia
    
    result = subprocess.run(
        ['python3', '-c', '''
import sys
sys.path.insert(0, ".kiro/scripts")
from log_prompt import get_prompt_content
print(get_prompt_content())
'''],
        env=env,
        capture_output=True,
        text=True
    )
    
    captured = result.stdout.strip()
    
    if captured == expected_placeholder:
        print("✅ PASSOU: Variável de ambiente vazia ignorada, placeholder usado")
        print(f"   Esperado: {expected_placeholder}")
        print(f"   Obtido:   {captured}")
    else:
        print("❌ FALHOU: Comportamento incorreto com env vazia")
        print(f"   Esperado: {expected_placeholder}")
        print(f"   Obtido:   {captured}")
    
    print()


def test_whitespace_only_env():
    """
    Testa que variável de ambiente com apenas espaços é ignorada.
    """
    print("=" * 60)
    print("Teste 6: Variável de ambiente com apenas espaços")
    print("=" * 60)
    
    expected_placeholder = "[Conteúdo do prompt não capturado automaticamente]"
    
    env = os.environ.copy()
    env['KIRO_PROMPT'] = "   \n\t   "  # Apenas whitespace
    
    result = subprocess.run(
        ['python3', '-c', '''
import sys
sys.path.insert(0, ".kiro/scripts")
from log_prompt import get_prompt_content
print(get_prompt_content())
'''],
        env=env,
        capture_output=True,
        text=True
    )
    
    captured = result.stdout.strip()
    
    if captured == expected_placeholder:
        print("✅ PASSOU: Variável com apenas espaços ignorada")
        print(f"   Esperado: {expected_placeholder}")
        print(f"   Obtido:   {captured}")
    else:
        print("❌ FALHOU: Comportamento incorreto com whitespace")
        print(f"   Esperado: {expected_placeholder}")
        print(f"   Obtido:   {captured}")
    
    print()


def main():
    """
    Executa todos os testes.
    """
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "TESTES DE CAPTURA DE PROMPT" + " " * 20 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")
    
    test_strategy_1_env_variable()
    test_strategy_2_stdin()
    test_strategy_3_fallback()
    test_priority_env_over_stdin()
    test_empty_env_variable()
    test_whitespace_only_env()
    
    print("=" * 60)
    print("Testes concluídos!")
    print("=" * 60)
    print("\nNota: Estes testes validam o comportamento da função")
    print("get_prompt_content() em diferentes cenários. O comportamento")
    print("real no contexto do hook do Kiro pode variar dependendo de")
    print("como o Kiro expõe o conteúdo do prompt.")
    print()


if __name__ == '__main__':
    main()
