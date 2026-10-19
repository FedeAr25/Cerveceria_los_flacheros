# 06 Cuaderno de defensa oral - Cervecería Los Flacheros (backend Django)

Documento de estudio para el desarrollador del backend. Defensa oral de la EFI, Ingeniería de Software 2026, docente Facundo Esteban Lemo. Defensa desde el martes 3 de noviembre; entrega lunes 2 de noviembre.

## 1. Cómo usar este cuaderno

Leelo dos veces.

Primera vez: antes de la defensa, para memorizar las respuestas principales de cada bloque y la ficha de 60 segundos.

Segunda vez: el día previo (lunes 2 de noviembre), repasando solo las preguntas marcadas como trampa en la sección 5 y el guion de apertura de la sección 6.

Este cuaderno es para vos, que hiciste el 100 por ciento del backend. Ema prepara lo del frontend por su lado. El docente evalúa solo el proyecto Django y el proceso seguido. La nota final es el promedio entre la del backend (Lemo) y la del frontend (Arballo).

## 2. Ficha de 60 segundos

Qué es Cervecería Los Flacheros: una API REST para administrar una cervecería artesanal. Estilos de cerveza, cervezas con stock, lotes de producción y sus etapas de fermentación, proveedores, materias primas, clientes, pedidos con sus líneas y opiniones de clientes. Tiene panel de administración completo, autenticación por sesión y por token, documentación automática con Swagger y ReDoc, y una vista de bienvenida en la raíz.

Con qué está hecho: Django 5.2.18 LTS, Django REST Framework 3.17, drf-spectacular, django-filter, django-cors-headers, django-environ, psycopg v3, PostgreSQL 17 en Docker Compose, Python 3.13, gestionado con uv 0.13.1. El front es Next.js con App Router y Tailwind, pero Lemo no lo evalúa.

Cuántas tablas y endpoints: 10 modelos en una sola app llamada core y 10 endpoints bajo /api/ (estilos, cervezas, lotes, etapas, proveedores, materias-primas, clientes, pedidos, lineas, opiniones), todos con ModelViewSet y router.

Qué lo hace diferente: se entregó justo lo que pide la consigna, nada de más. Exactamente 10 modelos y 10 endpoints. Stock como campo numérico en Cerveza y MateriaPrima sin entidad aparte. Usuario de Django sin customizar. Sin imágenes. Token nativo de DRF en vez de JWT. Permisos declarativos. Git solo local. Docker para la base de datos.

Marca: lema *Arte en cada trago, tradición en cada lote*. Colores: ámbar #F5A623, lúpulo #4A7C59, malta tostada #8B4513, espuma #F7F7F7, carbón #2B2B2B.
## 3. Las 17 consignas del docente y cómo demostrar cada una

| # | Consigna | Dónde se cumple en el proyecto | Cómo lo demuestro (comando o URL) | Qué digo |
|---|----------|-------------------------------|-----------------------------------|----------|
| 1 | Diez modelos o más con relaciones | core/models.py: los 10 modelos (Estilo, Cerveza, Lote, EtapaFermentacion, Proveedor, MateriaPrima, Cliente, Pedido, LineaPedido, Opinion) | uv run python manage.py inspectdb o el diagrama ER en docs/ | Tengo exactamente 10 modelos con relaciones: Cerveza depende de Estilo, Lote depende de Cerveza y del usuario, EtapaFermentacion depende de Lote, MateriaPrima depende de Proveedor, Pedido depende de Cliente, LineaPedido depende de Pedido y Cerveza, y Opinion depende de Cerveza y Cliente. |
| 2 | Planificación de tablas adjunta al README (diagrama ER) | docs/ y el README | Abrir el README y mostrar el diagrama ER | Antes de migrar diseñamos las tablas con un diagrama ER y lo adjuntamos al README, tal como pide la consigna. |
| 3 | API REST con al menos 8 de 10 modelos vía ViewSet | core/views.py: 10 ModelViewSet y DefaultRouter bajo /api/ | GET /api/cervezas/ y los otros nueve endpoints | Los 10 modelos están expuestos por API REST con ModelViewSet, así que cubro el mínimo de 8 con sobra. |
| 4 | Al menos 2 ViewSets CRUD con datos anidados solo en list (serializers anidados) | LoteViewSet y PedidoViewSet con get_serializer_class | GET /api/lotes/ devuelve etapas anidadas; GET /api/lotes/1/ devuelve plano. Igual con pedidos y líneas. | El anidado solo va en list: al listar lotes veo sus etapas, y al listar pedidos veo sus líneas. Al recuperar uno solo, el payload es plano. |
| 5 | Endpoints protegidos con autenticación de sesión y por token | settings.py: SessionAuthentication y TokenAuthentication; POST /api/auth-token/ | POST /api/auth-token/ devuelve el token y luego se usa en el encabezado Authorization: Token <key> | La API acepta sesión y token. Para el front usamos token porque las cookies ignoran el puerto y se compartirían entre localhost:3000 y localhost:8000. |
| 6 | Al menos 2 funciones personalizadas con @action | /api/cervezas/en_grifo/ y /api/pedidos/estadisticas/ (más la opcional POST /api/lotes/{id}/avanzar/) | Consultar /api/cervezas/en_grifo/ y /api/pedidos/estadisticas/ | Tengo dos acciones personalizadas: cervezas en grifo (lista pública) y estadísticas de pedidos (solo administradores). |
| 7 | Endpoints de get all paginados | settings.py: PageNumberPagination, PAGE_SIZE=10, page_size_query_param y max_page_size=50 | GET /api/cervezas/?page=2 y verificar las claves next, previous y results | Todos los listados están paginados globalmente de a 10, con opción de cambiar el tamaño hasta 50. |
| 8 | Al menos 1 ViewSet con filtros y búsquedas | CervezaViewSet con DjangoFilterBackend, SearchFilter y OrderingFilter | GET /api/cervezas?estilo=1&search=ipa&ordering=-precio | Cerveza se filtra por estilo y precio, se busca por nombre y se ordena por cualquier campo. |
| 9 | Endpoints de documentación (openapi, swagger, redoc) y API navegable | drf-spectacular: /api/schema/, /api/schema/swagger-ui/, /api/schema/redoc/ y browsable API | Abrir /api/schema/swagger-ui/ y /api/ en el navegador | La documentación se genera sola con OpenAPI y tiene Swagger UI, ReDoc y la API navegable de DRF. |
| 10 | Vista principal que renderice un template de bienvenida | core/views.py: vista para la ruta / y el template de bienvenida | Abrir http://localhost:8000/ en el navegador | La raíz muestra una vista de bienvenida con la identidad de marca de Los Flacheros. |
| 11 | Control total con panel de administración (filtros, ordenamiento y búsqueda) | core/admin.py con list_filter, search_fields, ordering e inlines | Entrar a /admin/ y filtrar, buscar y ordenar | El admin está totalmente configurado: filtros laterales, campos de búsqueda, ordenamiento por defecto e inlines de etapas y líneas. |
| 12 | uv como gestor de entornos virtuales | pyproject.toml, uv.lock y comandos uv | uv run python manage.py runserver | Usamos uv para instalar dependencias, crear el entorno virtual y ejecutar comandos, en vez de pip más venv. |
| 13 | CORS configurado | settings.py: CORS_ALLOWED_ORIGINS con http://localhost:3000 y django-cors-headers | Probar que el front de Next.js en el puerto 3000 consume la API | django-cors-headers permite que el front en localhost:3000 consuma la API en localhost:8000. |
| 14 | Proyecto dockerizado | docker-compose.yml, Dockerfile y PostgreSQL 17 | docker compose up -d | La base de datos corre en PostgreSQL 17 dentro de Docker Compose y el back se levanta con gunicorn. |
| 15 | Buen trabajo organizacional con Git (ramas, commits descriptivos) | Ramas feature, commits convencionales en español y merges --no-ff a main | git log --oneline --graph | Trabajamos por ramas feature, con commits descriptivos en español y fusiones sin fast-forward a main. |
| 16 | README con capturas | README.md con imágenes de Swagger, admin y endpoints | Abrir el README y mostrar las capturas | El README documenta el proyecto con capturas de pantalla de la API, el admin y la documentación. |
| 17 | Defensa oral explicando el funcionamiento del framework | Este cuaderno y la exposición oral | Responder las preguntas del docente | Este cuaderno me prepara para explicar cómo funciona Django y cada decisión que tomamos.
## 4. Preguntas por bloque

