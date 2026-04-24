"""
⚠️  SEEDER DE TESTE — NÃO USAR EM PRODUÇÃO ⚠️

Uso:
    python manage.py seed_test --settings=backend.settings.dev

O que faz:
  1. Remove todos os usuários não-superusuários (cascade apaga perfis, posts, vínculos)
  2. Cria 10 usuários de cada tipo: ELDER, CAREGIVER, GUARDIAN, PROFESSIONAL, INSTITUTION
  3. Cria posts variados no feed
  4. Cria vínculos entre cuidadores/responsáveis e idosos

Senha padrão de todos os usuários: Test@1234
"""

import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from accounts.models import (
    ElderProfile, CaregiverProfile, GuardianProfile,
    ProfessionalProfile, InstitutionProfile,
)
from links.models import CaregiverElderLink, GuardianElderLink
from posts.models.posts import Post

User = get_user_model()

PASSWORD = "Test@1234"

ELDERS = [
    ("Maria das Graças Silva",    "mariasilva",    "SP", "São Paulo"),
    ("José Roberto Oliveira",     "jroberto",      "RJ", "Rio de Janeiro"),
    ("Antônia Ferreira Lima",     "antoniafl",     "MG", "Belo Horizonte"),
    ("Francisco Souza Mendes",    "fsouza",        "BA", "Salvador"),
    ("Ana Lúcia Costa",           "analcosta",     "RS", "Porto Alegre"),
    ("Raimundo Pereira Neto",     "rpneto",        "CE", "Fortaleza"),
    ("Benedita Alves Rocha",      "balves",        "PE", "Recife"),
    ("Sebastião Gomes Carvalho",  "sgcarvalho",    "PR", "Curitiba"),
    ("Luzia Martins Campos",      "lmcampos",      "GO", "Goiânia"),
    ("Manoel Ribeiro Santana",    "mrsantana",     "AM", "Manaus"),
]

CAREGIVERS = [
    ("Camila Rodrigues Dias",     "camilard",    "SP", "São Paulo"),
    ("Lucas Ferreira Matos",      "lfmatos",     "RJ", "Rio de Janeiro"),
    ("Juliana Costa Pinto",       "jcpinto",     "MG", "Belo Horizonte"),
    ("Rafael Oliveira Cruz",      "rocruz",      "BA", "Salvador"),
    ("Fernanda Lima Barros",      "flbarros",    "RS", "Porto Alegre"),
    ("Pedro Alves Nunes",         "panunes",     "CE", "Fortaleza"),
    ("Aline Souza Monteiro",      "asmonteiro",  "PE", "Recife"),
    ("Tiago Mendes Araújo",       "tmaraujo",    "PR", "Curitiba"),
    ("Priscila Gomes Torres",     "pgtorres",    "GO", "Goiânia"),
    ("Bruno Ribeiro Cardoso",     "brcardoso",   "AM", "Manaus"),
]

GUARDIANS = [
    ("Isabela Santos Ramos",      "isramos",     "SP", "São Paulo"),
    ("Carlos Eduardo Vieira",     "cevieira",    "RJ", "Rio de Janeiro"),
    ("Mariana Pereira Lopes",     "mplopes",     "MG", "Belo Horizonte"),
    ("Daniel Almeida Figueiredo", "dafig",       "BA", "Salvador"),
    ("Tatiane Moreira Nascimento","tmnasc",       "RS", "Porto Alegre"),
    ("Felipe Carvalho Azevedo",   "fcazevedo",   "CE", "Fortaleza"),
    ("Larissa Gonçalves Freitas", "lgfreitas",   "PE", "Recife"),
    ("Rodrigo Teixeira Cunha",    "rtcunha",     "PR", "Curitiba"),
    ("Vanessa Borges Macedo",     "vbmacedo",    "GO", "Goiânia"),
    ("Marcos Antônio Pires",      "mapires",     "AM", "Manaus"),
]

PROFESSIONALS = [
    ("Dra. Helena Souza Braga",   "helenasb",    "SP", "São Paulo"),
    ("Dr. Ricardo Gomes Silva",   "ricardogs",   "RJ", "Rio de Janeiro"),
    ("Dra. Patrícia Nunes Lima",  "patriciaNL",  "MG", "Belo Horizonte"),
    ("Dr. Anderson Melo Costa",   "amcosta",     "BA", "Salvador"),
    ("Dra. Simone Faria Rocha",   "sfarocha",    "RS", "Porto Alegre"),
    ("Dr. Gustavo Alves Duarte",  "gaduarte",    "CE", "Fortaleza"),
    ("Dra. Renata Castro Brito",  "rcbrito",     "PE", "Recife"),
    ("Dr. Eduardo Ferraz Neto",   "efneto",      "PR", "Curitiba"),
    ("Dra. Claudia Pinto Vaz",    "cpvaz",       "GO", "Goiânia"),
    ("Dr. Alexandre Lima Dias",   "aldiasmed",   "AM", "Manaus"),
]

