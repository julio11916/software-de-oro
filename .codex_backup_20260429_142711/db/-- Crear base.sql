-- Crear base

CREATE DATABASE software_de_oro WITH ENCODING 'UTF8';

\c software_de_oro;

-- Usuarios y auditoría

CREATE TABLE usuarios (id_usuario BIGSERIAL PRIMARY KEY,
                                            nombre TEXT NOT NULL,
                                                        email TEXT NOT NULL UNIQUE,
                                                                            password_hash TEXT NOT NULL,
                                                                                               rol TEXT NOT NULL DEFAULT 'usuario',
                                                                                                                         estado TEXT NOT NULL DEFAULT 'activo',
                                                                                                                                                      fecha_registro TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                                                                                                                                                                                                  email_verified BOOLEAN NOT NULL DEFAULT FALSE,
                                                                                                                                                                                                                                          verification_code TEXT, verification_code_expiry TIMESTAMPTZ);


CREATE TABLE registros
    (id_registro BIGSERIAL PRIMARY KEY,
                           id_usuario BIGINT REFERENCES usuarios(id_usuario) ON DELETE CASCADE,
                                                                                       accion TEXT NOT NULL,
                                                                                                   fecha_accion TIMESTAMPTZ NOT NULL DEFAULT NOW());

-- Catálogo: fuerzas, prendas, categorías y productos

CREATE TABLE fuerza (id_fuerza SERIAL PRIMARY KEY,
                                      nombre TEXT NOT NULL UNIQUE);


CREATE TABLE prenda (id_prenda SERIAL PRIMARY KEY,
                                      nombre TEXT NOT NULL UNIQUE);


CREATE TABLE categoria_producto (id_categoria SERIAL PRIMARY KEY,
                                                     id_fuerza INT NOT NULL REFERENCES fuerza(id_fuerza),
                                                                                       id_prenda INT NOT NULL REFERENCES prenda(id_prenda),
                                                                                                                         descripcion TEXT, UNIQUE (id_fuerza,
                                                                                                                                                   id_prenda));


CREATE TABLE producto (id_producto SERIAL PRIMARY KEY,
                                          nombre TEXT NOT NULL,
                                                      descripcion TEXT, precio NUMERIC(12, 2) NOT NULL DEFAULT 0,
                                                                                                               stock INT NOT NULL DEFAULT 0,
                                                                                                                                          id_categoria INT REFERENCES categoria_producto(id_categoria),
                                                                                                                                                                      imagen_url TEXT, eliminado BOOLEAN NOT NULL DEFAULT FALSE);

-- Pedidos y pagos

CREATE TABLE pedidos (id_pedido SERIAL PRIMARY KEY,
                                       id_usuario BIGINT REFERENCES usuarios(id_usuario),
                                                                    fecha_pedido TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                                                                                                              estado TEXT NOT NULL DEFAULT 'pendiente');


CREATE TABLE detalle_pedido
    (id_detalle SERIAL PRIMARY KEY,
                       id_pedido INT NOT NULL REFERENCES pedidos(id_pedido) ON DELETE CASCADE,
                                                                                      id_producto INT NOT NULL REFERENCES producto(id_producto),
                                                                                                                          cantidad INT NOT NULL,
                                                                                                                                       subtotal NUMERIC(12, 2) NOT NULL);


CREATE TABLE promociones (id_promo SERIAL PRIMARY KEY,
                                          nombre TEXT NOT NULL,
                                                      descripcion TEXT, tipo_descuento TEXT CHECK (tipo_descuento IN ('porcentaje',
                                                                                                                      'monto')), valor_descuento NUMERIC(12, 2),
                                                                                                                                                 codigo TEXT UNIQUE,
                                                                                                                                                             fecha_inicio DATE, fecha_fin DATE, activo BOOLEAN NOT NULL DEFAULT TRUE);


CREATE TABLE pagos (id_pago SERIAL PRIMARY KEY,
                                   id_pedido INT REFERENCES pedidos(id_pedido),
                                                            monto NUMERIC(12, 2) NOT NULL,
                                                                                 metodo_pago TEXT, fecha_pago TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                                                                                                                                           estado_pago TEXT NOT NULL DEFAULT 'pendiente',
                                                                                                                                                                             id_promo INT REFERENCES promociones(id_promo),
                                                                                                                                                                                                     codigo_promo TEXT, tipo_descuento TEXT, valor_descuento NUMERIC(12, 2),
                                                                                                                                                                                                                                                             monto_descuento NUMERIC(12, 2));

-- Catálogo base solicitado

INSERT INTO fuerza (nombre)
VALUES ('Policia'),
       ('Ejercito'),
       ('Armada'),
       ('Gaula');


INSERT INTO prenda (nombre)
VALUES ('Busos'),
       ('Camibusos'),
       ('Gorras'),
       ('Panoletas'),
       ('Sudaderas'),
       ('Pantalonetas'),
       ('Colchas'),
       ('Tendidos'),
       ('Chuspas para ropa sucia'),
       ('Fundas para almohadas'),
       ('Camuflados');

-- Genera cada combinación fuerza + prenda como categoría

INSERT INTO categoria_producto (id_fuerza, id_prenda, descripcion)
SELECT f.id_fuerza,
       p.id_prenda,
       CONCAT(f.nombre, ' - ', p.nombre)
FROM fuerza f
CROSS JOIN prenda p;