### A. Django y el framework

1. ¿Qué es Django y por qué lo elegimos para este proyecto?
Respuesta hablada: Django es un framework web de Python que trae casi todo listo: ORM, admin, autenticación, URLs y plantillas. Lo elegimos porque acelera el desarrollo, es estable (LTS) y el docente pide específicamente un proyecto Django para la EFI.
Detalle técnico: Django 5.2.18 LTS en config/settings.py, con soporte hasta abril 2028. Compatible con drf-spectacular 0.30.0 y Django REST Framework 3.17.

2. ¿Qué es un framework?
Respuesta hablada: Es un conjunto de herramientas y reglas que te da la estructura base de una aplicación para que no tengas que programar todo desde cero, como el enrutado, la base de datos y el servidor.
Detalle técnico: En este caso Django provee el MVT, el ORM, el admin y el servidor de desarrollo; Django REST Framework le agrega la capa REST.

3. ¿Qué es un modelo en Django?
Respuesta hablada: Un modelo es una clase Python que representa una tabla de la base de datos. Cada atributo es una columna y cada instancia es una fila.
Detalle técnico: Definidos en core/models.py, heredan de models.Model. Ejemplo: class Cerveza(models.Model) con nombre, estilo (clave foránea), precio (DecimalField) y stock (IntegerField).

4. ¿Qué es una migración?
Respuesta hablada: Es un archivo que le dice a Django cómo pasó la base de datos de un estado a otro, como crear una tabla o agregar una columna, para que no tengamos que escribir SQL a mano.
Detalle técnico: Se generan con uv run python manage.py makemigrations y se aplican con uv run python manage.py migrate. Quedan versionadas en core/migrations/.

5. ¿Qué es el ORM?
Respuesta hablada: El ORM es el traductor entre Python y la base de datos. Te deja consultar y guardar datos con código Python en vez de escribir SQL.
Detalle técnico: Ejemplos reales: Cerveza.objects.filter(stock__gt=0) y Pedido.objects.select_related('cliente'). El backend usa PostgreSQL a través de psycopg v3.

6. ¿Qué es el admin de Django y para qué sirve?
Respuesta hablada: Es una interfaz lista para usar donde los administradores pueden dar de alta, editar y borrar registros de cada modelo sin programar pantallas.
Detalle técnico: Configurado en core/admin.py con ModelAdmin, list_filter, search_fields, ordering e inlines (EtapaFermentacion dentro de Lote y LineaPedido dentro de Pedido). Acceso en /admin/.

7. ¿Qué es una app en Django y por qué usamos una sola llamada core?
Respuesta hablada: Una app es un módulo del proyecto que hace una cosa específica. Usamos una sola app, core, porque la consigna se cumple con los 10 modelos y no queremos fragmentar el proyecto sin necesidad.
Detalle técnico: settings.py trae una sola app propia: 'core'. El proyecto se llama config y la app es core.