INSTITUTIONS = [
    ("Lar São Francisco",              "larsfranc",   "SP", "São Paulo"),
    ("Casa do Idoso Feliz",            "cidosofeliz", "RJ", "Rio de Janeiro"),
    ("ILPI Boa Vida",                  "boavida",     "MG", "Belo Horizonte"),
    ("Residência Sênior Bahia",        "rsbahia",     "BA", "Salvador"),
    ("Centro de Cuidados Gaúcho",      "ccgaucho",    "RS", "Porto Alegre"),
    ("Abrigo Esperança Ceará",         "abresperanca","CE", "Fortaleza"),
    ("Clínica Cuidar PE",              "ccuidarpe",   "PE", "Recife"),
    ("Lar da Saudade Paraná",          "larparana",   "PR", "Curitiba"),
    ("Instituto Vida Plena GO",        "ivpgo",       "GO", "Goiânia"),
    ("Centro de Atenção ao Idoso AM",  "caiam",       "AM", "Manaus"),
]

POSTS_CONTENT = [
    ("Dica importante para cuidadores: mantenha uma rotina estável para o idoso. Isso ajuda muito na qualidade do sono e na saúde mental. 💙", "CAREGIVER"),
    ("Bom dia a todos! Começando mais um dia de cuidado com amor e dedicação. Quem mais está na ativa hoje?", "CAREGIVER"),
    ("Alerta: quedas são a principal causa de hospitalização em idosos acima de 65 anos. Remova tapetes soltos e instale barras de apoio nos banheiros.", "PROFESSIONAL"),
    ("Hoje completamos 6 meses de acompanhamento com nossa idosa querida. Ver ela sorrir é a maior recompensa. 🥰", "CAREGIVER"),
    ("Dúvida: alguém tem experiência com idosos com Alzheimer leve? Preciso de dicas para o dia a dia.", "GUARDIAN"),
    ("Novidade na nossa ILPI: instalamos um jardim terapêutico. Os resultados na saúde emocional dos residentes têm sido incríveis!", "INSTITUTION"),
    ("A hidratação é essencial! Idosos sentem menos sede, por isso é fundamental oferecer água regularmente ao longo do dia.", "PROFESSIONAL"),
    ("Minha avó completou 84 anos essa semana! Obrigada a todos que fazem parte da rede de cuidados dela. 🎂", "GUARDIAN"),
    ("Lembrete: consultas preventivas regulares podem identificar problemas de saúde precocemente. Não negligencie os checkups!", "PROFESSIONAL"),
    ("Compartilhando uma conquista: nosso idoso deu os primeiros passos sem andador após 3 meses de fisioterapia! 🙌", "CAREGIVER"),
    ("A solidão é um dos maiores vilões da saúde do idoso. Visitas e conversas regulares fazem toda a diferença.", "GUARDIAN"),
    ("Encerramos o mês com 98% de satisfação dos familiares na nossa pesquisa interna. Muito orgulho da equipe!", "INSTITUTION"),
    ("Dica de alimentação: reduza o sal e aumente vegetais ricos em potássio para idosos com hipertensão.", "PROFESSIONAL"),
    ("Quem cuida também precisa de cuidado. Não se esqueçam de reservar um tempo para vocês, cuidadores!", "CAREGIVER"),
    ("Evento: amanhã teremos tarde cultural com música e dança para os nossos residentes. Família é bem-vinda!", "INSTITUTION"),
]


