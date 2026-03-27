# Library Management – Odoo 19 Community

Módulo desarrollado en **Odoo 19 Community** como solución para la gestión de biblioteca, cumpliendo con los requerimientos de la prueba técnica para pasante **Odoo Developer**.

El sistema permite la administración de libros, miembros, préstamos, automatizaciones, portal web del socio, seguridad por roles, integración con **Punto de Venta (POS)** e integración externa mediante **API REST**.

---

## 1. Levantamiento del entorno (DevOps – Punto 10)

Se configuró el entorno utilizando **Python + Virtual Environment (venv)**.

### Paso 1: Clonar repositorio

```bash
git clone https://github.com/TU_USUARIO/library_management.git
cd library_management
```

### Paso 2: Crear el entorno virtual

```bash
python -m venv venv
```

> Tener en cuenta que Odoo soporta versiones específicas de Python. Si se tienen varias versiones instaladas, conviene indicar explícitamente cuál se utilizará para el entorno virtual.

### Paso 3: Activar el entorno virtual

En Windows:

```bash
venv\Scripts\activate
```

### Paso 4: Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 5: Configuración de Odoo (`odoo.conf`)

Ejemplo de configuración usada:

```ini
[options]
admin_passwd = TU_HASH
db_host = localhost
db_port = 5432
db_user = odoo
db_password = admin
addons_path = C:\odoo\odoo19\odoo\addons,C:\odoo\odoo19\odoo\custom_addons
http_port = 8069
http_interface = 0.0.0.0
proxy_mode = False
```

### Paso 6: Ejecutar Odoo

```bash
python odoo-bin -c odoo.conf -d odoo19_library
```

### Para actualizar el módulo

```bash
python odoo-bin -c odoo.conf -d odoo19_library -u library_management
```

---

## 2. Instalación del módulo

- Acceder a: `http://127.0.0.1:8069/web`
- Activar **modo desarrollador** dentro de **Settings**
- Ir a **Apps**
- Ejecutar **Update Apps List**
- Buscar: **Library Management**
- Instalar el módulo

---

## 3. Dependencias utilizadas

El módulo se apoya en los siguientes módulos estándar de Odoo:

- `base`
- `mail`
- `website`
- `portal`
- `point_of_sale`
- `product`

---

## 4. Funcionalidades implementadas

## 4.1 Gestión de Libros

**Funcionalidad:** Registrar y administrar libros.

### Implementación
- Modelo: `library.book`
- Campos principales:
  - `name`
  - `author`
  - `isbn`
  - `publi_date`
  - `years_since_publication`
  - `is_available`
  - `product_id`

### Características implementadas
- Cálculo automático de años desde la publicación
- Visualización del campo en listado y formulario
- Filtros para:
  - libros disponibles
  - libros no disponibles
- Agrupación por:
  - autor
  - disponibilidad
- Validación para impedir préstamo cuando el libro no está disponible
- Relación con producto POS para operar el libro desde Punto de Venta

---

## 4.2 Gestión de Socios / Miembros

**Funcionalidad:** Permite registrar socios o miembros de la biblioteca.

### Implementación
- Basado en: `res.partner`
- Campos adicionales:
  - `is_library_member`
  - `member_code`
  - `member_date`

### Características implementadas
- Generación automática del código de socio mediante secuencia
- Identificador de socio inmutable
- Visualización del código en la ficha del contacto
- Menú específico para miembros de biblioteca

### Nota técnica
Se ajustó la lógica de `member.py` para:
- evitar edición manual del código
- generar el código al marcar un contacto como socio
- mantener consistencia al convertir contactos existentes en miembros

---

## 4.3 Sincronización entre Usuarios y Socios

**Funcionalidad:** Mantener relación coherente entre usuarios de Odoo y su contacto/socio asociado.

### Implementación
- Basado en: `res.users`
- Archivo relevante: `models/res_users.py`

### Características implementadas
- Sincronización con `partner_id`
- Identificación de usuarios relacionados con biblioteca o portal
- Apoyo a la conversión automática del contacto en socio cuando corresponde
- Ajustes para evitar conflictos entre usuarios internos y usuarios portal

### Ajuste importante realizado
En Odoo 19 se corrigió el uso de grupos para trabajar con `group_ids`, evitando errores al guardar usuarios.

---

## 4.4 Gestión de Préstamos

**Funcionalidad:** Permite registrar préstamos de libros a socios.