8. ¿Cuál es la diferencia entre MVT y MTV?
Respuesta hablada: No hay diferencia real, es lo mismo con nombres distintos. Django lo llama MVT (Modelo, Vista, Plantilla) porque la vista de Django es lo que en otros frameworks llaman controlador, y la plantilla es lo que otros llaman vista.
Detalle técnico: Modelo = core/models.py, Vista = core/views.py (ViewSets y la vista de bienvenida), Plantilla = templates/bienvenida.html. Las URLs las maneja config/urls.py con el router de Django REST Framework.

9. ¿Qué es manage.py?
Respuesta hablada: Es el script de línea de comandos de Django para crear migraciones, correr el servidor, crear superusuarios y ejecutar tests.
Detalle técnico: Se invoca con uv run python manage.py <comando>, por ejemplo uv run python manage.py runserver, uv run python manage.py migrate y uv run python manage.py createsuperuser.

10. ¿Qué es settings.py?
Respuesta hablada: Es el archivo de configuración central del proyecto: base de datos, apps instaladas, middlewares, autenticación, paginación, CORS y archivos estáticos.
Detalle técnico: Ruta config/settings.py. Ahí declaramos INSTALLED_APPS, REST_FRAMEWORK, CORS_ALLOWED_ORIGINS, DATABASES con PostgreSQL y PAGE_SIZE = 10.

11. ¿Qué es urls.py?
Respuesta hablada: Es el archivo que asocia cada URL con una vista. Es el mapa de navegación del proyecto.
Detalle técnico: config/urls.py registra el router de Django REST Framework bajo /api/, los endpoints de documentación (/api/schema/, /api/schema/swagger-ui/, /api/schema/redoc/), el token (/api/auth-token/), el admin (/admin/) y la vista de bienvenida en /.

12. ¿Qué son los archivos estáticos y qué hace collectstatic?
Respuesta hablada: Los archivos estáticos son CSS, JavaScript e imágenes que no cambian. collectstatic los reúne todos en una carpeta para que el servidor los sirva en producción.
Detalle técnico: Usamos whitenoise para servir estáticos sin servidor externo. En producción se corre uv run python manage.py collectstatic y whitenoise los sirve desde la misma aplicación gunicorn.

13. ¿Qué es whitenoise y por qué lo usamos?
Respuesta hablada: Whitenoise es una biblioteca que permite servir archivos estáticos directamente desde la aplicación Python, sin necesidad de un servidor web separado como Nginx.
Detalle técnico: whitenoise 6.12.0 instalado y configurado en settings.py (MIDDLEWARE y almacenamiento de estáticos). Útil para desplegar con gunicorn y no depender de Nginx en este proyecto.

### B. Modelos y base de datos

14. ¿Por qué exactamente 10 modelos y no más ni menos?
Respuesta hablada: La consigna pide al menos 10 modelos y al menos 8 endpoints. Cada modelo extra trae su serializer, viewset, admin, tests y migración, así que 10 es el punto justo: cumple sin agregar trabajo que no nos piden.
Detalle técnico: Los 10 modelos están en core/models.py: Estilo, Cerveza, Lote, EtapaFermentacion, Proveedor, MateriaPrima, Cliente, Pedido, LineaPedido y Opinion. Los 10 endpoints usan ModelViewSet y DefaultRouter.

15. ¿Cómo se relacionan los modelos entre sí?
Respuesta hablada: Un estilo tiene muchas cervezas. Una cerveza tiene muchos lotes. Un lote pertenece a una cerveza y puede tener un usuario asignado, y tiene muchas etapas de fermentación. Un proveedor provee muchas materias primas. Un cliente hace muchos pedidos. Un pedido tiene muchas líneas, y cada línea apunta a una cerveza. Una cerveza tiene muchas opiniones, y un cliente escribe muchas opiniones.
Detalle técnico: Relaciones concretas en core/models.py: Cerveza.estilo es ForeignKey a Estilo con on_delete=PROTECT; Lote.cerveza es ForeignKey a Cerveza con on_delete=PROTECT y Lote.usuario es ForeignKey a User con on_delete=SET_NULL; EtapaFermentacion.lote es ForeignKey a Lote con on_delete=CASCADE y related_name='etapas'; MateriaPrima.proveedor es ForeignKey a Proveedor con on_delete=SET_NULL; Pedido.cliente es ForeignKey a Cliente con on_delete=PROTECT; LineaPedido.pedido es ForeignKey a Pedido con on_delete=CASCADE y related_name='lineas', y LineaPedido.cerveza es ForeignKey a Cerveza con on_delete=PROTECT; Opinion.cerveza y Opinion.cliente son ForeignKey con on_delete=CASCADE.

16. ¿Qué es una clave foránea (FK)?
Respuesta hablada: Es una columna que apunta a la clave primaria de otra tabla, para vincular dos registros y evitar duplicar datos.
Detalle técnico: En Django se declara con models.ForeignKey. Ejemplo: Cerveza.estilo apunta a Estilo.id.

17. ¿Qué es on_delete y por qué usamos PROTECT, CASCADE y SET_NULL?
Respuesta hablada: on_delete define qué pasa con los registros relacionados cuando se borra el registro padre. PROTECT impide el borrado si hay hijos, CASCADE borra los hijos junto con el padre, y SET_NULL deja el hijo con el campo vacío si el padre se borra.
Detalle técnico: PROTECT en Cerveza.estilo, Lote.cerveza, Pedido.cliente y LineaPedido.cerveza: no queremos borrar una cerveza que tiene lotes ni un estilo que tiene cervezas. CASCADE en EtapaFermentacion.lote (si se borra el lote, no tienen sentido sus etapas), LineaPedido.pedido (si se borra el pedido, se borran sus líneas), Opinion.cerveza y Opinion.cliente. SET_NULL en Lote.usuario (si se borra el usuario, el lote se mantiene sin usuario asignado) y MateriaPrima.proveedor (si se borra el proveedor, la materia prima se mantiene sin proveedor).

