"""
Carga en Kiwi TCMS los datos del TP5: usuarios del equipo, categorias, plan de
pruebas y los 10 casos de prueba definidos en casos.json.

Se ejecuta dentro del contenedor (ver README.md de esta carpeta). Es idempotente:
si se corre dos veces, actualiza los casos en lugar de duplicarlos.
"""
import json

from django.contrib.auth.models import Group, User
from tcms.management.models import Priority, Product, Tag, Version
from tcms.testcases.models import Category, TestCase, TestCaseStatus
from tcms.testplans.models import PlanType, TestPlan

casos = json.load(open("/tmp/casos.json", encoding="utf-8"))

admin = User.objects.filter(is_superuser=True).order_by("id").first()
producto, _ = Product.objects.get_or_create(
    name="AgendaYA", defaults={"description": "Sistema de gestion de agenda y reservas - TP5"}
)
version, _ = Version.objects.get_or_create(value="1.0", product=producto)

administrador = Group.objects.get(name="Administrator")
tester = Group.objects.get(name="Tester")
EQUIPO = [
    ("santino", "Santino", "Barchiesi", administrador),
    ("maximo", "Maximo", "Estudillo", tester),
    ("joaquin", "Joaquin", "Garcia", tester),
    ("matias", "Matias", "Navarro", tester),
    ("fernando", "Fernando", "Martinez", tester),
]
for usuario, nombre, apellido, grupo in EQUIPO:
    u, creado = User.objects.get_or_create(
        username=usuario,
        defaults={"email": usuario + "@agendaya.com", "first_name": nombre, "last_name": apellido},
    )
    if creado:
        u.set_unusable_password()  # la contrasena se define desde el admin de Kiwi
        u.save()
    u.groups.set([grupo])

categorias = {
    "RFM1": Category.objects.get_or_create(name="Modulo 1 - Autenticacion", product=producto)[0],
    "RFM4": Category.objects.get_or_create(name="Modulo 4 - Reservas", product=producto)[0],
}

plan, _ = TestPlan.objects.get_or_create(
    name="TP5 - Casos de Prueba - Modulos 1 y 4",
    defaults={
        "author": admin,
        "product": producto,
        "product_version": version,
        "type": PlanType.objects.get(name="Function"),
    },
)
plan.text = (
    "Plan de pruebas del Trabajo Practico N5 - Grupo 4 - 4K10. Cubre los modulos 1 y 4 del sistema "
    "AgendaYA, con un caso positivo y uno negativo por cada requerimiento funcional analizado."
)
plan.save()

confirmado = TestCaseStatus.objects.get(name="CONFIRMED")
p1 = Priority.objects.get(value="P1")

for c in casos:
    lineas = [
        "**Objetivo:** " + c["objetivo"], "",
        "**Requerimientos asociados:** " + c["req"], "",
        "**Prerrequisitos:** " + " ".join(c["pre"]), "",
        "**Datos de prueba:** " + " / ".join(c["datos"]).replace(": / ", ": "), "",
        "**Tipo de prueba:** " + c["tipo"], "",
        "### Pasos", "",
        "| # | Accion del tester | Resultado esperado del sistema |",
        "|---|---|---|",
    ]
    for i, (accion, esperado) in enumerate(c["pasos"], 1):
        lineas.append("| %d | %s | %s |" % (i, accion.replace("|", "/"), esperado.replace("|", "/")))

    caso, _ = TestCase.objects.update_or_create(
        summary=c["id"] + " - " + c["titulo"].rstrip("."),
        defaults={
            "text": "\n".join(lineas),
            "requirement": c["req"],
            "notes": c["notas"],
            "author": admin,
            "case_status": confirmado,
            "priority": p1,
            "is_automated": False,
            "category": categorias["RFM1" if "RFM1" in c["id"] else "RFM4"],
        },
    )
    caso.add_tag(Tag.objects.get_or_create(name=c["tipo"].lower())[0])
    plan.add_case(caso)

print("Usuarios:", [(u.username, [g.name for g in u.groups.all()]) for u in User.objects.order_by("id")])
print("Casos en el plan:", plan.cases.count())