### Implementación
- Modelo: `library.loan`
- Relaciones:
  - `book_id`
  - `member_id`

### Reglas de negocio
- Máximo **5 préstamos activos o vencidos** por socio
- No permitir préstamo si el libro no está disponible
- Al crear préstamo, el libro pasa automáticamente a **no disponible**
- Al devolver, el libro vuelve a **disponible**

### Estados implementados
- `active`: Activo
- `overdue`: Vencido
- `returned`: Devuelto

---

## 4.5 Devolución de Libros

**Funcionalidad:** Registrar la devolución manual de libros.

### Implementación
- Acción en el modelo de préstamo para devolución

### Comportamiento
- Cambia el estado a `returned`
- Registra la fecha de devolución
- Libera nuevamente el libro
- Permite al socio recuperar cupo para nuevos préstamos

---

## 4.6 Automatización (CRON)

**Funcionalidad:** Detectar automáticamente préstamos vencidos.

### Implementación
- `Scheduled Action (ir.cron)`
- Método: `cron_mark_overdue_loans()`

### Comportamiento
- Revisa diariamente préstamos con más de 30 días
- Marca el préstamo como vencido
- Dispara el flujo de notificación por correo

---

## 4.7 Notificaciones por Email

**Funcionalidad:** Enviar correo automáticamente cuando un préstamo se vence.

### Implementación
- Plantilla de correo: `mail.template`
- Configuración SMTP para envío de correos

### Flujo
- El CRON detecta préstamos vencidos
- El sistema envía una notificación por correo al socio

---

## 4.8 Portal del Socio

**Funcionalidad:** Permitir al socio consultar sus préstamos desde el portal web y renovarlos cuando corresponda.

### Implementación
- Controlador personalizado en Odoo
- Integración dentro del website para mostrar el acceso **Mis Préstamos**
- Ruta de acceso: `/my/loans`

### Funciones disponibles
- Visualizar sus préstamos
- Ver libro, fecha de préstamo y estado
- Renovar préstamo si está activo y no vencido

### Ajustes realizados
Se actualizó la lógica del portal para trabajar mejor con:
- `partner_id`
- `commercial_partner_id`

Esto ayuda a mostrar correctamente los préstamos del socio portal, incluso cuando el contacto fue utilizado desde otros flujos como POS.

---

## 4.9 Accesos y permisos

**Funcionalidad:** Restringir acceso según el rol del usuario.

### Roles creados
- **Bibliotecario:** acceso total sobre libros, socios y préstamos
- **Usuario Público:** solo lectura de libros disponibles
- **Socio Portal:** acceso al website para consultar y renovar préstamos

### Implementación
- `res.groups`
- `ir.model.access.csv`
- `record rules`

### Cambios importantes realizados
- Separación entre usuario interno y usuario portal para evitar conflictos entre grupos excluyentes
- Ajustes en grupos y reglas para Odoo 19 Community
- Configuración de usuarios de prueba para demostrar restricciones en la interfaz

---

## 4.10 Integración con Productos para POS

**Funcionalidad:** Permitir que los libros se operen desde el Punto de Venta mediante productos estándar de Odoo.

### Implementación
- Extensión de `product.product`
- Campo agregado:
  - `is_library_item`

### Archivo relevante
- `models/product_product.py`

### Vista relevante
- `views/product_views.xml`

### Flujo implementado
1. Se crea un producto estándar
2. Se marca como:
   - disponible en POS
   - ítem de biblioteca
3. Se vincula el producto al libro desde `product_id`

Esto permite que el POS opere el libro sin crear una lógica paralela fuera del flujo estándar de Odoo.

---

## 4.11 Punto de Venta (POS)

**Funcionalidad:** Permitir registrar préstamos rápidos desde el flujo estándar de una venta en POS.

### Implementación
- Archivo relevante: `models/pos_order.py`

### Flujo implementado
En una orden POS, al seleccionar un cliente y confirmar:
- se valida que exista cliente
- se valida que el cliente sea socio
- se revisan las líneas de la orden
- si el producto está marcado como ítem de biblioteca:
  - se localiza el libro relacionado
  - se valida disponibilidad
  - se valida que el socio no tenga 5 préstamos activos
  - se crea automáticamente el préstamo
  - el libro pasa a no disponible

