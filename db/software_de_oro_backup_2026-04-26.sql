--
-- PostgreSQL database dump
--

\restrict ap4BvOUVDuY49qGNNwD1iOQMWkjbeLNlLlncPkmAAXKMtdcG2mFgqBRVT351Mb6

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
ALTER TABLE IF EXISTS ONLY public.categoria_producto DROP CONSTRAINT IF EXISTS categoria_producto_pkey;
ALTER TABLE IF EXISTS ONLY public.carrito_usuario DROP CONSTRAINT IF EXISTS carrito_usuario_pkey;
ALTER TABLE IF EXISTS public.categoria_producto ALTER COLUMN id_categoria DROP DEFAULT;
DROP TABLE IF EXISTS public.usuarios;
DROP TABLE IF EXISTS public.stripe_checkout;
DROP TABLE IF EXISTS public.registros;
DROP TABLE IF EXISTS public.promociones;
DROP TABLE IF EXISTS public.producto;
DROP TABLE IF EXISTS public.pedidos;
DROP TABLE IF EXISTS public.pagos;
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
    direccion text
);


--
-- Name: categoria_producto id_categoria; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categoria_producto ALTER COLUMN id_categoria SET DEFAULT nextval('public.categoria_producto_id_categoria_seq'::regclass);


--
-- Data for Name: carrito_usuario; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.carrito_usuario (email, carrito_json, updated_at) FROM stdin;
prueba.carrito@demo.local	[{"id_producto": 101, "nombre": "Prueba", "cantidad": 2, "precio": 15000.0, "subtotal": 30000.0}]	2026-04-07 13:46:43.954571-05
demo.logout@local.test	[{"cantidad": 3, "id_producto": 7, "nombre": "Demo", "precio": 2000.0, "subtotal": 6000.0}]	2026-04-07 13:47:46.466646-05
persistencia.test@local.test	[{"cantidad": 2, "id_producto": 1, "nombre": "Item A", "precio": 10000.0, "subtotal": 20000.0}]	2026-04-07 14:00:29.504371-05
img.test@local.test	[{"cantidad": 1, "id_producto": 1, "nombre": "Producto test", "precio": 10000.0, "subtotal": 10000.0, "imagen_url": "img/Empresa/producto_1.jpg", "descripcion": "Damn"}]	2026-04-07 14:25:41.012404-05
img2.test@local.test	[{"cantidad": 1, "id_producto": 1, "nombre": "X", "precio": 12000.0, "subtotal": 12000.0, "imagen_url": "img/Empresa/producto_1.jpg", "descripcion": "Damn"}]	2026-04-07 15:12:59.000695-05
julio@gmail.com	[{"id_producto": 4, "nombre": "Camiseta unisex sin estampado color negro", "descripcion": "Diseñada para brindar comodidad y estilo en cualquier ocasión. Ideal para quienes prefieren un estilo más sencillo y versátil.", "cantidad": 1, "precio": 50000.0, "subtotal": 50000.0, "talla": "S", "imagen_url": "img/Empresa/producto_4_1.jpg"}]	2026-04-22 19:54:52.641763-05
julio11916@gmail.com	[{"cantidad": 1, "descripcion": "Camiseta manga larga cómoda y resistente. Ideal para climas frescos y actividades diarias.", "id_producto": 11, "imagen_url": "img/Empresa/producto_11.jpg", "nombre": "Camiseta unisex manga larga sin estampado color negro", "precio": 80000.0, "subtotal": 80000.0, "talla": "XS"}]	2026-04-12 18:09:51.867534-05
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
\.


--
-- Data for Name: pagos; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.pagos (id_pago, id_pedido, monto, metodo_pago, fecha_pago, estado_pago, id_promo, codigo_promo, tipo_descuento, valor_descuento, monto_descuento, comprobante_url) FROM stdin;
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
36	36	50000	qr	2026-03-25 20:29:37	aprobado	1		porcentaje	50	50000	
46	48	80000	transferencia	2026-04-09 00:27:50	aprobado				0	0	
47	49	80000	tarjeta	2026-04-09 00:44:04	aprobado				0	0	
37	37	50000	efectivo	2026-03-27 14:14:32	aprobado	1		porcentaje	50	50000	
44	46	10000	tarjeta	2026-04-08 21:47:43	aprobado				0	0	
45	47	10000	tarjeta	2026-04-08 21:54:31	aprobado				0	0	
38	38	50000	transferencia	2026-03-27 16:51:25	aprobado	1		porcentaje	50	50000	
39	39	250000	transferencia	2026-04-08 14:36:43	aprobado				0	0	
\.


--
-- Data for Name: pedidos; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.pedidos (id_pedido, id_usuario, fecha_pedido, estado, cliente_telefono, cliente_direccion) FROM stdin;
56	2	2026-04-22 16:38:40	confirmado	3204567896	kjhgliuguykftrc
49	2	2026-04-09 00:44:04	pendiente		
50	2	2026-04-16 16:30:03	enviado		
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
30	nico@gmail.com	2026-03-25 19:10:26	completado		
31	nico@gmail.com	2026-03-25 19:23:24	completado		
32	nico@gmail.com	2026-03-25 19:33:13	completado		
33	nico@gmail.com	2026-03-25 19:35:47	completado		
34	nico@gmail.com	2026-03-25 19:40:22	completado		
35	nico@gmail.com	2026-03-25 19:56:06	completado		
36	nico@gmail.com	2026-03-25 20:29:37	completado		
37	nico@gmail.com	2026-03-27 14:14:32	completado		
38	nico@gmail.com	2026-03-27 16:51:25	completado		
39	12	2026-04-08 14:36:43	pendiente		
40	12	2026-04-08 14:45:29	pendiente		
41	12	2026-04-08 14:46:15	pendiente		
42	nico@gmail.com	2026-04-08 16:20:10	completado		
43	nico@gmail.com	2026-04-08 16:48:08	completado		
44	nico@gmail.com	2026-04-08 17:11:59	completado		
45	nico@gmail.com	2026-04-08 18:06:49	completado		
46	nico@gmail.com	2026-04-08 21:47:43	completado		
47	nico@gmail.com	2026-04-08 21:54:31	completado		
48	2	2026-04-09 00:27:50	pendiente		
\.