class Command(BaseCommand):
    help = "⚠️  Popula o banco com dados de TESTE. Apaga usuários não-superusuários antes."

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("\n[!] SEEDER DE TESTE iniciando...\n"))

        # ── 1. Limpar banco ───────────────────────────────────────────────────
        self.stdout.write("[1/4] Removendo usuarios nao-superusuarios...")
        deleted, _ = User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.SUCCESS(f"   -> {deleted} registros removidos (cascade).\n"))

        # ── 2. Criar usuários ─────────────────────────────────────────────────
        elders       = self._create_users(ELDERS,       "ELDER",       ElderProfile)
        caregivers   = self._create_users(CAREGIVERS,   "CAREGIVER",   CaregiverProfile, extra=self._caregiver_extra)
        guardians    = self._create_users(GUARDIANS,    "GUARDIAN",    GuardianProfile)
        professionals= self._create_users(PROFESSIONALS,"PROFESSIONAL",ProfessionalProfile, extra=self._professional_extra)
        institutions = self._create_users(INSTITUTIONS, "INSTITUTION", InstitutionProfile)

        # ── 3. Vínculos ───────────────────────────────────────────────────────
        self.stdout.write("[3/4] Criando vinculos...")
        self._create_links(elders, caregivers, guardians)

        # ── 4. Posts ──────────────────────────────────────────────────────────
        self.stdout.write("[4/4] Criando posts no feed...")
        self._create_posts(caregivers + guardians + professionals + institutions)

        self.stdout.write(self.style.SUCCESS(
            "\n[OK] Seeder concluido!"
            "\n     Usuarios criados: 50  (10 de cada tipo)"
            "\n     Senha padrao: Test@1234"
            "\n     Exemplo de login: camilard@amparo.test / Test@1234\n"
        ))

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _create_users(self, dataset, role, ProfileModel, extra=None):
        self.stdout.write(f"[2/4] Criando {len(dataset)} usuarios {role}...")
        users = []
        for full_name, username, state, city in dataset:
            email = f"{username}@amparo.test"
            user = User.objects.create_user(
                email=email,
                password=PASSWORD,
                full_name=full_name,
                role=role,
                is_verified=True,
                state=state,
                city=city,
            )
            profile_kwargs = {"user": user}
            if extra:
                profile_kwargs.update(extra(user))
            ProfileModel.objects.create(**profile_kwargs)
            users.append(user)
        self.stdout.write(self.style.SUCCESS(f"   ->{len(users)} criados.\n"))
        return users

    def _caregiver_extra(self, user):
        return {
            "bio": f"Cuidador(a) com experiência em acompanhamento de idosos. Baseado(a) em {user.city}.",
            "experience_years": random.randint(1, 15),
            "is_available": random.choice([True, True, False]),
        }

    def _professional_extra(self, user):
        return {}

    def _create_links(self, elders, caregivers, guardians):
        elder_profiles    = list(ElderProfile.objects.filter(user__in=elders))
        caregiver_profiles= list(CaregiverProfile.objects.filter(user__in=caregivers))
        guardian_profiles = list(GuardianProfile.objects.filter(user__in=guardians))

        link_statuses = ["ACTIVE", "ACTIVE", "ACTIVE", "PENDING", "ENDED"]

        # Each caregiver gets 1–2 elders
        for i, cp in enumerate(caregiver_profiles):
            for j in range(random.randint(1, 2)):
                ep = elder_profiles[(i + j) % len(elder_profiles)]
                if not CaregiverElderLink.objects.filter(caregiver=cp, elder=ep).exists():
                    CaregiverElderLink.objects.create(
                        caregiver=cp,
                        elder=ep,
                        status=random.choice(link_statuses),
                        agreed_hourly_rate=random.choice(["45.00", "55.00", "70.00", "80.00"]),
                        is_active=True,
                    )

        # Each guardian gets 1 elder
        for i, gp in enumerate(guardian_profiles):
            ep = elder_profiles[i % len(elder_profiles)]
            if not GuardianElderLink.objects.filter(guardian=gp, elder=ep).exists():
                GuardianElderLink.objects.create(
                    guardian=gp,
                    elder=ep,
                    status=random.choice(link_statuses),
                    relationship=random.choice(["CHILD", "SIBLING", "SPOUSE"]),
                    is_legal_guardian=random.choice([True, False]),
                    can_view_medical=True,
                    can_hire=True,
                )

        count = CaregiverElderLink.objects.count() + GuardianElderLink.objects.count()
        self.stdout.write(self.style.SUCCESS(f"   ->{count} vínculos criados.\n"))

    def _create_posts(self, authors):
        random.shuffle(authors)
        created = 0
        for i, (content, role) in enumerate(POSTS_CONTENT):
            # Pick an author whose role roughly matches
            matching = [u for u in authors if u.role == role]
            author = random.choice(matching) if matching else random.choice(authors)
            Post.objects.create(
                author=author,
                author_role=author.role,
                text=content,
                published_at=timezone.now() - timedelta(hours=random.randint(0, 72)),
            )
            created += 1
        self.stdout.write(self.style.SUCCESS(f"   ->{created} posts criados.\n"))
