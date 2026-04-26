from rest_framework import viewsets, mixins, status, serializers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from django.utils.translation import gettext_lazy as _
from django.db.models import Value, CharField
from django.core.exceptions import PermissionDenied

from core.exceptions.domain import ValidationError, ConflictError, NotFoundError
from links.services.link_services import (
    respond_to_caregiver_link,
    respond_to_guardian_link,
    respond_to_professional_link,
    respond_to_institution_link
)

from links.serializers.link_serializer import GenericLinkSerializer, LinkListSerializer
from links.models import (
    CaregiverElderLink,
    GuardianElderLink,
    ProfessionalElderLink,
    InstitutionElderLink,
)

class LinkRespondSerializer(serializers.Serializer):
    link_type = serializers.ChoiceField(choices=[
        ('caregiver', 'Caregiver'),
        ('guardian', 'Guardian'),
        ('professional', 'Professional'),
        ('institution', 'Institution'),
    ])
    link_id = serializers.IntegerField()
    action = serializers.ChoiceField(choices=[('approve', 'Approve'), ('reject', 'Reject')])

@extend_schema(tags=["Links"])
class LinkViewSet(viewsets.GenericViewSet):
    """
    ViewSet genérico para gerenciar vínculos (Links).
    Permite criar novos vínculos e listar ativos.
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return LinkListSerializer
        elif self.action == 'respond':
            return LinkRespondSerializer
        return GenericLinkSerializer

    def get_queryset(self):
        # Este ViewSet não é model-based tradicional, então queryset vazio por padrão
        # ou poderia retornar uma união, mas para 'create' não é estritamente necessário.
        return CaregiverElderLink.objects.none()

    @extend_schema(
        summary="Listar vínculos",
        description="Retorna uma lista de todos os vínculos associados ao usuário logado, independente do tipo.",
        responses={200: LinkListSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        user = request.user
        links = []
        
        # Helper para anotar o tipo de link
        def annotate_type(queryset, type_name, role_name):
            for link in queryset:
                link.link_type = type_name
                link.other_party_role = role_name
                links.append(link)

        # Se for Elder, busca todos os links onde ele é o elder
        if hasattr(user, 'elder_profile'):
            annotate_type(user.elder_profile.caregiver_links.all(), 'caregiver', 'Cuidador')
            annotate_type(user.elder_profile.guardian_links.all(), 'guardian', 'Responsável')
            annotate_type(user.elder_profile.professional_links.all(), 'professional', 'Profissional')
            annotate_type(user.elder_profile.institution_links.all(), 'institution', 'Instituição')

        # Se for Caregiver
        if hasattr(user, 'caregiver_profile'):
            annotate_type(user.caregiver_profile.elder_links.all(), 'caregiver', 'Idoso')

        # Se for Guardian
        if hasattr(user, 'guardian_profile'):
            annotate_type(user.guardian_profile.elder_links.all(), 'guardian', 'Idoso')

        # Se for Professional
        if hasattr(user, 'professional_profile'):
            annotate_type(user.professional_profile.elder_links.all(), 'professional', 'Idoso')

        # Se for Institution
        if hasattr(user, 'institution_profile'):
            annotate_type(user.institution_profile.elder_links.all(), 'institution', 'Idoso')

        # Ordenar por data de criação (mais recente primeiro)
        links.sort(key=lambda x: x.created_at, reverse=True)

        serializer = self.get_serializer(links, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Listar vínculos de uma pessoa",
        description="Retorna uma lista de vínculos ativos ou finalizados associados a uma pessoa específica (pelo ID do usuário).",
        responses={200: LinkListSerializer(many=True)}
    )
    def retrieve(self, request, pk=None, *args, **kwargs):
        from django.contrib.auth import get_user_model
        from django.shortcuts import get_object_or_404
        User = get_user_model()
        target_user = get_object_or_404(User, id=pk)

        links = []
        
        # Helper para anotar o tipo de link e filtrar
        def annotate_type_and_filter(queryset, type_name, role_name):
            filtered_qs = queryset.filter(status__in=['ACTIVE', 'ENDED'])
            for link in filtered_qs:
                link.link_type = type_name
                link.other_party_role = role_name
                links.append(link)

        # Se for Elder
        if hasattr(target_user, 'elder_profile'):
            annotate_type_and_filter(target_user.elder_profile.caregiver_links.all(), 'caregiver', 'Cuidador')
            annotate_type_and_filter(target_user.elder_profile.guardian_links.all(), 'guardian', 'Responsável')
            annotate_type_and_filter(target_user.elder_profile.professional_links.all(), 'professional', 'Profissional')
            annotate_type_and_filter(target_user.elder_profile.institution_links.all(), 'institution', 'Instituição')

        # Se for Caregiver
        if hasattr(target_user, 'caregiver_profile'):
            annotate_type_and_filter(target_user.caregiver_profile.elder_links.all(), 'caregiver', 'Idoso')

        # Se for Guardian
        if hasattr(target_user, 'guardian_profile'):
            annotate_type_and_filter(target_user.guardian_profile.elder_links.all(), 'guardian', 'Idoso')

        # Se for Professional
        if hasattr(target_user, 'professional_profile'):
            annotate_type_and_filter(target_user.professional_profile.elder_links.all(), 'professional', 'Idoso')

        # Se for Institution
        if hasattr(target_user, 'institution_profile'):
            annotate_type_and_filter(target_user.institution_profile.elder_links.all(), 'institution', 'Idoso')

        # Ordenar por data de criação (mais recente primeiro)
        links.sort(key=lambda x: x.created_at, reverse=True)

        # Usar o context={'request': request, 'target_user': target_user} para informar ao serializer
        serializer = self.get_serializer(links, many=True, context={'request': request, 'target_user': target_user})
        return Response(serializer.data)

    @extend_schema(
        summary="Criar novo vínculo",
        description="Cria um vínculo entre o usuário logado e um idoso. O tipo de vínculo é determinado pelo campo 'link_type'.",
        request=GenericLinkSerializer,
        responses={201: GenericLinkSerializer},
        examples=[
            OpenApiExample(
                'Caregiver Link',
                summary='Exemplo para Cuidador',
                description='Payload para um cuidador solicitar vínculo com um idoso.',
                value={
                    "link_type": "caregiver",
                    "elder": 1,
                    "agreed_hourly_rate": "50.00",
                    "notes": "Combinado valor inicial."
                }
            ),
            OpenApiExample(
                'Guardian Link',
                summary='Exemplo para Responsável',
                description='Payload para um responsável (familiar) solicitar vínculo.',
                value={
                    "link_type": "guardian",
                    "elder": 1,
                    "relationship": "CHILD",
                    "is_legal_guardian": True,
                    "can_view_medical": True,
                    "can_hire": True
                }
            ),
            OpenApiExample(
                'Professional Link',
                summary='Exemplo para Profissional',
                description='Payload para um profissional de saúde (fisioterapeuta, fono, etc).',
                value={
                    "link_type": "professional",
                    "elder": 1,
                    "service_mode": "HOME",
                    "goals": "Fisioterapia respiratória 3x semana",
                    "agreed_hourly_rate": "120.00"
                }
            ),
             OpenApiExample(
                'Institution Link',
                summary='Exemplo para Instituição',
                description='Payload para uma ILPI (Instituição de Longa Permanência).',
                value={
                    "link_type": "institution",
                    "elder": 1,
                    "admitted_at": "2024-01-01",
                    "room": "104",
                    "bed": "B"
                }
            ),
        ]
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        link = serializer.save()
        
        # Retorna os dados do link criado (pode precisar de um serializer de output mais detalhado ou usar o mesmo)
        # Para simplificar, retornamos uma mensagem de sucesso ou os dados básicos
        return Response({
            "status": "success",
            "message": _("Vínculo solicitado com sucesso."),
            "data": {
                "id": link.id,
                "status": link.status
            }
        }, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Responder a um vínculo",
        description="Permite aceitar ou rejeitar um vínculo. Requer `link_type`, `link_id` e `action` ('approve' ou 'reject').",
        request=LinkRespondSerializer,
        responses={200: GenericLinkSerializer}
    )
    @action(detail=False, methods=['post'], url_path='respond')
    def respond(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        link_type = data['link_type']
        link_id = data['link_id']
        action = data['action']
        
        try:
            if link_type == 'caregiver':
                link = respond_to_caregiver_link(link_id=link_id, user=request.user, action=action)
            elif link_type == 'guardian':
                link = respond_to_guardian_link(link_id=link_id, user=request.user, action=action)
            elif link_type == 'professional':
                link = respond_to_professional_link(link_id=link_id, user=request.user, action=action)
            elif link_type == 'institution':
                link = respond_to_institution_link(link_id=link_id, user=request.user, action=action)
            
            return Response({
                "status": "success",
                "message": _(f"Vínculo {action} com sucesso."),
                "data": {
                    "id": link.id,
                    "status": link.status
                }
            }, status=status.HTTP_200_OK)

        except (ValidationError, ConflictError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except NotFoundError as e:
             return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

    @extend_schema(
        summary="Encerrar um vínculo ativo",
        description="Encerra um vínculo ativo. Qualquer uma das partes envolvidas pode encerrar.",
    )
    @action(detail=False, methods=['post'], url_path='end')
    def end(self, request):
        link_type = request.data.get('link_type')
        link_id = request.data.get('link_id')

        MODEL_MAP = {
            'caregiver': CaregiverElderLink,
            'guardian': GuardianElderLink,
            'professional': ProfessionalElderLink,
            'institution': InstitutionElderLink,
        }

        model = MODEL_MAP.get(link_type)
        if not model:
            return Response({"error": _("Tipo de vínculo inválido.")}, status=status.HTTP_400_BAD_REQUEST)

        try:
            link = model.objects.get(id=link_id, status='ACTIVE')
        except model.DoesNotExist:
            return Response({"error": _("Vínculo ativo não encontrado.")}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        is_elder = hasattr(user, 'elder_profile') and link.elder.user == user
        is_other = (
            (link_type == 'caregiver' and hasattr(user, 'caregiver_profile') and link.caregiver.user == user) or
            (link_type == 'guardian' and hasattr(user, 'guardian_profile') and link.guardian.user == user) or
            (link_type == 'professional' and hasattr(user, 'professional_profile') and link.professional.user == user) or
            (link_type == 'institution' and hasattr(user, 'institution_profile') and link.institution.user == user)
        )

        if not (is_elder or is_other):
            return Response({"error": _("Sem permissão para encerrar este vínculo.")}, status=status.HTTP_403_FORBIDDEN)

        link.status = 'ENDED'
        link.is_active = False
        link.save(update_fields=['status', 'is_active'])

        return Response({"status": "success", "message": _("Vínculo encerrado.")}, status=status.HTTP_200_OK)