18. ¿Qué es related_name y para qué sirve?
Respuesta hablada: Es el nombre que le damos a la relación inversa para navegar desde el padre hacia los hijos con un nombre claro en vez de uno automático.
Detalle técnico: lote.etapas.all() gracias a related_name='etapas' en EtapaFermentacion.lote, y pedido.lineas.all() gracias a related_name='lineas' en LineaPedido.pedido.

19. ¿Qué son las choices en un modelo?
Respuesta hablada: Son una lista cerrada de valores permitidos para un campo, como los estados de una etapa de fermentación o de un lote.
Detalle técnico: Declaradas como tuplas o clases TextChoices en el modelo. Ejemplo: el estado de EtapaFermentacion con opciones como en_curso, finalizada o control_calidad.

20. ¿Qué es @property y dónde lo usamos?
Respuesta hablada: Es un método que se accede como si fuera un atributo, sin paréntesis. Sirve para calcular un valor a partir de otros campos sin guardarlo en la base de datos.
Detalle técnico: Cliente.nombre_completo devuelve el nombre completo armado a partir de nombre y apellido. LineaPedido.subtotal devuelve cantidad multiplicado por precio unitario. Se definen en core/models.py con el decorador @property.

21. ¿Por qué DecimalField para los precios y no FloatField?
Respuesta hablada: Porque con los números de punto flotante se pueden perder centavos por redondeo binario, y en ventas y cobros no nos podemos permitir ese error.
Detalle técnico: Cerveza.precio es models.DecimalField(max_digits=10, decimal_places=2) y LineaPedido.precio_unitario igual. DecimalField guarda el valor exactamente en la base de datos.

22. ¿Qué es un índice en la base de datos y por qué conviene?
Respuesta hablada: Es una estructura que acelera las búsquedas en una columna, como el índice de un libro. Conviene en columnas que filtramos mucho.
Detalle técnico: Se declara con db_index=True en el campo o con indexes en Meta de cada modelo. Ejemplo: Cerveza.stock y Cerveza.precio pueden tener índice porque se filtran y ordenan seguido.

23. ¿Qué son las migraciones y por qué se versionan?
Respuesta hablada: Son archivos con el historial de cambios de la base de datos. Se versionan para que cualquier integrante del equipo, o el servidor, aplique los mismos cambios en el mismo orden.
Detalle técnico: Cada migración es un archivo en core/migrations/ con nombre 0001_initial.py, 0002_..., etc. Se aplican con uv run python manage.py migrate y se revisan con uv run python manage.py showmigrations.

24. ¿Por qué PostgreSQL y no SQLite en Docker?
Respuesta hablada: Porque SQLite es un archivo local y no simula bien un servidor real. PostgreSQL es lo que usaría la cervecería en producción y lo corremos en un contenedor para que todos tengan la misma base de datos.
Detalle técnico: DATABASES en settings.py apunta a PostgreSQL con psycopg[binary] 3.3.6. Docker Compose levanta postgres:17 con un volumen para persistir los datos.

25. ¿Qué es db_index?
Respuesta hablada: Es una opción de Django que le dice a la base de datos que cree un índice en esa columna para que las consultas sean más rápidas.
Detalle técnico: Ejemplo: campo = models.CharField(max_length=100, db_index=True). Se usa en campos que filtramos seguido, como estilo en Cerveza o cliente en Pedido.

### C. Django REST Framework y la API

26. ¿Qué es una API REST?
Respuesta hablada: Es una forma de exponer datos de una aplicación por HTTP, donde cada recurso tiene una URL y se usan los verbos GET, POST, PUT, PATCH y DELETE para operar sobre ellos.
Detalle técnico: Nuestros recursos están bajo /api/ (estilos, cervezas, lotes, etc.) y responden en JSON.

27. ¿Qué es un serializer en Django REST Framework?
Respuesta hablada: Es el traductor que convierte un modelo de Django en JSON para enviarlo por la API, y convierte JSON entrante de nuevo en un modelo para guardarlo.
Detalle técnico: Heredan de serializers.ModelSerializer en core/serializers.py. Ejemplo: CervezaSerializer convierte una instancia de Cerveza en JSON con id, nombre, estilo, precio y stock.

28. ¿Qué es ModelSerializer?
Respuesta hablada: Es un serializer especial que se genera casi solo a partir de un modelo de Django, con los campos y las validaciones del modelo ya definidos.
Detalle técnico: class CervezaSerializer(serializers.ModelSerializer): class Meta: model = Cerveza; fields = '__all__'. Se usa en todos los ViewSets del proyecto.

29. ¿Qué es un ViewSet y qué ventaja tiene frente a vistas normales?
Respuesta hablada: Es una clase que agrupa todas las operaciones de un recurso (listar, crear, ver uno, editar, borrar) en un solo lugar, sin escribir una vista por cada acción.
Detalle técnico: Todos los endpoints usan viewsets.ModelViewSet. Con una sola clase obtenemos GET /api/cervezas/, POST /api/cervezas/, GET /api/cervezas/1/, PUT, PATCH y DELETE.

30. ¿Qué hace el router de Django REST Framework?
Respuesta hablada: El router crea automáticamente las URLs de cada ViewSet siguiendo las convenciones REST, para no tener que escribir path por path.
Detalle técnico: config/urls.py usa routers.DefaultRouter() y registra los 10 viewsets bajo el prefijo 'api'. Genera /api/estilos/, /api/cervezas/, /api/lotes/ y los demás.

31. ¿Qué es get_serializer_class y para qué lo usamos?
Respuesta hablada: Es un método del ViewSet que elige qué serializer usar según la acción que se esté ejecutando. Lo usamos para devolver datos anidados solo al listar y datos planos al crear o editar.
Detalle técnico:
`python
def get_serializer_class(self):
    if self.action == 'list':
        return LoteConEtapasSerializer
    return LoteSerializer
`
En LoteViewSet y PedidoViewSet. Así el anidado solo aparece en GET /api/lotes/ y GET /api/pedidos/.

