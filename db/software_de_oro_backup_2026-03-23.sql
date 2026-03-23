--
-- PostgreSQL database dump
--

\restrict gxSVogMxz2bGCW2npxm5yPATsU58jFnTC1r5vE8NmpV8skTBCzddj5DUINLr3Pa

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: categoria_producto; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.categoria_producto (
    id_categoria bigint NOT NULL,
    nombre_categoria text,
    descripcion text
);


ALTER TABLE public.categoria_producto OWNER TO postgres;

--
-- Name: categoria_producto_id_categoria_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.categoria_producto_id_categoria_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.categoria_producto_id_categoria_seq OWNER TO postgres;

--
-- Name: categoria_producto_id_categoria_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.categoria_producto_id_categoria_seq OWNED BY public.categoria_producto.id_categoria;


--
-- Name: detalle_pedido; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.detalle_pedido (
    id_detalle bigint,
    id_pedido bigint,
    id_producto bigint,
    cantidad bigint,
    subtotal double precision
);


ALTER TABLE public.detalle_pedido OWNER TO postgres;

--
-- Name: pagos; Type: TABLE; Schema: public; Owner: postgres
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
    monto_descuento double precision
);


ALTER TABLE public.pagos OWNER TO postgres;

--
-- Name: pedidos; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.pedidos (
    id_pedido bigint,
    id_usuario bigint,
    fecha_pedido text,
    estado text
);


ALTER TABLE public.pedidos OWNER TO postgres;

--
-- Name: producto; Type: TABLE; Schema: public; Owner: postgres
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
    eliminado boolean
);


ALTER TABLE public.producto OWNER TO postgres;

--
-- Name: promociones; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.promociones (
    id_promo bigint NOT NULL,
    nombre text,
    descripcion text,
    tipo_descuento text,
    valor_descuento numeric(12,2),
    codigo text,
    fecha_inicio date,
    fecha_fin date,
    activo boolean DEFAULT true,
    id_producto bigint
);


ALTER TABLE public.promociones OWNER TO postgres;

--
-- Name: promociones_id_promo_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.promociones_id_promo_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.promociones_id_promo_seq OWNER TO postgres;

--
-- Name: promociones_id_promo_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.promociones_id_promo_seq OWNED BY public.promociones.id_promo;


--
-- Name: registros; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.registros (
    id_registro bigint,
    id_usuario text,
    accion text,
    fecha_accion text
);


ALTER TABLE public.registros OWNER TO postgres;

--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: postgres
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
    verification_code double precision,
    verification_code_expiry text
);


ALTER TABLE public.usuarios OWNER TO postgres;

--
-- Name: categoria_producto id_categoria; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categoria_producto ALTER COLUMN id_categoria SET DEFAULT nextval('public.categoria_producto_id_categoria_seq'::regclass);


--
-- Name: promociones id_promo; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.promociones ALTER COLUMN id_promo SET DEFAULT nextval('public.promociones_id_promo_seq'::regclass);


--
-- Data for Name: categoria_producto; Type: TABLE DATA; Schema: public; Owner: postgres
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
-- Data for Name: detalle_pedido; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.detalle_pedido (id_detalle, id_pedido, id_producto, cantidad, subtotal) FROM stdin;
1	14	13	1	160
\.


--
-- Data for Name: pagos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pagos (id_pago, id_pedido, monto, metodo_pago, fecha_pago, estado_pago, id_promo, codigo_promo, tipo_descuento, valor_descuento, monto_descuento) FROM stdin;
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
\.


--
-- Data for Name: pedidos; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.pedidos (id_pedido, id_usuario, fecha_pedido, estado) FROM stdin;
5	8	2026-03-04 19:42:40	pendiente
6	8	2026-03-04 19:48:18	pendiente
7	8	2026-03-04 19:49:00	pendiente
8	8	2026-03-04 19:55:08	pendiente
9	8	2026-03-04 20:02:08	pendiente
10	8	2026-03-04 20:02:37	pendiente
11	8	2026-03-04 20:05:34	pendiente
12	8	2026-03-04 20:06:17	pendiente
13	2	2026-03-06 14:02:06	pendiente
14	2	2026-03-18 14:31:15	pendiente
\.


