from passlib.context import CryptContext
import resend

from dev_agent.core.config import get_settings
from dev_agent.database.repositories.users import UsersRepository
from dev_agent.auth.jwt import create_access_token

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    if len(password.encode('utf-8')) > 72:
        password = password[:72]
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    if len(plain.encode('utf-8')) > 72:
        plain = plain[:72]
    return pwd_context.verify(plain, hashed)


class AuthService:
    def __init__(self, users_repo: UsersRepository):
        self.users = users_repo
        self.settings = get_settings()

    async def register(self, email: str, password: str) -> dict:
        """
        Regista um utilizador novo.
        Devolve erro se o email já existe.
        Envia email de verificação com código.
        """
        existing = await self.users.find_by_email(email)
        if existing:
            raise ValueError("Email já registado")

        hashed = hash_password(password)
        user = await self.users.create(email, hashed)

        # Corrigido: Agora está dentro da função e chama com o "_" inicial
        await self._send_verification_email(email, user.verification_code)

        return {"message": "Registo bem-sucedido. Verifica o teu email."}

    async def verify_email(self, email: str, code: str) -> dict:
        """Verifica o código de 6 dígitos e activa a conta."""
        success = await self.users.verify_email(email, code)
        if not success:
            raise ValueError("Código inválido ou expirado")
        return {"message": "Email verificado com sucesso"}

    async def login(self, email: str, password: str) -> dict:
        """
        Faz login e devolve um JWT.
        Devolve erro se as credenciais são inválidas ou a conta não está verificada.
        """
        user = await self.users.find_by_email(email)
        
        if not user:
            raise ValueError("Credenciais inválidas")
        if not verify_password(password, user.hashed_password):
            raise ValueError("Credenciais inválidas")
        if not user.verified:
            raise ValueError("Conta não verificada. Verifica o teu email.")

        await self.users.update_last_login(user.id)

        token = create_access_token(user.id, user.email)
        return {"access_token": token, "token_type": "bearer"}

    # Corrigido: Agora o método pertence oficialmente à classe AuthService
    async def _send_verification_email(self, email: str, code: str) -> None:
        """Envia o email com o código de verificação via Resend."""
        resend.api_key = self.settings.resend_api_key
        
        try:
            resend.Emails.send({
                "from": self.settings.from_email,
                "to": email,
                "subject": "Ayanami Agent — Verification Code",
                "html": f"""
                    <div style="font-family: 'Courier New', Courier, monospace; max-width: 400px; margin: 40px auto; background: #0a0a0c; color: #e2e8f0; padding: 30px; border: 1px solid #2d3748; border-radius: 4px;">
                        <h2 style="color: #38bdf8; font-size: 20px; border-bottom: 1px solid #1e293b; padding-bottom: 10px; margin-top: 0;">[ AYANAMI AGENT ]</h2>
                        <p style="font-size: 14px; color: #94a3b8;">Protocolo de autenticação iniciado. O teu código de verificação é:</p>
                        <div style="font-size: 32px; font-weight: bold; letter-spacing: 6px; 
                                    background: #111827; color: #38bdf8; padding: 20px; text-align: center; border: 1px dashed #38bdf8; margin: 20px 0; border-radius: 4px;">
                            {code}
                        </div>
                        <p style="color: #64748b; font-size: 11px; margin-bottom: 0;">
                            > Este código expira em 15 minutos. Não partilhes esta chave.
                        </p>
                    </div>
                """,
            })
        except Exception as e:
            print(f"[AVISO DE TESTE]: Não foi possível enviar email para {email} devido às restrições do Resend. O utilizador foi registado sem verificação real, VOCE ESTA SUJEITA A TER A CONTA DELETADA. Erro original: {e}")