32. ¿Qué es @action y qué es detail?
Respuesta hablada: @action permite agregar endpoints personalizados a un ViewSet que no siguen el CRUD estándar. detail=False significa que actúa sobre la colección, como /cervezas/en_grifo/, y detail=True significa que actúa sobre un registro concreto, como /lotes/1/avanzar/.
Detalle técnico: Tres acciones: GET /api/cervezas/en_grifo/ (detail=False), GET /api/pedidos/estadisticas/ (detail=False, permiso IsAdminUser) y POST /api/lotes/{id}/avanzar/ (detail=True, opcional).

33. ¿Qué es la API navegable (browsable API)?
Respuesta hablada: Es la interfaz web de Django REST Framework que te permite navegar por la API y hacer peticiones desde el navegador, sin necesidad de un cliente externo.
Detalle técnico: Habilitada en settings.py con DEFAULT_RENDERER_CLASSES incluyendo BrowsableAPIRenderer. Se accede desde /api/cervezas/ abriendo la URL en el navegador.

34. ¿Qué son OpenAPI, Swagger y ReDoc?
Respuesta hablada: OpenAPI es el estándar que describe la API. Swagger UI y ReDoc son interfaces que leen esa descripción y la muestran bonita y navegable.
Detalle técnico: drf-spectacular 0.30.0 genera el esquema en /api/schema/, y expone /api/schema/swagger-ui/ y /api/schema/redoc/.

35. ¿Por qué paginar los listados?
Respuesta hablada: Para no devolver miles de registros de golpe y saturar el navegador o la conexión; se entregan de a poco.
Detalle técnico:
`python
PAGE_SIZE = 10
PAGE_SIZE_QUERY_PARAM = 'page_size'
MAX_PAGE_SIZE = 50
`
PageNumberPagination global en settings.py. La respuesta trae next, previous, count y results.

36. ¿Qué son los filter backends y para qué sirven?
Respuesta hablada: Son componentes de Django REST Framework que filtran, buscan y ordenan los resultados de un listado según los parámetros de la URL.
Detalle técnico: Usamos DjangoFilterBackend, SearchFilter y OrderingFilter. En CervezaViewSet se filtran por estilo y rango de precio, se busca por nombre y se ordena por precio o stock.
### D. Seguridad, tokens y CORS

37. ¿Cuál es la diferencia entre autenticación y autorización?
Respuesta hablada: Autenticación es saber quién sos (iniciar sesión o presentar un token). Autorización es saber si tenés permiso para hacer una acción, como ver, crear o borrar.
Detalle técnico: Autenticación con SessionAuthentication y TokenAuthentication. Autorización con IsAuthenticated, IsAdminOrReadOnly e IsAdminUser declarados en cada ViewSet o globalmente.

38. ¿Qué es una sesión en Django?
Respuesta hablada: Es una forma de recordar al usuario entre peticiones, guardando su identidad en el servidor y enviando una cookie al navegador.
Detalle técnico: Django usa django.contrib.sessions. La cookie se envía con cada request y el servidor la valida contra su almacenamiento.

39. ¿Qué es un token de Django REST Framework?
Respuesta hablada: Es una clave larga que el cliente obtiene tras loguearse y envía en el encabezado Authorization de cada pedido para identificarse sin enviar la contraseña otra vez.
Detalle técnico: módulo authtoken de DRF. Se obtiene con POST /api/auth-token/ enviando username y password; devuelve un objeto JSON con la clave token. Se usa como Authorization: Token <key>.

40. ¿Por qué configuramos ambos, sesión y token?
Respuesta hablada: Porque la consigna pide endpoints protegidos con autenticación de sesión y por token. La sesión sirve para el admin y la API navegable, y el token sirve para el frontend Next.js.
Detalle técnico: settings.py: DEFAULT_AUTHENTICATION_CLASSES = [SessionAuthentication, TokenAuthentication]. Token obtenido vía POST /api/auth-token/.

41. ¿Qué devuelve 401 y qué devuelve 403, y por qué?
Respuesta hablada: 401 es no estás autenticado, no te identificaste o tu token es inválido. 403 es estás autenticado pero no tenés permiso, como un cliente común que intenta ver estadísticas de pedidos.
Detalle técnico: 401 cuando falta el token o la sesión. 403 cuando IsAdminUser rechaza a un usuario no staff en GET /api/pedidos/estadisticas/.

42. ¿Qué es CSRF?
Respuesta hablada: CSRF es un ataque donde un sitio malo obliga al navegador del usuario a hacer una acción en otro sitio donde ya tiene sesión activa, usando las cookies que el navegador envía solo.
Detalle técnico: Django protege las peticiones con sesión mediante el token CSRF. Por eso no usamos sesión para el front: evitaríamos este problema y el problema de las cookies entre puertos.

43. ¿Qué es CORS y por qué el navegador lo bloquea?
Respuesta hablada: CORS es una seguridad del navegador que impide que una página en un dominio, como localhost:3000, lea respuestas de otro servidor, como localhost:8000, a menos que ese servidor lo permita explícitamente.
Detalle técnico:
`python
CORS_ALLOWED_ORIGINS = ['http://localhost:3000']
`
django-cors-headers 4.9.0 agrega el encabezado Access-Control-Allow-Origin. En settings.py se declara CORS_ALLOWED_ORIGINS con el origen http://localhost:3000.

44. ¿Qué es un preflight?
Respuesta hablada: Es una petición OPTIONS que el navegador envía antes de la petición real para preguntar si el servidor permite el método y los encabezados que se van a usar.
Detalle técnico: django-cors-headers responde a las preflight OPTIONS con los encabezados permitidos para que el navegador luego ejecute la petición GET o POST real.