--
-- Data for Name: producto; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.producto (id_producto, nombre, descripcion, precio, stock, id_categoria, fuerza, intendencia, imagen_url, eliminado) FROM stdin;
1	Camiseta mallada	Damn	60	10	1	Policia	Busos	img/Empresa/producto_1.jpg	t
2	Armando Estaban Quito	puro de corazon	100000	100	1	Gaula	Camibusos	img/Empresa/producto_2.jpg	t
3	Camiseta unisex con camuflado	Diseñada para brindar comodidad y estilo en cualquier ocasión. Disponible en versiones con camuflado, que incluyen diseños representativos y gráficos alusivos a la institución.	100	10	1	Ejercito	Camuflados	img/Empresa/producto_3.jpg	f
4	Camiseta unisex sin estampado color negro	Diseñada para brindar comodidad y estilo en cualquier ocasión. Ideal para quienes prefieren un estilo más sencillo y versátil.	50	10	1	Ejercito	Busos	img/Empresa/producto_4.jpg	f
5	Camiseta unisex sin estampado color blanco	Diseñada para brindar comodidad y estilo en cualquier ocasión. Ideal para quienes prefieren un estilo más sencillo y versátil.	50	10	1	Ejercito	Busos	img/Empresa/producto_5.jpg	f
6	Camiseta unisex color verde	Diseñada para brindar comodidad y estilo en cualquier ocasión. Ideal para quienes prefieren un estilo más sencillo y versátil.	50	10	1	Ejercito	Busos	img/Empresa/producto_6.jpg	f
7	Pantalón	Pantalón inspirado en el uniforme del Ejército Nacional de Colombia, diseñado para brindar resistencia, comodidad y funcionalidad en actividades diarias.	120	10	1	Ejercito	Camuflados	img/Empresa/producto_7.jpg	f
8	Guerrera	Prenda superior utilizado en el uniforme. Caracterizado por su diseño estructurado, funcional y representativo, pensado para brindar una apariencia formal y profesional.	160	10	1	Ejercito	Camuflados	img/Empresa/producto_8.jpg	f
9	Camiseta unisex sin estampado color negro	Diseñada para brindar comodidad y estilo en cualquier ocasión. Ideal para quienes prefieren un estilo más sencillo y versátil.	50	10	1	Policia	Busos	img/Empresa/producto_9.jpg	f
10	Camiseta unisex sin estampado color blanco	Diseñada para brindar comodidad y estilo en cualquier ocasión. Ideal para quienes prefieren un estilo más sencillo y versátil.	50	10	1	Policia	Busos	img/Empresa/producto_10.jpg	f
11	Camiseta unisex manga larga sin estampado color negro	Camiseta manga larga cómoda y resistente. Ideal para climas frescos y actividades diarias.	80	10	1	Ejercito	Camibusos	img/Empresa/producto_11.jpg	f
12	Camiseta unisex manga larga sin estampado color negro	Camiseta manga larga cómoda y resistente. Ideal para climas frescos y actividades diarias.	80	10	1	Policia	Camibusos	img/Empresa/producto_12.jpg	f
13	Guerrera	Prenda superior del uniforme. Se caracteriza por su diseño estructurado, funcional y representativo, pensado para brindar una apariencia formal y profesional.	160	9	1	Gaula	Camuflados	img/Empresa/producto_13.jpg	f
14	Pantalón	Pantalón inspirado en el uniforme del gaula, diseñado para brindar resistencia, comodidad y funcionalidad en actividades diarias.	180	10	1	Gaula	Camuflados	img/Empresa/producto_14.jpg	f
15	Camiseta unisex sin estampado color negro	Camiseta cómoda y resistente. Ideal para climas frescos y actividades diarias.	50	10	1	Gaula	Busos	img/Empresa/producto_15.jpg	f
16	Camiseta unisex sin estampado color blanco	Camiseta cómoda y resistente. Ideal para climas frescos y actividades diarias.	50	10	1	Gaula	Busos	img/Empresa/producto_16.jpg	f
17	Guerrera	Prenda superior del uniforme. Se caracteriza por su diseño estructurado, funcional y representativo, pensado para brindar una apariencia formal y profesional.	160	10	1	Policia	Camuflados	img/Empresa/producto_17.jpg	f
18	Pantalón	Pantalón inspirado en el uniforme de la policía, diseñado para brindar resistencia, comodidad y funcionalidad en actividades diarias.	180	10	1	Policia	Camuflados	img/Empresa/producto_18.jpg	f
19	Moño	Moño decorativo inspirado en accesorios formales utilizados en uniformes institucionales. Perfecto para completar un estilo elegante.	20	10	1	Policia	Panoletas	img/Empresa/producto_19.jpg	f
20	Pañoleta policia sin estampado	Diseñada para brindar comodidad y estilo en cualquier ocasión. Ideal para quienes prefieren un estilo más sencillo y versátil.	60	10	1	Policia	Panoletas	img/Empresa/producto_20.jpg	f
\.


