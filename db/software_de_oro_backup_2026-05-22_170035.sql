--
-- PostgreSQL database dump
--

\restrict 7dhnipAUeOD2jeHEeo0eEuSitJFfepVnYAeJtJ7mTGSQAqNchjO6DkblEygH0Sc

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY public.stripe_checkout DROP CONSTRAINT IF EXISTS stripe_checkout_pkey;
ALTER TABLE IF EXISTS ONLY public.orden_personalizada_precio DROP CONSTRAINT IF EXISTS orden_personalizada_precio_pkey;
ALTER TABLE IF EXISTS ONLY public.orden_personalizada DROP CONSTRAINT IF EXISTS orden_personalizada_pkey;
ALTER TABLE IF EXISTS ONLY public.categoria_producto DROP CONSTRAINT IF EXISTS categoria_producto_pkey;
ALTER TABLE IF EXISTS ONLY public.carrito_usuario DROP CONSTRAINT IF EXISTS carrito_usuario_pkey;
ALTER TABLE IF EXISTS public.orden_personalizada ALTER COLUMN id_orden_personalizada DROP DEFAULT;
ALTER TABLE IF EXISTS public.categoria_producto ALTER COLUMN id_categoria DROP DEFAULT;
DROP TABLE IF EXISTS public.usuarios;
DROP TABLE IF EXISTS public.stripe_checkout;
DROP TABLE IF EXISTS public.registros;
DROP TABLE IF EXISTS public.promociones;
DROP TABLE IF EXISTS public.producto;
DROP TABLE IF EXISTS public.pedidos;
DROP TABLE IF EXISTS public.pagos;
DROP TABLE IF EXISTS public.orden_personalizada_precio;
DROP SEQUENCE IF EXISTS public.orden_personalizada_id_orden_personalizada_seq;
DROP TABLE IF EXISTS public.orden_personalizada;
DROP TABLE IF EXISTS public.detalle_pedido;
DROP SEQUENCE IF EXISTS public.categoria_producto_id_categoria_seq;
DROP TABLE IF EXISTS public.categoria_producto;
DROP TABLE IF EXISTS public.carrito_usuario;
-- *not* dropping schema, since initdb creates it
--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

-- *not* creating schema, since initdb creates it


