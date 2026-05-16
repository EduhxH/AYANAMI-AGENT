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

    async def _send_verification_email(self, email: str, code: str) -> None:
        """Envia o email com o código de verificação via Resend."""
        resend.api_key = self.settings.resend_api_key
        
        resend.Emails.send({
            "from": self.settings.from_email,
            "to": email,
            "subject": "Dev Agent — Check your email",
            "html": f"""
                <div style="font-family: monospace; max-width: 400px; margin: 40px auto;">
                    <h2>Bem-vindo ao Dev Agent</h2>
                    <p>O teu código de verificação é:</p>
                    <div style="font-size: 36px; font-weight: bold; letter-spacing: 8px; 
                                background: #f0f0f0; padding: 20px; text-align: center;">
                        {code}
                    </div>
                    <p style="color: #666; font-size: 12px;">
                        Este código expira em 15 minutos.
                    </p>
                </div>
            """,
        })