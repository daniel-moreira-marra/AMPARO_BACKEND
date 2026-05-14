import os
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from core.events import dispatch

User = get_user_model()

def user_registered_handler(user_id: int, **kwargs):
    email = kwargs.get('email')
    role = kwargs.get('role')
    print(f"Event: User {user_id} ({email}) registered as {role}.")
    
    # Gerando o token seguro
    user = User.objects.get(id=user_id)
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    # Montando a URL do Front-end
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3080")
    link = f"{frontend_url}/confirmar-email?uid={uid}&token={token}"
    
    # O Envio de fato
    send_mail(
        subject="Bem-vindo ao Amparo! Confirme seu e-mail",
        message=f"Olá!\n\nPor favor, clique no link abaixo para confirmar o seu cadastro:\n{link}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )

def password_reset_requested_handler(user_id: int, **kwargs):
    email = kwargs.get('email')
    print(f"Event: Password reset requested for User {user_id} ({email}).")
    
    user = User.objects.get(id=user_id)
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3080")
    link = f"{frontend_url}/reset-password?uid={uid}&token={token}"
    
    send_mail(
        subject="Amparo - Redefinição de Senha",
        message=f"Você solicitou a redefinição de senha.\n\nClique no link abaixo para criar uma nova senha:\n{link}",
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )

def user_profile_updated_handler(user_id: int, **kwargs):
    print(f"Event: User {user_id} profile updated.")

def user_password_changed_handler(user_id: int, **kwargs):
    print(f"Event: User {user_id} password changed.")