--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA public IS '';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: carrito_usuario; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.carrito_usuario (
    email text NOT NULL,
    carrito_json text DEFAULT '[]'::text NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: categoria_producto; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.categoria_producto (
    id_categoria bigint NOT NULL,
    nombre_categoria text,
    descripcion text
);


--
-- Name: categoria_producto_id_categoria_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.categoria_producto_id_categoria_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: categoria_producto_id_categoria_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.categoria_producto_id_categoria_seq OWNED BY public.categoria_producto.id_categoria;


--
-- Name: detalle_pedido; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.detalle_pedido (
    id_detalle bigint,
    id_pedido bigint,
    id_producto bigint,
    cantidad bigint,
    subtotal double precision,
    talla text
);


--
-- Name: orden_personalizada; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.orden_personalizada (
    id_orden_personalizada bigint NOT NULL,
    usuario_email text,
    cliente_nombre text,
    cliente_correo text,
    cliente_telefono text,
    cliente_direccion text,
    rango text,
    fecha_contingencia text,
    identidad text,
    producto text,
    tecnica text,
    color text,
    estampado text,
    talla text,
    modelo_rh text,
    modelo_presilla text,
    precio numeric(12,2) DEFAULT 0 NOT NULL,
    estado text DEFAULT 'pendiente'::text NOT NULL,
    datos_json text DEFAULT '{}'::text NOT NULL,
    fecha_creacion timestamp with time zone DEFAULT now() NOT NULL,
    cantidad integer DEFAULT 1,
    imagen_url text
);


--
-- Name: orden_personalizada_id_orden_personalizada_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.orden_personalizada_id_orden_personalizada_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: orden_personalizada_id_orden_personalizada_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.orden_personalizada_id_orden_personalizada_seq OWNED BY public.orden_personalizada.id_orden_personalizada;


--
-- Name: orden_personalizada_precio; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.orden_personalizada_precio (
    producto text NOT NULL,
    nombre text NOT NULL,
    precio numeric(12,2) DEFAULT 0 NOT NULL
);


--
-- Name: pagos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pagos (
    id_pago bigint,
    id_pedido bigint,
    monto double precision,
    metodo_pago text,
    fecha_pago text,
    estado_pago text,
    id_promo text,
    codigo_promo text,
    tipo_descuento text,
    valor_descuento double precision,
    monto_descuento double precision,
    comprobante_url text
);


--
-- Name: pedidos; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pedidos (
    id_pedido bigint,
    id_usuario text,
    fecha_pedido text,
    estado text,
    cliente_telefono text,
    cliente_direccion text
);


--
-- Name: producto; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.producto (
    id_producto bigint,
    nombre text,
    descripcion text,
    precio double precision,
    stock bigint,
    id_categoria bigint,
    fuerza text,
    intendencia text,
    imagen_url text,
    eliminado boolean,
    destacado_dashboard boolean DEFAULT false
);


--
-- Name: promociones; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.promociones (
    id_promo bigint,
    nombre text,
    descripcion text,
    tipo_descuento text,
    valor_descuento double precision,
    id_producto bigint,
    codigo text,
    fecha_inicio text,
    fecha_fin text,
    activo boolean
);


--
-- Name: registros; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.registros (
    id_registro bigint,
    id_usuario text,
    accion text,
    fecha_accion text
);


--
-- Name: stripe_checkout; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.stripe_checkout (
    session_id text NOT NULL,
    usuario_email text NOT NULL,
    codigo_promo text DEFAULT ''::text NOT NULL,
    cart_hash text DEFAULT ''::text NOT NULL,
    total_esperado numeric(12,2) DEFAULT 0 NOT NULL,
    estado text DEFAULT 'creado'::text NOT NULL,
    id_pedido bigint,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    carrito_json text DEFAULT '[]'::text NOT NULL
);


--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.usuarios (
    id_usuario bigint,
    nombre text,
    email text,
    password_hash text,
    rol text,
    estado text,
    fecha_registro text,
    email_verified boolean,
    verification_code text,
    verification_code_expiry text,
    reset_token text,
    reset_token_expiry text,
    password_change_code text,
    password_change_code_expiry timestamp with time zone,
    telefono text,
    direccion text,
    terminos_identidad_aceptados boolean DEFAULT false NOT NULL,
    terminos_identidad_fecha timestamp with time zone
);


--
-- Name: categoria_producto id_categoria; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categoria_producto ALTER COLUMN id_categoria SET DEFAULT nextval('public.categoria_producto_id_categoria_seq'::regclass);


--
-- Name: orden_personalizada id_orden_personalizada; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orden_personalizada ALTER COLUMN id_orden_personalizada SET DEFAULT nextval('public.orden_personalizada_id_orden_personalizada_seq'::regclass);


--
-- Data for Name: carrito_usuario; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.carrito_usuario (email, carrito_json, updated_at) FROM stdin;
prueba.carrito@demo.local	[{"id_producto": 101, "nombre": "Prueba", "cantidad": 2, "precio": 15000.0, "subtotal": 30000.0}]	2026-04-07 13:46:43.954571-05
demo.logout@local.test	[{"cantidad": 3, "id_producto": 7, "nombre": "Demo", "precio": 2000.0, "subtotal": 6000.0}]	2026-04-07 13:47:46.466646-05
persistencia.test@local.test	[{"cantidad": 2, "id_producto": 1, "nombre": "Item A", "precio": 10000.0, "subtotal": 20000.0}]	2026-04-07 14:00:29.504371-05
img.test@local.test	[{"cantidad": 1, "id_producto": 1, "nombre": "Producto test", "precio": 10000.0, "subtotal": 10000.0, "imagen_url": "img/Empresa/producto_1.jpg", "descripcion": "Damn"}]	2026-04-07 14:25:41.012404-05
img2.test@local.test	[{"cantidad": 1, "id_producto": 1, "nombre": "X", "precio": 12000.0, "subtotal": 12000.0, "imagen_url": "img/Empresa/producto_1.jpg", "descripcion": "Damn"}]	2026-04-07 15:12:59.000695-05
julio@gmail.com	[{"cantidad": 1, "descripcion": "Prenda superior del uniforme. Se caracteriza por su diseño estructurado, funcional y representativo, pensado para brindar una apariencia formal y profesional.", "id_producto": 17, "imagen_url": "img/catalogo/policia/guerrera_policia.png", "monto_descuento": 100000.0, "nombre": "Guerrera", "precio": 160000.0, "promo_codigo": "", "promo_fecha_fin": "2026-05-16", "promo_id": 5, "promo_nombre": "gerrera", "promo_tipo_descuento": "valor_fijo", "promo_valor_descuento": 100000.0, "subtotal": 60000.0, "subtotal_bruto": 160000.0, "talla": "M"}]	2026-05-22 14:14:52.108078-05
julio11916@gmail.com	[{"cantidad": 1, "descripcion": "Camiseta manga larga cómoda y resistente. Ideal para climas frescos y actividades diarias.", "id_producto": 11, "imagen_url": "img/Empresa/producto_11.jpg", "nombre": "Camiseta unisex manga larga sin estampado color negro", "precio": 80000.0, "subtotal": 80000.0, "talla": "XS"}]	2026-04-29 15:55:25.578723-05
\.


--
-- Data for Name: categoria_producto; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.categoria_producto (id_categoria, nombre_categoria, descripcion) FROM stdin;
1	Policia - Busos	Intendencia Policia: Busos
2	Policia - Camibusos	Intendencia Policia: Camibusos
3	Policia - Gorras	Intendencia Policia: Gorras
4	Policia - Panoletas	Intendencia Policia: Panoletas
5	Policia - Sudaderas	Intendencia Policia: Sudaderas
6	Policia - Pantalonetas	Intendencia Policia: Pantalonetas
7	Policia - Colchas	Intendencia Policia: Colchas
8	Policia - Tendidos	Intendencia Policia: Tendidos
9	Policia - Chuspas para ropa sucia	Intendencia Policia: Chuspas para ropa sucia
10	Policia - Fundas para almohadas	Intendencia Policia: Fundas para almohadas
11	Policia - Camuflados	Intendencia Policia: Camuflados
12	Ejercito - Busos	Intendencia Ejercito: Busos
13	Ejercito - Camibusos	Intendencia Ejercito: Camibusos
14	Ejercito - Gorras	Intendencia Ejercito: Gorras
15	Ejercito - Panoletas	Intendencia Ejercito: Panoletas
16	Ejercito - Sudaderas	Intendencia Ejercito: Sudaderas
17	Ejercito - Pantalonetas	Intendencia Ejercito: Pantalonetas
18	Ejercito - Colchas	Intendencia Ejercito: Colchas
19	Ejercito - Tendidos	Intendencia Ejercito: Tendidos
20	Ejercito - Chuspas para ropa sucia	Intendencia Ejercito: Chuspas para ropa sucia
21	Ejercito - Fundas para almohadas	Intendencia Ejercito: Fundas para almohadas
22	Ejercito - Camuflados	Intendencia Ejercito: Camuflados
23	Armada - Busos	Intendencia Armada: Busos
24	Armada - Camibusos	Intendencia Armada: Camibusos
25	Armada - Gorras	Intendencia Armada: Gorras
26	Armada - Panoletas	Intendencia Armada: Panoletas
27	Armada - Sudaderas	Intendencia Armada: Sudaderas
28	Armada - Pantalonetas	Intendencia Armada: Pantalonetas
29	Armada - Colchas	Intendencia Armada: Colchas
30	Armada - Tendidos	Intendencia Armada: Tendidos
31	Armada - Chuspas para ropa sucia	Intendencia Armada: Chuspas para ropa sucia
32	Armada - Fundas para almohadas	Intendencia Armada: Fundas para almohadas
33	Armada - Camuflados	Intendencia Armada: Camuflados
34	Gaula - Busos	Intendencia Gaula: Busos
35	Gaula - Camibusos	Intendencia Gaula: Camibusos
36	Gaula - Gorras	Intendencia Gaula: Gorras
37	Gaula - Panoletas	Intendencia Gaula: Panoletas
38	Gaula - Sudaderas	Intendencia Gaula: Sudaderas
39	Gaula - Pantalonetas	Intendencia Gaula: Pantalonetas
40	Gaula - Colchas	Intendencia Gaula: Colchas
41	Gaula - Tendidos	Intendencia Gaula: Tendidos
42	Gaula - Chuspas para ropa sucia	Intendencia Gaula: Chuspas para ropa sucia
43	Gaula - Fundas para almohadas	Intendencia Gaula: Fundas para almohadas
44	Gaula - Camuflados	Intendencia Gaula: Camuflados
\.


--
-- Data for Name: detalle_pedido; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.detalle_pedido (id_detalle, id_pedido, id_producto, cantidad, subtotal, talla) FROM stdin;
41	35	3	1	50000	
42	36	3	1	50000	
43	37	3	1	50000	
44	38	3	1	50000	
45	39	4	1	50000	
46	39	5	1	50000	
47	39	6	1	50000	
48	39	3	1	100000	
49	40	4	1	50000	
61	54	13	1	160000	XS
62	55	4	1	50000	XL
50	41	4	1	50000	
51	44	3	1	100000	
59	52	4	1	50000	S
60	53	4	1	50000	S
52	45	11	1	80000	XS
53	46	19	1	10000	XS
54	47	19	1	10000	XS
55	48	11	1	80000	M
56	49	11	1	80000	XXXL
57	50	13	1	160000	M
58	51	13	1	160000	XS
1	14	13	1	160	
2	15	19	1	10000	
3	16	19	1	10000	
4	17	19	1	10000	
5	18	19	1	10000	
6	19	19	1	10000	
7	20	19	1	10000	
8	21	19	1	10000	
9	22	19	1	10000	
10	23	19	1	10000	
11	24	9	1	50000	
12	24	10	1	50000	
13	24	12	1	80000	
14	24	17	1	160000	
15	24	18	1	180000	
16	24	19	1	10000	
17	24	20	1	60000	
18	25	9	1	50000	
19	25	10	1	50000	
20	25	12	1	80000	
21	25	17	1	160000	
22	25	18	1	180000	
23	25	19	1	10000	
24	25	20	1	60000	
25	25	3	1	50000	
26	25	4	1	50000	
27	25	5	1	50000	
28	25	6	1	50000	
29	25	7	1	120000	
30	25	8	1	160000	
31	25	11	1	80000	
32	26	20	1	60000	
33	27	11	1	80000	
34	28	12	1	80000	
35	29	12	2	160000	
36	30	12	1	80000	
37	31	3	1	50000	
38	32	3	1	50000	
39	33	3	1	50000	
40	34	3	1	50000	
63	56	4	1	50000	S
64	57	4	1	50000	S
65	58	0	1	12000	L
66	59	12	1	80000	L
67	60	12	1	80000	XS
68	61	3	2	200000	XS
\.


--
-- Data for Name: orden_personalizada; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.orden_personalizada (id_orden_personalizada, usuario_email, cliente_nombre, cliente_correo, cliente_telefono, cliente_direccion, rango, fecha_contingencia, identidad, producto, tecnica, color, estampado, talla, modelo_rh, modelo_presilla, precio, estado, datos_json, fecha_creacion, cantidad, imagen_url) FROM stdin;
1	julio@gmail.com	julio cesar	julio@gmail.com	3219047309	diagonal7	drago	2026-05-13	Policia	guerrera	Bordado	Azul Noche	Escudos	L			160000.00	cancelada	{"cliente": {"nombre": "julio cesar", "rango": "drago", "direccion": "diagonal7", "correo": "julio@gmail.com", "telefono": "3219047309", "fecha_contingencia": "2026-05-13"}, "detalle": {"identidad": "Policia", "producto": "guerrera", "producto_label": "Guerrera", "tecnica": "Bordado", "color": "Azul Noche", "estampado": "Escudos", "talla": "L", "modelo_rh": "", "modelo_presilla": "", "cantidad": 1, "precio_unitario": 160000, "precio_total": 160000, "imagen_url": "/static/img/prendas/Policia/guerrera/guerrera_policia.png", "vista_prenda": "delantera"}}	2026-05-13 13:19:22.683328-05	1	/static/img/prendas/Policia/guerrera/guerrera_policia.png
\.


--
-- Data for Name: orden_personalizada_precio; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.orden_personalizada_precio (producto, nombre, precio) FROM stdin;
guerrera	Guerrera	160000.00
buso_tactico	Buso tactico	95000.00
buso tactico	Buso tactico	95000.00
gorra	Gorra	35000.00
paoleta	Panoleta	28000.00
panoleta	Panoleta	28000.00
pañoleta	Panoleta	28000.00
buso-manga-larga	Buso manga larga	85000.00
presillas	Presillas	15000.00
rh	RH	12000.00
gafete del nombre o apellido	Gafete de nombre o apellido	12000.00
buso	Buso	50000.00
paÃ±oleta	PaÃ±oleta	28000.00
escudos	Escudos	0.00
parches	Parches	0.00
\.


--
-- Data for Name: pagos; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.pagos (id_pago, id_pedido, monto, metodo_pago, fecha_pago, estado_pago, id_promo, codigo_promo, tipo_descuento, valor_descuento, monto_descuento, comprobante_url) FROM stdin;
24	24	590000	transferencia	2026-03-25 17:54:38	aprobado				0	0	
25	25	1150000	tarjeta	2026-03-25 18:05:47	aprobado	1		porcentaje	50	50000	
26	26	60000	tarjeta	2026-03-25 18:34:52	aprobado				0	0	
27	27	80000	tarjeta	2026-03-25 18:49:29	aprobado				0	0	
28	28	80000	tarjeta	2026-03-25 18:56:24	aprobado				0	0	
48	50	160000	tarjeta	2026-04-16 16:30:04	aprobado				0	0	
49	51	160000	tarjeta	2026-04-16 17:42:38	aprobado				0	0	
29	29	160000	efectivo	2026-03-25 19:05:41	aprobado				0	0	
30	30	80000	efectivo	2026-03-25 19:10:26	aprobado				0	0	
31	31	50000	qr	2026-03-25 19:23:24	aprobado	1		porcentaje	50	50000	
32	32	50000	qr	2026-03-25 19:33:14	aprobado	1		porcentaje	50	50000	
33	33	50000	qr	2026-03-25 19:35:47	aprobado	1		porcentaje	50	50000	
34	34	50000	qr	2026-03-25 19:40:22	aprobado	1		porcentaje	50	50000	
35	35	50000	qr	2026-03-25 19:56:07	aprobado	1		porcentaje	50	50000	
40	40	50000	transferencia	2026-04-08 14:45:29	aprobado				0	0	
41	41	50000	transferencia	2026-04-08 14:46:15	aprobado				0	0	
52	54	160000	tarjeta	2026-04-16 18:50:57	aprobado				0	0	
53	55	50000	transferencia	2026-04-16 20:30:58	aprobado				0	0	
54	56	50000	transferencia	2026-04-22 16:38:40	aprobado				0	0	
42	44	100000	transferencia	2026-04-08 17:11:59	aprobado				0	0	
43	45	80000	qr	2026-04-08 18:06:49	aprobado				0	0	
5	5	120	tarjeta	2026-03-04 19:42:40	aprobado	\N			0	0	
6	6	60	tarjeta	2026-03-04 19:48:18	aprobado	\N			0	0	
7	7	60	tarjeta	2026-03-04 19:49:00	aprobado	\N			0	0	
8	8	60	tarjeta	2026-03-04 19:55:08	aprobado	\N			0	0	
9	9	60	tarjeta	2026-03-04 20:02:08	aprobado	\N			0	0	
10	10	60	transferencia	2026-03-04 20:02:37	aprobado	\N			0	0	
11	11	60	tarjeta	2026-03-04 20:05:34	aprobado	\N			0	0	
12	12	60	tarjeta	2026-03-04 20:06:17	aprobado	\N			0	0	
13	13	200	tarjeta	2026-03-06 14:02:06	aprobado	\N			0	0	
14	14	160	tarjeta	2026-03-18 14:31:15	aprobado				0	0	
15	15	10000	transferencia	2026-03-25 15:12:42	aprobado				0	0	
16	16	10000	tarjeta	2026-03-25 15:46:55	aprobado				0	0	
17	17	10000	transferencia	2026-03-25 15:47:56	aprobado				0	0	
18	18	10000	tarjeta	2026-03-25 16:19:50	aprobado				0	0	
19	19	10000	qr	2026-03-25 16:28:10	aprobado				0	0	
20	20	10000	transferencia	2026-03-25 16:43:35	aprobado				0	0	
21	21	10000	efectivo	2026-03-25 17:08:48	aprobado				0	0	
22	22	10000	qr	2026-03-25 17:17:22	aprobado				0	0	
23	23	10000	tarjeta	2026-03-25 17:30:05	aprobado				0	0	
50	52	50000	transferencia	2026-04-16 18:20:23	aprobado				0	0	
51	53	50000	tarjeta	2026-04-16 18:45:10	aprobado				0	0	
36	36	50000	qr	2026-03-25 20:29:37	aprobado	1		porcentaje	50	50000	
46	48	80000	transferencia	2026-04-09 00:27:50	aprobado				0	0	
47	49	80000	tarjeta	2026-04-09 00:44:04	aprobado				0	0	
37	37	50000	efectivo	2026-03-27 14:14:32	aprobado	1		porcentaje	50	50000	
44	46	10000	tarjeta	2026-04-08 21:47:43	aprobado				0	0	
45	47	10000	tarjeta	2026-04-08 21:54:31	aprobado				0	0	
38	38	50000	transferencia	2026-03-27 16:51:25	aprobado	1		porcentaje	50	50000	
39	39	250000	transferencia	2026-04-08 14:36:43	aprobado				0	0	
55	57	50000	transferencia	2026-04-29 15:22:40	aprobado				0	0	img/comprobantes/comprobante_pedido_57_20260429_152240_517277.png
56	58	12000	tarjeta	2026-05-01 13:36:20	aprobado				0	0	
57	59	80000	transferencia	2026-05-11 14:01:51	aprobado				0	0	img/comprobantes/comprobante_pedido_59_20260511_140151_586201.png
58	60	80000	tarjeta	2026-05-12 13:16:55	aprobado				0	0	
59	61	200000	efectivo	2026-05-15 14:35:14	aprobado				0	0	\N
\.


--
-- Data for Name: pedidos; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.pedidos (id_pedido, id_usuario, fecha_pedido, estado, cliente_telefono, cliente_direccion) FROM stdin;
30	nico@gmail.com	2026-03-25 19:10:26	completado		
31	nico@gmail.com	2026-03-25 19:23:24	completado		
32	nico@gmail.com	2026-03-25 19:33:13	completado		
33	nico@gmail.com	2026-03-25 19:35:47	completado		
34	nico@gmail.com	2026-03-25 19:40:22	completado		
35	nico@gmail.com	2026-03-25 19:56:06	completado		
36	nico@gmail.com	2026-03-25 20:29:37	completado		
37	nico@gmail.com	2026-03-27 14:14:32	completado		
38	nico@gmail.com	2026-03-27 16:51:25	completado		
58	2	2026-05-01 13:36:20	confirmado	3135264367	adsfgvzsd<ge<
59	2	2026-05-11 14:01:51	confirmado	3135264367	adsfgvzsd<ge<
60	nico@gmail.com	2026-05-12 13:16:55	completado		
39	12	2026-04-08 14:36:43	pendiente		
40	12	2026-04-08 14:45:29	pendiente		
41	12	2026-04-08 14:46:15	empaquetado		
42	nico@gmail.com	2026-04-08 16:20:10	completado		
43	nico@gmail.com	2026-04-08 16:48:08	completado		
57	2	2026-04-29 15:22:40	enviado	3204567896	adsafasasa
44	nico@gmail.com	2026-04-08 17:11:59	completado		
45	nico@gmail.com	2026-04-08 18:06:49	completado		
46	nico@gmail.com	2026-04-08 21:47:43	completado		
47	nico@gmail.com	2026-04-08 21:54:31	completado		
48	2	2026-04-09 00:27:50	pendiente		
56	2	2026-04-22 16:38:40	enviado	3204567896	kjhgliuguykftrc
49	2	2026-04-09 00:44:04	pendiente		
50	2	2026-04-16 16:30:03	empaquetado		
51	nico@gmail.com	2026-04-16 17:42:38	completado		
52	2	2026-04-16 18:20:23	entregado		
53	2	2026-04-16 18:45:10	entregado		
54	nico@gmail.com	2026-04-16 18:50:57	completado		
55	2	2026-04-16 20:30:58	entregado	3204567896	kjhgliuguykftrc
5	8	2026-03-04 19:42:40	entregado		
6	8	2026-03-04 19:48:18	pendiente		
7	8	2026-03-04 19:49:00	pendiente		
8	8	2026-03-04 19:55:08	pendiente		
9	8	2026-03-04 20:02:08	pendiente		
10	8	2026-03-04 20:02:37	pendiente		
11	8	2026-03-04 20:05:34	pendiente		
12	8	2026-03-04 20:06:17	pendiente		
13	2	2026-03-06 14:02:06	pendiente		
14	2	2026-03-18 14:31:15	pendiente		
15	nico@gmail.com	2026-03-25 15:12:42	completado		
16	nico@gmail.com	2026-03-25 15:46:55	completado		
17	nico@gmail.com	2026-03-25 15:47:56	completado		
18	nico@gmail.com	2026-03-25 16:19:50	completado		
19	nico@gmail.com	2026-03-25 16:28:10	completado		
20	nico@gmail.com	2026-03-25 16:43:35	completado		
21	nico@gmail.com	2026-03-25 17:08:48	completado		
22	nico@gmail.com	2026-03-25 17:17:22	completado		
23	nico@gmail.com	2026-03-25 17:30:04	completado		
24	nico@gmail.com	2026-03-25 17:54:38	completado		
25	nico@gmail.com	2026-03-25 18:05:47	completado		
26	nico@gmail.com	2026-03-25 18:34:52	completado		
27	nico@gmail.com	2026-03-25 18:49:29	completado		
28	nico@gmail.com	2026-03-25 18:56:24	completado		
29	nico@gmail.com	2026-03-25 19:05:41	completado		
61	nico@gmail.com	2026-05-15 14:35:14	completado		
\.


--
-- Data for Name: producto; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.producto (id_producto, nombre, descripcion, precio, stock, id_categoria, fuerza, intendencia, imagen_url, eliminado, destacado_dashboard) FROM stdin;
59	sudadera 	xxxxxxxx	65000	10	1	Armada	Sudaderas	img/catalogo/armada/uniforme_descanso_armada1.png	f	f
60	buso de descanso	xxxxxxxx	50000	10	1	Gaula	Busos	img/catalogo/gaula/buso_descanso_gaula.png	f	f
61	pantaloneta	xxxxxxxx	70000	10	1	Gaula	Pantalonetas	img/catalogo/gaula/pantaloneta_descanso_gaula.png	f	f
41	buso táctico para la policía color negro	xxxxxxxx	95000	10	1	Policia	Camibusos	img/catalogo/policia/buso_tactico_color_negro.png	f	f
42	buso táctico para la policía color verde	xxxxxxxx	95000	10	1	Policia	Camibusos	img/catalogo/policia/buso_tactico_color_verde.png	f	f
43	gerrera	xxxxxxxx	160000	10	1	Policia	Camuflados	img/catalogo/policia/gerrera_verde_policia.png	f	f
44	Pantalón	xxxxxxxx	120000	10	1	Policia	Camuflados	img/catalogo/policia/pantalon_verde_policia.png	f	f
45	buso táctico para el ejecito color verde	xxxxxxxx	95000	10	1	Ejercito	Camibusos	img/catalogo/ejercito/buso_táctico_ejercito_color_verde.png	f	f
47	buso táctico para el ejecito sin camuflado	xxxxxxxx	95000	10	1	Ejercito	Camibusos	img/catalogo/ejercito/buso_táctico_ejercito_sin_camuflado.png	f	f
48	chaqueta 	xxxxxxxx	80000	10	1	Armada	Sudaderas	img/catalogo/armada/uniforme_descanso_armada_color_negro.png	f	f
49	sudadera 	xxxxxxxx	65000	10	1	Armada	Sudaderas	img/catalogo/armada/uniforme_descanso_armada_color_negro2.png	f	f
50	chaqueta 	xxxxxxxx	80000	10	1	Gaula	Sudaderas	img/catalogo/gaula/uniforme_descanso_gaula_pixelado1.png	f	f
51	sudadera 	xxxxxxxx	65000	10	1	Gaula	Sudaderas	img/catalogo/gaula/uniforme_descanso_gaula_pixelado.png	f	f
52	chaqueta 	xxxxxxxx	80000	10	1	Gaula	Sudaderas	img/catalogo/gaula/uniforme_descanso_gaula.png	f	f
53	sudadera 	xxxxxxxx	65000	10	1	Gaula	Sudaderas	img/catalogo/gaula/uniforme_descanso_gaula1.png	f	f
46	buso táctico para el ejecito color verde oscuro	xxxxxxxx	95000	10	1	Ejercito	Camibusos	img/catalogo/ejercito/buso_táctico_ejercito_color_verde2.png	f	f
27	Gorra Beisbolera policia azul	xxxxxxxx	35000	10	1	Policia	Gorras	img/catalogo/policia/gorra_azul.png	f	f
30	Gorra Beisbolera 	xxxxxxxx	35000	10	1	Accesorios	Gorras	img/catalogo/accesorios/Gorra negra.png	f	f
28	Gorra Beisbolera policia	xxxxxxxx	35000	10	1	Policia	Gorras	img/catalogo/policia/gorra_estandar.png	f	f
29	Gorra Beisbolera policía verde 	xxxxxxxx	35000	10	1	Policia	Gorras	img/catalogo/policia/gorra_verde.png	f	f
21	Camiseta unisex sin estampado color verde	xxxxxxxx	50000	10	1	Variado	Busos		t	f
22	Camiseta unisex sin estampado color beige claro	xxxxxxxx	50000	10	1	Variado	Busos		t	f
3	Camiseta unisex con camuflado	Diseñada para brindar comodidad y estilo en cualquier ocasión. Disponible en versiones con camuflado, que incluyen diseños representativos y gráficos alusivos a la institución.	100000	8	1	Ejercito	Camuflados	img/catalogo/ejercito/t-shirt_short_estampada.png	f	t
6	Camiseta unisex color verde	Diseñada para brindar comodidad y estilo en cualquier ocasión. Ideal para quienes prefieren un estilo más sencillo y versátil.	50000	10	1	Ejercito	Busos	img/catalogo/ejercito/t-shirt_short_green.png	f	t
7	Pantalón	Pantalón inspirado en el uniforme del Ejército Nacional de Colombia, diseñado para brindar resistencia, comodidad y funcionalidad en actividades diarias.	120000	10	1	Ejercito	Camuflados	img/catalogo/ejercito/pantalon_ejercito.png	f	t
8	Guerrera	Prenda superior utilizado en el uniforme. Caracterizado por su diseño estructurado, funcional y representativo, pensado para brindar una apariencia formal y profesional.	160000	10	1	Ejercito	Camuflados	img/catalogo/ejercito/guerrera_ejercito.png	f	t
12	Camiseta unisex manga larga sin estampado color negro	Camiseta manga larga cómoda y resistente. Ideal para climas frescos y actividades diarias.	80000	9	1	Variado	Camibusos	img/catalogo/Variado/Camiseta_mangalarga_negro.jpg	f	t
13	Guerrera	Prenda superior del uniforme. Se caracteriza por su diseño estructurado, funcional y representativo, pensado para brindar una apariencia formal y profesional.	160000	10	1	Gaula	Camuflados	img/catalogo/gaula/guerrera_gaula.png	f	t
14	Pantalón	Pantalón inspirado en el uniforme del gaula, diseñado para brindar resistencia, comodidad y funcionalidad en actividades diarias.	120000	10	1	Gaula	Camuflados	img/catalogo/gaula/pantalon_gaula.png	f	t
34	pañoleta blanca	xxxxxxxx	15000	10	1	Accesorios	Pañoletas	img/catalogo/accesorios/pañoleta blanca.png	f	f
35	pañoleta verde	xxxxxxxx	15000	10	1	Accesorios	Pantalonetas	img/catalogo/accesorios/pañoleta verde.png	f	f
36	pañoleta negra	xxxxxxxx	15000	10	1	Accesorios	Pañoletas	img/catalogo/accesorios/pañoleta negro.png	f	f
31	pasamontañas 	xxxxxxxx	28000	10	1	Accesorios	Pañoletas	img/catalogo/accesorios/pasamontañas.png	f	f
32	funda cama	xxxxxxxx	30000	10	1	Accesorios	Colchas	img/catalogo/accesorios/funda_para_cama.png	f	f
33	funda para almohada	xxxxxxxx	10000	10	1	Accesorios	Fundas para almohadas	img/catalogo/accesorios/funda_almohadas.png	f	f
15	Camiseta unisex sin estampado color negro	Camiseta cómoda y resistente. Ideal para climas frescos y actividades diarias.	50000	10	1	Variado	Busos	img/catalogo/Variado/Camiseta_negro.jpg	f	t
16	Camiseta unisex sin estampado color blanco	Camiseta cómoda y resistente. Ideal para climas frescos y actividades diarias.	50000	10	1	Variado	Busos	img/catalogo/Variado/Camiseta_blanco.jpg	f	t
17	Guerrera	Prenda superior del uniforme. Se caracteriza por su diseño estructurado, funcional y representativo, pensado para brindar una apariencia formal y profesional.	160000	10	1	Policia	Camuflados	img/catalogo/policia/guerrera_policia.png	f	t
18	Pantalón	Pantalón inspirado en el uniforme de la policía, diseñado para brindar resistencia, comodidad y funcionalidad en actividades diarias.	120000	10	1	Policia	Camuflados	img/catalogo/policia/pantalon_policia.png	f	t
19	Moño	Moño decorativo inspirado en accesorios formales utilizados en uniformes institucionales. Perfecto para completar un estilo elegante.	10000	10	1	Policia	Panoletas	img/catalogo/policia/Moño.jpg	f	t
20	Pañoleta policia sin estampado	Diseñada para brindar comodidad y estilo en cualquier ocasión. Ideal para quienes prefieren un estilo más sencillo y versátil.	60000	10	1	Policia	Panoletas	img/catalogo/policia/Pañoleta_policia.jpg	t	t
23	Camiseta unisex sin estampado color verde	xxxxxxxx	50000	10	1	Variado	Busos	img/catalogo/Variado/Camiseta_verde.png	f	f
24	Camiseta unisex sin estampado color beige claro	xxxxxxxx	50000	10	1	Variado	Busos	img/catalogo/Variado/Camiseta_Beige_claro.png	f	f
25	Gorra Beisbolera gaula	xxxxxxxx	35000	10	1	Gaula	Gorras	img/catalogo/gaula/gaula_cap.png	f	f
26	Gorra Beisbolera	xxxxxxxx	35000	10	1	Accesorios	Gorras	img/catalogo/accesorios/Gorra negra.png	t	f
37	pañoleta beige	xxxxxxxx	15000	10	1	Accesorios	Pañoletas	img/catalogo/accesorios/pañoleta Beige.png	f	f
38	gerrera	xxxxxxxx	160000	10	1	Armada	Camuflados	img/catalogo/armada/gerrera.png	f	f
39	pantalón	xxxxxxxx	120000	10	1	Armada	Camuflados	img/catalogo/armada/pantalon_camuflado.png	f	f
40	buso táctico para la policía color beige	xxxxxxxx	95000	10	1	Policia	Camibusos	img/catalogo/policia/buso_tactico_color_beige.png	f	f
54	sudadera 	xxxxxxxx	65000	10	1	Ejercito	Sudaderas	img/catalogo/ejercito/uniforme_descanso_ejercito1.png	f	f
55	chaqueta 	xxxxxxxx	80000	10	1	Ejercito	Sudaderas	img/catalogo/ejercito/uniforme_descanso_ejercito.png	f	f
56	sudadera 	xxxxxxxx	65000	10	1	Policia	Sudaderas	img/catalogo/policia/uniforme_descanso_policia1.png	f	f
57	chaqueta 	xxxxxxxx	80000	10	1	Policia	Sudaderas	img/catalogo/policia/uniforme_descanso_policia.png	f	f
58	chaqueta 	xxxxxxxx	80000	10	1	Armada	Sudaderas	img/catalogo/armada/uniforme_descanso_armada.png	f	f
62	buso 	xxxxxxxx	50000	10	1	Ejercito	Busos	img/catalogo/ejercito/buso_descanso_ejercito.png	f	f
63	pantaloneta	xxxxxxxx	70000	10	1	Ejercito	Pantalonetas	img/catalogo/ejercito/pantaloneta_descanso_ejercito.png	f	f
64	buso de descanso	xxxxxxxx	50000	10	1	Policia	Busos	img/catalogo/policia/buso_descanso_policia.png	f	f
65	pantaloneta	xxxxxxxx	70000	10	1	Policia	Pantalonetas	img/catalogo/policia/pantaloneta_descanso_policia.png	f	f
66	buso de descanso	xxxxxxxx	50000	10	1	Armada	Busos	img/catalogo/armada/buso_descanso_armada.png	f	f
67	pantaloneta	xxxxxxxx	70000	10	1	Armada	Pantalonetas	img/catalogo/armada/pantaloneta_descanso_armada.png	f	f
\.


--
-- Data for Name: promociones; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.promociones (id_promo, nombre, descripcion, tipo_descuento, valor_descuento, id_producto, codigo, fecha_inicio, fecha_fin, activo) FROM stdin;
1	Promo Camiseta unisex con camuflado		porcentaje	50	3		2026-03-25	2026-03-27	t
2	Promo Guerrera		valor_fijo	140000	13		2026-03-25	2026-03-25	t
3	Promo Guerrera		valor_fijo	100000	17		2026-05-15	2026-05-16	f
4	Promo Camiseta unisex sin estampado color negro		valor_fijo	30000	15				f
5	gerrera		valor_fijo	100000	17		2026-05-15	2026-05-16	t
\.


--
-- Data for Name: registros; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.registros (id_registro, id_usuario, accion, fecha_accion) FROM stdin;
117	nico@gmail.com	Promocion desactivada: Promo Camiseta unisex con camuflado	2026-03-25 13:12:36
197	nico@gmail.com	Inicio de sesión exitoso	2026-04-03 12:20:55
122	nico@gmail.com	POS registro venta #15 por COP 10.000,00 (1 producto(s))\n- total bruto: COP 10.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 092893264\n- teléfono: 3204567896	2026-03-25 15:12:42
123	nico@gmail.com	Inicio de sesión exitoso	2026-03-25 15:46:09
97	nico@gmail.com	Actualizo producto 'Pantalón' (ID 14)\n- precio: COP 180,00 -> COP 180.000,00	2026-03-24 14:45:15
124	nico@gmail.com	POS registro venta #16 por COP 10.000,00 (1 producto(s))\n- total bruto: COP 10.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 15:46:55
225	nico@gmail.com	Actualizo producto 'Camiseta unisex con camuflado' (ID 3)\n- stock: 5 -> 10	2026-04-08 18:03:06
125	nico@gmail.com	POS registro venta #17 por COP 10.000,00 (1 producto(s))\n- total bruto: COP 10.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 15:47:56
127	nico@gmail.com	POS registro venta #18 por COP 10.000,00 (1 producto(s))\n- total bruto: COP 10.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 16:19:50
239	nico@gmail.com	Inicio de sesión exitoso	2026-04-12 18:09:03
128	nico@gmail.com	POS registro venta #19 por COP 10.000,00 (1 producto(s))\n- total bruto: COP 10.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 16:28:10
111	nico@gmail.com	Inicio de sesion exitoso	2026-03-24 17:08:32
84	nico@gmail.com	Inicio de sesion exitoso	2026-03-24 14:39:04
103	nico@gmail.com	Actualizo producto 'Moño' (ID 19)\n- precio: COP 20,00 -> COP 10.000,00	2026-03-24 14:46:22
104	nico@gmail.com	Actualizo producto 'Pantalón' (ID 18)\n- precio: COP 180,00 -> COP 180.000,00	2026-03-24 14:46:32
106	nico@gmail.com	Inicio de sesion exitoso	2026-03-24 14:51:37
107	nico@gmail.com	Restauro producto: Armando Estaban Quito (ID 2)	2026-03-24 16:27:08
108	nico@gmail.com	Actualizo producto 'Armando Estaban Quito' (ID 2)\n- sin cambios detectados	2026-03-24 16:28:18
219	nico@gmail.com	Inicio de sesiÃƒÂ³n exitoso	2026-04-08 15:59:53
220	nico@gmail.com	Inicio de sesiÃƒÂ³n exitoso	2026-04-08 16:08:57
223	nico@gmail.com	POS registro venta #44 por COP 100.000,00 (1 producto(s))\n- total bruto: COP 100.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- telÃƒÂ©fono: 3204567896	2026-04-08 17:11:59
224	nico@gmail.com	Actualizo producto 'Camiseta unisex color verde' (ID 6)\n- stock: 4 -> 10	2026-04-08 18:02:58
226	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color negro' (ID 4)\n- stock: 7 -> 10	2026-04-08 18:03:18
228	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color blanco' (ID 5)\n- sin cambios detectados	2026-04-08 18:03:24
68	nico@gmail.com	Creo producto 'Moño' (ID 19)\n- precio: COP 20,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Panoletas	2026-03-18 14:33:51
229	nico@gmail.com	POS registro venta #45 por COP 80.000,00 (1 producto(s))\n- total bruto: COP 80.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- telÃƒÂ©fono: 3204567896	2026-04-08 18:06:49
28	nico@gmail.com	Inicio de sesión exitoso	2026-03-14 16:08:55
377	nico@gmail.com	Promoción creada: Promo Guerrera\n- producto ID: 17\n- descuento: COP 100.000,00\n- código: N/A	2026-05-15 14:19:16
245	nico@gmail.com	Inicio de sesión exitoso	2026-04-16 16:36:31
248	nico@gmail.com	POS registro venta #51 por COP 160.000,00 (1 producto(s))\n- total bruto: COP 160.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-04-16 17:42:38
129	nico@gmail.com	POS registro venta #20 por COP 10.000,00 (1 producto(s))\n- total bruto: COP 10.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 16:43:35
130	nico@gmail.com	Inicio de sesión exitoso	2026-03-25 17:08:15
131	nico@gmail.com	Inicio de sesión exitoso	2026-03-25 17:08:16
155	nico@gmail.com	Actualizo producto 'Camiseta unisex manga larga sin estampado color negro' (ID 11)\n- stock: 9 -> 10	2026-03-25 18:09:42
77	nico@gmail.com	Inicio de sesion exitoso	2026-03-18 15:04:30
132	nico@gmail.com	POS registro venta #21 por COP 10.000,00 (1 producto(s))\n- total bruto: COP 10.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 17:08:48
173	nico@gmail.com	Actualizo producto 'Camiseta unisex con camuflado' (ID 3)\n- stock: 4 -> 10	2026-03-25 20:30:48
175	nico@gmail.com	Inicio de sesión exitoso	2026-03-27 13:22:05
133	nico@gmail.com	POS registro venta #22 por COP 10.000,00 (1 producto(s))\n- total bruto: COP 10.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 17:17:22
134	nico@gmail.com	POS registro venta #23 por COP 10.000,00 (1 producto(s))\n- total bruto: COP 10.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 17:30:05
272	nico@gmail.com	Inicio de sesiÃ³n exitoso	2026-04-21 16:16:24
156	nico@gmail.com	Actualizo producto 'Guerrera' (ID 13)\n- stock: 9 -> 10	2026-03-25 18:10:05
157	nico@gmail.com	Actualizo producto 'Guerrera' (ID 8)\n- stock: 9 -> 10	2026-03-25 18:10:12
80	nico@gmail.com	Inicio de sesion exitoso	2026-03-23 17:20:19
158	nico@gmail.com	Actualizo producto 'Pantalón' (ID 7)\n- stock: 9 -> 10	2026-03-25 18:10:22
403	nico@gmail.com	Elimino producto: Pañoleta policia sin estampado (ID 20)	2026-05-19 15:03:46
404	nico@gmail.com	Actualizo producto 'Gorra Beisbolera' (ID 26)\n- fuerza: Variado -> Accesorios	2026-05-19 15:04:28
159	nico@gmail.com	POS registro venta #26 por COP 60.000,00 (1 producto(s))\n- total bruto: COP 60.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 18:34:53
160	nico@gmail.com	Actualizo producto 'Pañoleta policia sin estampado' (ID 20)\n- stock: 9 -> 10	2026-03-25 18:41:51
271	nico@gmail.com	Administrador actualizÃ³ prendas destacadas por categorÃ­a:\n- EjÃ©rcito: 5 (6, 5, 4, 11, 3)\n- PolicÃ­a: 5 (10, 9, 12, 17, 18)\n- Armada: 0 (ninguna)\n- Total destacadas: 10	2026-04-21 16:15:58
161	nico@gmail.com	POS registro venta #27 por COP 80.000,00 (1 producto(s))\n- total bruto: COP 80.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 18:49:29
38	nico@gmail.com	Inicio de sesion exitoso	2026-03-17 17:03:36
47	nico@gmail.com	Elimino producto: Armando Estaban Quito (ID 2)	2026-03-18 13:23:43
162	nico@gmail.com	POS registro venta #28 por COP 80.000,00 (1 producto(s))\n- total bruto: COP 80.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 18:56:24
163	nico@gmail.com	POS registro venta #29 por COP 160.000,00 (1 producto(s))\n- total bruto: COP 160.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 19:05:41
277	nico@gmail.com	Cambio de estado para usuario hola3@gmail.com (ID 5) -> inactivo	2026-04-22 13:05:11
137	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color blanco' (ID 10)\n- stock: 9 -> 10	2026-03-25 18:03:25
118	nico@gmail.com	Promocion activada: Promo Camiseta unisex con camuflado	2026-03-25 13:12:46
120	nico@gmail.com	Inicio de sesion exitoso	2026-03-25 13:20:35
41	nico@gmail.com	Inicio de sesion exitoso	2026-03-18 13:13:07
193	admin	Contrasena restablecida por recuperacion para somosdecimob2020@gmail.com	2026-04-03 11:26:18
269	nico@gmail.com	Inicio de sesiÃ³n exitoso	2026-04-21 16:15:19
67	nico@gmail.com	Inicio de sesion exitoso	2026-03-18 14:32:38
126	nico@gmail.com	Actualizo producto 'Moño' (ID 19)\n- stock: 7 -> 10	2026-03-25 15:52:35
69	nico@gmail.com	Creo producto 'Pañoleta policia sin estampado' (ID 20)\n- precio: COP 60,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Panoletas	2026-03-18 14:36:43
74	nico@gmail.com	Inicio de sesion exitoso	2026-03-18 14:56:43
3	nico@gmail.com	Creo producto 'Camiseta mallada' (ID 1)\n- precio: COP 60,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Busos	2026-03-07 01:25:52
417	nico@gmail.com	Actualizo producto 'Pantalón' (ID 14)\n- precio: COP 180.000,00 -> COP 120.000,00	2026-05-19 15:52:24
115	nico@gmail.com	Promocion desactivada: Promo Camiseta unisex con camuflado	2026-03-25 13:12:28
85	nico@gmail.com	Actualizo producto 'Camiseta unisex con camuflado' (ID 3)\n- precio: COP 100,00 -> COP 100.000,00	2026-03-24 14:39:38
86	nico@gmail.com	Inicio de sesion exitoso	2026-03-24 14:41:37
87	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color negro' (ID 4)\n- precio: COP 50,00 -> COP 50.000,00	2026-03-24 14:41:57
88	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color blanco' (ID 5)\n- precio: COP 50,00 -> COP 50.000,00	2026-03-24 14:42:20
89	nico@gmail.com	Actualizo producto 'Camiseta unisex color verde' (ID 6)\n- precio: COP 50,00 -> COP 50.000,00	2026-03-24 14:42:31
252	nico@gmail.com	Inicio de sesión exitoso	2026-04-16 18:46:17
20	nico@gmail.com	Inicio de sesión exitoso	2026-03-13 14:38:22
138	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color negro' (ID 9)\n- stock: 9 -> 10	2026-03-25 18:03:35
139	nico@gmail.com	Actualizo producto 'Guerrera' (ID 17)\n- stock: 9 -> 10	2026-03-25 18:03:55
141	nico@gmail.com	Actualizo producto 'Moño' (ID 19)\n- stock: 3 -> 10	2026-03-25 18:04:20
142	nico@gmail.com	Actualizo producto 'Pañoleta policia sin estampado' (ID 20)\n- stock: 9 -> 10	2026-03-25 18:04:30
253	nico@gmail.com	Actualizo estado de pedido #53: pendiente -> enviado	2026-04-16 18:46:40
310	nico@gmail.com	Inicio de sesión exitoso	2026-04-29 15:55:35
189	admin	Enlace de recuperacion enviado a nachoher072+recoverytest1775230812@gmail.com	2026-04-03 10:40:14
143	nico@gmail.com	POS registro venta #25 por COP 1.150.000,00 (14 producto(s))\n- total bruto: COP 1.200.000,00\n- descuento aplicado: COP 50.000,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 18:05:47
144	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color negro' (ID 9)\n- stock: 9 -> 10	2026-03-25 18:08:20
145	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color blanco' (ID 10)\n- stock: 9 -> 10	2026-03-25 18:08:26
146	nico@gmail.com	Actualizo producto 'Camiseta unisex manga larga sin estampado color negro' (ID 12)\n- stock: 9 -> 10	2026-03-25 18:08:32
147	nico@gmail.com	Actualizo producto 'Guerrera' (ID 17)\n- stock: 9 -> 10	2026-03-25 18:08:38
149	nico@gmail.com	Actualizo producto 'Moño' (ID 19)\n- stock: 9 -> 10	2026-03-25 18:08:54
152	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color negro' (ID 4)\n- stock: 9 -> 10	2026-03-25 18:09:15
323	nico@gmail.com	Inicio de sesión exitoso	2026-04-30 17:10:46
153	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color blanco' (ID 5)\n- stock: 9 -> 10	2026-03-25 18:09:20
154	nico@gmail.com	Actualizo producto 'Camiseta unisex color verde' (ID 6)\n- stock: 9 -> 10	2026-03-25 18:09:31
102	nico@gmail.com	Actualizo producto 'Pañoleta policia sin estampado' (ID 20)\n- sin cambios detectados	2026-03-24 14:46:02
63	nico@gmail.com	Creo producto 'Guerrera' (ID 17)\n- precio: COP 160,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Camuflados	2026-03-18 14:23:44
100	nico@gmail.com	Actualizo producto 'Guerrera' (ID 17)\n- precio: COP 160,00 -> COP 160.000,00	2026-03-24 14:45:51
101	nico@gmail.com	Actualizo producto 'Pañoleta policia sin estampado' (ID 20)\n- precio: COP 60,00 -> COP 60.000,00	2026-03-24 14:46:02
90	nico@gmail.com	Actualizo producto 'Pantalón' (ID 7)\n- precio: COP 120,00 -> COP 120.000,00	2026-03-24 14:42:41
91	nico@gmail.com	Actualizo producto 'Guerrera' (ID 8)\n- precio: COP 160,00 -> COP 160.000,00	2026-03-24 14:42:53
186	nico@gmail.com	Inicio de sesión exitoso	2026-04-02 17:30:25
188	admin	Nuevo usuario registrado y verificado: julio cesar otalvaro sanchez	2026-04-02 18:52:23
190	admin	Contrasena restablecida por recuperacion para nachoher072+recoverytest1775230812@gmail.com	2026-04-03 10:40:14
196	admin	Nuevo usuario registrado y verificado: jilmer	2026-04-03 11:55:51
198	nico@gmail.com	Inicio de sesión exitoso	2026-04-06 20:37:32
199	nico@gmail.com	Inicio de sesión exitoso	2026-04-06 22:30:20
2	nico@gmail.com	Inicio de sesión exitoso	2026-03-07 01:19:16
121	nico@gmail.com	Promocion creada: Promo Guerrera\n- producto ID: 13\n- descuento: COP 140.000,00\n- codigo: N/A	2026-03-25 13:22:32
31	nico@gmail.com	Inicio de sesión exitoso	2026-03-16 21:17:20
36	nico@gmail.com	Inicio de sesion exitoso	2026-03-17 16:50:35
92	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color negro' (ID 9)\n- precio: COP 50,00 -> COP 50.000,00	2026-03-24 14:43:31
94	nico@gmail.com	Actualizo producto 'Camiseta unisex manga larga sin estampado color negro' (ID 11)\n- precio: COP 80,00 -> COP 80.000,00	2026-03-24 14:43:53
254	nico@gmail.com	Actualizo estado de pedido #53: enviado -> entregado	2026-04-16 18:46:44
95	nico@gmail.com	Actualizo producto 'Camiseta unisex manga larga sin estampado color negro' (ID 12)\n- precio: COP 80,00 -> COP 80.000,00	2026-03-24 14:44:49
259	nico@gmail.com	Inicio de sesión exitoso	2026-04-20 15:22:16
4	nico@gmail.com	Actualizo producto 'Camiseta mallada' (ID 1)\n- sin cambios detectados	2026-03-07 01:26:25
222	nico@gmail.com	Inicio de sesiÃƒÂ³n exitoso	2026-04-08 16:45:00
227	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color blanco' (ID 5)\n- stock: 9 -> 10	2026-04-08 18:03:24
5	nico@gmail.com	Creo producto 'Armando Estaban Quito' (ID 2)\n- precio: COP 100.000,00\n- stock: 100\n- fuerza: Gaula\n- intendencia: Camibusos	2026-03-07 01:45:18
135	nico@gmail.com	POS registro venta #24 por COP 590.000,00 (7 producto(s))\n- total bruto: COP 590.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 17:54:38
179	nico@gmail.com	Inicio de sesión exitoso	2026-03-27 16:43:07
136	nico@gmail.com	Actualizo producto 'Camiseta unisex manga larga sin estampado color negro' (ID 12)\n- stock: 9 -> 10	2026-03-25 18:03:10
39	nico@gmail.com	Inicio de sesion exitoso	2026-03-18 12:57:52
284	nico@gmail.com	Actualizo estado de pedido #50: pendiente -> enviado	2026-04-22 16:57:50
230	nico@gmail.com	POS registro venta #46 por COP 10.000,00 (1 producto(s))\n- total bruto: COP 10.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- telÃƒÂ©fono: 3204567896	2026-04-08 21:47:43
247	nico@gmail.com	Inicio de sesión exitoso	2026-04-16 17:39:42
231	nico@gmail.com	POS registro venta #47 por COP 10.000,00 (1 producto(s))\n- total bruto: COP 10.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- telÃƒÂ©fono: 3204567896	2026-04-08 21:54:31
232	nico@gmail.com	Actualizo producto 'Moño' (ID 19)\n- stock: 8 -> 10	2026-04-08 21:55:28
234	nico@gmail.com	Inicio de sesión exitoso	2026-04-09 00:02:43
22	nico@gmail.com	Inicio de sesión exitoso	2026-03-13 15:29:20
192	admin	Enlace de recuperacion enviado a somosdecimob2020@gmail.com	2026-04-03 11:24:56
241	nico@gmail.com	Inicio de sesión exitoso	2026-04-16 12:49:34
150	nico@gmail.com	Actualizo producto 'Pañoleta policia sin estampado' (ID 20)\n- stock: 9 -> 10	2026-03-25 18:09:03
42	nico@gmail.com	Creo producto 'Camiseta unisex con camuflado' (ID 3)\n- precio: COP 100,00\n- stock: 10\n- fuerza: Ejercito\n- intendencia: Camuflados	2026-03-18 13:17:14
43	nico@gmail.com	Creo producto 'Camiseta unisex sin estampado color negro' (ID 4)\n- precio: COP 50,00\n- stock: 10\n- fuerza: Ejercito\n- intendencia: Busos	2026-03-18 13:21:36
45	nico@gmail.com	Inicio de sesion exitoso	2026-03-18 13:22:49
46	nico@gmail.com	Elimino producto: Camiseta mallada (ID 1)	2026-03-18 13:23:37
140	nico@gmail.com	Actualizo producto 'Pantalón' (ID 18)\n- stock: 9 -> 10	2026-03-25 18:04:04
48	nico@gmail.com	Creo producto 'Camiseta unisex sin estampado color blanco' (ID 5)\n- precio: COP 50,00\n- stock: 10\n- fuerza: Ejercito\n- intendencia: Busos	2026-03-18 13:29:21
6	nico@gmail.com	Inicio de sesión exitoso	2026-03-07 16:33:28
49	nico@gmail.com	Creo producto 'Camiseta manga larga color verde' (ID 6)\n- precio: COP 50,00\n- stock: 10\n- fuerza: Ejercito\n- intendencia: Busos	2026-03-18 13:31:28
148	nico@gmail.com	Actualizo producto 'Pantalón' (ID 18)\n- stock: 9 -> 10	2026-03-25 18:08:47
50	nico@gmail.com	Actualizo producto 'Camiseta manga corta color verde' (ID 6)\n- nombre: 'Camiseta manga larga color verde' -> 'Camiseta manga corta color verde'	2026-03-18 13:33:21
112	nico@gmail.com	Elimino producto: Armando Estaban Quito (ID 2)	2026-03-24 21:41:00
109	nico@gmail.com	Actualizo producto 'Armando Estaban Quito' (ID 2)\n- sin cambios detectados	2026-03-24 16:48:24
51	nico@gmail.com	Actualizo producto 'Camiseta unisex manga corta color verde' (ID 6)\n- nombre: 'Camiseta manga corta color verde' -> 'Camiseta unisex manga corta color verde'	2026-03-18 13:33:34
52	nico@gmail.com	Actualizo producto 'Camiseta unisex color verde' (ID 6)\n- nombre: 'Camiseta unisex manga corta color verde' -> 'Camiseta unisex color verde'	2026-03-18 13:33:49
53	nico@gmail.com	Creo producto 'Pantalón' (ID 7)\n- precio: COP 120,00\n- stock: 10\n- fuerza: Ejercito\n- intendencia: Camuflados	2026-03-18 13:35:14
54	nico@gmail.com	Creo producto 'Guerrera' (ID 8)\n- precio: COP 160,00\n- stock: 10\n- fuerza: Ejercito\n- intendencia: Camuflados	2026-03-18 13:37:24
187	nico@gmail.com	Inicio de sesión exitoso	2026-04-02 17:45:54
55	nico@gmail.com	Creo producto 'Camiseta unisex sin estampado color negro' (ID 9)\n- precio: COP 50,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Busos	2026-03-18 13:40:23
405	nico@gmail.com	Actualizo producto 'Gorra Beisbolera' (ID 26)\n- sin cambios detectados	2026-05-19 15:05:49
56	nico@gmail.com	Creo producto 'Camiseta unisex sin estampado color blanco' (ID 10)\n- precio: COP 50,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Busos	2026-03-18 13:41:20
57	nico@gmail.com	Creo producto 'Camiseta unisex manga larga sin estampado color negro' (ID 11)\n- precio: COP 80,00\n- stock: 10\n- fuerza: Ejercito\n- intendencia: Camibusos	2026-03-18 13:46:48
93	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color blanco' (ID 10)\n- precio: COP 50,00 -> COP 50.000,00	2026-03-24 14:43:39
242	nico@gmail.com	Actualizo producto 'Camiseta unisex manga larga sin estampado color negro' (ID 11)\n- stock: 7 -> 10	2026-04-16 12:50:19
113	nico@gmail.com	Inicio de sesion exitoso	2026-03-25 13:07:08
300	nico@gmail.com	Inicio de sesión exitoso	2026-04-28 13:09:29
114	nico@gmail.com	Promocion creada: Promo Camiseta unisex con camuflado\n- producto ID: 3\n- descuento: 50.00%\n- codigo: N/A	2026-03-25 13:11:43
261	nico@gmail.com	Inicio de sesión exitoso	2026-04-21 14:00:41
256	nico@gmail.com	Inicio de sesión exitoso	2026-04-16 18:54:32
96	nico@gmail.com	Actualizo producto 'Guerrera' (ID 13)\n- precio: COP 160,00 -> COP 160.000,00	2026-03-24 14:44:58
98	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color negro' (ID 15)\n- precio: COP 50,00 -> COP 50.000,00	2026-03-24 14:45:29
151	nico@gmail.com	Actualizo producto 'Camiseta unisex con camuflado' (ID 3)\n- stock: 9 -> 10	2026-03-25 18:09:10
99	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color blanco' (ID 16)\n- precio: COP 50,00 -> COP 50.000,00	2026-03-24 14:45:40
274	nico@gmail.com	Actualizo estado de pedido #55: confirmado -> enviado	2026-04-21 16:20:21
367	nico@gmail.com	Actualizo producto 'Camiseta unisex manga larga sin estampado color negro' (ID 12)\n- stock: 9 -> 10	2026-05-11 16:53:35
58	nico@gmail.com	Creo producto 'Camiseta unisex manga larga sin estampado color negro' (ID 12)\n- precio: COP 80,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Camibusos	2026-03-18 13:47:35
116	nico@gmail.com	Promocion activada: Promo Camiseta unisex con camuflado	2026-03-25 13:12:28
34	nico@gmail.com	Inicio de sesión exitoso	2026-03-17 15:53:47
59	nico@gmail.com	Creo producto 'Guerrera' (ID 13)\n- precio: COP 160,00\n- stock: 10\n- fuerza: Gaula\n- intendencia: Camuflados	2026-03-18 14:14:00
60	nico@gmail.com	Creo producto 'Pantalón' (ID 14)\n- precio: COP 180,00\n- stock: 10\n- fuerza: Gaula\n- intendencia: Camuflados	2026-03-18 14:15:35
61	nico@gmail.com	Creo producto 'Camiseta unisex sin estampado color negro' (ID 15)\n- precio: COP 50,00\n- stock: 10\n- fuerza: Gaula\n- intendencia: Busos	2026-03-18 14:18:51
62	nico@gmail.com	Creo producto 'Camiseta unisex sin estampado color blanco' (ID 16)\n- precio: COP 50,00\n- stock: 10\n- fuerza: Gaula\n- intendencia: Busos	2026-03-18 14:20:17
64	nico@gmail.com	Creo producto 'Pantalón' (ID 18)\n- precio: COP 180,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Camuflados	2026-03-18 14:25:10
235	nico@gmail.com	Administrador actualizó prendas destacadas:\n- total destacadas: 5\n- ids: 6, 5, 4, 11, 8	2026-04-09 00:03:19
164	nico@gmail.com	POS registro venta #30 por COP 80.000,00 (1 producto(s))\n- total bruto: COP 80.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 19:10:26
165	nico@gmail.com	Actualizo producto 'Camiseta unisex manga larga sin estampado color negro' (ID 12)\n- stock: 6 -> 10	2026-03-25 19:21:58
301	nico@gmail.com	Inicio de sesión exitoso	2026-04-28 13:12:41
166	nico@gmail.com	Actualizo producto 'Camiseta unisex manga larga sin estampado color negro' (ID 11)\n- stock: 9 -> 10	2026-03-25 19:22:10
167	nico@gmail.com	POS registro venta #31 por COP 50.000,00 (1 producto(s))\n- total bruto: COP 100.000,00\n- descuento aplicado: COP 50.000,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 19:23:24
168	nico@gmail.com	POS registro venta #32 por COP 50.000,00 (1 producto(s))\n- total bruto: COP 100.000,00\n- descuento aplicado: COP 50.000,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 19:33:14
169	nico@gmail.com	POS registro venta #33 por COP 50.000,00 (1 producto(s))\n- total bruto: COP 100.000,00\n- descuento aplicado: COP 50.000,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 19:35:47
318	nico@gmail.com	Inicio de sesión exitoso	2026-04-30 12:10:42
314	nico@gmail.com	Actualizo estado de pedido #57: empaquetado -> enviado	2026-04-29 15:57:48
170	nico@gmail.com	POS registro venta #34 por COP 50.000,00 (1 producto(s))\n- total bruto: COP 100.000,00\n- descuento aplicado: COP 50.000,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 19:40:22
171	nico@gmail.com	POS registro venta #35 por COP 50.000,00 (1 producto(s))\n- total bruto: COP 100.000,00\n- descuento aplicado: COP 50.000,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 19:56:07
333	nico@gmail.com	Actualizó precio personalizado 'buso' a COP 50.000,00	2026-05-01 11:31:22
334	nico@gmail.com	Actualizó solicitud personalizada #4 a cancelada	2026-05-01 11:32:01
172	nico@gmail.com	POS registro venta #36 por COP 50.000,00 (1 producto(s))\n- total bruto: COP 100.000,00\n- descuento aplicado: COP 50.000,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 20:29:37
344	nico@gmail.com	Inicio de sesión exitoso	2026-05-08 15:44:17
176	nico@gmail.com	POS registro venta #37 por COP 50.000,00 (1 producto(s))\n- total bruto: COP 100.000,00\n- descuento aplicado: COP 50.000,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-27 14:14:32
178	nico@gmail.com	Inicio de sesión exitoso	2026-03-27 15:12:36
180	nico@gmail.com	POS registro venta #38 por COP 50.000,00 (1 producto(s))\n- total bruto: COP 100.000,00\n- descuento aplicado: COP 50.000,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-27 16:51:25
181	nico@gmail.com	Inicio de sesión exitoso	2026-04-02 16:45:28
183	admin	Nuevo usuario registrado: julio cesar otalvaro sanchez	2026-04-02 16:50:05
255	nico@gmail.com	POS registro venta #54 por COP 160.000,00 (1 producto(s))\n- total bruto: COP 160.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-04-16 18:50:57
324	nico@gmail.com	Inicio de sesión exitoso	2026-04-30 21:39:37
262	nico@gmail.com	Administrador actualizó prendas destacadas por categoría:\n- Ejército: 5 (6, 5, 4, 11, 8)\n- Policía: 4 (10, 9, 12, 17)\n- Armada: 0 (ninguna)\n- Total destacadas: 9	2026-04-21 14:00:58
263	nico@gmail.com	Administrador actualizó prendas destacadas por categoría:\n- Ejército: 5 (6, 5, 4, 11, 8)\n- Policía: 4 (10, 9, 12, 17)\n- Armada: 0 (ninguna)\n- Total destacadas: 9	2026-04-21 14:01:00
264	nico@gmail.com	Administrador actualizó prendas destacadas por categoría:\n- Ejército: 5 (6, 5, 4, 11, 8)\n- Policía: 4 (10, 9, 12, 17)\n- Armada: 0 (ninguna)\n- Total destacadas: 9	2026-04-21 14:01:06
265	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color negro' (ID 4)\n- stock: 7 -> 10	2026-04-21 14:01:44
266	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color negro' (ID 9)\n- stock: 10 -> 0	2026-04-21 14:02:01
360	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color blanco' (ID 16)\n- fuerza: Gaula -> Variado	2026-05-11 16:47:36
267	nico@gmail.com	Administrador actualizó prendas destacadas por categoría:\n- Ejército: 5 (6, 5, 4, 11, 8)\n- Policía: 4 (10, 9, 12, 17)\n- Armada: 0 (ninguna)\n- Total destacadas: 9	2026-04-21 14:02:23
268	nico@gmail.com	Actualizo estado de pedido #55: pendiente -> confirmado	2026-04-21 14:24:00
270	nico@gmail.com	Administrador actualizÃ³ prendas destacadas por categorÃ­a:\n- EjÃ©rcito: 5 (6, 5, 4, 11, 8)\n- PolicÃ­a: 5 (10, 9, 12, 17, 18)\n- Armada: 0 (ninguna)\n- Total destacadas: 10	2026-04-21 16:15:50
364	nico@gmail.com	Elimino producto: Camiseta unisex manga larga sin estampado color negro (ID 11)	2026-05-11 16:48:36
415	nico@gmail.com	Creo producto 'pañoleta negra' (ID 36)\n- precio: COP 15.000,00\n- stock: 10\n- fuerza: Accesorios\n- intendencia: Pañoletas\n- imagenes: 1	2026-05-19 15:49:16
273	nico@gmail.com	Administrador actualizÃ³ prendas destacadas por categorÃ­a:\n- EjÃ©rcito: 5 (6, 5, 4, 11, 3)\n- PolicÃ­a: 5 (10, 9, 12, 17, 18)\n- Armada: 0 (ninguna)\n- Total destacadas: 10	2026-04-21 16:16:36
275	nico@gmail.com	Actualizo estado de pedido #55: enviado -> entregado	2026-04-21 16:37:24
276	nico@gmail.com	Actualizo estado de pedido #5: pendiente -> entregado	2026-04-21 16:37:51
280	nico@gmail.com	Inicio de sesiÃ³n exitoso	2026-04-22 16:46:32
281	nico@gmail.com	Administrador actualizÃ³ prendas destacadas por categorÃ­a:\n- EjÃ©rcito: 5 (6, 5, 4, 11, 3)\n- PolicÃ­a: 5 (10, 9, 12, 17, 18)\n- Armada: 0 (ninguna)\n- Total destacadas: 10	2026-04-22 16:46:38
282	nico@gmail.com	Actualizo revision de pago para pedido #56: pendiente_comprobante -> en_revision	2026-04-22 16:56:50
283	nico@gmail.com	Actualizo estado de pedido #52: pendiente -> entregado	2026-04-22 16:57:44
286	nico@gmail.com	Inicio de sesiÃ³n exitoso	2026-04-24 12:54:38
287	nico@gmail.com	Administrador actualizó prendas destacadas por categoría:\n- Ejército: 5 (6, 5, 4, 11, 3)\n- Policía: 7 (10, 9, 12, 17, 18, 19, 20)\n- Armada: 0 (ninguna)\n- Total destacadas: 12	2026-04-24 13:29:16
289	nico@gmail.com	Administrador actualizó prendas destacadas por categoría:\n- Ejército: 7 (6, 5, 4, 11, 3, 8, 7)\n- Policía: 7 (10, 9, 12, 17, 18, 19, 20)\n- Armada: 0 (ninguna)\n- Total destacadas: 14	2026-04-24 14:17:44
291	nico@gmail.com	Inicio de sesión exitoso	2026-04-26 13:09:01
293	nico@gmail.com	Administrador actualizó prendas destacadas por categoría:\n- Ejército: 0 (ninguna)\n- Policía: 7 (10, 9, 12, 17, 18, 19, 20)\n- Armada: 0 (ninguna)\n- Total destacadas: 7	2026-04-26 14:12:42
294	nico@gmail.com	Administrador actualizó prendas destacadas por categoría:\n- Ejército: 7 (6, 5, 4, 11, 3, 8, 7)\n- Policía: 7 (10, 9, 12, 17, 18, 19, 20)\n- Armada: 0 (ninguna)\n- Total destacadas: 14	2026-04-26 14:12:52
295	nico@gmail.com	Actualizo revision de pago para pedido #56: en_revision -> aprobado	2026-04-26 14:13:13
299	nico@gmail.com	Inicio de sesión exitoso	2026-04-28 12:45:19
302	nico@gmail.com	Inicio de sesión exitoso	2026-04-28 14:41:04
303	nico@gmail.com	Actualizo estado de pedido #50: enviado -> empaquetado	2026-04-29 13:47:02
304	nico@gmail.com	Actualizo estado de pedido #56: confirmado -> enviado	2026-04-29 14:26:08
305	nico@gmail.com	Actualizo estado de pedido #41: pendiente -> empaquetado	2026-04-29 14:26:50
311	nico@gmail.com	Actualizo revision de pago para pedido #57: pendiente_comprobante -> en_revision	2026-04-29 15:57:12
312	nico@gmail.com	Actualizo revision de pago para pedido #57: en_revision -> aprobado	2026-04-29 15:57:24
313	nico@gmail.com	Actualizo estado de pedido #57: confirmado -> empaquetado	2026-04-29 15:57:39
321	nico@gmail.com	Inicio de sesión exitoso	2026-04-30 12:26:42
330	nico@gmail.com	Actualizó solicitud personalizada #4 a cancelada	2026-05-01 11:26:20
331	nico@gmail.com	Actualizó solicitud personalizada #3 a completada	2026-05-01 11:26:28
332	nico@gmail.com	Actualizó precio personalizado 'buso' a COP 0,00	2026-05-01 11:30:58
343	nico@gmail.com	Actualizó solicitud personalizada #11 a pendiente	2026-05-01 13:37:39
345	nico@gmail.com	Inicio de sesión exitoso	2026-05-11 14:05:54
346	nico@gmail.com	Actualizo revision de pago para pedido #59: pendiente_comprobante -> aprobado	2026-05-11 14:07:49
347	nico@gmail.com	Elimino definitivamente el producto: Camiseta mallada (ID 1)	2026-05-11 14:11:20
348	nico@gmail.com	Elimino definitivamente el producto: Armando Estaban Quito (ID 2)	2026-05-11 14:11:23
349	nico@gmail.com	Inicio de sesión exitoso	2026-05-11 15:24:39
398	nico@gmail.com	Creo producto 'Gorra Beisbolera' (ID 26)\n- precio: COP 35.000,00\n- stock: 10\n- fuerza: Variado\n- intendencia: Gorras\n- imagenes: 1	2026-05-19 14:57:31
350	nico@gmail.com	Administrador actualizo prendas destacadas por categoria:\n- Ejercito: 7 (6, 5, 4, 11, 3, 8, 7)\n- Policia: 7 (10, 9, 12, 17, 18, 19, 20)\n- Armada: 0 (ninguna)\n- Gaula: 3 (16, 15, 13)\n- Total destacadas: 17	2026-05-11 15:56:22
402	nico@gmail.com	Creo producto 'Gorra Beisbolera policía verde ' (ID 29)\n- precio: COP 35.000,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Gorras\n- imagenes: 1	2026-05-19 15:02:31
351	nico@gmail.com	Administrador actualizo prendas destacadas por categoria:\n- Ejercito: 7 (6, 5, 4, 11, 3, 8, 7)\n- Policia: 7 (10, 9, 12, 17, 18, 19, 20)\n- Armada: 0 (ninguna)\n- Gaula: 4 (16, 15, 13, 14)\n- Total destacadas: 18	2026-05-11 15:56:44
352	nico@gmail.com	Administrador actualizo prendas destacadas por categoria:\n- Ejercito: 7 (6, 5, 4, 11, 3, 8, 7)\n- Policia: 7 (10, 9, 12, 17, 18, 19, 20)\n- Armada: 0 (ninguna)\n- Gaula: 4 (16, 15, 13, 14)\n- Total destacadas: 18	2026-05-11 15:57:02
353	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color negro' (ID 4)\n- fuerza: Ejercito -> Variado	2026-05-11 16:45:58
354	nico@gmail.com	Actualizo producto 'Camiseta unisex manga larga sin estampado color negro' (ID 12)\n- fuerza: Policia -> Variado	2026-05-11 16:46:15
355	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color negro' (ID 9)\n- fuerza: Policia -> Variado	2026-05-11 16:46:27
356	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color blanco' (ID 10)\n- fuerza: Policia -> Variado	2026-05-11 16:46:44
357	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color blanco' (ID 5)\n- fuerza: Ejercito -> Variado	2026-05-11 16:46:59
358	nico@gmail.com	Actualizo producto 'Camiseta unisex manga larga sin estampado color negro' (ID 11)\n- fuerza: Ejercito -> Variado	2026-05-11 16:47:16
359	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color negro' (ID 15)\n- fuerza: Gaula -> Variado	2026-05-11 16:47:29
361	nico@gmail.com	Elimino producto: Camiseta unisex sin estampado color negro (ID 4)	2026-05-11 16:48:03
362	nico@gmail.com	Elimino producto: Camiseta unisex sin estampado color blanco (ID 5)	2026-05-11 16:48:12
363	nico@gmail.com	Elimino producto: Camiseta unisex sin estampado color blanco (ID 10)	2026-05-11 16:48:25
365	nico@gmail.com	Elimino producto: Camiseta unisex sin estampado color negro (ID 9)	2026-05-11 16:48:45
366	nico@gmail.com	Actualizo producto 'Guerrera' (ID 13)\n- stock: 7 -> 10	2026-05-11 16:53:24
368	nico@gmail.com	POS registro venta #60 por COP 80.000,00 (1 producto(s))\n- total bruto: COP 80.000,00\n- descuento aplicado: COP 0,00\n- cliente: julio\n- correo: julio11916@gmail.com\n- documento: 1111042086\n- telefono: 3102577460	2026-05-12 13:16:55
369	nico@gmail.com	Inicio de sesión exitoso	2026-05-13 13:15:38
370	nico@gmail.com	Inicio de sesión exitoso	2026-05-13 14:03:36
371	nico@gmail.com	Administrador actualizo prendas destacadas por categoria:\n- Ejercito: 4 (6, 3, 8, 7)\n- Policia: 4 (17, 18, 19, 20)\n- Armada: 0 (ninguna)\n- Gaula: 2 (13, 14)\n- Variado: 3 (16, 15, 12)\n- Total destacadas: 13	2026-05-13 14:03:47
372	nico@gmail.com	Elimino definitivamente el producto: Camiseta unisex sin estampado color negro (ID 4)	2026-05-15 13:20:18
373	nico@gmail.com	Elimino definitivamente el producto: Camiseta unisex sin estampado color blanco (ID 5)	2026-05-15 13:20:20
374	nico@gmail.com	Elimino definitivamente el producto: Camiseta unisex sin estampado color negro (ID 9)	2026-05-15 13:20:23
375	nico@gmail.com	Elimino definitivamente el producto: Camiseta unisex sin estampado color blanco (ID 10)	2026-05-15 13:20:27
376	nico@gmail.com	Elimino definitivamente el producto: Camiseta unisex manga larga sin estampado color negro (ID 11)	2026-05-15 13:20:29
378	nico@gmail.com	Promoción creada: Promo Camiseta unisex sin estampado color negro\n- producto ID: 15\n- descuento: COP 30.000,00\n- código: N/A	2026-05-15 14:21:09
379	nico@gmail.com	Promocion desactivada: Promo Camiseta unisex sin estampado color negro	2026-05-15 14:21:15
380	nico@gmail.com	POS registro venta #61 por COP 200.000,00 (1 producto(s))\n- total bruto: COP 200.000,00\n- descuento aplicado: COP 0,00\n- cliente: julio\n- correo: julio11916@gmail.com\n- documento: 1111042086\n- telefono: 3102577460	2026-05-15 14:35:14
381	nico@gmail.com	Promoción creada: gerrera\n- producto ID: 17\n- descuento: COP 100.000,00\n- código: N/A	2026-05-15 21:35:18
382	nico@gmail.com	Promocion desactivada: Promo Guerrera	2026-05-15 21:35:29
383	nico@gmail.com	Promocion desactivada: Promo Camiseta unisex con camuflado	2026-05-15 21:35:41
384	nico@gmail.com	Promocion activada: Promo Camiseta unisex con camuflado	2026-05-15 21:35:47
385	nico@gmail.com	Inicio de sesión exitoso	2026-05-17 14:58:22
386	nico@gmail.com	Inicio de sesión exitoso	2026-05-17 15:43:24
387	nico@gmail.com	Actualizo solicitud personalizada #1 a cancelada	2026-05-17 15:43:36
388	nico@gmail.com	Inicio de sesión exitoso	2026-05-19 14:20:02
389	nico@gmail.com	Creo producto 'Camiseta unisex sin estampado color verde' (ID 21)\n- precio: COP 50.000,00\n- stock: 10\n- fuerza: Variado\n- intendencia: Busos\n- imagenes: 1	2026-05-19 14:37:01
390	nico@gmail.com	Creo producto 'Camiseta unisex sin estampado color beige claro' (ID 22)\n- precio: COP 50.000,00\n- stock: 10\n- fuerza: Variado\n- intendencia: Busos\n- imagenes: 1	2026-05-19 14:39:55
391	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color verde' (ID 21)\n- sin cambios detectados	2026-05-19 14:46:40
392	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color verde' (ID 21)\n- sin cambios detectados	2026-05-19 14:47:42
393	nico@gmail.com	Elimino producto: Camiseta unisex sin estampado color verde (ID 21)	2026-05-19 14:48:13
394	nico@gmail.com	Creo producto 'Camiseta unisex sin estampado color verde' (ID 23)\n- precio: COP 50.000,00\n- stock: 10\n- fuerza: Variado\n- intendencia: Busos\n- imagenes: 1	2026-05-19 14:48:37
395	nico@gmail.com	Elimino producto: Camiseta unisex sin estampado color beige claro (ID 22)	2026-05-19 14:48:54
396	nico@gmail.com	Creo producto 'Camiseta unisex sin estampado color beige claro' (ID 24)\n- precio: COP 50.000,00\n- stock: 10\n- fuerza: Variado\n- intendencia: Busos\n- imagenes: 1	2026-05-19 14:49:16
397	nico@gmail.com	Creo producto 'Gorra Beisbolera gaula' (ID 25)\n- precio: COP 35.000,00\n- stock: 10\n- fuerza: Gaula\n- intendencia: Gorras\n- imagenes: 1	2026-05-19 14:53:24
399	nico@gmail.com	Creo producto 'Gorra Beisbolera policia' (ID 27)\n- precio: COP 35.000,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Gorras\n- imagenes: 1	2026-05-19 14:58:32
400	nico@gmail.com	Creo producto 'Gorra Beisbolera policia' (ID 28)\n- precio: COP 35.000,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Gorras\n- imagenes: 1	2026-05-19 15:01:21
401	nico@gmail.com	Actualizo producto 'Gorra Beisbolera policia azul' (ID 27)\n- nombre: 'Gorra Beisbolera policia' -> 'Gorra Beisbolera policia azul'	2026-05-19 15:01:46
406	nico@gmail.com	Actualizo producto 'Gorra Beisbolera' (ID 26)\n- sin cambios detectados	2026-05-19 15:13:01
407	nico@gmail.com	Actualizo producto 'Gorra Beisbolera' (ID 26)\n- sin cambios detectados	2026-05-19 15:28:43
408	nico@gmail.com	Elimino producto: Gorra Beisbolera (ID 26)	2026-05-19 15:29:22
409	nico@gmail.com	Creo producto 'Gorra Beisbolera ' (ID 30)\n- precio: COP 35.000,00\n- stock: 10\n- fuerza: Accesorios\n- intendencia: Gorras\n- imagenes: 1	2026-05-19 15:30:11
410	nico@gmail.com	Creo producto 'pasamontañas ' (ID 31)\n- precio: COP 28.000,00\n- stock: 10\n- fuerza: Accesorios\n- intendencia: Pañoletas\n- imagenes: 1	2026-05-19 15:35:56
411	nico@gmail.com	Creo producto 'funda cama' (ID 32)\n- precio: COP 30.000,00\n- stock: 10\n- fuerza: Accesorios\n- intendencia: Colchas\n- imagenes: 1	2026-05-19 15:41:23
412	nico@gmail.com	Creo producto 'funda para almohada' (ID 33)\n- precio: COP 10.000,00\n- stock: 10\n- fuerza: Accesorios\n- intendencia: Fundas para almohadas\n- imagenes: 1	2026-05-19 15:42:31
413	nico@gmail.com	Creo producto 'pañoleta blanca' (ID 34)\n- precio: COP 15.000,00\n- stock: 10\n- fuerza: Accesorios\n- intendencia: Pañoletas\n- imagenes: 1	2026-05-19 15:48:21
414	nico@gmail.com	Creo producto 'pañoleta verde' (ID 35)\n- precio: COP 15.000,00\n- stock: 10\n- fuerza: Accesorios\n- intendencia: Pantalonetas\n- imagenes: 1	2026-05-19 15:48:47
416	nico@gmail.com	Creo producto 'pañoleta beige' (ID 37)\n- precio: COP 15.000,00\n- stock: 10\n- fuerza: Accesorios\n- intendencia: Pañoletas\n- imagenes: 1	2026-05-19 15:49:39
418	nico@gmail.com	Actualizo producto 'Pantalón' (ID 18)\n- precio: COP 180.000,00 -> COP 120.000,00	2026-05-19 15:52:39
419	nico@gmail.com	Creo producto 'gerrera' (ID 38)\n- precio: COP 160.000,00\n- stock: 10\n- fuerza: Armada\n- intendencia: Camuflados\n- imagenes: 1	2026-05-19 15:53:35
420	nico@gmail.com	Creo producto 'pantalón' (ID 39)\n- precio: COP 120.000,00\n- stock: 10\n- fuerza: Armada\n- intendencia: Camuflados\n- imagenes: 1	2026-05-19 15:54:20
421	nico@gmail.com	Creo producto 'buso táctico para la policía color beige ' (ID 40)\n- precio: COP 95.000,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Busos\n- imagenes: 1	2026-05-19 16:10:24
422	nico@gmail.com	Creo producto 'buso táctico para la policía color negro' (ID 41)\n- precio: COP 95.000,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Busos\n- imagenes: 1	2026-05-19 16:11:04
423	nico@gmail.com	Creo producto 'buso táctico para la policía color verde' (ID 42)\n- precio: COP 95.000,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Camibusos\n- imagenes: 1	2026-05-19 16:12:18
424	nico@gmail.com	Actualizo producto 'buso táctico para la policía color beige' (ID 40)\n- nombre: 'buso táctico para la policía color beige ' -> 'buso táctico para la policía color beige'\n- intendencia: Busos -> Camibusos	2026-05-19 16:12:33
425	nico@gmail.com	Actualizo producto 'buso táctico para la policía color negro' (ID 41)\n- intendencia: Busos -> Camibusos	2026-05-19 16:12:42
426	nico@gmail.com	Inicio de sesión exitoso	2026-05-19 16:48:32
427	nico@gmail.com	Creo producto 'gerrera' (ID 43)\n- precio: COP 160.000,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Camuflados\n- imagenes: 1	2026-05-19 16:53:24
428	nico@gmail.com	Creo producto 'Pantalón' (ID 44)\n- precio: COP 120.000,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Camuflados\n- imagenes: 1	2026-05-22 13:42:56
429	nico@gmail.com	Creo producto 'buso táctico para el ejecito color verde' (ID 45)\n- precio: COP 95.000,00\n- stock: 10\n- fuerza: Ejercito\n- intendencia: Camibusos\n- imagenes: 1	2026-05-22 13:51:07
430	nico@gmail.com	Creo producto 'buso táctico para el ejecito color verde oscuro' (ID 46)\n- precio: COP 95.000,00\n- stock: 10\n- fuerza: Ejercito\n- intendencia: Camibusos\n- imagenes: 1	2026-05-22 13:52:10
431	nico@gmail.com	Creo producto 'buso táctico para el ejecito sin camuflado' (ID 47)\n- precio: COP 95.000,00\n- stock: 10\n- fuerza: Ejercito\n- intendencia: Camibusos\n- imagenes: 1	2026-05-22 13:53:02
432	nico@gmail.com	Inicio de sesión exitoso	2026-05-22 14:15:03
433	nico@gmail.com	Creo producto 'chaqueta ' (ID 48)\n- precio: COP 80.000,00\n- stock: 10\n- fuerza: Armada\n- intendencia: Sudaderas\n- imagenes: 1	2026-05-22 16:26:56
434	nico@gmail.com	Creo producto 'sudadera ' (ID 49)\n- precio: COP 65.000,00\n- stock: 10\n- fuerza: Armada\n- intendencia: Sudaderas\n- imagenes: 1	2026-05-22 16:27:48
435	nico@gmail.com	Creo producto 'chaqueta ' (ID 50)\n- precio: COP 80.000,00\n- stock: 10\n- fuerza: Gaula\n- intendencia: Sudaderas\n- imagenes: 1	2026-05-22 16:29:26
436	nico@gmail.com	Creo producto 'sudadera ' (ID 51)\n- precio: COP 65.000,00\n- stock: 10\n- fuerza: Gaula\n- intendencia: Sudaderas\n- imagenes: 1	2026-05-22 16:30:13
437	nico@gmail.com	Creo producto 'chaqueta ' (ID 52)\n- precio: COP 80.000,00\n- stock: 10\n- fuerza: Gaula\n- intendencia: Sudaderas\n- imagenes: 1	2026-05-22 16:32:52
438	nico@gmail.com	Creo producto 'sudadera ' (ID 53)\n- precio: COP 65.000,00\n- stock: 10\n- fuerza: Gaula\n- intendencia: Sudaderas\n- imagenes: 1	2026-05-22 16:34:23
439	nico@gmail.com	Creo producto 'sudadera ' (ID 54)\n- precio: COP 65.000,00\n- stock: 10\n- fuerza: Ejercito\n- intendencia: Sudaderas\n- imagenes: 1	2026-05-22 16:37:02
440	nico@gmail.com	Creo producto 'chaqueta ' (ID 55)\n- precio: COP 80.000,00\n- stock: 10\n- fuerza: Ejercito\n- intendencia: Sudaderas\n- imagenes: 1	2026-05-22 16:37:27
441	nico@gmail.com	Creo producto 'sudadera ' (ID 56)\n- precio: COP 65.000,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Sudaderas\n- imagenes: 1	2026-05-22 16:38:53
442	nico@gmail.com	Creo producto 'chaqueta ' (ID 57)\n- precio: COP 80.000,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Sudaderas\n- imagenes: 1	2026-05-22 16:39:44
443	nico@gmail.com	Creo producto 'chaqueta ' (ID 58)\n- precio: COP 80.000,00\n- stock: 10\n- fuerza: Armada\n- intendencia: Sudaderas\n- imagenes: 1	2026-05-22 16:41:12
444	nico@gmail.com	Creo producto 'sudadera ' (ID 59)\n- precio: COP 65.000,00\n- stock: 10\n- fuerza: Armada\n- intendencia: Sudaderas\n- imagenes: 1	2026-05-22 16:41:52
445	nico@gmail.com	Creo producto 'buso de descanso' (ID 60)\n- precio: COP 50.000,00\n- stock: 10\n- fuerza: Gaula\n- intendencia: Busos\n- imagenes: 1	2026-05-22 16:48:38
446	nico@gmail.com	Creo producto 'pantaloneta' (ID 61)\n- precio: COP 70.000,00\n- stock: 10\n- fuerza: Gaula\n- intendencia: Pantalonetas\n- imagenes: 1	2026-05-22 16:49:21
447	nico@gmail.com	Creo producto 'buso ' (ID 62)\n- precio: COP 50.000,00\n- stock: 10\n- fuerza: Ejercito\n- intendencia: Busos\n- imagenes: 1	2026-05-22 16:51:03
448	nico@gmail.com	Creo producto 'pantaloneta' (ID 63)\n- precio: COP 70.000,00\n- stock: 10\n- fuerza: Ejercito\n- intendencia: Pantalonetas\n- imagenes: 1	2026-05-22 16:51:31
449	nico@gmail.com	Creo producto 'buso de descanso' (ID 64)\n- precio: COP 50.000,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Busos\n- imagenes: 1	2026-05-22 16:52:28
450	nico@gmail.com	Creo producto 'pantaloneta' (ID 65)\n- precio: COP 70.000,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Pantalonetas\n- imagenes: 1	2026-05-22 16:52:53
451	nico@gmail.com	Creo producto 'buso de descanso' (ID 66)\n- precio: COP 50.000,00\n- stock: 10\n- fuerza: Armada\n- intendencia: Busos\n- imagenes: 1	2026-05-22 16:53:46
452	nico@gmail.com	Creo producto 'pantaloneta' (ID 67)\n- precio: COP 70.000,00\n- stock: 10\n- fuerza: Armada\n- intendencia: Pantalonetas\n- imagenes: 1	2026-05-22 16:54:10
\.


--
-- Data for Name: stripe_checkout; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.stripe_checkout (session_id, usuario_email, codigo_promo, cart_hash, total_esperado, estado, id_pedido, created_at, updated_at, carrito_json) FROM stdin;
cs_test_a1ncQ1hpt1iS6vEHuILqrfVxRTtpvD1NNnp3p0jYXIiuHpwHkijWnpgyDR	julio11916@gmail.com		a74506b29f638fb8d65fc6716e408ef822ebf390ccf77212c55dddae5037cd01	250000.00	creado	\N	2026-04-07 17:19:49.031198-05	2026-04-07 17:19:49.031198-05	[{"cantidad": 1, "descripcion": "Diseñada para brindar comodidad y estilo en cualquier ocasión. Ideal para quienes prefieren un estilo más sencillo y versátil.", "id_producto": 4, "imagen_url": "img/Empresa/producto_4.jpg", "nombre": "Camiseta unisex sin estampado color negro", "precio": 50000.0, "subtotal": 50000.0}, {"cantidad": 1, "descripcion": "Diseñada para brindar comodidad y estilo en cualquier ocasión. Ideal para quienes prefieren un estilo más sencillo y versátil.", "id_producto": 5, "imagen_url": "img/Empresa/producto_5.jpg", "nombre": "Camiseta unisex sin estampado color blanco", "precio": 50000.0, "subtotal": 50000.0}, {"cantidad": 1, "descripcion": "Diseñada para brindar comodidad y estilo en cualquier ocasión. Ideal para quienes prefieren un estilo más sencillo y versátil.", "id_producto": 6, "imagen_url": "img/Empresa/producto_6.jpg", "nombre": "Camiseta unisex color verde", "precio": 50000.0, "subtotal": 50000.0}, {"cantidad": 1, "descripcion": "Diseñada para brindar comodidad y estilo en cualquier ocasión. Disponible en versiones con camuflado, que incluyen diseños representativos y gráficos alusivos a la institución.", "id_producto": 3, "imagen_url": "img/Empresa/producto_3.jpg", "nombre": "Camiseta unisex con camuflado", "precio": 100000.0, "subtotal": 100000.0}]
cs_test_a19nYMDVaYdQPdiZeWhawnNdH3GdReQcvXmMtLqzq10lZttGkNYwT5EVOa	julio11916@gmail.com		a74506b29f638fb8d65fc6716e408ef822ebf390ccf77212c55dddae5037cd01	250000.00	creado	\N	2026-04-07 17:22:31.524285-05	2026-04-07 17:22:31.524285-05	[{"cantidad": 1, "descripcion": "Diseñada para brindar comodidad y estilo en cualquier ocasión. Ideal para quienes prefieren un estilo más sencillo y versátil.", "id_producto": 4, "imagen_url": "img/Empresa/producto_4.jpg", "nombre": "Camiseta unisex sin estampado color negro", "precio": 50000.0, "subtotal": 50000.0}, {"cantidad": 1, "descripcion": "Diseñada para brindar comodidad y estilo en cualquier ocasión. Ideal para quienes prefieren un estilo más sencillo y versátil.", "id_producto": 5, "imagen_url": "img/Empresa/producto_5.jpg", "nombre": "Camiseta unisex sin estampado color blanco", "precio": 50000.0, "subtotal": 50000.0}, {"cantidad": 1, "descripcion": "Diseñada para brindar comodidad y estilo en cualquier ocasión. Ideal para quienes prefieren un estilo más sencillo y versátil.", "id_producto": 6, "imagen_url": "img/Empresa/producto_6.jpg", "nombre": "Camiseta unisex color verde", "precio": 50000.0, "subtotal": 50000.0}, {"cantidad": 1, "descripcion": "Diseñada para brindar comodidad y estilo en cualquier ocasión. Disponible en versiones con camuflado, que incluyen diseños representativos y gráficos alusivos a la institución.", "id_producto": 3, "imagen_url": "img/Empresa/producto_3.jpg", "nombre": "Camiseta unisex con camuflado", "precio": 100000.0, "subtotal": 100000.0}]
cs_test_a1ABTwsbGavJ6dVQGYy4zsxi25eeS1AfHsHtyWt8O0wGKSvS6K0aeIKtRp	julio11916@gmail.com		a74506b29f638fb8d65fc6716e408ef822ebf390ccf77212c55dddae5037cd01	250000.00	creado	\N	2026-04-07 17:22:37.612763-05	2026-04-07 17:22:37.612763-05	[{"cantidad": 1, "descripcion": "Diseñada para brindar comodidad y estilo en cualquier ocasión. Ideal para quienes prefieren un estilo más sencillo y versátil.", "id_producto": 4, "imagen_url": "img/Empresa/producto_4.jpg", "nombre": "Camiseta unisex sin estampado color negro", "precio": 50000.0, "subtotal": 50000.0}, {"cantidad": 1, "descripcion": "Diseñada para brindar comodidad y estilo en cualquier ocasión. Ideal para quienes prefieren un estilo más sencillo y versátil.", "id_producto": 5, "imagen_url": "img/Empresa/producto_5.jpg", "nombre": "Camiseta unisex sin estampado color blanco", "precio": 50000.0, "subtotal": 50000.0}, {"cantidad": 1, "descripcion": "Diseñada para brindar comodidad y estilo en cualquier ocasión. Ideal para quienes prefieren un estilo más sencillo y versátil.", "id_producto": 6, "imagen_url": "img/Empresa/producto_6.jpg", "nombre": "Camiseta unisex color verde", "precio": 50000.0, "subtotal": 50000.0}, {"cantidad": 1, "descripcion": "Diseñada para brindar comodidad y estilo en cualquier ocasión. Disponible en versiones con camuflado, que incluyen diseños representativos y gráficos alusivos a la institución.", "id_producto": 3, "imagen_url": "img/Empresa/producto_3.jpg", "nombre": "Camiseta unisex con camuflado", "precio": 100000.0, "subtotal": 100000.0}]
cs_test_a1vAI0PHPbgpeeYsxTcCZ1JztOMGCok9tos3kdxEs7B0TmMPXFXmPkiQmj	julio@gmail.com		38102666268463674a52145b1deff6f66edfd7f25e856697a392cbf08ef8b56f	80000.00	creado	\N	2026-04-09 00:23:10.384839-05	2026-04-09 00:23:10.384839-05	[{"cantidad": 1, "descripcion": "Camiseta manga larga cómoda y resistente. Ideal para climas frescos y actividades diarias.", "id_producto": 11, "imagen_url": "img/Empresa/producto_11.jpg", "nombre": "Camiseta unisex manga larga sin estampado color negro", "precio": 80000.0, "subtotal": 80000.0, "talla": "M"}]
cs_test_a1zrJ1d624hOfv3qBVOvA3LDnugMYJRh8P7p0gH08QJx8iqIUYpKysRBJX	julio@gmail.com		38102666268463674a52145b1deff6f66edfd7f25e856697a392cbf08ef8b56f	80000.00	creado	\N	2026-04-09 00:27:38.147213-05	2026-04-09 00:27:38.147213-05	[{"cantidad": 1, "descripcion": "Camiseta manga larga cómoda y resistente. Ideal para climas frescos y actividades diarias.", "id_producto": 11, "imagen_url": "img/Empresa/producto_11.jpg", "nombre": "Camiseta unisex manga larga sin estampado color negro", "precio": 80000.0, "subtotal": 80000.0, "talla": "M"}]
cs_test_a1LmtoD4yWSi4ilxy9vuinAT7v9iUtv6eu61b2D4BWU2JVFgvvo2pJS5lW	julio@gmail.com		0d9a9b0b644b8bfeb9bbc2363fc0c476ba7e7e39fadc4f9c8273be70eee452ca	80000.00	pagado	49	2026-04-09 00:36:30.909931-05	2026-04-09 00:44:05.021227-05	[{"cantidad": 1, "descripcion": "Camiseta manga larga cómoda y resistente. Ideal para climas frescos y actividades diarias.", "id_producto": 11, "imagen_url": "img/Empresa/producto_11.jpg", "nombre": "Camiseta unisex manga larga sin estampado color negro", "precio": 80000.0, "subtotal": 80000.0, "talla": "XXXL"}]
cs_test_a1Vh2vTLokUUbl3WV4HQI5zSFC9dmwlj3yS2ivkV9uet4w6Czd0TyLjgkC	julio@gmail.com		55102327574194b803a3da816a12767076732310bf41df4cc18a7e735719e6ec	160000.00	creado	\N	2026-04-16 16:10:15.334553-05	2026-04-16 16:10:15.334553-05	[{"cantidad": 1, "descripcion": "Prenda superior del uniforme. Se caracteriza por su diseño estructurado, funcional y representativo, pensado para brindar una apariencia formal y profesional.", "id_producto": 13, "imagen_url": "img/Empresa/producto_13.jpg", "nombre": "Guerrera", "precio": 160000.0, "subtotal": 160000.0, "talla": "M"}]
cs_test_a1aASL7zo0qS4tkYt7OuwZVCSRZ2HmLvX0OzcWUI2uBWPo1po9U2oFjHhc	julio@gmail.com		55102327574194b803a3da816a12767076732310bf41df4cc18a7e735719e6ec	160000.00	creado	\N	2026-04-16 16:10:15.536881-05	2026-04-16 16:10:15.536881-05	[{"cantidad": 1, "descripcion": "Prenda superior del uniforme. Se caracteriza por su diseño estructurado, funcional y representativo, pensado para brindar una apariencia formal y profesional.", "id_producto": 13, "imagen_url": "img/Empresa/producto_13.jpg", "nombre": "Guerrera", "precio": 160000.0, "subtotal": 160000.0, "talla": "M"}]
cs_test_a1DhWMAL8H0HRNF5Yi74iveYHY3VgZG5HtGRYCLqyKmyCWrbxWmTiNX1cx	julio@gmail.com		55102327574194b803a3da816a12767076732310bf41df4cc18a7e735719e6ec	160000.00	pagado	50	2026-04-16 16:29:23.225784-05	2026-04-16 16:30:04.186984-05	[{"cantidad": 1, "descripcion": "Prenda superior del uniforme. Se caracteriza por su diseño estructurado, funcional y representativo, pensado para brindar una apariencia formal y profesional.", "id_producto": 13, "imagen_url": "img/Empresa/producto_13.jpg", "nombre": "Guerrera", "precio": 160000.0, "subtotal": 160000.0, "talla": "M"}]
cs_test_a131u779f8ytcmh1y9iOu0Azaq22Ox4injhfODxUyBJXugJKnBQd87s6s1	julio@gmail.com		5506a3cf0b9884528f019ea1715f993f13ed8b48a32b0c8cc17fe68fb3dba3dc	50000.00	pagado	53	2026-04-16 18:42:38.085818-05	2026-04-16 18:45:10.937583-05	[{"cantidad": 1, "descripcion": "Diseñada para brindar comodidad y estilo en cualquier ocasión. Ideal para quienes prefieren un estilo más sencillo y versátil.", "id_producto": 4, "imagen_url": "img/Empresa/producto_4.jpg", "nombre": "Camiseta unisex sin estampado color negro", "precio": 50000.0, "subtotal": 50000.0, "talla": "S"}]
cs_test_a1viXGwU38ndZ6IYIfF4qEe0SKtwLfsTjCIYK7nHGm483owgG0hWeJf0TI	julio@gmail.com		5ad2293156c6db8b023159773f428428180ca6be1229475981fef0c18037449f	50000.00	creado	\N	2026-04-22 13:47:45.574711-05	2026-04-22 13:47:45.574711-05	[{"cantidad": 1, "descripcion": "Diseñada para brindar comodidad y estilo en cualquier ocasión. Ideal para quienes prefieren un estilo más sencillo y versátil.", "id_producto": 4, "imagen_url": "img/Empresa/producto_4_1.jpg", "nombre": "Camiseta unisex sin estampado color negro", "precio": 50000.0, "subtotal": 50000.0, "talla": "S"}]
cs_test_a1cqlM1Jx5GDt2VPER9HcqlQFIryuXxxJNOcrDs3v7SIlFHaiF3qZI4TEX	julio@gmail.com		5ad2293156c6db8b023159773f428428180ca6be1229475981fef0c18037449f	50000.00	creado	\N	2026-04-29 14:54:38.055912-05	2026-04-29 14:54:38.055912-05	[{"cantidad": 1, "descripcion": "Diseñada para brindar comodidad y estilo en cualquier ocasión. Ideal para quienes prefieren un estilo más sencillo y versátil.", "id_producto": 4, "imagen_url": "img/Empresa/producto_4_1.jpg", "nombre": "Camiseta unisex sin estampado color negro", "precio": 50000.0, "subtotal": 50000.0, "talla": "S"}]
cs_test_a1roFiWVRRRVQyKukdVJ5oKrUI8PQRoDeqrJ3nfDhgt6ZtZE1h5PurG0Ar	julio@gmail.com		85af84fede680296664934685e6c7506929f5854aaac5001e9d6ca816e99ecc0	50000.00	creado	\N	2026-04-30 02:08:10.189483-05	2026-04-30 02:08:10.189483-05	[{"cantidad": 1, "descripcion": "Diseñada para brindar comodidad y estilo en cualquier ocasión. Ideal para quienes prefieren un estilo más sencillo y versátil.", "id_producto": 4, "imagen_url": "img/Empresa/producto_4_1.jpg", "nombre": "Camiseta unisex sin estampado color negro", "precio": 50000.0, "subtotal": 50000.0, "talla": "XL"}]
cs_test_a1PYwnfIAWTxF4UOqlLVyTdgFACKMU3gBGYEPO7N0Diua7Yb8sc2Zxh5b1	julio@gmail.com		e4ba91d714262d32c17ddf8232ab33f777f7092c22900d16fa4936a444173bce	12000.00	pagado	58	2026-05-01 13:35:48.515167-05	2026-05-01 13:36:20.284808-05	[{"cantidad": 1, "descripcion": "Identidad: Policia | Color: Azul Noche | Técnica: Bordado | Estampado: Ninguno | Rango: drago | Fecha contingencia: 2026-05-01", "id_orden_personalizada": 11, "id_producto": 0, "imagen_url": "img/personalizadas/gafete_preview_20260501_132035_679521_ea5df843.png", "nombre": "Prenda personalizada - Gafete de nombre o apellido", "personalizado": true, "precio": 12000.0, "subtotal": 12000.0, "talla": "L"}]
cs_test_a15jE1YHQWlscMveSc2kXxTdfVsYAmzbJm9ABkY3C6r96ZYdaW00khlMw1	julio@gmail.com		4b66a3672d2f2324051adfd50143c6cdd919b7e4957395b8d94456500e6c66f2	100000.00	creado	\N	2026-05-12 13:20:51.768016-05	2026-05-12 13:20:51.768016-05	[{"cantidad": 1, "descripcion": "Diseñada para brindar comodidad y estilo en cualquier ocasión. Disponible en versiones con camuflado, que incluyen diseños representativos y gráficos alusivos a la institución.", "id_producto": 3, "imagen_url": "img/Empresa/producto_3_1.jpg", "nombre": "Camiseta unisex con camuflado", "precio": 100000.0, "subtotal": 100000.0, "talla": "L"}]
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.usuarios (id_usuario, nombre, email, password_hash, rol, estado, fecha_registro, email_verified, verification_code, verification_code_expiry, reset_token, reset_token_expiry, password_change_code, password_change_code_expiry, telefono, direccion, terminos_identidad_aceptados, terminos_identidad_fecha) FROM stdin;
12	julio cesar otalvaro sanchez	julio11916@gmail.com	scrypt:32768:8:1$gyCyGHOJIsL3kD7o$bd88fa0a8f98b2af0afee2c62c5bacbe89cec318d32fab3d1974769017c11c330e0427854170c5023db442262aedf508790a7b20dbb48cf70e8638eae9025b94	normal	activo	2026-04-02 18:52:23	t		\N		\N	906298	2026-04-08 14:38:15-05	nan	diagonal7#1-28 rocio parte alta	t	2026-05-22 14:06:41-05
13	jilmer	c65238944@gmail.com	scrypt:32768:8:1$omQpXag2INR8SgL1$e9acff045519d2bd46f7c429390c1189e2e02abc29b7a9e6d076d20a98f667464472ed40b3d14253739785c0f955d5eb7cae9a10abfd0872a4f933ef60cbaa9a	normal	activo	2026-04-03 11:55:51	t		\N		\N		\N	\N	\N	f	\N
1	Nico	nico@gmail.com	scrypt:32768:8:1$3oBOoha9lG4w3a2E$7b2225fd3dfb693854e6664a153332f011956c20a8c756e57a7e5aeebe20a83ee83fb67aca68c2927b54e8be91ea3574d5ed0b942afecd0518d372a17f0aec1d	admin	activo	2026-02-06 14:55:32	f		\N		\N		\N	\N	\N	t	\N
2	Julio	julio@gmail.com	scrypt:32768:8:1$LelqMtI3TmTMyzOE$bebb09284b93879bd665d266791c9d2b8fb8ddd46c90620e350e6cfbce10695ae1bdcfbe52fae9a7cd79af1bec0e0bacea6a1dc725a5c757f07ad6d499b4e29b	normal	activo	2026-02-06 14:55:32	f	801703	2026-03-06 14:07:29		\N		\N	3219047309	diagonal7	t	\N
3	Alvaréx Freo	alv@gmail.com	admin	normal	activo	2026-02-06 16:40:07	f		\N		\N		\N	\N	\N	f	\N
4	jilmer	hola@gmail.com	admin	admin	activo	2026-02-20 15:47:06	f		\N		\N		\N	\N	\N	f	\N
5	Isabel	hola3@gmail.com	123456789	normal	inactivo	2026-02-20 15:47:36	f		\N		\N		\N	\N	\N	f	\N
6	Tatiana Rivera	tatis@gmail.com	admin	normal	activo	2026-02-25 22:35:53	f		\N		\N		\N	\N	\N	f	\N
7	Tatiana Rivera	tr3303419@gmail.com	admin	normal	inactivo	2026-02-26 22:54:23	f		\N		\N		\N	\N	\N	f	\N
8	David	david@gmail.com	4321	normal	activo	2026-03-04 19:37:39	f		\N		\N		\N	\N	\N	f	\N
9	David	rodriguezsierradavidsantiago@gmail.com	54321	normal	activo	2026-03-04 22:56:35	t	844313	2026-03-04 23:45:18		\N		\N	\N	\N	f	\N
10	Catalina rodriguez	catar@gmail.com	Catalina1.	normal	activo	2026-03-13 15:30:56	f		\N		\N		\N	\N	\N	f	\N
11	julio cesar otalvaro sanchez	somosdecimob2020@gmail.com	scrypt:32768:8:1$xXEaOs4nnTL7BFLU$2c58839161a345654ccc41bb69e2d88185b4082bc0f5b443e92a7b294b9c36029c515fa8f46b0d6dbced71ecafe5edc07def0dc5089c22658654c6006d70dd50	normal	activo	2026-04-02 16:50:05	t		\N		\N		\N	\N	\N	f	\N
\.


--
-- Name: categoria_producto_id_categoria_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.categoria_producto_id_categoria_seq', 44, true);


--
-- Name: orden_personalizada_id_orden_personalizada_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.orden_personalizada_id_orden_personalizada_seq', 1, true);


--
-- Name: carrito_usuario carrito_usuario_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.carrito_usuario
    ADD CONSTRAINT carrito_usuario_pkey PRIMARY KEY (email);


--
-- Name: categoria_producto categoria_producto_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categoria_producto
    ADD CONSTRAINT categoria_producto_pkey PRIMARY KEY (id_categoria);


--
-- Name: orden_personalizada orden_personalizada_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orden_personalizada
    ADD CONSTRAINT orden_personalizada_pkey PRIMARY KEY (id_orden_personalizada);


--
-- Name: orden_personalizada_precio orden_personalizada_precio_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orden_personalizada_precio
    ADD CONSTRAINT orden_personalizada_precio_pkey PRIMARY KEY (producto);


--
-- Name: stripe_checkout stripe_checkout_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stripe_checkout
    ADD CONSTRAINT stripe_checkout_pkey PRIMARY KEY (session_id);


--
-- PostgreSQL database dump complete
--

\unrestrict 7dhnipAUeOD2jeHEeo0eEuSitJFfepVnYAeJtJ7mTGSQAqNchjO6DkblEygH0Sc