45. ¿Por qué el frontend no debe usar login por sesión?
Respuesta hablada: Porque las cookies ignoran el puerto: localhost:3000 y localhost:8000 comparten las mismas cookies, lo que abriría la puerta a que el front lea o envíe cookies de sesión del back sin querer. Además CSRF complica el uso entre orígenes.
Detalle técnico: El frontend Next.js usa SOLO Authorization: Token <key> obtenido de POST /api/auth-token/, nunca login por sesión ni cookies de sesión.

46. ¿Qué pasa si el token es inválido o expiró?
Respuesta hablada: La API devuelve 401 No autorizado y el frontend debe pedir al usuario que vuelva a iniciar sesión para obtener un token nuevo.
Detalle técnico: TokenAuthentication valida la clave contra la tabla authtoken_token. Si no existe o está mal formada, DRF responde 401 con el encabezado WWW-Authenticate.

47. ¿Cómo se protege el admin de Django?
Respuesta hablada: El admin solo lo pueden usar usuarios autenticados con permiso de staff, y se accede por /admin/ después de iniciar sesión.
Detalle técnico: django.contrib.admin requiere autenticación. Los superusuarios se crean con uv run python manage.py createsuperuser. Los ViewSets de estilos y proveedores usan IsAdminOrReadOnly para que solo administradores puedan modificar.

### E. Proceso, herramientas y Git

48. ¿Por qué usamos uv y no pip más venv?
Respuesta hablada: Porque uv es mucho más rápido para crear el entorno virtual e instalar dependencias, y maneja todo con un solo archivo, pyproject.toml, más un archivo de bloqueo.
Detalle técnico: uv 0.13.1. Comandos: uv init, uv add django djangorestframework drf-spectacular django-filter django-cors-headers django-environ psycopg-binary gunicorn whitenoise pytest pytest-django ruff, y uv run python manage.py <comando>. Se decidió en la fase de entorno, al arrancar el proyecto el 19 de octubre de 2026.

49. ¿Qué es pyproject.toml?
Respuesta hablada: Es el archivo donde se declaran las dependencias del proyecto y sus versiones, reemplazando al requirements.txt clásico.
Detalle técnico: Contiene las dependencias con versiones: django 5.2.18, djangorestframework 3.17.x, drf-spectacular 0.30.0, django-filter 26.2, django-cors-headers 4.9.0, django-environ 0.14.0, psycopg[binary] 3.3.6, gunicorn 26.2.0, whitenoise 6.12.0, pytest, pytest-django y ruff 0.17.1.

50. ¿Qué es uv.lock y por qué se commitea?
Respuesta hablada: Es el archivo que fija las versiones exactas resueltas de todas las dependencias, incluyendo las dependencias de las dependencias. Se commitea para que todos instalen exactamente lo mismo.
Detalle técnico: Generado por uv. Al hacer uv sync se respeta uv.lock, evitando sorpresas de versiones distintas entre mi máquina, la de Ema y el servidor.

51. ¿Qué es Docker y qué resuelve en este proyecto?
Respuesta hablada: Docker empaqueta la aplicación y sus dependencias en contenedores para que corran igual en cualquier máquina. Aquí lo usamos sobre todo para la base de datos.
Detalle técnico: Docker Compose v5.6.0 levanta PostgreSQL 17 en un contenedor con volumen persistente. El back se corre localmente con uv y se sirve con gunicorn.

52. ¿Qué es Docker Compose?
Respuesta hablada: Es una herramienta que levanta varios contenedores a la vez con un solo archivo y un solo comando, conectándolos entre sí.
Detalle técnico:
`yaml
services:
  db:
    image: postgres:17
    ports:
      - 5432:5432
`
docker-compose.yml define el servicio de postgres:17 (puerto 5432, variables de usuario, contraseña y base de datos) y opcionalmente el servicio del backend.

53. ¿Por qué PostgreSQL en un contenedor y no instalado en Windows?
Respuesta hablada: Para no instalar nada en Windows ni dejar basura en el registro, y para que Ema y yo tengamos la misma versión de base de datos sin configurar nada a mano.
Detalle técnico: postgres:17 en Docker Compose. settings.py lee las variables de conexión con django-environ (DB_HOST=localhost, DB_PORT=5432, DB_NAME, DB_USER, DB_PASSWORD).

54. ¿Qué es gunicorn y por qué no corre en Windows?
Respuesta hablada: Gunicorn es el servidor que sirve la aplicación Django en producción. No lo usamos en Windows porque está pensado para sistemas tipo Unix; en desarrollo usamos el servidor de Django.
Detalle técnico: gunicorn 26.2.0 instalado. En producción se corre uv run gunicorn config.wsgi. En Windows no es el servidor de desarrollo habitual, aunque puede instalarse con WSL.

55. ¿Qué es pytest y qué es pytest-django?
Respuesta hablada: pytest es el framework de pruebas de Python. pytest-django le agrega soporte para configurar la base de datos de tests y cargar los settings de Django automáticamente.
Detalle técnico: Pruebas en core/tests/. Se corren con uv run pytest. Se prueban serializers, viewsets, permisos y los endpoints @action.

56. ¿Qué es ruff?
Respuesta hablada: Es un linter y formateador de Python muy rápido que revisa que el código siga buenas prácticas y tenga estilo uniforme.
Detalle técnico: ruff 0.17.1. Se corre con uv run ruff check . y uv run ruff format . antes de commitear.

57. ¿Cómo se trabajó con ramas y commits?
Respuesta hablada: Cada funcionalidad se hizo en una rama feature (por ejemplo feature/modelos, feature/api, feature/docker), con commits descriptivos en español, y se fusionó a main con git merge --no-ff para conservar el historial de cada rama.
Detalle técnico: Ramas locales únicamente, sin servidor remoto público; la publicación del proyecto la hace el usuario por su cuenta. Commits tipo: feat: agregar modelos de cervecería, fix: corregir permiso en estadísticas.

