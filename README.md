# AgendaYa

Funcionalidad mínima del sistema AgendaYa, desarrollada para poder ejecutar los
casos de prueba diseñados en el **Trabajo Práctico N.º 5** de Ingeniería y
Calidad de Software (UTN FRM, 4K10 — Grupo 4).

No es el sistema completo: se implementó únicamente lo que cubren los diez casos
de prueba, tal como indica el punto 4 del enunciado.

## Requisitos

- Node.js 18 o superior (se desarrolló con Node 24)

## Puesta en marcha

```
npm install
npm start
```

Abrir `http://localhost:3000`.

Para volver al estado inicial entre corridas de prueba:

```
npm run reset
```

## Usuarios precargados

Corresponden a los prerrequisitos de los casos de prueba.

| Correo | Contraseña | Usado en |
|---|---|---|
| admin@agendaya.com | Contrasena123! | CP-001, CP-002 |
| hola.comova@agendaya.com | Recuperar2025! | CP-005 |

## Estructura

```
server.js              Endpoints HTTP y reglas de negocio
src/db.js              Persistencia en archivo JSON
src/correo.js          Envío de correo (registrado en consola y bitácora)
public/                Pantallas
  index.html           Ingreso
  registro.html        Crear cuenta
  recuperar.html       Recuperar contraseña
  restablecer.html     Fijar contraseña nueva
  reservar.html        Reserva de turno
  dashboard.html       Panel del administrador
scripts/reset-db.js    Reinicio del estado de prueba
data/                  Base de datos y bitácora de correos (se crean al arrancar)
```

## Requerimientos implementados

| Requerimiento | Descripción | Casos |
|---|---|---|
| AYA-M01-RF-01 | Registro de administrador | CP-003, CP-004 |
| AYA-M01-RF-02 | Recuperación de contraseña | CP-005, CP-006 |
| AYA-M01-RF-04 | Inicio de sesión | CP-001, CP-002 |
| AYA-M04-RF-03 | Confirmación de reserva | CP-007, CP-008 |
| AYA-M04-RF-05 | Prevención de reservas duplicadas | CP-009, CP-010 |

## Guía de ejecución de los casos de prueba

### Módulo 1 — Autenticación

**CP-001 — Inicio de sesión exitoso.** En `/`, ingresar `admin@agendaya.com` y
`Contrasena123!`. El sistema redirige al panel y muestra el usuario en la
cabecera.

**CP-002 — Contraseña incorrecta.** En `/`, ingresar `admin@agendaya.com` y
`ContrasenaInvalida123`. Aparece el mensaje *Contrasena incorrecta, intentelo de
nuevo* y el campo de contraseña queda vacío.

**CP-003 — Registro exitoso.** En `/registro.html`, cargar Leonel Messi,
`leo.messi@gmail.com` y `Messimessi12`. La cuenta se crea y se accede al panel.

**CP-004 — Correo ya registrado.** Repetir el paso anterior con el mismo correo.
No se crea la cuenta y el campo queda resaltado con el motivo.

**CP-005 — Recuperación con correo registrado.** En `/recuperar.html`, ingresar
`hola.comova@agendaya.com`. Aparece *Revisa tu correo de entrada*. El correo
enviado se verifica en la consola del servidor o en `data/correos.log`.

**CP-006 — Recuperación con correo inexistente.** Repetir con
`hola.comova12@agendaya.com`. No se envía ningún correo y se muestra *El correo
ingresado no se encuentra previamente registrado*.

### Módulo 4 — Reservas

**CP-007 — Reserva confirmada.** En `/reservar.html`, elegir un horario, cargar
nombre y correo, y confirmar. La reserva queda en estado Confirmada; en la
bitácora aparecen el correo al invitado y el aviso al administrador.

**CP-008 — Falta el correo.** Elegir un horario, cargar solo el nombre y
confirmar. El formulario no se envía y el campo de correo queda resaltado.

**CP-009 — Botón deshabilitado tras un click.** Completar el formulario y hacer
un click en Confirmar Reserva. El botón se deshabilita y pasa a *Procesando
reserva...*.

**CP-010 — Clicks múltiples.** Completar el formulario y hacer varios clicks
rápidos sobre Confirmar Reserva. Verificar en `/api/reservas` (o en el panel) que
se creó un único registro.

## Prevención de la doble reserva

El requerimiento AYA-M04-RF-05 se resolvió con dos barreras independientes:

1. **En el navegador.** Una bandera `enviando` se evalúa de forma sincrónica al
   comienzo del manejador del click. El atributo `disabled` por sí solo no
   alcanza: entre dos clicks muy rápidos el navegador puede despachar el segundo
   evento antes de que el DOM se repinte.

