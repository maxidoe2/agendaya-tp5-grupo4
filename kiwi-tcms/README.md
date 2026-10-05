# Kiwi TCMS — gestión de los casos de prueba

Kiwi TCMS es la herramienta de gestión de casos de prueba elegida por el equipo
(punto 5 del enunciado). Corre localmente con Docker.

## Levantar Kiwi

Requisito: Docker Desktop encendido.

```
cd kiwi-tcms
docker compose up -d
```

Se levantan dos contenedores: `kiwi_db` (MariaDB) y `kiwi_web` (Kiwi TCMS). La
primera vez tarda uno o dos minutos en preparar la base.

Entrar a **https://localhost:8443**. El certificado es autofirmado, así que el
navegador muestra una advertencia: *Configuración avanzada → Continuar a
localhost*.

Para apagarlo: `docker compose down`. Los datos quedan guardados en los volúmenes
de Docker; no usar `down -v`, porque los borra.

## Primera vez: crear el administrador

```
docker compose exec web /Kiwi/manage.py createsuperuser
```

Para cambiar la contraseña de un usuario existente:

```
docker compose exec web /Kiwi/manage.py changepassword admin
```

## Cargar los casos de prueba

`cargar_casos.py` crea el producto AgendaYA, el plan de pruebas, las categorías,
los usuarios del equipo con su rol y los 10 casos definidos en `casos.json`. Se
puede correr más de una vez: actualiza los casos sin duplicarlos.

```
docker compose cp casos.json web:/tmp/casos.json
docker compose cp cargar_casos.py web:/tmp/cargar_casos.py
docker compose exec -T web sh -c "/Kiwi/manage.py shell < /tmp/cargar_casos.py"
docker compose exec web /Kiwi/manage.py refresh_permissions
```

El último comando asigna a los grupos Administrator y Tester los permisos que
trae Kiwi por defecto.

Durante la carga aparecen errores `ConnectionRefusedError`: son los correos de
aviso que Kiwi intenta enviar al crear o modificar casos, y fallan porque no hay
un servidor de correo configurado. No afectan los datos cargados.

> Desde Git Bash en Windows, anteponer `MSYS_NO_PATHCONV=1` a los comandos
> `docker compose exec`, o la ruta `/Kiwi/manage.py` se reescribe y falla.

## Usuarios y roles

| Integrante | Usuario | Rol |
|---|---|---|
| Barchiesi Santino | santino | Administrator |
| Estudillo Máximo | maximo | Tester |
| García Joaquín | joaquin | Tester |
| Navarro Matías | matias | Tester |
| Martinez Fernando | fernando | Tester |

Los usuarios se crean sin contraseña. Para que un integrante pueda ingresar, el
administrador le define una desde *Administración → Usuarios*.
