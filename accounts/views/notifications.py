from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from core.exceptions.responses import success_response
from core.docs.schemas import (
    get_success_response_serializer,
    ERROR_401_UNAUTHORIZED,
    ERROR_403_FORBIDDEN,
    ERROR_404_NOT_FOUND,
)
from ..models import Notification


# ─── Inline serializers for schema generation ────────────────────────────────

class NotificationItemSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="ID da notificação.")
    type = serializers.ChoiceField(
        choices=["LINK_REQUEST", "LINK_ACCEPTED"],
        help_text="Tipo da notificação.",
    )
    message = serializers.CharField(help_text="Mensagem legível para o usuário.")
    is_read = serializers.BooleanField(help_text="Se a notificação já foi lida.")
    created_at = serializers.DateTimeField(help_text="Data de criação (ISO 8601).")
    actor_name = serializers.CharField(help_text="Nome de quem gerou a notificação.")
    link_type = serializers.CharField(
        allow_null=True,
        help_text="Tipo de vínculo relacionado (caregiver, guardian, professional, institution).",
    )
    link_id = serializers.IntegerField(
        allow_null=True,
        help_text="ID do vínculo relacionado.",
    )


class NotificationListDataSerializer(serializers.Serializer):
    notifications = NotificationItemSerializer(many=True)
    unread_count = serializers.IntegerField(help_text="Total de notificações não lidas.")


class MarkReadDataSerializer(serializers.Serializer):
    id = serializers.IntegerField(help_text="ID da notificação marcada como lida.")


class MarkAllReadDataSerializer(serializers.Serializer):
    marked = serializers.BooleanField(help_text="Sempre true quando bem-sucedido.")


# ─── Views ────────────────────────────────────────────────────────────────────

class NotificationListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Notificações"],
        summary="Listar notificações do usuário",
        description=(
            "Retorna as últimas 50 notificações do usuário autenticado, "
            "ordenadas da mais recente para a mais antiga, "
            "junto com o total de não lidas.\n\n"
            "**Tipos de notificação:**\n"
            "- `LINK_REQUEST` — outro usuário solicitou vínculo com o idoso\n"
            "- `LINK_ACCEPTED` — o idoso aceitou seu pedido de vínculo"
        ),
        responses={
            200: get_success_response_serializer(NotificationListDataSerializer),
            401: ERROR_401_UNAUTHORIZED,
        },
        examples=[
            OpenApiExample(
                "Resposta com notificações",
                value={
                    "success": True,
                    "data": {
                        "notifications": [
                            {
                                "id": 12,
                                "type": "LINK_REQUEST",
                                "message": "João Silva solicitou vínculo como Cuidador.",
                                "is_read": False,
                                "created_at": "2026-04-20T14:30:00Z",
                                "actor_name": "João Silva",
                                "link_type": "caregiver",
                                "link_id": 7,
                            },
                            {
                                "id": 11,
                                "type": "LINK_ACCEPTED",
                                "message": "Seu pedido de vínculo foi aceito.",
                                "is_read": True,
                                "created_at": "2026-04-18T09:00:00Z",
                                "actor_name": "Dona Maria",
                                "link_type": "guardian",
                                "link_id": 3,
                            },
                        ],
                        "unread_count": 1,
                    },
                },
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def get(self, request):
        notifications = Notification.objects.filter(recipient=request.user).order_by("-created_at")[:50]
        unread_count = Notification.objects.filter(recipient=request.user, is_read=False).count()

        data = [
            {
                "id": n.id,
                "type": n.type,
                "message": n.message,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat(),
                "actor_name": n.actor_name,
                "link_type": n.link_type,
                "link_id": n.link_id,
            }
            for n in notifications
        ]
        return success_response(data={"notifications": data, "unread_count": unread_count})


class MarkNotificationReadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Notificações"],
        summary="Marcar notificação como lida",
        description=(
            "Marca uma notificação específica como lida. "
            "Só o destinatário da notificação pode marcá-la."
        ),
        parameters=[
            OpenApiParameter(
                name="pk",
                location=OpenApiParameter.PATH,
                type=OpenApiTypes.INT,
                description="ID da notificação a ser marcada como lida.",
                required=True,
            ),
        ],
        request=None,
        responses={
            200: get_success_response_serializer(MarkReadDataSerializer),
            401: ERROR_401_UNAUTHORIZED,
            404: ERROR_404_NOT_FOUND,
        },
        examples=[
            OpenApiExample(
                "Notificação marcada como lida",
                value={"success": True, "data": {"id": 12}},
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def post(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.is_read = True
        notification.save(update_fields=["is_read"])
        return success_response(data={"id": pk})


class MarkAllNotificationsReadView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Notificações"],
        summary="Marcar todas as notificações como lidas",
        description=(
            "Marca todas as notificações não lidas do usuário autenticado como lidas. "
            "Não requer corpo na requisição."
        ),
        request=None,
        responses={
            200: get_success_response_serializer(MarkAllReadDataSerializer),
            401: ERROR_401_UNAUTHORIZED,
        },
        examples=[
            OpenApiExample(
                "Todas marcadas como lidas",
                value={"success": True, "data": {"marked": True}},
                response_only=True,
                status_codes=["200"],
            ),
        ],
    )
    def post(self, request):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        return success_response(data={"marked": True})