2. **En el servidor.** Antes de crear la reserva se verifica que no exista otra
   para el mismo invitado y horario. Si el control del navegador fallara, el
   backend responde 409 y no genera un segundo registro.

## Decisiones técnicas

**Persistencia en archivo JSON.** El enunciado pide implementar solo la
funcionalidad cubierta por los casos de prueba. Un archivo plano evita instalar
un motor de base de datos sin perder la posibilidad de verificar el estado. La
interfaz de `src/db.js` es la de un repositorio, de modo que reemplazarla por una
base real no obligaría a modificar `server.js`.

**Correo registrado en lugar de enviado.** Los casos CP-005 y CP-007 requieren
verificar que el envío se dispara. Escribir el correo en consola y en
`data/correos.log` permite comprobarlo de forma objetiva sin depender de una
casilla real ni de un servicio externo.

**Hash de contraseñas con `crypto.scrypt`.** Se usa el módulo nativo de Node en
lugar de una dependencia externa. Las contraseñas nunca se guardan en texto
plano.

## Nota sobre el CP-006

El caso especifica como resultado esperado el mensaje *El correo ingresado no se
encuentra previamente registrado*, y así fue implementado. La propia nota del
caso observa que, por seguridad, convendría un mensaje genérico que no revele si
un correo está registrado o no, ya que permite enumerar cuentas válidas. Queda
señalado como mejora para una próxima iteración.

## Limitaciones conocidas

Al tratarse de la funcionalidad mínima para ejecutar los casos de prueba, quedan
fuera de alcance aspectos que el sistema completo debería cubrir:

- `/api/reservas` y `/api/estado` no requieren sesión, por lo que los datos de los
  invitados quedan accesibles. El enunciado exige que no sean públicos.
- El inicio de sesión responde *El usuario no existe* ante un correo no
  registrado, lo que también permite enumerar cuentas (igual que el CP-006).
- Los horarios están fijos y no se valida que el turno sea futuro.
- La sesión del panel se guarda solo en el navegador; no hay token en el servidor.

## Evidencias

Capturas de la ejecución de los casos de prueba y de la herramienta de gestión.

### Ejecución de los casos (`docs/evidencias/app`)

| Caso | Captura |
|---|---|
| CP-001 | [Inicio de sesión exitoso](docs/evidencias/app/CP-001.png) |
| CP-002 | [Contraseña incorrecta](docs/evidencias/app/CP-002.png) |
| CP-003 | [Registro exitoso](docs/evidencias/app/CP-003.png) |
| CP-004 | [Correo ya registrado](docs/evidencias/app/CP-004.png) |
| CP-005 | [Recuperación con correo registrado](docs/evidencias/app/CP-005.png) · [correo enviado](docs/evidencias/app/CP-005-Verificacion.png) |
| CP-006 | [Recuperación con correo inexistente](docs/evidencias/app/CP-006.png) |
| CP-007 | [Reserva confirmada](docs/evidencias/app/CP-007.png) · [correos enviados](docs/evidencias/app/CP-007-Verificacion.png) |
| CP-008 | [Falta el correo](docs/evidencias/app/CP-008.png) |
| CP-009 | [Botón deshabilitado tras un click](docs/evidencias/app/CP-009.png) |
| CP-010 | [Clicks múltiples](docs/evidencias/app/CP-010.png) · [un único registro](docs/evidencias/app/CP-010-Verificacion.png) |

### Kiwi TCMS (`docs/evidencias/kiwi`)

Los casos se gestionaron en Kiwi TCMS, instalado localmente con Docker. Se creó
el producto AgendaYA, el plan de pruebas TP-1 con los 10 casos y un usuario por
integrante: `santino` con rol Administrator y `maximo`, `joaquin`, `matias` y
`fernando` con rol Tester.

- [Producto AgendaYA](docs/evidencias/kiwi/01_kiwi_producto_agendaya.png)
- [Plan de pruebas con los 10 casos](docs/evidencias/kiwi/02_kiwi_plan_de_pruebas_10_casos.png)
- [Detalle del caso CP-002](docs/evidencias/kiwi/03_kiwi_detalle_cp002.png)
- [Usuarios del equipo](docs/evidencias/kiwi/04_kiwi_usuarios_del_equipo.png)
- Roles: [santino](docs/evidencias/kiwi/05_kiwi_rol_administrator_santino.png) ·
  [maximo](docs/evidencias/kiwi/05_kiwi_rol_tester_maximo.png) ·
  [joaquin](docs/evidencias/kiwi/05_kiwi_rol_tester_joaquin.png) ·
  [matias](docs/evidencias/kiwi/05_kiwi_rol_tester_matias.png) ·
  [fernando](docs/evidencias/kiwi/05_kiwi_rol_tester_fernando.png)
