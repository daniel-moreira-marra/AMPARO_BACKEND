from rest_framework import serializers
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema_field
from links.models import (
    CaregiverElderLink,
    GuardianElderLink,
    ProfessionalElderLink,
    InstitutionElderLink,
)
from accounts.models import (
    ElderProfile,
    CaregiverProfile,
    GuardianProfile,
    ProfessionalProfile,
    InstitutionProfile,
    Notification,
)


def _notify_link_request(elder_user, actor_name: str, link_type: str, link_id: int):
    Notification.objects.create(
        recipient=elder_user,
        type=Notification.LINK_REQUEST,
        message=f"{actor_name} solicitou um vínculo com você.",
        actor_name=actor_name,
        link_type=link_type,
        link_id=link_id,
    )

class GenericLinkSerializer(serializers.Serializer):
    """
    Serializer genérico para criar vínculos de qualquer tipo.
    O tipo de vínculo é determinado pelo campo 'link_type'.
    """
    LINK_TYPES = (
        ('caregiver', _('Cuidador')),
        ('guardian', _('Responsável')),
        ('professional', _('Profissional')),
        ('institution', _('Instituição')),
    )

    link_type = serializers.ChoiceField(choices=LINK_TYPES)
    elder = serializers.PrimaryKeyRelatedField(queryset=ElderProfile.objects.all())
    
    # Campos específicos para cada tipo de vínculo (opcionais na validação geral)
    # Caregiver
    agreed_hourly_rate = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    
    # Guardian
    relationship = serializers.ChoiceField(choices=GuardianElderLink._meta.get_field('relationship').choices, required=False)
    is_legal_guardian = serializers.BooleanField(required=False)
    can_view_medical = serializers.BooleanField(required=False)
    can_hire = serializers.BooleanField(required=False)

    # Professional
    service_mode = serializers.ChoiceField(choices=ProfessionalElderLink._meta.get_field('service_mode').choices, required=False)
    goals = serializers.CharField(required=False)

    # Institution
    admitted_at = serializers.DateField(required=False)
    room = serializers.CharField(required=False)
    bed = serializers.CharField(required=False)

    # Campos comuns
    started_at = serializers.DateField(required=False)
    notes = serializers.CharField(required=False)

    def validate(self, attrs):
        link_type = attrs.get('link_type')
        user = self.context['request'].user

        # Validações específicas por tipo
        if link_type == 'caregiver':
            if not hasattr(user, 'caregiver_profile'):
                raise serializers.ValidationError(_("Usuário não é um cuidador."))
            # Adicionar outras validações específicas aqui
            
        elif link_type == 'guardian':
            if not hasattr(user, 'guardian_profile'):
                raise serializers.ValidationError(_("Usuário não é um responsável."))

        elif link_type == 'professional':
            if not hasattr(user, 'professional_profile'):
                raise serializers.ValidationError(_("Usuário não é um profissional."))

        elif link_type == 'institution':
            if not hasattr(user, 'institution_profile'):
                raise serializers.ValidationError(_("Usuário não é uma instituição."))

        return attrs

    def create(self, validated_data):
        link_type = validated_data.pop('link_type')
        user = self.context['request'].user
        elder = validated_data.get('elder')

        if link_type == 'caregiver':
            caregiver = user.caregiver_profile
            if CaregiverElderLink.objects.filter(caregiver=caregiver, elder=elder, is_active=True).exists():
                raise serializers.ValidationError({"elder": _("Já existe um vínculo ativo com este idoso.")})
            link = CaregiverElderLink.objects.create(
                caregiver=caregiver,
                elder=elder,
                status=CaregiverElderLink.Status.PENDING,
                started_at=validated_data.get('started_at'),
                agreed_hourly_rate=validated_data.get('agreed_hourly_rate'),
                notes=validated_data.get('notes', ''),
            )
            _notify_link_request(elder.user, caregiver.user.full_name, 'caregiver', link.id)
            return link

        elif link_type == 'guardian':
            guardian = user.guardian_profile
            if GuardianElderLink.objects.filter(guardian=guardian, elder=elder, is_active=True).exists():
                raise serializers.ValidationError({"elder": _("Já existe um vínculo ativo com este idoso.")})
            link = GuardianElderLink.objects.create(
                guardian=guardian,
                elder=elder,
                status=GuardianElderLink.Status.PENDING,
                relationship=validated_data.get('relationship') or 'OTHER',
                is_legal_guardian=validated_data.get('is_legal_guardian', False),
                can_view_medical=validated_data.get('can_view_medical', True),
                can_hire=validated_data.get('can_hire', True),
            )
            _notify_link_request(elder.user, guardian.user.full_name, 'guardian', link.id)
            return link

        elif link_type == 'professional':
            professional = user.professional_profile
            if ProfessionalElderLink.objects.filter(professional=professional, elder=elder, is_active=True).exists():
                raise serializers.ValidationError({"elder": _("Já existe um vínculo ativo com este idoso.")})
            link = ProfessionalElderLink.objects.create(
                professional=professional,
                elder=elder,
                status=ProfessionalElderLink.Status.PENDING,
                started_at=validated_data.get('started_at'),
                agreed_hourly_rate=validated_data.get('agreed_hourly_rate'),
                service_mode=validated_data.get('service_mode') or '',
                goals=validated_data.get('goals', ''),
                notes=validated_data.get('notes', ''),
            )
            _notify_link_request(elder.user, professional.user.full_name, 'professional', link.id)
            return link

        elif link_type == 'institution':
            institution = user.institution_profile
            if InstitutionElderLink.objects.filter(institution=institution, elder=elder, is_active=True).exists():
                raise serializers.ValidationError({"elder": _("Já existe um vínculo ativo com este idoso.")})
            link = InstitutionElderLink.objects.create(
                institution=institution,
                elder=elder,
                status=InstitutionElderLink.Status.PENDING,
                admitted_at=validated_data.get('admitted_at'),
                room=validated_data.get('room', ''),
                bed=validated_data.get('bed', ''),
                notes=validated_data.get('notes', ''),
            )
            _notify_link_request(elder.user, institution.user.full_name, 'institution', link.id)
            return link

        raise serializers.ValidationError(_("Tipo de vínculo inválido."))

