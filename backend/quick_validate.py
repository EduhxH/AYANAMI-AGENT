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


def test_email_agent_logic():
    """Valida a logica interna do EmailAgent com mocks."""
    print("\n" + "=" * 80)
    print("[TESTE] Validacao de logica interna - EmailAgent")
    print("=" * 80)
    
    import sys
    from pathlib import Path
    src_dir = str(Path(__file__).parent / "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
        
    import asyncio
    from unittest.mock import AsyncMock, MagicMock, patch
    from dev_agent.agents.email_agent import EmailAgent, EmailIntent
    
    mock_emails = [
        {"id": "1", "from": "GitHub <noreply@github.com>", "subject": "Alert", "snippet": "Auto alert"},
        {"id": "2", "from": "Render <no-reply@render.com>", "subject": "Build failed", "snippet": "System"},
        {"id": "3", "from": "John Doe <john.doe@example.com>", "subject": "Hello Friend", "snippet": "How are you?"},
        {"id": "4", "from": "Uber <noreply@uber.com>", "subject": "Receipt", "snippet": "Receipt"},
        {"id": "5", "from": "Jane Doe <jane.doe@example.com>", "subject": "Meeting", "snippet": "Let's meet"},
    ]
    
    settings_mock = MagicMock()
    settings_mock.groq_api_key = "fake_key"
    settings_mock.groq_model = "fake_model"
    
    async def run_tests():
        with patch("dev_agent.agents.email_agent.get_settings", return_value=settings_mock), \
             patch("dev_agent.agents.email_agent.AsyncGroq") as mock_groq_class, \
             patch("dev_agent.agents.email_agent.GmailReader") as mock_reader_class, \
             patch("dev_agent.agents.email_agent.GmailSender") as mock_sender_class:
            
            mock_reader = mock_reader_class.return_value
            mock_reader.get_recent_emails = AsyncMock(return_value=mock_emails)
            
            mock_sender = mock_sender_class.return_value
            mock_sender.send_email = AsyncMock(return_value={"status": "sent"})
            
            mock_groq = mock_groq_class.return_value
            mock_completion = AsyncMock()
            mock_completion.choices = [
                MagicMock(message=MagicMock(content="Mocked regenerated body response"))
            ]
            mock_groq.chat.completions.create = AsyncMock(return_value=mock_completion)
            
            agent = EmailAgent(token="fake_token")
            
            # TEST 1: Recipient is missing, but query is confirmation query and history is provided, should inherit recipient from previous turn
            mock_json_content = '{"recipient": "john.doe@example.com", "subject": "Hi", "body": "This is the message body."}'
            mock_completion1 = MagicMock()
            mock_completion1.choices = [MagicMock(message=MagicMock(content=mock_json_content))]
            mock_groq.chat.completions.create.return_value = mock_completion1

            intent1 = EmailIntent(
                intent="send",
                recipient=None,
                subject="Hi",
                body="This is the message body.",
                reasoning="Send simple mail"
            )
            fake_history = [
                {"role": "user", "content": "envie o email sobre a receita"},
                {"role": "assistant", "content": "Ok, gerando rascunho..."}
            ]
            res1 = await agent._handle_send(intent1, query="envie o email", history=fake_history)
            assert res1.success is True, f"Failed test 1: {res1.error}"
            assert res1.data["recipient"] == "john.doe@example.com", f"Expected john.doe@example.com, got {res1.data['recipient']}"
            assert res1.data["subject"] == "Hi"

            # TEST 1b: Recipient cannot be resolved with certainty (no history, no name match), should abort with strict message
            intent1b = EmailIntent(
                intent="send",
                recipient=None,
                subject="Hi",
                body="This is the message body.",
                reasoning="Send simple mail"
            )
            res1b = await agent._handle_send(intent1b, query="envie o email")
            assert res1b.success is False
            assert res1b.error == "Não consegui resgatar o e-mail do destinatário no histórico. Por favor, me informe o endereço correto para o envio."
            
            # TEST 2: Subject is "Sem assunto", should prefix original subject "Hello Friend" with "Re: "
            intent2 = EmailIntent(
                intent="send",
                recipient=None,
                subject="Sem assunto",
                body="This is the message body.",
                reasoning="Send simple mail"
            )
            res2 = await agent._handle_send(intent2, query="Envie para o John Doe")
            assert res2.success is True, f"Failed test 2: {res2.error}"
            assert res2.data["recipient"] == "john.doe@example.com"
            assert res2.data["subject"] == "Re: Hello Friend", f"Expected 'Re: Hello Friend', got '{res2.data['subject']}'"
            
            # TEST 3: Body is missing, should regenerate using LLM
            intent3 = EmailIntent(
                intent="send",
                recipient="john.doe@example.com",
                subject="Hello Friend",
                body="",
                reasoning="Send suggest"
            )
            mock_completion_body = MagicMock()
            mock_completion_body.choices = [
                MagicMock(message=MagicMock(content="Mocked regenerated body response"))
            ]
            mock_groq.chat.completions.create.return_value = mock_completion_body

            res3 = await agent._handle_send(intent3, query="envie esta sugestão para o John Doe")
            assert res3.success is True, f"Failed test 3: {res3.error}"
            assert "Mocked regenerated body" in res3.data["body_preview"], f"Body preview doesn't contain regenerated text: {res3.data['body_preview']}"
            
            # TEST 4: EmailIntent Pydantic validation checks
            from pydantic import ValidationError
            
            # A valid email recipient should pass validation
            intent_ok = EmailIntent(
                intent="send",
                recipient="eduardo@example.com",
                subject="Hi",
                body="Body",
                reasoning="OK"
            )
            assert intent_ok.recipient == "eduardo@example.com"
 
            # An empty/null recipient should pass validation (fallback to infer/real user)
            intent_null = EmailIntent(
                intent="send",
                recipient=None,
                subject="Hi",
                body="Body",
                reasoning="OK"
            )
            assert intent_null.recipient is None
 
            # A name string recipient (non-email) should raise validation error
            try:
                EmailIntent(
                    intent="send",
                    recipient="Eduardo Carvalho",
                    subject="Hi",
                    body="Body",
                    reasoning="Should Fail"
                )
                assert False, "Expected ValidationError for non-email recipient 'Eduardo Carvalho', but it passed."
            except (ValueError, ValidationError) as val_err:
                # Success: validation error raised as expected
                pass
            
            # TEST 5: Extract email address by name query matching and filtering out system/bot domains
            mock_emails_ext = [
                {"id": "1", "from": "Eduardo Carvalho <no-reply@render.com>", "subject": "Delivery Status Notification (Failure)", "snippet": "Failed to deliver"},
                {"id": "2", "from": "System Daemon <mailer-daemon@gmail.com>", "subject": "Failure Notice", "snippet": "Undeliverable"},
                {"id": "3", "from": "Eduardo Carvalho <eduardo.carvalho@gmail.com>", "subject": "Re: Proposta", "snippet": "Aqui está a proposta"},
                {"id": "4", "from": "John Doe <john.doe@example.com>", "subject": "Hello Friend", "snippet": "How are you?"},
            ]
            mock_reader.get_recent_emails.return_value = mock_emails_ext
            
            intent5 = EmailIntent(
                intent="send",
                recipient=None,
                subject="Hello",
                body="Body context",
                reasoning="Send to Eduardo"
            )
            
            res5 = await agent._handle_send(intent5, query="Envie um email para o Eduardo Carvalho")
            assert res5.success is True, f"Failed test 5: {res5.error}"
            assert res5.data["recipient"] == "eduardo.carvalho@gmail.com", f"Expected eduardo.carvalho@gmail.com, got {res5.data['recipient']}"

            # TEST 6: Spam and non-human domain validation checks
            assert agent._is_valid_human_email("temu@eu.temuemail") is False
            assert agent._is_valid_human_email("test@teste.com") is False
            assert agent._is_valid_human_email("promo@spamdomain.com") is False
            assert agent._is_valid_human_email("hello@company.com") is True
            
            # Restore default mock emails
            mock_reader.get_recent_emails.return_value = mock_emails
            
            print("[OK] Todos os testes logicos do EmailAgent passaram!")
            return True

    try:
        return asyncio.run(run_tests())
    except Exception as e:
        print(f"[ERRO] Falha ao correr testes logicos: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_chat_memory_logic():
    """Valida a persistencia do historico de conversa e injecao de memoria com mocks."""
    print("\n" + "=" * 80)
    print("[TESTE] Validacao de logica de Chat Memory - Orchestrator & Repo")
    print("=" * 80)

    import sys
    from pathlib import Path
    src_dir = str(Path(__file__).parent / "src")
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

    import asyncio
    from unittest.mock import AsyncMock, MagicMock, patch
    import dev_agent.database.repositories.users
    import dev_agent.database.repositories.user_preferences
    from dev_agent.database.models.chat_message import ChatMessage
    from dev_agent.database.repositories.chat_messages import ChatMessagesRepository
    from dev_agent.orchestrator.orchestrator import Orchestrator
    from dev_agent.core.models import TaskRequest

    # Test 1: Pydantic model ChatMessage
    msg = ChatMessage(user_id="user123", role="user", content="Ola, recordas-te de mim?")
    assert msg.user_id == "user123"
    assert msg.role == "user"
    assert msg.content == "Ola, recordas-te de mim?"
    assert msg.agent_used is None
    print("[OK] Modelo ChatMessage instanciado com sucesso")

    # Test 2: ChatMessagesRepository
    mock_db = MagicMock()
    mock_collection = MagicMock()
    mock_db.chat_messages = mock_collection
    
    # Mock insert_one
    mock_insert_result = MagicMock()
    mock_insert_result.inserted_id = "msg_id_123"
    mock_collection.insert_one = AsyncMock(return_value=mock_insert_result)

    # Mock find().sort().limit()
    mock_cursor = MagicMock()
    mock_cursor.to_list = AsyncMock(return_value=[
        {"_id": "msg_id_123", "user_id": "user123", "role": "user", "content": "Ola, recordas-te de mim?", "timestamp": "2026-05-20T10:00:00"}
    ])
    mock_collection.find.return_value.sort.return_value.limit.return_value = mock_cursor

    async def run_tests():
        repo = ChatMessagesRepository(mock_db)
        
        # Test save_message
        saved = await repo.save_message(user_id="user123", role="user", content="Ola, recordas-te de mim?")
        assert saved.id == "msg_id_123"
        assert saved.user_id == "user123"
        assert mock_collection.insert_one.called
        print("[OK] Repositorio save_message funcional")

        # Test get_history
        history = await repo.get_history(user_id="user123", limit=10)
        assert len(history) == 1
        assert history[0]["content"] == "Ola, recordas-te de mim?"
        assert mock_collection.find.called
        print("[OK] Repositorio get_history funcional")

        # Test 3: Orchestrator Injecting History
        settings_mock = MagicMock()
        settings_mock.groq_api_key = "fake_key"
        settings_mock.groq_model = "fake_model"

        with patch("dev_agent.orchestrator.orchestrator.get_settings", return_value=settings_mock), \
             patch("dev_agent.orchestrator.orchestrator.AsyncGroq") as mock_groq_class, \
             patch("dev_agent.orchestrator.orchestrator.Planner") as mock_planner_class:
            
            mock_groq = mock_groq_class.return_value
            mock_completion = AsyncMock()
            mock_completion.choices = [
                MagicMock(message=MagicMock(content="Claro que sim! Chamas-te Joao."))
            ]
            mock_groq.chat.completions.create = AsyncMock(return_value=mock_completion)

            orchestrator = Orchestrator()
            orchestrator.planner.decide_agents = AsyncMock(return_value=[])
            
            # Setup task and fake user context
            task = TaskRequest(
                query="Como me chamo?",
                user_id="user123"
            )
            user_data = {"user_id": "user123"}
            
            # Mock historical context
            fake_history = [
                {"role": "user", "content": "Chamo-me Joao."},
                {"role": "assistant", "content": "Sim, ola! Qual e o teu nome?"},
                {"role": "user", "content": "Ola, recordas-te de mim?"}
            ]
            
            # Mock Dispatcher running and returning empty results (since it's a general intent)
            with patch("dev_agent.orchestrator.orchestrator.Dispatcher") as mock_dispatcher_class, \
                 patch("dev_agent.preferences.hooks.get_database", return_value=mock_db), \
                 patch("dev_agent.database.repositories.users.UsersRepository") as mock_users_repo_class, \
                 patch("dev_agent.preferences.hooks.UserPreferencesRepository") as mock_prefs_repo_class, \
                 patch("dev_agent.preferences.hooks.build_agent_system_preamble", return_value="fake_preamble"), \
                 patch("dev_agent.preferences.hooks.with_system_preamble", side_effect=lambda msgs: [{"role": "system", "content": "fake_preamble"}] + msgs):
                
                mock_dispatcher = mock_dispatcher_class.return_value
                mock_dispatcher.run = AsyncMock(return_value=[])
                
                result = await orchestrator.handle(task, user_data, history=fake_history)
                assert result.summary == "Claro que sim! Chamas-te Joao."
                
                # Verify calls made to AsyncGroq create
                create_mock = mock_groq.chat.completions.create
                assert create_mock.called
                
                # Check messages argument structure in LLM call
                called_kwargs = create_mock.call_args[1]
                called_messages = called_kwargs["messages"]
                
                # We expect the messages to be:
                # 1. oldest: "Ola, recordas-te de mim?"
                # 2. "Sim, ola! Qual e o teu nome?"
                # 3. "Chamo-me Joao."
                # 4. Current user prompt
                assert len(called_messages) == 4
                assert called_messages[0]["role"] == "user"
                assert called_messages[0]["content"] == "Ola, recordas-te de mim?"
                assert called_messages[1]["role"] == "assistant"
                assert called_messages[1]["content"] == "Sim, ola! Qual e o teu nome?"
                assert called_messages[2]["role"] == "user"
                assert called_messages[2]["content"] == "Chamo-me Joao."
                assert "Como me chamo?" in called_messages[3]["content"]
                
                print("[OK] Orquestrador injetou historico estruturalmente nas chamadas do LLM!")

                # Test 4: Verificar se o Orchestrator funciona com os Hooks de preferência instalados
                from dev_agent.preferences.hooks import install_orchestrator_hooks
                
                mock_user = MagicMock()
                mock_user.email = "joao@example.com"
                
                mock_users_repo = mock_users_repo_class.return_value
                mock_users_repo.find_by_id = AsyncMock(return_value=mock_user)
                
                mock_prefs_repo = mock_prefs_repo_class.return_value
                mock_prefs_repo.get_or_create = AsyncMock(return_value=MagicMock())
                
                install_orchestrator_hooks()
                
                create_mock.reset_mock()
                
                result_hook = await orchestrator.handle(task, user_data, history=fake_history)
                assert result_hook.summary == "Claro que sim! Chamas-te Joao."
                assert create_mock.called
                
                called_kwargs_hook = create_mock.call_args[1]
                called_messages_hook = called_kwargs_hook["messages"]
                
                assert len(called_messages_hook) == 5
                assert called_messages_hook[0]["role"] == "system"
                assert called_messages_hook[0]["content"] == "fake_preamble"
                assert called_messages_hook[1]["role"] == "user"
                assert called_messages_hook[1]["content"] == "Ola, recordas-te de mim?"
                assert called_messages_hook[2]["role"] == "assistant"
                assert called_messages_hook[2]["content"] == "Sim, ola! Qual e o teu nome?"
                assert called_messages_hook[3]["role"] == "user"
                assert called_messages_hook[3]["content"] == "Chamo-me Joao."
                assert "Como me chamo?" in called_messages_hook[4]["content"]
                
                print("[OK] Hooks instalados com sucesso, a repassar historico de mensagens e preamble!")

                # Test 5: Verificar se o Orchestrator funciona com as Extension Patches instaladas
                from dev_agent.extensions.install import install_agent_extensions
                
                install_agent_extensions()
                
                create_mock.reset_mock()
                
                result_ext = await orchestrator.handle(task, user_data, history=fake_history)
                assert result_ext.summary == "Claro que sim! Chamas-te Joao."
                assert create_mock.called
                
                called_kwargs_ext = create_mock.call_args[1]
                called_messages_ext = called_kwargs_ext["messages"]
                
                assert len(called_messages_ext) == 5
                assert called_messages_ext[0]["role"] == "system"
                assert called_messages_ext[0]["content"] == "fake_preamble"
                assert called_messages_ext[1]["role"] == "user"
                assert called_messages_ext[1]["content"] == "Ola, recordas-te de mim?"
                assert called_messages_ext[2]["role"] == "assistant"
                assert called_messages_ext[2]["content"] == "Sim, ola! Qual e o teu nome?"
                assert called_messages_ext[3]["role"] == "user"
                assert called_messages_ext[3]["content"] == "Chamo-me Joao."
                assert "Como me chamo?" in called_messages_ext[4]["content"]
                
                print("[OK] Extension patches instaladas com sucesso, a repassar historico pela cadeia de wrappers!")
                return True

    try:
        return asyncio.run(run_tests())
    except Exception as e:
        print(f"[ERRO] Falha ao correr testes logicos de memory: {e}")
        import traceback
        traceback.print_exc()
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
        ("Lógica EmailAgent", test_email_agent_logic),
        ("Lógica ChatMemory", test_chat_memory_logic),
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
