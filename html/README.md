# VETA · Aplicación web

Aplicación responsive para controlar inversiones inmobiliarias mes a mes. Está construida con Next.js, React, Supabase y Recharts, y preparada para desplegarse en Vercel.

## Qué registra

Cada proyecto conserva los supuestos originales de compra y financiamiento. Luego, para cada mes, permite ingresar por separado:

- arriendo efectivamente cobrado;
- dividendo pagado;
- días de vacancia;
- comisión de administración;
- gastos comunes;
- contribuciones;
- seguro;
- mantención regular;
- arreglos extraordinarios;
- otros gastos y notas.

El tablero calcula el flujo real, el flujo estimado, la diferencia, el desembolso de bolsillo y los acumulados. También incluye una proyección anual y exportación CSV compatible con Google Sheets.

La vista **Real y socios** permite compartir el proyecto con otra cuenta, definir porcentajes de participación y distribuir cada movimiento con montos exactos. Cada movimiento guarda el valor UF de su fecha, por lo que los aportes también se pueden comparar en UF y en pesos equivalentes de hoy.

El valor actual distingue tres referencias:

- valor de compra reajustado por la UF actual;
- estimación del motor en UF, aplicando la plusvalía configurada;
- valor de mercado manual, para usar una tasación o comparables cuando existan.

La UF se consulta desde `mindicador.cl` y siempre queda editable como respaldo.

La compra también separa el pie contractual, el bono pie de la inmobiliaria, el efectivo pagado al comprar y una eventual devolución de IVA con estado y fecha. El escenario tributario permite indicar si la vivienda está acogida a DFL2, su superficie construida, el tipo de titular y su orden por fecha de adquisición. Para inmuebles no exentos se puede usar una tasa efectiva estimada o evaluar el régimen opcional DFL2 del 5% que comienza en 2027.

> Estos campos sirven para comparar escenarios y caja real; no reemplazan una revisión tributaria. La devolución de IVA del artículo 27 bis no es automática y puede ser incompatible con operaciones de arriendo exentas de IVA.

## 1. Configurar Supabase

1. Abre el SQL Editor del proyecto de Supabase.
2. Ejecuta completo [`supabase/schema.sql`](supabase/schema.sql). El script crea tablas, índices y políticas RLS para que sólo el propietario y los participantes invitados puedan acceder a cada inversión.
3. En **Authentication → URL Configuration**, agrega la URL de producción de Vercel como `Site URL` y como redirect permitido. Para desarrollo agrega `http://localhost:3000/**`.
4. En **Authentication → Email Templates → Confirm signup**, usa una URL de confirmación compatible con SSR:

   ```text
   {{ .SiteURL }}/auth/confirm?token_hash={{ .TokenHash }}&type=email
   ```

La aplicación usa la clave pública de Supabase y RLS; no necesita ni expone una clave secreta o `service_role`.

## 2. Variables de entorno

Copia `.env.example` como `.env.local` y reemplaza los valores:

```env
NEXT_PUBLIC_SUPABASE_URL=https://TU-PROYECTO.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=sb_publishable_TU_CLAVE_PUBLICA
```

Sin estas variables la app funciona en modo local y guarda los datos sólo en el navegador. Con las variables configuradas exige inicio de sesión y sincroniza en Supabase.

## 3. Ejecutar localmente

```bash
npm install
npm run dev
```

Abre `http://localhost:3000`.

Verificaciones disponibles:

```bash
npm run typecheck
npm run lint
npm test
npm run build
```

## 4. Desplegar en Vercel

1. Importa el repositorio de GitHub en Vercel.
2. Define `html` como **Root Directory**.
3. Agrega las dos variables de Supabase a Production y Preview.
4. Despliega y copia la URL final a la configuración de Auth de Supabase.
5. Ejecuta un nuevo despliegue después de cambiar variables de entorno.

Los siguientes commits se desplegarán automáticamente desde GitHub.

## Uso desde el teléfono

La interfaz se adapta a pantallas pequeñas y declara un Web App Manifest. Desde el navegador móvil se puede usar **Agregar a pantalla de inicio** para abrir VETA como una aplicación independiente.

## Google Sheets

Supabase es la fuente de datos principal. El botón **Exportar** genera un CSV con el detalle mensual, listo para importar en Google Sheets. Esto evita usar una hoja como base de datos transaccional y conserva Sheets para análisis, conciliación o reportes compartidos.

## Estructura principal

```text
app/                       páginas, autenticación y API
components/investment/     interfaz de seguimiento
lib/investment.ts          cálculos y proyecciones
lib/supabase/              clientes SSR y sesión
supabase/schema.sql        tablas y políticas RLS
public/manifest.webmanifest
```