### Configuración funcional realizada para POS
Para poder operar el flujo POS se realizó lo siguiente:
- configuración de localización fiscal base
- creación de un Punto de Venta
- creación de un producto del libro con:
  - tipo bienes
  - precio `0.00`
  - disponible en POS
  - `is_library_item = True`
- vinculación del producto con el libro
- uso de un cliente socio dentro de la orden

### Resultado actual
- El POS **sí fue implementado y probado**
- La orden POS crea correctamente el préstamo
- El préstamo aparece en el módulo `library.loan`
- El libro queda marcado como **no disponible**

### Nota técnica
Si en el POS se intenta generar el recibo/factura PDF y no está instalado `wkhtmltopdf`, Odoo puede mostrar error al imprimir el comprobante.  
Para la prueba funcional del préstamo, el flujo puede completarse desmarcando la opción de impresión del recibo.

---

## 4.12 Integración Externa (API REST)

**Funcionalidad:** Consultar disponibilidad de un libro a través del ISBN.

### Endpoint
```http
GET /api/books/availability?isbn=XXXX
```

### Respuesta esperada
Si el ISBN existe:
- `id`
- `isbn`
- `titulo`
- `disponibilidad`

Si el ISBN no existe:
- mensaje claro de error
- código HTTP adecuado

---

## 5. Pruebas y validaciones

Se realizaron pruebas para validar el correcto funcionamiento del sistema.

### Caso 1: Registro de préstamo manual
**Pasos:**
1. Crear socio
2. Crear libro disponible
3. Registrar préstamo

**Resultado esperado:**
- préstamo creado
- libro pasa a **No disponible**

---

### Caso 2: Vencimiento automático
**Pasos:**
1. Crear préstamo con fecha mayor a 30 días
2. Ejecutar CRON manualmente

**Resultado esperado:**
- estado cambia a **Vencido**
- se envía el correo

---

### Caso 3: Renovación en portal
**Pasos:**
1. Ingresar a **Mis Préstamos** en website
2. Presionar **Renovar**

**Resultado esperado:**
- préstamo renovado
- no permite renovar préstamos vencidos

---

### Caso 4: Permisos
**Pasos:**
1. Iniciar sesión con distintos roles

**Resultado esperado:**
- **Bibliotecario:** acceso total
- **Usuario Público:** solo lectura de libros disponibles
- **Socio Portal:** acceso únicamente al portal web

---

### Caso 5: API REST
**Petición:**
```http
GET /api/books/availability?isbn=123
```

**Resultado esperado:**
- retorna disponibilidad o error claro

---

### Caso 6: Préstamo desde POS
**Pasos:**
1. Crear producto del libro
2. Marcarlo como disponible en POS
3. Marcarlo como ítem de biblioteca
4. Vincularlo al libro
5. Abrir sesión POS
6. Seleccionar cliente socio
7. Confirmar la orden

**Resultado esperado:**
- se crea el préstamo
- el libro queda no disponible

---

## 6. Estructura general del proyecto

```text
library_management/
│
├── models/
│   ├── member.py
│   ├── res_users.py
│   ├── book.py
│   ├── loan.py
│   ├── product_product.py
│   └── pos_order.py
│
├── views/
│   ├── member_views.xml
│   ├── book_views.xml
│   ├── loan_views.xml
│   ├── menu_views.xml
│   ├── product_views.xml
│   └── portal_templates.xml
│
├── security/
│   ├── library_security.xml
│   ├── ir.model.access.csv
│   └── library_record_rules.xml
│
├── data/
│   ├── member_sequence.xml
│   ├── loan_email_template.xml
│   └── loan_cron.xml
│
├── controllers/
│   ├── portal.py
│   └── api.py
│
├── __manifest__.py
└── __init__.py
```

---

## 7. Información relevante

- Proyecto trabajado sobre **Odoo 19 Community**
- Se utilizaron módulos estándar de Odoo como base para las integraciones
- La lógica crítica del negocio fue colocada en backend para evitar inconsistencias
- El código de socio se genera por secuencia y se mantiene inmutable
- El portal fue ajustado para reflejar correctamente los préstamos del socio
- POS fue implementado y probado funcionalmente
- Para impresión PDF desde POS puede requerirse `wkhtmltopdf`

---

## 8. Estado del proyecto

- Funcional
- Listo para demostración
- Alineado con los requerimientos principales de la prueba técnica

---

## 9. Autor

**Leonardo Isai Zepeda Tolentino**  
Desarrollado como prueba técnica para pasante **Odoo Developer**.
