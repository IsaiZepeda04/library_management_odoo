Library Management – Odoo 19

Modulo desarrollado en Odoo 19 como solución para la gestión de biblioteca, cumpliendo con los requerimientos de la prueba técnica para pasante Odoo Developer en Treming.

El sistema permite la administración de libros, miembros, prestamos, automatizaciones, portal web(socio), seguridad por roles e integración externa mediante API REST.

1.	Levantamiento del Entorno (DevOps – Punto 10/Prueba tecnica)
Se configuro el entorno utilizando Python + Vitual Environment (venv), a continuación, el desglose de este:
Paso 1: Clonar repositorio
		git clone https://github.com/TU_USUARIO/library_management.git
        cd library_management
Paso 2: Crear el entorno virtual
		python -m venv venv 
	tener en cuenta que Odoo soporta ciertas versiones de Python en este caso si tienes más de una versión es bueno especificar cual se usara en el venv
Paso 3: Activar el entorno virtual
	venv\Scripts\activate
Paso 4: Instalar dependencias
	pip install -r requeriments.txt
Paso 5: Configuracion de Odoo, dentro del archivo odoo.conf
	addons_path = addons,custom_addons
    db_host = localhost
    db_port = 5432
    db_user = odoo
    db_password = odoo
Paso 6: Ejecutar Odoo
		python odoo-bin -c odoo.conf -d odoo19_library
	Para actualizer el módulo:
		python odoo-bin -c odoo.conf -d odoo19_library -u library_management
        
2.	Instalación del modulo
•	Acceder a:
	https://localhost:8069
•	Activar modo desarrollador(dentro de Settings de Odoo)
•	Ir a Apss y Update Apps List
•	Buscar: Library Management
•	Instalar

FUNCIONALIDADES
3.	Gestión de Libros
Funcionalidad: Registrar y administrar libros.
Implementación:
•	modelo: library.book
•	Campos:
o	name
o	isbn
o	state(disponible/no disponible)
Validaciones: no permite el préstamo si el libro no está disponible.

4.	Gestión de Socios/Miembros
Funcionalidad: Permite registrar socios/miembros de la biblioteca.
Implementación:
•	Basado en: res.partner
•	Campos adicionales:
o	is_library_member
o	member_code
o	member_date
Característica: Generación automática de código de socio

5.	Gestión de Prestamos
Funcionalidad: Permite registrar prestamos de libros a socios/miembros.
Implementación:
•	Modelo: library.loan
•	Relacion:
o	book_id
o	member_id
Reglas:
•	Máximo 5 prestamos activos por socios
•	No permitir préstamo si el libro no está disponible.
Estados:
•	active: Activo
•	overdue: Vencido
•	returned: Devuelto

6.	Automatización (CRON)
Funcionalidad: Automatiza la detección de préstamos vencidos.
Implementación:
•	Scheduled Action(ir.cron)
•	Método:
	cron_mark_overdue_loans()
Comportamiento: 
•	Marca prestamos como vencidos después de 30 días
•	Envía notificación por correo

7.	Notificaciones por Email
Funcionalidad: Enviar correo automáticamente cuando se vence un prestamo.
Implementación: 
•	Plantilla: mail.template
•	Configuración SMTP(Gmail)
Flujo:
•	CRON detecta prestamos vencidos
•	Se envía el correo al socio 

8.	Portal del Socio
Funcionalidad: Permite al socio consultar sus prestamos desde el Portal Web, muestra la información más relevante y además da la opción de renovar el préstamo.
Implementación:
•	Controlador personalizado en Odoo
•	Integración dentro del website para mostrar el acceso “Mis Prestamos”
•	Ruta de acceso al listado: /my/loans
•	Funciones disponibles:
•	Visualizar sus prestamos
•	Ver libros, fechas de préstamo y estado
•	Renovar préstamo cuando este activo

9.	Accesos y permisos
Funcionalidad: Restringir acceso según el rol.
Roles creados:
•	Bibliotecario: Acceso total
•	Usuario Publico: Solo lectura de libros disponibles
Implementación:
•	Res.gropus
•	Record rules

10.	Punto de Venta (POS)
Estado: No implementado completamente
Motivo: El modulo POS tiene dependencia de pago (Accouting) por lo que no fue posible completarlo en el entorno local.

11.	Integración Externa (API REST)
Funcionalidad: permite consultar disponibilidad a través de url con el uso del ISBN del libro.
Endpoint: GET /api/books/availability?isbn=XXXX
Respuestas: Si se encuentra el ISBN se mostrará el “id, isbn, titulo y disponibilidad”; caso contrario “libro no encontrado”

12.	Pruebas y Validaciones
Se realizaron pruebas para validar el correcto funcionamiento del sistema.

Caso 1: Registro de Préstamo
Pasos:
1.	Crear socio
2.	Crear libro disponible
3.	Registrar préstamo
Resultado esperado:
•	Préstamo creado 
•	Libro pasa a “No disponible”

Caso 2: Vencimiento Automático
Pasos:
1.	Crear préstamo con fecha mayor a 30 días
2.	Ejecutar CRON manualmente
Resultado esperado:
•	Estado cambia a “Vencido”
•	Se envía el correo

Caso 3: Renovación
Pasos:
1.	Ingresar a “Mis Prestamos” en la website
2.	Presionar “Renovar”
Resultado esperado:
•	Fecha actualizada
•	No permite renovar prestamos vencidos

Caso 4: Permisos
Pasos:
1.	Iniciar sesión con distintos roles
Resultado esperado:
•	Bibliotecario: acceso total
•	Usuario Publico: solo lectura

Caso 5: API REST
Petición:
GET /api/books/availability?isbn=123
Resultado esperado:
•	Retorna disponibilidad o error

Estructura General del Proyecto
library_management/
│
├── models/
├── views/
├── security/
├── data/
├── controllers/
├── __manifest__.py
└── __init__.py

Estado del Proyecto
-	Funcional
-	Listo para demostración

Autor
Leonardo Isai Zepeda Tolentino, desarrollado como prueba técnica para pasante Odoo Developer en Treming