--
-- Data for Name: promociones; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.promociones (id_promo, nombre, descripcion, tipo_descuento, valor_descuento, codigo, fecha_inicio, fecha_fin, activo, id_producto) FROM stdin;
\.


--
-- Data for Name: registros; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.registros (id_registro, id_usuario, accion, fecha_accion) FROM stdin;
1	julio@gmail.com	Inicio de sesión exitoso	2026-03-07 01:04:11
2	nico@gmail.com	Inicio de sesión exitoso	2026-03-07 01:19:16
3	nico@gmail.com	Creo producto 'Camiseta mallada' (ID 1)\n- precio: COP 60,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Busos	2026-03-07 01:25:52
4	nico@gmail.com	Actualizo producto 'Camiseta mallada' (ID 1)\n- sin cambios detectados	2026-03-07 01:26:25
5	nico@gmail.com	Creo producto 'Armando Estaban Quito' (ID 2)\n- precio: COP 100.000,00\n- stock: 100\n- fuerza: Gaula\n- intendencia: Camibusos	2026-03-07 01:45:18
6	nico@gmail.com	Inicio de sesión exitoso	2026-03-07 16:33:28
7	julio@gmail.com	Inicio de sesión exitoso	2026-03-07 16:35:29
8	julio@gmail.com	Inicio de sesión exitoso	2026-03-07 17:41:23
9	julio@gmail.com	Inicio de sesión exitoso	2026-03-07 17:41:58
10	julio@gmail.com	Inicio de sesión exitoso	2026-03-07 17:43:19
11	julio@gmail.com	Inicio de sesión exitoso	2026-03-07 17:43:19
12	julio@gmail.com	Inicio de sesión exitoso	2026-03-09 16:42:10
13	julio@gmail.com	Inicio de sesión exitoso	2026-03-09 16:58:05
14	julio@gmail.com	Inicio de sesión exitoso	2026-03-10 16:35:58
15	julio@gmail.com	Inicio de sesión exitoso	2026-03-11 12:38:04
16	julio@gmail.com	Inicio de sesión exitoso	2026-03-11 15:16:53
17	julio@gmail.com	Inicio de sesión exitoso	2026-03-11 15:33:52
18	julio@gmail.com	Inicio de sesión exitoso	2026-03-11 22:52:48
19	julio@gmail.com	Inicio de sesión exitoso	2026-03-13 14:37:21
20	nico@gmail.com	Inicio de sesión exitoso	2026-03-13 14:38:22
21	julio@gmail.com	Inicio de sesión exitoso	2026-03-13 14:41:50
22	nico@gmail.com	Inicio de sesión exitoso	2026-03-13 15:29:20
23	julio@gmail.com	Inicio de sesión exitoso	2026-03-13 15:29:52
24	catar@gmail.com	Nuevo usuario registrado: Catalina rodriguez	2026-03-13 15:30:56
25	julio@gmail.com	Inicio de sesión exitoso	2026-03-13 16:07:43
26	julio@gmail.com	Inicio de sesión exitoso	2026-03-14 15:53:58
27	julio@gmail.com	Inicio de sesión exitoso	2026-03-14 16:07:12
28	nico@gmail.com	Inicio de sesión exitoso	2026-03-14 16:08:55
29	julio@gmail.com	Inicio de sesión exitoso	2026-03-16 12:43:10
30	julio@gmail.com	Inicio de sesión exitoso	2026-03-16 17:24:26
31	nico@gmail.com	Inicio de sesión exitoso	2026-03-16 21:17:20
32	julio@gmail.com	Inicio de sesión exitoso	2026-03-16 21:18:02
33	julio@gmail.com	Inicio de sesión exitoso	2026-03-17 15:52:42
34	nico@gmail.com	Inicio de sesión exitoso	2026-03-17 15:53:47
35	julio@gmail.com	Inicio de sesión exitoso	2026-03-17 16:07:22
36	nico@gmail.com	Inicio de sesion exitoso	2026-03-17 16:50:35
37	julio@gmail.com	Inicio de sesion exitoso	2026-03-17 16:55:01
38	nico@gmail.com	Inicio de sesion exitoso	2026-03-17 17:03:36
39	nico@gmail.com	Inicio de sesion exitoso	2026-03-18 12:57:52
40	julio@gmail.com	Inicio de sesion exitoso	2026-03-18 13:00:31
41	nico@gmail.com	Inicio de sesion exitoso	2026-03-18 13:13:07
42	nico@gmail.com	Creo producto 'Camiseta unisex con camuflado' (ID 3)\n- precio: COP 100,00\n- stock: 10\n- fuerza: Ejercito\n- intendencia: Camuflados	2026-03-18 13:17:14
43	nico@gmail.com	Creo producto 'Camiseta unisex sin estampado color negro' (ID 4)\n- precio: COP 50,00\n- stock: 10\n- fuerza: Ejercito\n- intendencia: Busos	2026-03-18 13:21:36
44	julio@gmail.com	Inicio de sesion exitoso	2026-03-18 13:22:05
45	nico@gmail.com	Inicio de sesion exitoso	2026-03-18 13:22:49
46	nico@gmail.com	Elimino producto: Camiseta mallada (ID 1)	2026-03-18 13:23:37
47	nico@gmail.com	Elimino producto: Armando Estaban Quito (ID 2)	2026-03-18 13:23:43
48	nico@gmail.com	Creo producto 'Camiseta unisex sin estampado color blanco' (ID 5)\n- precio: COP 50,00\n- stock: 10\n- fuerza: Ejercito\n- intendencia: Busos	2026-03-18 13:29:21
49	nico@gmail.com	Creo producto 'Camiseta manga larga color verde' (ID 6)\n- precio: COP 50,00\n- stock: 10\n- fuerza: Ejercito\n- intendencia: Busos	2026-03-18 13:31:28
50	nico@gmail.com	Actualizo producto 'Camiseta manga corta color verde' (ID 6)\n- nombre: 'Camiseta manga larga color verde' -> 'Camiseta manga corta color verde'	2026-03-18 13:33:21
51	nico@gmail.com	Actualizo producto 'Camiseta unisex manga corta color verde' (ID 6)\n- nombre: 'Camiseta manga corta color verde' -> 'Camiseta unisex manga corta color verde'	2026-03-18 13:33:34
52	nico@gmail.com	Actualizo producto 'Camiseta unisex color verde' (ID 6)\n- nombre: 'Camiseta unisex manga corta color verde' -> 'Camiseta unisex color verde'	2026-03-18 13:33:49
53	nico@gmail.com	Creo producto 'Pantalón' (ID 7)\n- precio: COP 120,00\n- stock: 10\n- fuerza: Ejercito\n- intendencia: Camuflados	2026-03-18 13:35:14
54	nico@gmail.com	Creo producto 'Guerrera' (ID 8)\n- precio: COP 160,00\n- stock: 10\n- fuerza: Ejercito\n- intendencia: Camuflados	2026-03-18 13:37:24
55	nico@gmail.com	Creo producto 'Camiseta unisex sin estampado color negro' (ID 9)\n- precio: COP 50,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Busos	2026-03-18 13:40:23
56	nico@gmail.com	Creo producto 'Camiseta unisex sin estampado color blanco' (ID 10)\n- precio: COP 50,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Busos	2026-03-18 13:41:20
57	nico@gmail.com	Creo producto 'Camiseta unisex manga larga sin estampado color negro' (ID 11)\n- precio: COP 80,00\n- stock: 10\n- fuerza: Ejercito\n- intendencia: Camibusos	2026-03-18 13:46:48
58	nico@gmail.com	Creo producto 'Camiseta unisex manga larga sin estampado color negro' (ID 12)\n- precio: COP 80,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Camibusos	2026-03-18 13:47:35
59	nico@gmail.com	Creo producto 'Guerrera' (ID 13)\n- precio: COP 160,00\n- stock: 10\n- fuerza: Gaula\n- intendencia: Camuflados	2026-03-18 14:14:00
60	nico@gmail.com	Creo producto 'Pantalón' (ID 14)\n- precio: COP 180,00\n- stock: 10\n- fuerza: Gaula\n- intendencia: Camuflados	2026-03-18 14:15:35
61	nico@gmail.com	Creo producto 'Camiseta unisex sin estampado color negro' (ID 15)\n- precio: COP 50,00\n- stock: 10\n- fuerza: Gaula\n- intendencia: Busos	2026-03-18 14:18:51
62	nico@gmail.com	Creo producto 'Camiseta unisex sin estampado color blanco' (ID 16)\n- precio: COP 50,00\n- stock: 10\n- fuerza: Gaula\n- intendencia: Busos	2026-03-18 14:20:17
63	nico@gmail.com	Creo producto 'Guerrera' (ID 17)\n- precio: COP 160,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Camuflados	2026-03-18 14:23:44
64	nico@gmail.com	Creo producto 'Pantalón' (ID 18)\n- precio: COP 180,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Camuflados	2026-03-18 14:25:10
65	julio@gmail.com	Inicio de sesion exitoso	2026-03-18 14:29:18
66	julio@gmail.com	Creo pedido #14 con 1 producto(s) por COP 160,00	2026-03-18 14:31:15
67	nico@gmail.com	Inicio de sesion exitoso	2026-03-18 14:32:38
68	nico@gmail.com	Creo producto 'Moño' (ID 19)\n- precio: COP 20,00\n- stock: 10\n- fuerza: Policia\n- intendencia: Panoletas	2026-03-18 14:33:51
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
79	julio@gmail.com	Inicio de sesion exitoso	2026-03-23 17:20:06
80	nico@gmail.com	Inicio de sesion exitoso	2026-03-23 17:20:19
81	julio@gmail.com	Inicio de sesion exitoso	2026-03-23 17:22:56
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.usuarios (id_usuario, nombre, email, password_hash, rol, estado, fecha_registro, email_verified, verification_code, verification_code_expiry) FROM stdin;
1	Nico	nico@gmail.com	admin	admin	activo	2026-02-06 14:55:32	f	\N	\N
2	Julio	julio@gmail.com	admin	normal	activo	2026-02-06 14:55:32	f	801703	2026-03-06 14:07:29
3	Alvaréx Freo	alv@gmail.com	admin	normal	activo	2026-02-06 16:40:07	f	\N	\N
4	jilmer	hola@gmail.com	admin	admin	activo	2026-02-20 15:47:06	f	\N	\N
5	Isabel	hola3@gmail.com	123456789	normal	activo	2026-02-20 15:47:36	f	\N	\N
6	Tatiana Rivera	tatis@gmail.com	admin	normal	activo	2026-02-25 22:35:53	f	\N	\N
7	Tatiana Rivera	tr3303419@gmail.com	admin	normal	inactivo	2026-02-26 22:54:23	f	\N	\N
8	David	david@gmail.com	4321	normal	activo	2026-03-04 19:37:39	f	\N	\N
9	David	rodriguezsierradavidsantiago@gmail.com	54321	normal	activo	2026-03-04 22:56:35	t	844313	2026-03-04 23:45:18
10	Catalina rodriguez	catar@gmail.com	Catalina1.	normal	activo	2026-03-13 15:30:56	\N	\N	\N
\.


--
-- Name: categoria_producto_id_categoria_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.categoria_producto_id_categoria_seq', 44, true);


--
-- Name: promociones_id_promo_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.promociones_id_promo_seq', 1, false);


--
-- Name: categoria_producto categoria_producto_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categoria_producto
    ADD CONSTRAINT categoria_producto_pkey PRIMARY KEY (id_categoria);


--
-- Name: promociones promociones_codigo_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.promociones
    ADD CONSTRAINT promociones_codigo_key UNIQUE (codigo);


--
-- Name: promociones promociones_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.promociones
    ADD CONSTRAINT promociones_pkey PRIMARY KEY (id_promo);


--
-- PostgreSQL database dump complete
--

\unrestrict gxSVogMxz2bGCW2npxm5yPATsU58jFnTC1r5vE8NmpV8skTBCzddj5DUINLr3Pa

