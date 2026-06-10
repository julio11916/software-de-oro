--
-- PostgreSQL database dump
--

\restrict jBP6GePU5nutNvsgxawlUsp0UAegNMf5h1ikSQGnQi7lXaA16bXUvoHuLqaK6cT

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
    cliente_direccion text,
    documento_validacion_json text DEFAULT ''::text NOT NULL
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
    terminos_identidad_fecha timestamp with time zone,
    cedula text,
    email_alternativo text
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

\unrestrict jBP6GePU5nutNvsgxawlUsp0UAegNMf5h1ikSQGnQi7lXaA16bXUvoHuLqaK6cT