58. ¿Cuáles fueron los criterios para recortar alcance?
Respuesta hablada: No agregar nada que no pida la consigna. Por eso no hay módulo de stock aparte, no hay usuario custom, no hay imágenes, no hay JWT, no hay más de 10 modelos ni más de 10 endpoints.
Detalle técnico: Cada corte se justifica en las decisiones de diseño de la defensa: stock como campo numérico, auth.User nativo, sin Pillow o ImageField, TokenAuthentication nativo.

59. ¿Qué fue lo más difícil del proyecto?
Respuesta hablada: Coordinar los dos frentes, back y front, para que los endpoints coincidieran con lo que el front necesita, y configurar Docker con PostgreSQL y CORS para que el front de otro puerto pudiera consumir la API.
Detalle técnico: El ajuste de CORS_ALLOWED_ORIGINS con http://localhost:3000 y el acuerdo del formato de paginación (next, previous, count, results) entre back y front.

60. ¿Qué harías distinto en un próximo proyecto?
Respuesta hablada: Agregar tests desde la primera semana en vez de al final, y definir el contrato de la API con el front antes de escribir los serializers, para evitar rehacer campos.
Detalle técnico: También documentar cada endpoint con ejemplos en drf-spectacular y usar variables de entorno con django-environ desde el inicio para no hardcodear secretos.

### F. Lo que puede preguntar del frontend

61. ¿Cómo se conecta el frontend con el backend?
Respuesta hablada: El front en Next.js, puerto 3000, hace peticiones fetch a http://localhost:8000/api/ y envía el token en el encabezado Authorization de cada llamada que requiera autenticación.
Detalle técnico: CORS configurado en el back para permitir http://localhost:3000. Los endpoints se consumen con fetch y se maneja la respuesta paginada (results, next, previous).

62. ¿Qué es CORS en la práctica para este proyecto?
Respuesta hablada: Es que el back permite explícitamente que el front de localhost:3000 lea las respuestas de la API en localhost:8000, cosa que el navegador bloquearía por defecto.
Detalle técnico: django-cors-headers con CORS_ALLOWED_ORIGINS que incluye http://localhost:3000. El back agrega Access-Control-Allow-Origin a las respuestas.

63. ¿Qué endpoint usa el front para el catálogo de cervezas?
Respuesta hablada: GET /api/cervezas/ para listar todas las cervezas paginadas, y GET /api/cervezas/en_grifo/ para las que están disponibles para servir.
Detalle técnico: Se puede agregar ?page=2, ?estilo=1, ?search=... y ?ordering=... para filtrar y ordenar el catálogo.

64. ¿Cómo maneja el front el token?
Respuesta hablada: El front hace login con POST /api/auth-token/ enviando usuario y contraseña, guarda el token devuelto y lo envía en cada petición como Authorization: Token <key>. Nunca usa cookies de sesión.
Detalle técnico: Debido a la trampa de CSRF y cookies entre puertos (localhost:3000 y localhost:8000 comparten cookies), el token por encabezado es la opción segura y sencilla.

65. ¿Qué formato de paginación espera el front?
Respuesta hablada: Espera un objeto con count, next, previous y results, donde results es la lista de cervezas de esa página.
Detalle técnico: PageNumberPagination con PAGE_SIZE = 10. El front puede pedir ?page=2 o cambiar el tamaño con ?page_size=20, hasta 50.

66. ¿Por qué el backend y el frontend son proyectos separados y qué ventaja tiene?
Respuesta hablada: Porque el back es una API y el front es una aplicación Next.js independiente. Separados se pueden desarrollar en paralelo, desplegar por separado y cambiar uno sin romper el otro.
Detalle técnico: Ema trabaja en Next.js con App Router y Tailwind; yo trabajo en Django y Django REST Framework. Se comunican solo por HTTP y JSON a través de /api/.

## 5. Preguntas trampa

T1. ¿Por qué no usaste JWT en vez del token de DRF?
Respuesta hablada: Porque la consigna pide sesión y tokens, y el token nativo de DRF, authtoken, se configura en una línea. JWT requeriría una biblioteca extra, claves de firma y más código que no nos piden.
Detalle técnico: POST /api/auth-token/ devuelve el token de la tabla authtoken_token. JWT no está instalado ni configurado en el proyecto.

T2. ¿No es mucho 10 modelos para una EFI?
Respuesta hablada: No, porque la consigna pide al menos 10 modelos y al menos 8 endpoints. Diez es el mínimo exacto, no un exceso.
Detalle técnico: Los 10 modelos de core/models.py cumplen la consigna sin agregar entidades que no se piden.

T3. ¿Por qué una sola app en vez de varias?
Respuesta hablada: Porque el mínimo del docente se cumple sin fragmentar el proyecto. Más apps significan más archivos de registro, URLs y configuración sin beneficio para esta entrega.
Detalle técnico: settings.py trae una sola app propia: 'core'. El proyecto se llama config.

T4. ¿El admin de Django no es suficiente como API?
Respuesta hablada: No. El admin es una interfaz para administradores, no una API REST consumible por un frontend. La consigna pide endpoints REST bajo /api/ con ViewSets, y eso es lo que entregamos.
Detalle técnico: /admin/ sirve para gestión interna; /api/cervezas/ y los demás sirven JSON para el front Next.js y para la documentación Swagger.

T5. ¿Por qué no usaste GraphQL?
Respuesta hablada: Porque la consigna pide API REST con ViewSets. GraphQL agregaría una biblioteca nueva, un esquema aparte y un endpoint único que no es lo que se pidió.
Detalle técnico: El proyecto expone recursos REST bajo /api/ con ModelViewSet y DefaultRouter, exactamente como pide la consigna.