--
-- Data for Name: producto; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.producto (id_producto, nombre, descripcion, precio, stock, id_categoria, fuerza, intendencia, imagen_url, eliminado, destacado_dashboard) FROM stdin;
2	Armando Estaban Quito	puro de corazon	100000	100	1	Gaula	Camibusos	img/Empresa/producto_2_1.jpg	t	f
3	Camiseta unisex con camuflado	Diseñada para brindar comodidad y estilo en cualquier ocasión. Disponible en versiones con camuflado, que incluyen diseños representativos y gráficos alusivos a la institución.	100000	10	1	Ejercito	Camuflados	img/Empresa/producto_3_1.jpg	f	t
4	Camiseta unisex sin estampado color negro	Diseñada para brindar comodidad y estilo en cualquier ocasión. Ideal para quienes prefieren un estilo más sencillo y versátil.	50000	9	1	Ejercito	Busos	img/Empresa/producto_4.jpg	f	t
5	Camiseta unisex sin estampado color blanco	Diseñada para brindar comodidad y estilo en cualquier ocasión. Ideal para quienes prefieren un estilo más sencillo y versátil.	50000	10	1	Ejercito	Busos	img/Empresa/producto_5.jpg	f	t
6	Camiseta unisex color verde	Diseñada para brindar comodidad y estilo en cualquier ocasión. Ideal para quienes prefieren un estilo más sencillo y versátil.	50000	10	1	Ejercito	Busos	img/Empresa/producto_6.jpg	f	t
7	Pantalón	Pantalón inspirado en el uniforme del Ejército Nacional de Colombia, diseñado para brindar resistencia, comodidad y funcionalidad en actividades diarias.	120000	10	1	Ejercito	Camuflados	img/Empresa/producto_7.jpg	f	t
8	Guerrera	Prenda superior utilizado en el uniforme. Caracterizado por su diseño estructurado, funcional y representativo, pensado para brindar una apariencia formal y profesional.	160000	10	1	Ejercito	Camuflados	img/Empresa/producto_8.jpg	f	t
9	Camiseta unisex sin estampado color negro	Diseñada para brindar comodidad y estilo en cualquier ocasión. Ideal para quienes prefieren un estilo más sencillo y versátil.	50000	0	1	Policia	Busos	img/Empresa/producto_9_1.jpg	f	t
10	Camiseta unisex sin estampado color blanco	Diseñada para brindar comodidad y estilo en cualquier ocasión. Ideal para quienes prefieren un estilo más sencillo y versátil.	50000	10	1	Policia	Busos	img/Empresa/producto_10.jpg	f	t
11	Camiseta unisex manga larga sin estampado color negro	Camiseta manga larga cómoda y resistente. Ideal para climas frescos y actividades diarias.	80000	10	1	Ejercito	Camibusos	img/Empresa/producto_11.jpg	f	t
12	Camiseta unisex manga larga sin estampado color negro	Camiseta manga larga cómoda y resistente. Ideal para climas frescos y actividades diarias.	80000	10	1	Policia	Camibusos	img/Empresa/producto_12.jpg	f	t
13	Guerrera	Prenda superior del uniforme. Se caracteriza por su diseño estructurado, funcional y representativo, pensado para brindar una apariencia formal y profesional.	160000	7	1	Gaula	Camuflados	img/Empresa/producto_13.jpg	f	f
14	Pantalón	Pantalón inspirado en el uniforme del gaula, diseñado para brindar resistencia, comodidad y funcionalidad en actividades diarias.	180000	10	1	Gaula	Camuflados	img/Empresa/producto_14.jpg	f	f
15	Camiseta unisex sin estampado color negro	Camiseta cómoda y resistente. Ideal para climas frescos y actividades diarias.	50000	10	1	Gaula	Busos	img/Empresa/producto_15.jpg	f	f
16	Camiseta unisex sin estampado color blanco	Camiseta cómoda y resistente. Ideal para climas frescos y actividades diarias.	50000	10	1	Gaula	Busos	img/Empresa/producto_16.jpg	f	f
17	Guerrera	Prenda superior del uniforme. Se caracteriza por su diseño estructurado, funcional y representativo, pensado para brindar una apariencia formal y profesional.	160000	10	1	Policia	Camuflados	img/Empresa/producto_17.jpg	f	t
18	Pantalón	Pantalón inspirado en el uniforme de la policía, diseñado para brindar resistencia, comodidad y funcionalidad en actividades diarias.	180000	10	1	Policia	Camuflados	img/Empresa/producto_18.jpg	f	t
19	Moño	Moño decorativo inspirado en accesorios formales utilizados en uniformes institucionales. Perfecto para completar un estilo elegante.	10000	10	1	Policia	Panoletas	img/Empresa/producto_19.jpg	f	t
20	Pañoleta policia sin estampado	Diseñada para brindar comodidad y estilo en cualquier ocasión. Ideal para quienes prefieren un estilo más sencillo y versátil.	60000	10	1	Policia	Panoletas	img/Empresa/producto_20.jpg	f	t
1	Camiseta mallada	Damn	60	10	1	Policia	Busos	img/Empresa/producto_1.jpg	t	f
\.


--
-- Data for Name: promociones; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.promociones (id_promo, nombre, descripcion, tipo_descuento, valor_descuento, id_producto, codigo, fecha_inicio, fecha_fin, activo) FROM stdin;
1	Promo Camiseta unisex con camuflado		porcentaje	50	3		2026-03-25	2026-03-27	t
2	Promo Guerrera		valor_fijo	140000	13		2026-03-25	2026-03-25	t
\.


