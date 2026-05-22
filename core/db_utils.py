import os
import re

import pandas as pd
import sqlalchemy as sa

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


def load_local_env():
    """Carga variables desde .env aun si python-dotenv no esta instalado."""
    if load_dotenv is not None:
        load_dotenv()
        return

    project_root = os.path.dirname(os.path.dirname(__file__)) if os.path.basename(os.path.dirname(__file__)) == "core" else os.path.dirname(__file__)
    env_path = os.path.join(project_root, ".env")
    if not os.path.exists(env_path):
        return

    with open(env_path, "r", encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


load_local_env()

def _normalize_database_url(raw_url):
    url = str(raw_url or "").strip()
    if not url:
        return "postgresql+psycopg://postgres:admin@localhost:5432/software_de_oro"
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://") :]
    if url.startswith("postgresql://") and not url.startswith("postgresql+"):
        return "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


DATABASE_URL = _normalize_database_url(
    os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:admin@localhost:5432/software_de_oro",
    )
)
engine = sa.create_engine(DATABASE_URL, future=True)


IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _safe_identifier(value):
    ident = str(value or "").strip()
    if not IDENTIFIER_PATTERN.fullmatch(ident):
        raise ValueError(f"Identificador SQL invalido: {value!r}")
    return ident


def ensure_tables():
    """Crea y ajusta las tablas base de la aplicacion en PostgreSQL."""
    ddl = """
    CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario BIGSERIAL PRIMARY KEY,
        nombre TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        rol TEXT NOT NULL DEFAULT 'usuario',
        estado TEXT NOT NULL DEFAULT 'activo',
        fecha_registro TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        telefono TEXT,
        direccion TEXT,
        email_verified BOOLEAN NOT NULL DEFAULT FALSE,
        verification_code TEXT,
        verification_code_expiry TIMESTAMPTZ,
        reset_token TEXT,
        reset_token_expiry TIMESTAMPTZ,
        password_change_code TEXT,
        password_change_code_expiry TIMESTAMPTZ,
        terminos_identidad_aceptados BOOLEAN NOT NULL DEFAULT FALSE,
        terminos_identidad_fecha TIMESTAMPTZ
    );
    CREATE TABLE IF NOT EXISTS registros (
        id_registro BIGSERIAL PRIMARY KEY,
        id_usuario BIGINT,
        accion TEXT NOT NULL,
        fecha_accion TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS categoria_producto (
        id_categoria BIGSERIAL PRIMARY KEY,
        nombre_categoria TEXT,
        descripcion TEXT
    );
    CREATE TABLE IF NOT EXISTS producto (
        id_producto BIGSERIAL PRIMARY KEY,
        nombre TEXT,
        descripcion TEXT,
        precio NUMERIC(12,2),
        stock INT,
        id_categoria BIGINT,
        imagen_url TEXT,
        eliminado BOOLEAN DEFAULT FALSE,
        destacado_dashboard BOOLEAN DEFAULT FALSE,
        fuerza TEXT,
        intendencia TEXT
    );
    CREATE TABLE IF NOT EXISTS pedidos (
        id_pedido BIGSERIAL PRIMARY KEY,
        id_usuario BIGINT,
        fecha_pedido TIMESTAMPTZ DEFAULT NOW(),
        estado TEXT,
        cliente_telefono TEXT,
        cliente_direccion TEXT
    );
    CREATE TABLE IF NOT EXISTS detalle_pedido (
        id_detalle BIGSERIAL PRIMARY KEY,
        id_pedido BIGINT,
        id_producto BIGINT,
        cantidad INT,
        subtotal NUMERIC(12,2),
        talla TEXT
    );
    CREATE TABLE IF NOT EXISTS promociones (
        id_promo BIGSERIAL PRIMARY KEY,
        nombre TEXT,
        descripcion TEXT,
        tipo_descuento TEXT,
        valor_descuento NUMERIC(12,2),
        id_producto BIGINT,
        codigo TEXT UNIQUE,
        fecha_inicio DATE,
        fecha_fin DATE,
        activo BOOLEAN DEFAULT TRUE
    );
    CREATE TABLE IF NOT EXISTS pagos (
        id_pago BIGSERIAL PRIMARY KEY,
        id_pedido BIGINT,
        monto NUMERIC(12,2),
        metodo_pago TEXT,
        fecha_pago TIMESTAMPTZ DEFAULT NOW(),
        estado_pago TEXT,
        comprobante_url TEXT,
        id_promo BIGINT,
        codigo_promo TEXT,
        tipo_descuento TEXT,
        valor_descuento NUMERIC(12,2),
        monto_descuento NUMERIC(12,2)
    );
    CREATE TABLE IF NOT EXISTS carrito_usuario (
        email TEXT PRIMARY KEY,
        carrito_json TEXT NOT NULL DEFAULT '[]',
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS stripe_checkout (
        session_id TEXT PRIMARY KEY,
        usuario_email TEXT NOT NULL,
        codigo_promo TEXT NOT NULL DEFAULT '',
        carrito_json TEXT NOT NULL DEFAULT '[]',
        cart_hash TEXT NOT NULL DEFAULT '',
        total_esperado NUMERIC(12,2) NOT NULL DEFAULT 0,
        estado TEXT NOT NULL DEFAULT 'creado',
        id_pedido BIGINT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """
    with engine.begin() as conn:
        conn.execute(sa.text(ddl))
        conn.execute(sa.text("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS reset_token TEXT"))
        conn.execute(sa.text("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS reset_token_expiry TIMESTAMPTZ"))
        conn.execute(sa.text("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS password_change_code TEXT"))
        conn.execute(sa.text("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS password_change_code_expiry TIMESTAMPTZ"))
        conn.execute(sa.text("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS telefono TEXT"))
        conn.execute(sa.text("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS direccion TEXT"))
        conn.execute(sa.text("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS terminos_identidad_aceptados BOOLEAN NOT NULL DEFAULT FALSE"))
        conn.execute(sa.text("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS terminos_identidad_fecha TIMESTAMPTZ"))
        conn.execute(sa.text("ALTER TABLE producto ADD COLUMN IF NOT EXISTS fuerza TEXT"))
        conn.execute(sa.text("ALTER TABLE producto ADD COLUMN IF NOT EXISTS intendencia TEXT"))
        conn.execute(sa.text("ALTER TABLE producto ADD COLUMN IF NOT EXISTS destacado_dashboard BOOLEAN DEFAULT FALSE"))
        conn.execute(sa.text("ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS cliente_telefono TEXT"))
        conn.execute(sa.text("ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS cliente_direccion TEXT"))
        conn.execute(sa.text("ALTER TABLE detalle_pedido ADD COLUMN IF NOT EXISTS talla TEXT"))
        conn.execute(sa.text("ALTER TABLE pagos ADD COLUMN IF NOT EXISTS comprobante_url TEXT"))
        conn.execute(sa.text("ALTER TABLE promociones ADD COLUMN IF NOT EXISTS id_producto BIGINT"))
        conn.execute(sa.text("ALTER TABLE stripe_checkout ADD COLUMN IF NOT EXISTS carrito_json TEXT NOT NULL DEFAULT '[]'"))


def read_table_df(table_name):
    table = _safe_identifier(table_name)
    with engine.connect() as conn:
        return pd.read_sql(sa.text(f'SELECT * FROM "{table}"'), conn)


def replace_table_df(table_name, df):
    """
    Reemplaza el contenido de una tabla preservando su estructura (DDL, constraints e indices).
    """
    table = _safe_identifier(table_name)
    data = df if df is not None else pd.DataFrame()

    with engine.begin() as conn:
        conn.execute(sa.text(f'DELETE FROM "{table}"'))
        if not data.empty:
            data.to_sql(table, con=conn, if_exists="append", index=False, method="multi")


def next_id(table_name, id_column):
    table = _safe_identifier(table_name)
    column = _safe_identifier(id_column)
    with engine.connect() as conn:
        query = sa.text(f'SELECT COALESCE(MAX("{column}"), 0) + 1 FROM "{table}"')
        return int(conn.execute(query).scalar_one())


def init_db():
    ensure_tables()
    return engine


init_db()

__all__ = [
    "DATABASE_URL",
    "engine",
    "ensure_tables",
    "init_db",
    "next_id",
    "read_table_df",
    "replace_table_df",
]