T6. ¿El anidado en detail no sería más útil que solo en list?
Respuesta hablada: Para esta entrega no. La consigna pide anidados solo en list, y poner todo anidado al recuperar un solo lote o pedido haría el payload más grande y complejo de lo necesario.
Detalle técnico: get_serializer_class devuelve el serializer anidado solo si self.action == 'list'. En retrieve (GET /api/lotes/1/) se devuelve el serializer plano.

T7. ¿Docker no es overhead para una EFI?
Respuesta hablada: Para la base de datos no, porque PostgreSQL en contenedor nos da la misma base de datos a ambos integrantes sin instalar nada en Windows. El overhead sería instalar y configurar PostgreSQL a mano en cada computadora.
Detalle técnico: docker-compose.yml levanta postgres:17 con volumen persistente. El back se ejecuta con uv y el servidor de desarrollo o gunicorn.

T8. ¿Usaste Django 5.2 y no 6.1, no está viejo?
Respuesta hablada: No, Django 5.2 es LTS, soporte largo, hasta abril 2028, y drf-spectacular 0.30 solo declara compatibilidad hasta Django 6.0. La 5.2 es la opción estable y compatible.
Detalle técnico: Django 5.2.18 LTS. drf-spectacular 0.30.0 soporta hasta Django 6.0 y Django REST Framework 3.17. Python 3.13.

T9. ¿Por qué SQLite no te servía?
Respuesta hablada: Porque SQLite es un archivo local y no representa un servidor de base de datos real. La cervecería necesita PostgreSQL y nosotros lo corremos en Docker para que sea idéntico en todas las máquinas.
Detalle técnico: settings.py usa DATABASES con motor postgresql y psycopg[binary] 3.3.6, conectando al contenedor postgres:17 en el puerto 5432.

T10. ¿El filtro por precio es seguro?
Respuesta hablada: Sí, porque se filtra en el servidor con DjangoFilterBackend y no se ejecuta SQL a mano. El usuario solo envía el valor y el ORM lo compara como número.
Detalle técnico: CervezaViewSet usa django-filter con el campo precio. No hay interpolación de strings en consultas, así que no hay inyección SQL.

## 6. Guion de apertura (2 minutos)

Texto para ensayar de corrido, suena natural, no leído.

Buenas tardes, profesor Lemo. Soy [tu nombre] y con Ema presentamos el proyecto Cervecería Los Flacheros, la evaluación final integradora de Ingeniería de Software. Yo me encargué del cien por ciento del backend en Django y Ema del frontend en Next.js.

El problema que resolvemos es administrar una cervecería artesanal: controlar estilos, cervezas con su stock, lotes de producción y sus etapas de fermentación, proveedores, materias primas, clientes, pedidos con sus líneas y las opiniones de los clientes.

La solución es una API REST con Django 5.2 LTS y Django REST Framework. Diez modelos, todos en una sola app llamada core, y diez endpoints bajo /api/, todos con ModelViewSet y router. Hay autenticación por sesión y por token, documentación automática con Swagger y ReDoc, paginación, filtros y búsquedas, y un panel de administración completo.

Algunas decisiones que tomamos a propósito: usamos exactamente diez modelos y diez endpoints porque la consigna lo pide y no queremos agregar código de más. El stock es un campo numérico en la cerveza y en la materia prima, sin una entidad aparte. Usamos el usuario de Django sin customizar, no usamos imágenes, y el token es el nativo de DRF porque la consigna pide sesión y tokens y eso se configura en una línea.

El proyecto está dockerizado con PostgreSQL 17, usa uv para manejar dependencias, gunicorn para servir y whitenoise para estáticos. Trabajamos con ramas feature, commits en español y fusiones a main sin fast-forward.

El backend está listo para defender. Gracias, quedo a disposición de sus preguntas.

## 7. Cierre y preguntas del público

Tres frases de cierre:

1. Eso es todo lo que tiene el backend de Cervecería Los Flacheros. Gracias por su atención.
2. Quedo a disposición para cualquier pregunta sobre la API, el admin o las decisiones que tomamos.
3. Si quieren, podemos recorrer algún endpoint en vivo en Swagger o en el panel de administración.

Qué hacer si no sabés algo: no inventes. Decí algo como: eso no lo implementé porque la consigna no lo pedía y preferimos no agregar código de más, pero si tuviera que hacerlo usaría X. Ejemplo concreto: si te preguntan por JWT y no lo usaste, decí: no usé JWT porque la consigna pide sesión y tokens, y el authtoken de DRF se configura en una línea. Si el proyecto creciera, migraría a JWT con una biblioteca dedicada.

## 8. Plan de repaso (3 días previos)

Domingo 1 de noviembre (entrega):
- Leer la ficha de 60 segundos y memorizarla.
- Leer el guion de apertura y ensayarlo dos veces en voz alta.
- Revisar las 17 consignas y cómo se demuestra cada una (sección 3).
- Levantar el proyecto localmente y probar: uv run python manage.py migrate, uv run python manage.py runserver, /api/, /api/schema/swagger-ui/, /admin/.

Lunes 2 de noviembre (día previo a la defensa):
- Repasar solo las preguntas trampa (sección 5) y sus respuestas.
- Ensayar el guion de apertura una vez más.
- Verificar que los 10 modelos y los 10 endpoints respondan en la API.
- Revisar el diagrama ER y el README con capturas para mencionarlos si se pide.

Martes 3 de noviembre (defensa):
- Llevar este cuaderno impreso o en el celular.
- Llevar la laptop con el proyecto levantado para mostrar en vivo si se pide.
- Responder con la respuesta hablada corta primero; usar el detalle técnico solo si el profesor pide más precisión.
- Si no sabés algo, usar la frase de cierre: no lo implementé porque X, pero es lo que haría.