class LinkListSerializer(serializers.Serializer):
    """
    Serializer para listar vínculos com informações resumidas e normalizadas.
    """
    id = serializers.IntegerField()
    status = serializers.CharField()
    link_type = serializers.CharField()
    created_at = serializers.DateTimeField()
    notes = serializers.CharField(default='')

    # IDs das contas envolvidas
    elder_id = serializers.IntegerField()
    other_party_id = serializers.SerializerMethodField()

    # Informações da contraparte (quem não é o usuário logado)
    other_party_name = serializers.SerializerMethodField()
    other_party_role = serializers.CharField()
    other_party_bio = serializers.SerializerMethodField()
    other_party_extra = serializers.SerializerMethodField()

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_other_party_name(self, obj):
        user = self.context.get('target_user', self.context.get('request').user)
        
        # Se o user é o Elder do link, o "other" é o profissional/cuidador
        if hasattr(obj, 'elder') and obj.elder.user == user:
            if isinstance(obj, CaregiverElderLink):
                return obj.caregiver.user.full_name
            elif isinstance(obj, GuardianElderLink):
                return obj.guardian.user.full_name
            elif isinstance(obj, ProfessionalElderLink):
                return obj.professional.user.full_name
            elif isinstance(obj, InstitutionElderLink):
                return obj.institution.user.full_name
        
        # Se não, o "other" é o Elder
        if hasattr(obj, 'elder'):
             return obj.elder.user.full_name
             
        return "N/A"

    @extend_schema_field(serializers.IntegerField(allow_null=True))
    def get_other_party_id(self, obj):
        user = self.context.get('target_user', self.context.get('request').user)

        # Se o user é o Elder do link, o "other" é o profissional/cuidador/etc
        if hasattr(obj, 'elder') and obj.elder.user == user:
            if isinstance(obj, CaregiverElderLink):
                return obj.caregiver.user.id
            elif isinstance(obj, GuardianElderLink):
                return obj.guardian.user.id
            elif isinstance(obj, ProfessionalElderLink):
                return obj.professional.user.id
            elif isinstance(obj, InstitutionElderLink):
                return obj.institution.user.id

        # Se não, o "other" é o Elder
        if hasattr(obj, 'elder'):
             return obj.elder.user.id

        return None

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_other_party_bio(self, obj):
        user = self.context.get('target_user', self.context.get('request').user)

        if hasattr(obj, 'elder') and obj.elder.user == user:
            if isinstance(obj, CaregiverElderLink):
                return obj.caregiver.bio or None
            elif isinstance(obj, GuardianElderLink):
                return None
            elif isinstance(obj, ProfessionalElderLink):
                return obj.professional.bio or None
            elif isinstance(obj, InstitutionElderLink):
                p = obj.institution
                return p.bio if hasattr(p, 'bio') else None

        if hasattr(obj, 'elder'):
            elder = obj.elder
            preferred = elder.preferred_name
            return f'Chamado(a) por "{preferred}"' if preferred else None

        return None

    @extend_schema_field(serializers.ListField(child=serializers.CharField(), allow_null=True))
    def get_other_party_extra(self, obj):
        user = self.context.get('target_user', self.context.get('request').user)

        if hasattr(obj, 'elder') and obj.elder.user == user:
            if isinstance(obj, CaregiverElderLink):
                c = obj.caregiver
                tags = []
                if c.experience_years:
                    years = c.experience_years
                    tags.append(f"{years} {'ano' if years == 1 else 'anos'} de experiência")
                location = ', '.join(filter(None, [c.city, c.state]))
                if location:
                    tags.append(location)
                return tags or None

            elif isinstance(obj, GuardianElderLink):
                g = obj.guardian
                tags = []
                tags.append(g.get_relationship_display())
                if g.is_legal_guardian:
                    tags.append("Responsável legal")
                return tags or None

            elif isinstance(obj, ProfessionalElderLink):
                p = obj.professional
                tags = []
                if p.profession == 'OTHER':
                    tags.append(p.profession_other or 'Outro')
                else:
                    tags.append(p.get_profession_display())
                if p.council and p.license_number:
                    tags.append(f"{p.council}: {p.license_number}")
                location = ', '.join(filter(None, [p.city, p.state]))
                if location:
                    tags.append(location)
                return tags or None

            elif isinstance(obj, InstitutionElderLink):
                i = obj.institution
                tags = []
                tags.append(i.get_institution_type_display())
                if i.capacity:
                    tags.append(f"Cap. {i.capacity} residentes")
                return tags or None

        return None
