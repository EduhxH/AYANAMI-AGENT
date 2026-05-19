#!/usr/bin/env python3
"""
Script simplificado de validação sem caracteres unicode.
"""

import re
import sys
from pathlib import Path


def test_imports():
    """Testa se os imports funcionam."""
    print("\n" + "=" * 80)
    print("[TESTE] Validacao de imports")
    print("=" * 80)
    
    file_path = Path(__file__).parent / "src" / "dev_agent" / "agents" / "email_agent.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        compile(content, str(file_path), 'exec')
        
        required_imports = [
            "from dev_agent.tools.email.sender import GmailSender",
            "from dev_agent.tools.email.reader import GmailReader",
        ]
        
        all_ok = True
        for imp in required_imports:
            if imp in content:
                print("[OK] Import: " + imp)
            else:
                print("[ERRO] Import ausente: " + imp)
                all_ok = False
        
        return all_ok
    except Exception as e:
        print("[ERRO] " + str(e))
        return False


def test_sender_exists():
    """Testa se GmailSender existe."""
    print("\n" + "=" * 80)
    print("[TESTE] Validacao de GmailSender")
    print("=" * 80)
    
    file_path = Path(__file__).parent / "src" / "dev_agent" / "tools" / "email" / "sender.py"
    
    if not file_path.exists():
        print("[ERRO] Arquivo nao encontrado: " + str(file_path))
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        compile(content, str(file_path), 'exec')
        print("[OK] Sintaxe valida")
        
        if "class GmailSender:" in content:
            print("[OK] Classe GmailSender encontrada")
            return True
        else:
            print("[ERRO] Classe GmailSender nao encontrada")
            return False
    except Exception as e:
        print("[ERRO] " + str(e))
        return False


def test_init_files():
    """Testa se os __init__.py existem."""
    print("\n" + "=" * 80)
    print("[TESTE] Validacao de __init__.py")
    print("=" * 80)
    
    files_to_check = [
        Path(__file__).parent / "src" / "dev_agent" / "tools" / "__init__.py",
        Path(__file__).parent / "src" / "dev_agent" / "tools" / "email" / "__init__.py",
    ]
    
    all_ok = True
    for fpath in files_to_check:
        if fpath.exists():
            print("[OK] Arquivo existe: " + fpath.name)
        else:
            print("[ERRO] Arquivo nao encontrado: " + fpath.name)
            all_ok = False
    
    return all_ok


def test_email_init_exports():
    """Testa se __init__.py exporta GmailSender."""
    print("\n" + "=" * 80)
    print("[TESTE] Validacao de exports em __init__.py")
    print("=" * 80)
    
    file_path = Path(__file__).parent / "src" / "dev_agent" / "tools" / "email" / "__init__.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if "GmailSender" in content and "GmailReader" in content:
            print("[OK] Ambas classes exportadas em __init__.py")
            return True
        else:
            print("[ERRO] Classes nao estao exportadas corretamente")
            return False
    except Exception as e:
        print("[ERRO] " + str(e))
        return False


def main():
    """Executa validacoes."""
    print("\n" + "=" * 80)
    print("[VALIDACAO] Estrutura de modulos de email")
    print("=" * 80)
    
    tests = [
        ("Imports", test_imports),
        ("GmailSender", test_sender_exists),
        ("__init__.py", test_init_files),
        ("Exports", test_email_init_exports),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print("\n[EXCECAO] " + name + ": " + str(e))
            results.append((name, False))
    
    print("\n" + "=" * 80)
    print("[RESUMO] Resultados")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(status + " " + name)
    
    print("\nTotal: " + str(passed) + "/" + str(total) + " testes passaram")
    
    if passed == total:
        print("\nTodas as validacoes passaram!")
        return 0
    else:
        print("\nAlgumas validacoes falharam")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