--
-- Data for Name: registros; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.registros (id_registro, id_usuario, accion, fecha_accion) FROM stdin;
121	nico@gmail.com	Promocion creada: Promo Guerrera\n- producto ID: 13\n- descuento: COP 140.000,00\n- codigo: N/A	2026-03-25 13:22:32
216	julio11916@gmail.com	Creo pedido #39 con 4 producto(s) por COP 250.000,00	2026-04-08 14:36:43
28	nico@gmail.com	Inicio de sesión exitoso	2026-03-14 16:08:55
29	julio@gmail.com	Inicio de sesión exitoso	2026-03-16 12:43:10
30	julio@gmail.com	Inicio de sesión exitoso	2026-03-16 17:24:26
31	nico@gmail.com	Inicio de sesión exitoso	2026-03-16 21:17:20
36	nico@gmail.com	Inicio de sesion exitoso	2026-03-17 16:50:35
37	julio@gmail.com	Inicio de sesion exitoso	2026-03-17 16:55:01
38	nico@gmail.com	Inicio de sesion exitoso	2026-03-17 17:03:36
47	nico@gmail.com	Elimino producto: Armando Estaban Quito (ID 2)	2026-03-18 13:23:43
92	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color negro' (ID 9)\n- precio: COP 50,00 -> COP 50.000,00	2026-03-24 14:43:31
94	nico@gmail.com	Actualizo producto 'Camiseta unisex manga larga sin estampado color negro' (ID 11)\n- precio: COP 80,00 -> COP 80.000,00	2026-03-24 14:43:53
254	nico@gmail.com	Actualizo estado de pedido #53: enviado -> entregado	2026-04-16 18:46:44
95	nico@gmail.com	Actualizo producto 'Camiseta unisex manga larga sin estampado color negro' (ID 12)\n- precio: COP 80,00 -> COP 80.000,00	2026-03-24 14:44:49
96	nico@gmail.com	Actualizo producto 'Guerrera' (ID 13)\n- precio: COP 160,00 -> COP 160.000,00	2026-03-24 14:44:58
97	nico@gmail.com	Actualizo producto 'Pantalón' (ID 14)\n- precio: COP 180,00 -> COP 180.000,00	2026-03-24 14:45:15
98	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color negro' (ID 15)\n- precio: COP 50,00 -> COP 50.000,00	2026-03-24 14:45:29
151	nico@gmail.com	Actualizo producto 'Camiseta unisex con camuflado' (ID 3)\n- stock: 9 -> 10	2026-03-25 18:09:10
99	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color blanco' (ID 16)\n- precio: COP 50,00 -> COP 50.000,00	2026-03-24 14:45:40
100	nico@gmail.com	Actualizo producto 'Guerrera' (ID 17)\n- precio: COP 160,00 -> COP 160.000,00	2026-03-24 14:45:51
101	nico@gmail.com	Actualizo producto 'Pañoleta policia sin estampado' (ID 20)\n- precio: COP 60,00 -> COP 60.000,00	2026-03-24 14:46:02
102	nico@gmail.com	Actualizo producto 'Pañoleta policia sin estampado' (ID 20)\n- sin cambios detectados	2026-03-24 14:46:02
103	nico@gmail.com	Actualizo producto 'Moño' (ID 19)\n- precio: COP 20,00 -> COP 10.000,00	2026-03-24 14:46:22
104	nico@gmail.com	Actualizo producto 'Pantalón' (ID 18)\n- precio: COP 180,00 -> COP 180.000,00	2026-03-24 14:46:32
105	julio@gmail.com	Inicio de sesion exitoso	2026-03-24 14:47:22
106	nico@gmail.com	Inicio de sesion exitoso	2026-03-24 14:51:37
107	nico@gmail.com	Restauro producto: Armando Estaban Quito (ID 2)	2026-03-24 16:27:08
108	nico@gmail.com	Actualizo producto 'Armando Estaban Quito' (ID 2)\n- sin cambios detectados	2026-03-24 16:28:18
113	nico@gmail.com	Inicio de sesion exitoso	2026-03-25 13:07:08
114	nico@gmail.com	Promocion creada: Promo Camiseta unisex con camuflado\n- producto ID: 3\n- descuento: 50.00%\n- codigo: N/A	2026-03-25 13:11:43
115	nico@gmail.com	Promocion desactivada: Promo Camiseta unisex con camuflado	2026-03-25 13:12:28
117	nico@gmail.com	Promocion desactivada: Promo Camiseta unisex con camuflado	2026-03-25 13:12:36
118	nico@gmail.com	Promocion activada: Promo Camiseta unisex con camuflado	2026-03-25 13:12:46
119	julio@gmail.com	Inicio de sesion exitoso	2026-03-25 13:16:14
120	nico@gmail.com	Inicio de sesion exitoso	2026-03-25 13:20:35
217	julio11916@gmail.com	Creo pedido #40 con 1 producto(s) por COP 50.000,00	2026-04-08 14:45:29
122	nico@gmail.com	POS registro venta #15 por COP 10.000,00 (1 producto(s))\n- total bruto: COP 10.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 092893264\n- teléfono: 3204567896	2026-03-25 15:12:42
123	nico@gmail.com	Inicio de sesión exitoso	2026-03-25 15:46:09
124	nico@gmail.com	POS registro venta #16 por COP 10.000,00 (1 producto(s))\n- total bruto: COP 10.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 15:46:55
125	nico@gmail.com	POS registro venta #17 por COP 10.000,00 (1 producto(s))\n- total bruto: COP 10.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 15:47:56
127	nico@gmail.com	POS registro venta #18 por COP 10.000,00 (1 producto(s))\n- total bruto: COP 10.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 16:19:50
128	nico@gmail.com	POS registro venta #19 por COP 10.000,00 (1 producto(s))\n- total bruto: COP 10.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 16:28:10
129	nico@gmail.com	POS registro venta #20 por COP 10.000,00 (1 producto(s))\n- total bruto: COP 10.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 16:43:35
130	nico@gmail.com	Inicio de sesión exitoso	2026-03-25 17:08:15
131	nico@gmail.com	Inicio de sesión exitoso	2026-03-25 17:08:16
132	nico@gmail.com	POS registro venta #21 por COP 10.000,00 (1 producto(s))\n- total bruto: COP 10.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 17:08:48
173	nico@gmail.com	Actualizo producto 'Camiseta unisex con camuflado' (ID 3)\n- stock: 4 -> 10	2026-03-25 20:30:48
175	nico@gmail.com	Inicio de sesión exitoso	2026-03-27 13:22:05
133	nico@gmail.com	POS registro venta #22 por COP 10.000,00 (1 producto(s))\n- total bruto: COP 10.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 17:17:22
134	nico@gmail.com	POS registro venta #23 por COP 10.000,00 (1 producto(s))\n- total bruto: COP 10.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 17:30:05
23	julio@gmail.com	Inicio de sesión exitoso	2026-03-13 15:29:52
24	catar@gmail.com	Nuevo usuario registrado: Catalina rodriguez	2026-03-13 15:30:56
79	julio@gmail.com	Inicio de sesion exitoso	2026-03-23 17:20:06
80	nico@gmail.com	Inicio de sesion exitoso	2026-03-23 17:20:19
81	julio@gmail.com	Inicio de sesion exitoso	2026-03-23 17:22:56
82	julio@gmail.com	Inicio de sesion exitoso	2026-03-24 14:19:10
83	julio@gmail.com	Inicio de sesion exitoso	2026-03-24 14:37:07
84	nico@gmail.com	Inicio de sesion exitoso	2026-03-24 14:39:04
85	nico@gmail.com	Actualizo producto 'Camiseta unisex con camuflado' (ID 3)\n- precio: COP 100,00 -> COP 100.000,00	2026-03-24 14:39:38
86	nico@gmail.com	Inicio de sesion exitoso	2026-03-24 14:41:37
87	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color negro' (ID 4)\n- precio: COP 50,00 -> COP 50.000,00	2026-03-24 14:41:57
88	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color blanco' (ID 5)\n- precio: COP 50,00 -> COP 50.000,00	2026-03-24 14:42:20
89	nico@gmail.com	Actualizo producto 'Camiseta unisex color verde' (ID 6)\n- precio: COP 50,00 -> COP 50.000,00	2026-03-24 14:42:31
90	nico@gmail.com	Actualizo producto 'Pantalón' (ID 7)\n- precio: COP 120,00 -> COP 120.000,00	2026-03-24 14:42:41
91	nico@gmail.com	Actualizo producto 'Guerrera' (ID 8)\n- precio: COP 160,00 -> COP 160.000,00	2026-03-24 14:42:53
188	admin	Nuevo usuario registrado y verificado: julio cesar otalvaro sanchez	2026-04-02 18:52:23
189	admin	Enlace de recuperacion enviado a nachoher072+recoverytest1775230812@gmail.com	2026-04-03 10:40:14
190	admin	Contrasena restablecida por recuperacion para nachoher072+recoverytest1775230812@gmail.com	2026-04-03 10:40:14
191	nachoher072+recoverytest1775230812@gmail.com	Inicio de sesión exitoso	2026-04-03 10:40:14
194	somosdecimob2020@gmail.com	Inicio de sesión exitoso	2026-04-03 11:26:49
195	julio@gmail.com	Inicio de sesión exitoso	2026-04-03 11:31:17
196	admin	Nuevo usuario registrado y verificado: jilmer	2026-04-03 11:55:51
197	nico@gmail.com	Inicio de sesión exitoso	2026-04-03 12:20:55
198	nico@gmail.com	Inicio de sesión exitoso	2026-04-06 20:37:32
199	nico@gmail.com	Inicio de sesión exitoso	2026-04-06 22:30:20
200	julio11916@gmail.com	Inicio de sesión exitoso	2026-04-07 13:25:03
201	julio11916@gmail.com	Inicio de sesión exitoso	2026-04-07 13:28:04
202	julio11916@gmail.com	Inicio de sesión exitoso	2026-04-07 13:53:33
203	julio11916@gmail.com	Inicio de sesión exitoso	2026-04-07 14:11:49
204	julio11916@gmail.com	Inicio de sesión exitoso	2026-04-07 14:21:25
205	julio11916@gmail.com	Inicio de sesión exitoso	2026-04-07 14:39:38
206	julio@gmail.com	Inicio de sesión exitoso	2026-04-07 14:39:55
207	julio11916@gmail.com	Inicio de sesión exitoso	2026-04-07 14:43:12
208	julio11916@gmail.com	Inicio de sesiÃ³n exitoso	2026-04-08 13:12:32
209	julio11916@gmail.com	Usuario julio11916@gmail.com actualizo su perfil	2026-04-08 13:15:44
210	julio11916@gmail.com	Usuario julio11916@gmail.com cambiÃ³ su contraseÃ±a	2026-04-08 13:16:43
211	julio11916@gmail.com	Inicio de sesiÃ³n exitoso	2026-04-08 13:16:54
213	julio11916@gmail.com	Codigo de cambio de contrasena enviado a julio11916@gmail.com	2026-04-08 14:07:07
214	julio11916@gmail.com	Usuario julio11916@gmail.com cambio su contrasena con codigo de seguridad	2026-04-08 14:07:49
215	julio11916@gmail.com	Codigo de cambio de contrasena enviado a julio11916@gmail.com	2026-04-08 14:31:18
218	julio11916@gmail.com	Creo pedido #41 con 1 producto(s) por COP 50.000,00	2026-04-08 14:46:15
219	nico@gmail.com	Inicio de sesiÃƒÂ³n exitoso	2026-04-08 15:59:53
220	nico@gmail.com	Inicio de sesiÃƒÂ³n exitoso	2026-04-08 16:08:57
221	julio@gmail.com	Inicio de sesiÃƒÂ³n exitoso	2026-04-08 16:22:56
223	nico@gmail.com	POS registro venta #44 por COP 100.000,00 (1 producto(s))\n- total bruto: COP 100.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- telÃƒÂ©fono: 3204567896	2026-04-08 17:11:59
224	nico@gmail.com	Actualizo producto 'Camiseta unisex color verde' (ID 6)\n- stock: 4 -> 10	2026-04-08 18:02:58
225	nico@gmail.com	Actualizo producto 'Camiseta unisex con camuflado' (ID 3)\n- stock: 5 -> 10	2026-04-08 18:03:06
226	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color negro' (ID 4)\n- stock: 7 -> 10	2026-04-08 18:03:18
227	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color blanco' (ID 5)\n- stock: 9 -> 10	2026-04-08 18:03:24
228	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color blanco' (ID 5)\n- sin cambios detectados	2026-04-08 18:03:24
229	nico@gmail.com	POS registro venta #45 por COP 80.000,00 (1 producto(s))\n- total bruto: COP 80.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- telÃƒÂ©fono: 3204567896	2026-04-08 18:06:49
230	nico@gmail.com	POS registro venta #46 por COP 10.000,00 (1 producto(s))\n- total bruto: COP 10.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- telÃƒÂ©fono: 3204567896	2026-04-08 21:47:43
231	nico@gmail.com	POS registro venta #47 por COP 10.000,00 (1 producto(s))\n- total bruto: COP 10.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- telÃƒÂ©fono: 3204567896	2026-04-08 21:54:31
232	nico@gmail.com	Actualizo producto 'Moño' (ID 19)\n- stock: 8 -> 10	2026-04-08 21:55:28
233	julio@gmail.com	Inicio de sesión exitoso	2026-04-08 23:45:28
234	nico@gmail.com	Inicio de sesión exitoso	2026-04-09 00:02:43
22	nico@gmail.com	Inicio de sesión exitoso	2026-03-13 15:29:20
192	admin	Enlace de recuperacion enviado a somosdecimob2020@gmail.com	2026-04-03 11:24:56
240	julio11916@gmail.com	Inicio de sesión exitoso	2026-04-12 18:09:19
241	nico@gmail.com	Inicio de sesión exitoso	2026-04-16 12:49:34
150	nico@gmail.com	Actualizo producto 'Pañoleta policia sin estampado' (ID 20)\n- stock: 9 -> 10	2026-03-25 18:09:03
42	nico@gmail.com	Creo producto 'Camiseta unisex con camuflado' (ID 3)\n- precio: COP 100,00\n- stock: 10\n- fuerza: Ejercito\n- intendencia: Camuflados	2026-03-18 13:17:14
43	nico@gmail.com	Creo producto 'Camiseta unisex sin estampado color negro' (ID 4)\n- precio: COP 50,00\n- stock: 10\n- fuerza: Ejercito\n- intendencia: Busos	2026-03-18 13:21:36
44	julio@gmail.com	Inicio de sesion exitoso	2026-03-18 13:22:05
45	nico@gmail.com	Inicio de sesion exitoso	2026-03-18 13:22:49
46	nico@gmail.com	Elimino producto: Camiseta mallada (ID 1)	2026-03-18 13:23:37
48	nico@gmail.com	Creo producto 'Camiseta unisex sin estampado color blanco' (ID 5)\n- precio: COP 50,00\n- stock: 10\n- fuerza: Ejercito\n- intendencia: Busos	2026-03-18 13:29:21
49	nico@gmail.com	Creo producto 'Camiseta manga larga color verde' (ID 6)\n- precio: COP 50,00\n- stock: 10\n- fuerza: Ejercito\n- intendencia: Busos	2026-03-18 13:31:28
148	nico@gmail.com	Actualizo producto 'Pantalón' (ID 18)\n- stock: 9 -> 10	2026-03-25 18:08:47
50	nico@gmail.com	Actualizo producto 'Camiseta manga corta color verde' (ID 6)\n- nombre: 'Camiseta manga larga color verde' -> 'Camiseta manga corta color verde'	2026-03-18 13:33:21
112	nico@gmail.com	Elimino producto: Armando Estaban Quito (ID 2)	2026-03-24 21:41:00
109	nico@gmail.com	Actualizo producto 'Armando Estaban Quito' (ID 2)\n- sin cambios detectados	2026-03-24 16:48:24
110	julio@gmail.com	Inicio de sesion exitoso	2026-03-24 17:02:28
111	nico@gmail.com	Inicio de sesion exitoso	2026-03-24 17:08:32
51	nico@gmail.com	Actualizo producto 'Camiseta unisex manga corta color verde' (ID 6)\n- nombre: 'Camiseta manga corta color verde' -> 'Camiseta unisex manga corta color verde'	2026-03-18 13:33:34
52	nico@gmail.com	Actualizo producto 'Camiseta unisex color verde' (ID 6)\n- nombre: 'Camiseta unisex manga corta color verde' -> 'Camiseta unisex color verde'	2026-03-18 13:33:49
53	nico@gmail.com	Creo producto 'Pantalón' (ID 7)\n- precio: COP 120,00\n- stock: 10\n- fuerza: Ejercito\n- intendencia: Camuflados	2026-03-18 13:35:14
54	nico@gmail.com	Creo producto 'Guerrera' (ID 8)\n- precio: COP 160,00\n- stock: 10\n- fuerza: Ejercito\n- intendencia: Camuflados	2026-03-18 13:37:24
55	nico@gmail.com	Creo producto 'Camiseta unisex sin estampado color negro' (ID 9)\n- precio: COP 50,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Busos	2026-03-18 13:40:23
56	nico@gmail.com	Creo producto 'Camiseta unisex sin estampado color blanco' (ID 10)\n- precio: COP 50,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Busos	2026-03-18 13:41:20
57	nico@gmail.com	Creo producto 'Camiseta unisex manga larga sin estampado color negro' (ID 11)\n- precio: COP 80,00\n- stock: 10\n- fuerza: Ejercito\n- intendencia: Camibusos	2026-03-18 13:46:48
93	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color blanco' (ID 10)\n- precio: COP 50,00 -> COP 50.000,00	2026-03-24 14:43:39
58	nico@gmail.com	Creo producto 'Camiseta unisex manga larga sin estampado color negro' (ID 12)\n- precio: COP 80,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Camibusos	2026-03-18 13:47:35
116	nico@gmail.com	Promocion activada: Promo Camiseta unisex con camuflado	2026-03-25 13:12:28
59	nico@gmail.com	Creo producto 'Guerrera' (ID 13)\n- precio: COP 160,00\n- stock: 10\n- fuerza: Gaula\n- intendencia: Camuflados	2026-03-18 14:14:00
60	nico@gmail.com	Creo producto 'Pantalón' (ID 14)\n- precio: COP 180,00\n- stock: 10\n- fuerza: Gaula\n- intendencia: Camuflados	2026-03-18 14:15:35
61	nico@gmail.com	Creo producto 'Camiseta unisex sin estampado color negro' (ID 15)\n- precio: COP 50,00\n- stock: 10\n- fuerza: Gaula\n- intendencia: Busos	2026-03-18 14:18:51
62	nico@gmail.com	Creo producto 'Camiseta unisex sin estampado color blanco' (ID 16)\n- precio: COP 50,00\n- stock: 10\n- fuerza: Gaula\n- intendencia: Busos	2026-03-18 14:20:17
63	nico@gmail.com	Creo producto 'Guerrera' (ID 17)\n- precio: COP 160,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Camuflados	2026-03-18 14:23:44
64	nico@gmail.com	Creo producto 'Pantalón' (ID 18)\n- precio: COP 180,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Camuflados	2026-03-18 14:25:10
17	julio@gmail.com	Inicio de sesión exitoso	2026-03-11 15:33:52
18	julio@gmail.com	Inicio de sesión exitoso	2026-03-11 22:52:48
19	julio@gmail.com	Inicio de sesión exitoso	2026-03-13 14:37:21
21	julio@gmail.com	Inicio de sesión exitoso	2026-03-13 14:41:50
235	nico@gmail.com	Administrador actualizó prendas destacadas:\n- total destacadas: 5\n- ids: 6, 5, 4, 11, 8	2026-04-09 00:03:19
236	julio@gmail.com	Inicio de sesión exitoso	2026-04-09 00:03:54
237	julio@gmail.com	Creo pedido #48 con 1 producto(s) por COP 80.000,00	2026-04-09 00:27:50
256	nico@gmail.com	Inicio de sesión exitoso	2026-04-16 18:54:32
238	julio@gmail.com	Stripe confirmado. Pedido #49 creado por COP 80.000,00	2026-04-09 00:44:05
239	nico@gmail.com	Inicio de sesión exitoso	2026-04-12 18:09:03
242	nico@gmail.com	Actualizo producto 'Camiseta unisex manga larga sin estampado color negro' (ID 11)\n- stock: 7 -> 10	2026-04-16 12:50:19
243	julio@gmail.com	Inicio de sesión exitoso	2026-04-16 12:51:48
244	julio@gmail.com	Stripe confirmado. Pedido #50 creado por COP 160.000,00	2026-04-16 16:30:04
245	nico@gmail.com	Inicio de sesión exitoso	2026-04-16 16:36:31
246	julio@gmail.com	Inicio de sesión exitoso	2026-04-16 17:07:53
247	nico@gmail.com	Inicio de sesión exitoso	2026-04-16 17:39:42
248	nico@gmail.com	POS registro venta #51 por COP 160.000,00 (1 producto(s))\n- total bruto: COP 160.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-04-16 17:42:38
249	julio@gmail.com	Inicio de sesión exitoso	2026-04-16 18:19:47
39	nico@gmail.com	Inicio de sesion exitoso	2026-03-18 12:57:52
40	julio@gmail.com	Inicio de sesion exitoso	2026-03-18 13:00:31
41	nico@gmail.com	Inicio de sesion exitoso	2026-03-18 13:13:07
193	admin	Contrasena restablecida por recuperacion para somosdecimob2020@gmail.com	2026-04-03 11:26:18
65	julio@gmail.com	Inicio de sesion exitoso	2026-03-18 14:29:18
269	nico@gmail.com	Inicio de sesiÃ³n exitoso	2026-04-21 16:15:19
66	julio@gmail.com	Creo pedido #14 con 1 producto(s) por COP 160,00	2026-03-18 14:31:15
67	nico@gmail.com	Inicio de sesion exitoso	2026-03-18 14:32:38
68	nico@gmail.com	Creo producto 'Moño' (ID 19)\n- precio: COP 20,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Panoletas	2026-03-18 14:33:51
126	nico@gmail.com	Actualizo producto 'Moño' (ID 19)\n- stock: 7 -> 10	2026-03-25 15:52:35
69	nico@gmail.com	Creo producto 'Pañoleta policia sin estampado' (ID 20)\n- precio: COP 60,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Panoletas	2026-03-18 14:36:43
70	julio@gmail.com	Inicio de sesion exitoso	2026-03-18 14:37:42
71	julio@gmail.com	Inicio de sesion exitoso	2026-03-18 14:39:00
72	julio@gmail.com	Inicio de sesion exitoso	2026-03-18 14:42:57
73	julio@gmail.com	Inicio de sesion exitoso	2026-03-18 14:44:23
74	nico@gmail.com	Inicio de sesion exitoso	2026-03-18 14:56:43
75	julio@gmail.com	Inicio de sesion exitoso	2026-03-18 14:59:13
76	julio@gmail.com	Inicio de sesion exitoso	2026-03-18 15:01:26
77	nico@gmail.com	Inicio de sesion exitoso	2026-03-18 15:04:30
78	julio@gmail.com	Inicio de sesion exitoso	2026-03-18 15:06:52
25	julio@gmail.com	Inicio de sesión exitoso	2026-03-13 16:07:43
26	julio@gmail.com	Inicio de sesión exitoso	2026-03-14 15:53:58
12	julio@gmail.com	Inicio de sesión exitoso	2026-03-09 16:42:10
13	julio@gmail.com	Inicio de sesión exitoso	2026-03-09 16:58:05
20	nico@gmail.com	Inicio de sesión exitoso	2026-03-13 14:38:22
1	julio@gmail.com	Inicio de sesión exitoso	2026-03-07 01:04:11
2	nico@gmail.com	Inicio de sesión exitoso	2026-03-07 01:19:16
3	nico@gmail.com	Creo producto 'Camiseta mallada' (ID 1)\n- precio: COP 60,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Busos	2026-03-07 01:25:52
4	nico@gmail.com	Actualizo producto 'Camiseta mallada' (ID 1)\n- sin cambios detectados	2026-03-07 01:26:25
222	nico@gmail.com	Inicio de sesiÃƒÂ³n exitoso	2026-04-08 16:45:00
5	nico@gmail.com	Creo producto 'Armando Estaban Quito' (ID 2)\n- precio: COP 100.000,00\n- stock: 100\n- fuerza: Gaula\n- intendencia: Camibusos	2026-03-07 01:45:18
6	nico@gmail.com	Inicio de sesión exitoso	2026-03-07 16:33:28
7	julio@gmail.com	Inicio de sesión exitoso	2026-03-07 16:35:29
8	julio@gmail.com	Inicio de sesión exitoso	2026-03-07 17:41:23
9	julio@gmail.com	Inicio de sesión exitoso	2026-03-07 17:41:58
10	julio@gmail.com	Inicio de sesión exitoso	2026-03-07 17:43:19
11	julio@gmail.com	Inicio de sesión exitoso	2026-03-07 17:43:19
14	julio@gmail.com	Inicio de sesión exitoso	2026-03-10 16:35:58
15	julio@gmail.com	Inicio de sesión exitoso	2026-03-11 12:38:04
16	julio@gmail.com	Inicio de sesión exitoso	2026-03-11 15:16:53
32	julio@gmail.com	Inicio de sesión exitoso	2026-03-16 21:18:02
33	julio@gmail.com	Inicio de sesión exitoso	2026-03-17 15:52:42
34	nico@gmail.com	Inicio de sesión exitoso	2026-03-17 15:53:47
35	julio@gmail.com	Inicio de sesión exitoso	2026-03-17 16:07:22
27	julio@gmail.com	Inicio de sesión exitoso	2026-03-14 16:07:12
135	nico@gmail.com	POS registro venta #24 por COP 590.000,00 (7 producto(s))\n- total bruto: COP 590.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 17:54:38
136	nico@gmail.com	Actualizo producto 'Camiseta unisex manga larga sin estampado color negro' (ID 12)\n- stock: 9 -> 10	2026-03-25 18:03:10
137	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color blanco' (ID 10)\n- stock: 9 -> 10	2026-03-25 18:03:25
138	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color negro' (ID 9)\n- stock: 9 -> 10	2026-03-25 18:03:35
139	nico@gmail.com	Actualizo producto 'Guerrera' (ID 17)\n- stock: 9 -> 10	2026-03-25 18:03:55
140	nico@gmail.com	Actualizo producto 'Pantalón' (ID 18)\n- stock: 9 -> 10	2026-03-25 18:04:04
141	nico@gmail.com	Actualizo producto 'Moño' (ID 19)\n- stock: 3 -> 10	2026-03-25 18:04:20
142	nico@gmail.com	Actualizo producto 'Pañoleta policia sin estampado' (ID 20)\n- stock: 9 -> 10	2026-03-25 18:04:30
253	nico@gmail.com	Actualizo estado de pedido #53: pendiente -> enviado	2026-04-16 18:46:40
143	nico@gmail.com	POS registro venta #25 por COP 1.150.000,00 (14 producto(s))\n- total bruto: COP 1.200.000,00\n- descuento aplicado: COP 50.000,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 18:05:47
144	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color negro' (ID 9)\n- stock: 9 -> 10	2026-03-25 18:08:20
145	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color blanco' (ID 10)\n- stock: 9 -> 10	2026-03-25 18:08:26
146	nico@gmail.com	Actualizo producto 'Camiseta unisex manga larga sin estampado color negro' (ID 12)\n- stock: 9 -> 10	2026-03-25 18:08:32
147	nico@gmail.com	Actualizo producto 'Guerrera' (ID 17)\n- stock: 9 -> 10	2026-03-25 18:08:38
149	nico@gmail.com	Actualizo producto 'Moño' (ID 19)\n- stock: 9 -> 10	2026-03-25 18:08:54
152	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color negro' (ID 4)\n- stock: 9 -> 10	2026-03-25 18:09:15
153	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color blanco' (ID 5)\n- stock: 9 -> 10	2026-03-25 18:09:20
154	nico@gmail.com	Actualizo producto 'Camiseta unisex color verde' (ID 6)\n- stock: 9 -> 10	2026-03-25 18:09:31
155	nico@gmail.com	Actualizo producto 'Camiseta unisex manga larga sin estampado color negro' (ID 11)\n- stock: 9 -> 10	2026-03-25 18:09:42
156	nico@gmail.com	Actualizo producto 'Guerrera' (ID 13)\n- stock: 9 -> 10	2026-03-25 18:10:05
157	nico@gmail.com	Actualizo producto 'Guerrera' (ID 8)\n- stock: 9 -> 10	2026-03-25 18:10:12
158	nico@gmail.com	Actualizo producto 'Pantalón' (ID 7)\n- stock: 9 -> 10	2026-03-25 18:10:22
212	julio11916@gmail.com	Codigo de cambio de contrasena enviado a julio11916@gmail.com	2026-04-08 13:45:59
159	nico@gmail.com	POS registro venta #26 por COP 60.000,00 (1 producto(s))\n- total bruto: COP 60.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 18:34:53
160	nico@gmail.com	Actualizo producto 'Pañoleta policia sin estampado' (ID 20)\n- stock: 9 -> 10	2026-03-25 18:41:51
161	nico@gmail.com	POS registro venta #27 por COP 80.000,00 (1 producto(s))\n- total bruto: COP 80.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 18:49:29
162	nico@gmail.com	POS registro venta #28 por COP 80.000,00 (1 producto(s))\n- total bruto: COP 80.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 18:56:24
163	nico@gmail.com	POS registro venta #29 por COP 160.000,00 (1 producto(s))\n- total bruto: COP 160.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 19:05:41
164	nico@gmail.com	POS registro venta #30 por COP 80.000,00 (1 producto(s))\n- total bruto: COP 80.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 19:10:26
165	nico@gmail.com	Actualizo producto 'Camiseta unisex manga larga sin estampado color negro' (ID 12)\n- stock: 6 -> 10	2026-03-25 19:21:58
166	nico@gmail.com	Actualizo producto 'Camiseta unisex manga larga sin estampado color negro' (ID 11)\n- stock: 9 -> 10	2026-03-25 19:22:10
167	nico@gmail.com	POS registro venta #31 por COP 50.000,00 (1 producto(s))\n- total bruto: COP 100.000,00\n- descuento aplicado: COP 50.000,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 19:23:24
168	nico@gmail.com	POS registro venta #32 por COP 50.000,00 (1 producto(s))\n- total bruto: COP 100.000,00\n- descuento aplicado: COP 50.000,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 19:33:14
169	nico@gmail.com	POS registro venta #33 por COP 50.000,00 (1 producto(s))\n- total bruto: COP 100.000,00\n- descuento aplicado: COP 50.000,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 19:35:47
170	nico@gmail.com	POS registro venta #34 por COP 50.000,00 (1 producto(s))\n- total bruto: COP 100.000,00\n- descuento aplicado: COP 50.000,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 19:40:22
171	nico@gmail.com	POS registro venta #35 por COP 50.000,00 (1 producto(s))\n- total bruto: COP 100.000,00\n- descuento aplicado: COP 50.000,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 19:56:07
172	nico@gmail.com	POS registro venta #36 por COP 50.000,00 (1 producto(s))\n- total bruto: COP 100.000,00\n- descuento aplicado: COP 50.000,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-25 20:29:37
174	julio@gmail.com	Inicio de sesión exitoso	2026-03-25 21:17:33
176	nico@gmail.com	POS registro venta #37 por COP 50.000,00 (1 producto(s))\n- total bruto: COP 100.000,00\n- descuento aplicado: COP 50.000,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-27 14:14:32
177	julio@gmail.com	Inicio de sesión exitoso	2026-03-27 15:11:37
178	nico@gmail.com	Inicio de sesión exitoso	2026-03-27 15:12:36
179	nico@gmail.com	Inicio de sesión exitoso	2026-03-27 16:43:07
180	nico@gmail.com	POS registro venta #38 por COP 50.000,00 (1 producto(s))\n- total bruto: COP 100.000,00\n- descuento aplicado: COP 50.000,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-03-27 16:51:25
181	nico@gmail.com	Inicio de sesión exitoso	2026-04-02 16:45:28
182	julio@gmail.com	Inicio de sesión exitoso	2026-04-02 16:47:30
183	admin	Nuevo usuario registrado: julio cesar otalvaro sanchez	2026-04-02 16:50:05
184	somosdecimoB2020@gmail.com	Código de autenticación generado para somosdecimoB2020@gmail.com (modo desarrollo)	2026-04-02 16:50:20
185	somosdecimoB2020@gmail.com	Usuario somosdecimoB2020@gmail.com verificó su correo electrónico	2026-04-02 16:51:18
186	nico@gmail.com	Inicio de sesión exitoso	2026-04-02 17:30:25
187	nico@gmail.com	Inicio de sesión exitoso	2026-04-02 17:45:54
250	julio@gmail.com	Creo pedido #52 con 1 producto(s) por COP 50.000,00	2026-04-16 18:20:23
251	julio@gmail.com	Stripe confirmado. Pedido #53 creado por COP 50.000,00	2026-04-16 18:45:10
252	nico@gmail.com	Inicio de sesión exitoso	2026-04-16 18:46:17
255	nico@gmail.com	POS registro venta #54 por COP 160.000,00 (1 producto(s))\n- total bruto: COP 160.000,00\n- descuento aplicado: COP 0,00\n- cliente: cata\n- correo: ratalina@gmail.com\n- documento: 34795368972\n- teléfono: 3204567896	2026-04-16 18:50:57
257	julio@gmail.com	Inicio de sesión exitoso	2026-04-16 19:59:58
258	julio@gmail.com	Creo pedido #55 con 1 producto(s) por COP 50.000,00	2026-04-16 20:30:58
259	nico@gmail.com	Inicio de sesión exitoso	2026-04-20 15:22:16
260	julio@gmail.com	Inicio de sesión exitoso	2026-04-21 13:02:59
261	nico@gmail.com	Inicio de sesión exitoso	2026-04-21 14:00:41
262	nico@gmail.com	Administrador actualizó prendas destacadas por categoría:\n- Ejército: 5 (6, 5, 4, 11, 8)\n- Policía: 4 (10, 9, 12, 17)\n- Armada: 0 (ninguna)\n- Total destacadas: 9	2026-04-21 14:00:58
263	nico@gmail.com	Administrador actualizó prendas destacadas por categoría:\n- Ejército: 5 (6, 5, 4, 11, 8)\n- Policía: 4 (10, 9, 12, 17)\n- Armada: 0 (ninguna)\n- Total destacadas: 9	2026-04-21 14:01:00
264	nico@gmail.com	Administrador actualizó prendas destacadas por categoría:\n- Ejército: 5 (6, 5, 4, 11, 8)\n- Policía: 4 (10, 9, 12, 17)\n- Armada: 0 (ninguna)\n- Total destacadas: 9	2026-04-21 14:01:06
265	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color negro' (ID 4)\n- stock: 7 -> 10	2026-04-21 14:01:44
266	nico@gmail.com	Actualizo producto 'Camiseta unisex sin estampado color negro' (ID 9)\n- stock: 10 -> 0	2026-04-21 14:02:01
267	nico@gmail.com	Administrador actualizó prendas destacadas por categoría:\n- Ejército: 5 (6, 5, 4, 11, 8)\n- Policía: 4 (10, 9, 12, 17)\n- Armada: 0 (ninguna)\n- Total destacadas: 9	2026-04-21 14:02:23
268	nico@gmail.com	Actualizo estado de pedido #55: pendiente -> confirmado	2026-04-21 14:24:00
270	nico@gmail.com	Administrador actualizÃ³ prendas destacadas por categorÃ­a:\n- EjÃ©rcito: 5 (6, 5, 4, 11, 8)\n- PolicÃ­a: 5 (10, 9, 12, 17, 18)\n- Armada: 0 (ninguna)\n- Total destacadas: 10	2026-04-21 16:15:50
271	nico@gmail.com	Administrador actualizÃ³ prendas destacadas por categorÃ­a:\n- EjÃ©rcito: 5 (6, 5, 4, 11, 3)\n- PolicÃ­a: 5 (10, 9, 12, 17, 18)\n- Armada: 0 (ninguna)\n- Total destacadas: 10	2026-04-21 16:15:58
272	nico@gmail.com	Inicio de sesiÃ³n exitoso	2026-04-21 16:16:24
273	nico@gmail.com	Administrador actualizÃ³ prendas destacadas por categorÃ­a:\n- EjÃ©rcito: 5 (6, 5, 4, 11, 3)\n- PolicÃ­a: 5 (10, 9, 12, 17, 18)\n- Armada: 0 (ninguna)\n- Total destacadas: 10	2026-04-21 16:16:36
274	nico@gmail.com	Actualizo estado de pedido #55: confirmado -> enviado	2026-04-21 16:20:21
275	nico@gmail.com	Actualizo estado de pedido #55: enviado -> entregado	2026-04-21 16:37:24
276	nico@gmail.com	Actualizo estado de pedido #5: pendiente -> entregado	2026-04-21 16:37:51
277	nico@gmail.com	Cambio de estado para usuario hola3@gmail.com (ID 5) -> inactivo	2026-04-22 13:05:11
278	julio@gmail.com	Inicio de sesiÃ³n exitoso	2026-04-22 13:45:38
279	julio@gmail.com	Creo pedido #56 con 1 producto(s) por COP 50.000,00	2026-04-22 16:38:40
280	nico@gmail.com	Inicio de sesiÃ³n exitoso	2026-04-22 16:46:32
281	nico@gmail.com	Administrador actualizÃ³ prendas destacadas por categorÃ­a:\n- EjÃ©rcito: 5 (6, 5, 4, 11, 3)\n- PolicÃ­a: 5 (10, 9, 12, 17, 18)\n- Armada: 0 (ninguna)\n- Total destacadas: 10	2026-04-22 16:46:38
282	nico@gmail.com	Actualizo revision de pago para pedido #56: pendiente_comprobante -> en_revision	2026-04-22 16:56:50
283	nico@gmail.com	Actualizo estado de pedido #52: pendiente -> entregado	2026-04-22 16:57:44
284	nico@gmail.com	Actualizo estado de pedido #50: pendiente -> enviado	2026-04-22 16:57:50
285	julio@gmail.com	Usuario julio@gmail.com actualizo su perfil	2026-04-22 20:50:15
286	nico@gmail.com	Inicio de sesiÃ³n exitoso	2026-04-24 12:54:38
287	nico@gmail.com	Administrador actualizó prendas destacadas por categoría:\n- Ejército: 5 (6, 5, 4, 11, 3)\n- Policía: 7 (10, 9, 12, 17, 18, 19, 20)\n- Armada: 0 (ninguna)\n- Total destacadas: 12	2026-04-24 13:29:16
288	julio11916@gmail.com	Inicio de sesión exitoso	2026-04-24 13:45:28
289	nico@gmail.com	Administrador actualizó prendas destacadas por categoría:\n- Ejército: 7 (6, 5, 4, 11, 3, 8, 7)\n- Policía: 7 (10, 9, 12, 17, 18, 19, 20)\n- Armada: 0 (ninguna)\n- Total destacadas: 14	2026-04-24 14:17:44
290	julio@gmail.com	Inicio de sesión exitoso	2026-04-26 13:07:44
291	nico@gmail.com	Inicio de sesión exitoso	2026-04-26 13:09:01
292	admin@test.local	Administrador actualizo prendas destacadas por categoria:\n- Ejercito: 0 (ninguna)\n- Policia: 0 (ninguna)\n- Armada: 0 (ninguna)\n- Total destacadas: 0	2026-04-26 13:18:25
293	nico@gmail.com	Administrador actualizó prendas destacadas por categoría:\n- Ejército: 0 (ninguna)\n- Policía: 7 (10, 9, 12, 17, 18, 19, 20)\n- Armada: 0 (ninguna)\n- Total destacadas: 7	2026-04-26 14:12:42
294	nico@gmail.com	Administrador actualizó prendas destacadas por categoría:\n- Ejército: 7 (6, 5, 4, 11, 3, 8, 7)\n- Policía: 7 (10, 9, 12, 17, 18, 19, 20)\n- Armada: 0 (ninguna)\n- Total destacadas: 14	2026-04-26 14:12:52
295	nico@gmail.com	Actualizo revision de pago para pedido #56: en_revision -> aprobado	2026-04-26 14:13:13
296	julio@gmail.com	Inicio de sesión exitoso	2026-04-26 14:13:48
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
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.usuarios (id_usuario, nombre, email, password_hash, rol, estado, fecha_registro, email_verified, verification_code, verification_code_expiry, reset_token, reset_token_expiry, password_change_code, password_change_code_expiry, telefono, direccion) FROM stdin;
12	julio cesar otalvaro sanchez	julio11916@gmail.com	scrypt:32768:8:1$gyCyGHOJIsL3kD7o$bd88fa0a8f98b2af0afee2c62c5bacbe89cec318d32fab3d1974769017c11c330e0427854170c5023db442262aedf508790a7b20dbb48cf70e8638eae9025b94	normal	activo	2026-04-02 18:52:23	t		\N		\N	906298	2026-04-08 14:38:15-05	\N	\N
13	jilmer	c65238944@gmail.com	scrypt:32768:8:1$omQpXag2INR8SgL1$e9acff045519d2bd46f7c429390c1189e2e02abc29b7a9e6d076d20a98f667464472ed40b3d14253739785c0f955d5eb7cae9a10abfd0872a4f933ef60cbaa9a	normal	activo	2026-04-03 11:55:51	t		\N		\N		\N	\N	\N
1	Nico	nico@gmail.com	scrypt:32768:8:1$3oBOoha9lG4w3a2E$7b2225fd3dfb693854e6664a153332f011956c20a8c756e57a7e5aeebe20a83ee83fb67aca68c2927b54e8be91ea3574d5ed0b942afecd0518d372a17f0aec1d	admin	activo	2026-02-06 14:55:32	f		\N		\N		\N	\N	\N
2	Julio	julio@gmail.com	scrypt:32768:8:1$LelqMtI3TmTMyzOE$bebb09284b93879bd665d266791c9d2b8fb8ddd46c90620e350e6cfbce10695ae1bdcfbe52fae9a7cd79af1bec0e0bacea6a1dc725a5c757f07ad6d499b4e29b	normal	activo	2026-02-06 14:55:32	f	801703	2026-03-06 14:07:29		\N		\N	3204567896	adsafasasa
3	Alvaréx Freo	alv@gmail.com	admin	normal	activo	2026-02-06 16:40:07	f		\N		\N		\N	\N	\N
4	jilmer	hola@gmail.com	admin	admin	activo	2026-02-20 15:47:06	f		\N		\N		\N	\N	\N
5	Isabel	hola3@gmail.com	123456789	normal	inactivo	2026-02-20 15:47:36	f		\N		\N		\N	\N	\N
6	Tatiana Rivera	tatis@gmail.com	admin	normal	activo	2026-02-25 22:35:53	f		\N		\N		\N	\N	\N
7	Tatiana Rivera	tr3303419@gmail.com	admin	normal	inactivo	2026-02-26 22:54:23	f		\N		\N		\N	\N	\N
8	David	david@gmail.com	4321	normal	activo	2026-03-04 19:37:39	f		\N		\N		\N	\N	\N
9	David	rodriguezsierradavidsantiago@gmail.com	54321	normal	activo	2026-03-04 22:56:35	t	844313	2026-03-04 23:45:18		\N		\N	\N	\N
10	Catalina rodriguez	catar@gmail.com	Catalina1.	normal	activo	2026-03-13 15:30:56	f		\N		\N		\N	\N	\N
11	julio cesar otalvaro sanchez	somosdecimob2020@gmail.com	scrypt:32768:8:1$xXEaOs4nnTL7BFLU$2c58839161a345654ccc41bb69e2d88185b4082bc0f5b443e92a7b294b9c36029c515fa8f46b0d6dbced71ecafe5edc07def0dc5089c22658654c6006d70dd50	normal	activo	2026-04-02 16:50:05	t		\N		\N		\N	\N	\N
\.


--
-- Name: categoria_producto_id_categoria_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.categoria_producto_id_categoria_seq', 44, true);


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
-- Name: stripe_checkout stripe_checkout_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.stripe_checkout
    ADD CONSTRAINT stripe_checkout_pkey PRIMARY KEY (session_id);


--
-- PostgreSQL database dump complete
--

\unrestrict ap4BvOUVDuY49qGNNwD1iOQMWkjbeLNlLlncPkmAAXKMtdcG2mFgqBRVT351Mb6

