#!/usr/bin/env python3
"""
Script simplificado de validação das correções no módulo de email.
Valida a sintaxe e lógica sem dependências externas.
"""

import re
import sys
from pathlib import Path


def test_email_agent_syntax():
    """Valida a sintaxe do arquivo email_agent.py."""
    print("\n" + "=" * 80)
    print("[TESTE] Validação de sintaxe - email_agent.py")
    print("=" * 80)
    
    file_path = Path(__file__).parent / "src" / "dev_agent" / "agents" / "email_agent.py"
    
    if not file_path.exists():
        print(f"✗ Arquivo não encontrado: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Compilar para verificar sintaxe
        compile(content, str(file_path), 'exec')
        print(f"✓ Sintaxe Python válida")
        
        # Verificar importações
        required_imports = [
            "from dev_agent.tools.email.sender import GmailSender",
            "from dev_agent.tools.email.reader import GmailReader",
            "import re",
        ]
        
        for imp in required_imports:
            if imp in content:
                print(f"✓ Import encontrado: {imp}")
            else:
                print(f"✗ Import NÃO encontrado: {imp}")
                return False
        
        # Verificar métodos críticos
        required_methods = [
            "def _is_send_intent",
            "def _extract_email_details",
            "async def run",
        ]
        
        for method in required_methods:
            if method in content:
                print(f"✓ Método encontrado: {method}")
            else:
                print(f"✗ Método NÃO encontrado: {method}")
                return False
        
        return True
        
    except SyntaxError as e:
        print(f"✗ Erro de sintaxe: {e}")
        return False
    except Exception as e:
        print(f"✗ Erro: {e}")
        return False


def test_sender_syntax():
    """Valida a sintaxe do arquivo sender.py."""
    print("\n" + "=" * 80)
    print("[TESTE] Validação de sintaxe - sender.py")
    print("=" * 80)
    
    file_path = Path(__file__).parent / "src" / "dev_agent" / "tools" / "email" / "sender.py"
    
    if not file_path.exists():
        print(f"✗ Arquivo não encontrado: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Compilar para verificar sintaxe
        compile(content, str(file_path), 'exec')
        print(f"✓ Sintaxe Python válida")
        
        # Verificar classe
        if "class GmailSender:" in content:
            print(f"✓ Classe GmailSender encontrada")
        else:
            print(f"✗ Classe GmailSender NÃO encontrada")
            return False
        
        # Verificar métodos críticos
        required_methods = [
            "def _create_message",
            "async def send_email",
        ]
        
        for method in required_methods:
            if method in content:
                print(f"✓ Método encontrado: {method}")
            else:
                print(f"✗ Método NÃO encontrado: {method}")
                return False
        
        return True
        
    except SyntaxError as e:
        print(f"✗ Erro de sintaxe: {e}")
        return False
    except Exception as e:
        print(f"✗ Erro: {e}")
        return False


def test_planner_syntax():
    """Valida a sintaxe e conteúdo do arquivo planner.py."""
    print("\n" + "=" * 80)
    print("[TESTE] Validação de sintaxe - planner.py")
    print("=" * 80)
    
    file_path = Path(__file__).parent / "src" / "dev_agent" / "orchestrator" / "planner.py"
    
    if not file_path.exists():
        print(f"✗ Arquivo não encontrado: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Compilar para verificar sintaxe
        compile(content, str(file_path), 'exec')
        print(f"✓ Sintaxe Python válida")
        
        # Verificar palavras-chave de email
        email_keywords = [
            "envie", "enviar", "mande", "mandar", "responda", "responder",
            "escreva", "escrever", "gere uma resposta", "gere uma proposta",
            "resposta", "envio", "compose", "rascunho", "draft", "correio"
        ]
        
        missing_keywords = []
        for keyword in email_keywords:
            if keyword not in content:
                missing_keywords.append(keyword)
        
        if missing_keywords:
            print(f"✗ Palavras-chave ausentes: {missing_keywords}")
            return False
        else:
            print(f"✓ Todas as {len(email_keywords)} palavras-chave de email presentes")
        
        # Verificar que email é reconhecido no LLM prompt
        if 'Usa o agente "email" quando o pedido envolver:' in content:
            print(f"✓ Email prompt detalhado presente")
        else:
            print(f"✗ Email prompt detalhado NÃO encontrado")
            return False
        
        return True
        
    except SyntaxError as e:
        print(f"✗ Erro de sintaxe: {e}")
        return False
    except Exception as e:
        print(f"✗ Erro: {e}")
        return False


def test_dispatcher_syntax():
    """Valida a sintaxe do arquivo dispatcher.py."""
    print("\n" + "=" * 80)
    print("[TESTE] Validação de sintaxe - dispatcher.py")
    print("=" * 80)
    
    file_path = Path(__file__).parent / "src" / "dev_agent" / "orchestrator" / "dispatcher.py"
    
    if not file_path.exists():
        print(f"✗ Arquivo não encontrado: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Compilar para verificar sintaxe
        compile(content, str(file_path), 'exec')
        print(f"✓ Sintaxe Python válida")
        
        # Verificar suporte para google_token
        if 'token = self.user_data.get("google_token")' in content:
            print(f"✓ Extração de google_token presente")
        else:
            print(f"✗ Extração de google_token NÃO encontrada")
            return False
        
        return True
        
    except SyntaxError as e:
        print(f"✗ Erro de sintaxe: {e}")
        return False
    except Exception as e:
        print(f"✗ Erro: {e}")
        return False


def test_query_route_syntax():
    """Valida a sintaxe do arquivo query.py."""
    print("\n" + "=" * 80)
    print("[TESTE] Validação de sintaxe - query.py route")
    print("=" * 80)
    
    file_path = Path(__file__).parent / "src" / "dev_agent" / "api" / "routes" / "query.py"
    
    if not file_path.exists():
        print(f"✗ Arquivo não encontrado: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Compilar para verificar sintaxe
        compile(content, str(file_path), 'exec')
        print(f"✓ Sintaxe Python válida")
        
        # Verificar que google_refresh_token é passado
        if '"google_refresh_token": user.google_refresh_token' in content:
            print(f"✓ google_refresh_token passado em user_data")
        else:
            print(f"✗ google_refresh_token NÃO encontrado em user_data")
            return False
        
        return True
        
    except SyntaxError as e:
        print(f"✗ Erro de sintaxe: {e}")
        return False
    except Exception as e:
        print(f"✗ Erro: {e}")
        return False


def analyze_send_intent_logic():
    """Analisa a lógica de _is_send_intent sem executar."""
    print("\n" + "=" * 80)
    print("[ANÁLISE] Lógica de _is_send_intent()")
    print("=" * 80)
    
    file_path = Path(__file__).parent / "src" / "dev_agent" / "agents" / "email_agent.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extrair o método
    match = re.search(r'def _is_send_intent\(self, query: str\) -> bool:.*?(?=\n    def |\n    async def |\Z)', content, re.DOTALL)
    
    if not match:
        print("✗ Método _is_send_intent não encontrado")
        return False
    
    method_content = match.group(0)
    
    # Verificar palavras-chave
    keywords = [
        "envie", "enviar", "mande", "mandar", "responda", "responder",
        "escreva", "escrever", "compose", "envio", "gere uma proposta",
    ]
    
    found_keywords = 0
    for kw in keywords:
        if kw in method_content:
            found_keywords += 1
    
    print(f"✓ Encontradas {found_keywords}/{len(keywords)} palavras-chave de envio")
    
    # Verificar detecção de aspas
    if 'if \'"\' in query and len(query) > 50:' in method_content or 'if \'"\' in query' in method_content:
        print(f"✓ Detecção de aspas duplas presente")
    else:
        print(f"✗ Detecção de aspas duplas ausente")
        return False
    
    if "if \"'\" in query and len(query) > 50:" in method_content or "if \"'\" in query" in method_content:
        print(f"✓ Detecção de aspas simples presente")
    else:
        print(f"✗ Detecção de aspas simples ausente")
        return False
    
    return True


def analyze_extract_email_logic():
    """Analisa a lógica de _extract_email_details sem executar."""
    print("\n" + "=" * 80)
    print("[ANÁLISE] Lógica de _extract_email_details()")
    print("=" * 80)
    
    file_path = Path(__file__).parent / "src" / "dev_agent" / "agents" / "email_agent.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extrair o método
    match = re.search(r'async def _extract_email_details\(self, query: str\).*?(?=\n    def |\n    async def |\Z)', content, re.DOTALL)
    
    if not match:
        print("✗ Método _extract_email_details não encontrado")
        return False
    
    method_content = match.group(0)
    
    # Verificar extração de email
    if r'[\w\.-]+@[\w\.-]+\.\w+' in method_content:
        print(f"✓ Regex de extração de email presente")
    else:
        print(f"✗ Regex de extração de email ausente")
        return False
    
    # Verificar extração de assunto
    if 'subject' in method_content.lower():
        print(f"✓ Lógica de extração de assunto presente")
    else:
        print(f"✗ Lógica de extração de assunto ausente")
        return False
    
    # Verificar retorno de tupla
    if 'return recipient, subject, body' in method_content:
        print(f"✓ Retorno de tupla (recipient, subject, body) presente")
    else:
        print(f"✗ Retorno de tupla ausente")
        return False
    
    return True


def main():
    """Executa todos os testes."""
    print("\n" + "=" * 80)
    print("[VALIDAÇÃO] Análise de Correções do Módulo de Email")
    print("=" * 80)
    
    tests = [
        ("Sintaxe - email_agent.py", test_email_agent_syntax),
        ("Sintaxe - sender.py", test_sender_syntax),
        ("Sintaxe - planner.py", test_planner_syntax),
        ("Sintaxe - dispatcher.py", test_dispatcher_syntax),
        ("Sintaxe - query.py", test_query_route_syntax),
        ("Lógica - _is_send_intent()", analyze_send_intent_logic),
        ("Lógica - _extract_email_details()", analyze_extract_email_logic),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ Exceção em {name}: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 80)
    print("[RESUMO] Resultados de Validação")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n✓ Todas as validações passaram!")
        return 0
    else:
        print(f"\n✗ {total - passed} validações falharam")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
