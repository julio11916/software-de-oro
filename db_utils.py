import os
import pandas as pd
import sqlalchemy as sa

# Tablas y archivos heredados de Excel
EXCEL_TABLES = {
    "usuarios": "usuarios.xlsx",
    "registros": "registros.xlsx",
    "promociones": "promociones.xlsx",
    "categoria_producto": "categoria_producto.xlsx",
    "producto": "producto.xlsx",
    "pedidos": "pedidos.xlsx",
    "detalle_pedido": "detalle_pedido.xlsx",
    "pagos": "pagos.xlsx",
}

# Referencias originales para proxys
_pd_read_excel_original = pd.read_excel
_pd_to_excel_original = pd.DataFrame.to_excel
_os_path_exists_original = os.path.exists

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql+psycopg://postgres:@localhost:5432/software_de_oro"
)
engine = sa.create_engine(DATABASE_URL, future=True)


def ensure_tables():
    """Crea tablas vacias en Postgres si no existen (sustituye a los .xlsx)."""
    ddl = """
    CREATE TABLE IF NOT EXISTS usuarios (
        id_usuario BIGSERIAL PRIMARY KEY,
        nombre TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        rol TEXT NOT NULL DEFAULT 'usuario',
        estado TEXT NOT NULL DEFAULT 'activo',
        fecha_registro TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        email_verified BOOLEAN NOT NULL DEFAULT FALSE,
        verification_code TEXT,
        verification_code_expiry TIMESTAMPTZ
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
        eliminado BOOLEAN DEFAULT FALSE
    );
    CREATE TABLE IF NOT EXISTS pedidos (
        id_pedido BIGSERIAL PRIMARY KEY,
        id_usuario BIGINT,
        fecha_pedido TIMESTAMPTZ DEFAULT NOW(),
        estado TEXT
    );
    CREATE TABLE IF NOT EXISTS detalle_pedido (
        id_detalle BIGSERIAL PRIMARY KEY,
        id_pedido BIGINT,
        id_producto BIGINT,
        cantidad INT,
        subtotal NUMERIC(12,2)
    );
    CREATE TABLE IF NOT EXISTS promociones (
        id_promo BIGSERIAL PRIMARY KEY,
        nombre TEXT,
        descripcion TEXT,
        tipo_descuento TEXT,
        valor_descuento NUMERIC(12,2),
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
        id_promo BIGINT,
        codigo_promo TEXT,
        tipo_descuento TEXT,
        valor_descuento NUMERIC(12,2),
        monto_descuento NUMERIC(12,2)
    );
    """
    with engine.begin() as conn:
        conn.execute(sa.text(ddl))


def cleanup_orphans_and_add_fks():
    """Borra huerfanos y agrega llaves foraneas si no existen."""
    return  # desactivado para evitar errores sobre datos existentes


def bootstrap_tables_from_excel():
    """Si la tabla no existe o esta vacia, la crea y llena desde los .xlsx existentes."""
    inspector = sa.inspect(engine)
    for table, filename in EXCEL_TABLES.items():
        path = os.path.join("bd", filename)
        if not _os_path_exists_original(path):
            continue

        table_exists = inspector.has_table(table)
        row_count = 0
        if table_exists:
            with engine.connect() as conn:
                row_count = conn.execute(sa.text(f"SELECT COUNT(*) FROM {table}")).scalar_one()

        if (not table_exists) or row_count == 0:
            df = _pd_read_excel_original(path)
            if df.empty:
                continue
            df.to_sql(table, con=engine, if_exists="replace", index=False)
    inspector.clear_cache()


def _read_excel_proxy(path, *args, **kwargs):
    """Redirige lecturas de bd/*.xlsx a tablas SQL."""
    if isinstance(path, str) and path.startswith("bd/"):
        table = os.path.splitext(os.path.basename(path))[0]
        with engine.connect() as conn:
            return pd.read_sql(sa.text(f"SELECT * FROM {table}"), conn)
    return _pd_read_excel_original(path, *args, **kwargs)


def _to_excel_proxy(self, excel_writer, *args, **kwargs):
    """Redirige escrituras de bd/*.xlsx a tablas SQL; demas usos siguen igual."""
    if isinstance(excel_writer, str) and excel_writer.startswith("bd/"):
        table = os.path.splitext(os.path.basename(excel_writer))[0]
        self.to_sql(table, con=engine, if_exists="replace", index=False)
        return
    return _pd_to_excel_original(self, excel_writer, *args, **kwargs)


def _path_exists_proxy(path):
    """Hace que las rutas bd/*.xlsx 'existan' aunque los archivos ya no esten."""
    if isinstance(path, str) and path.startswith("bd/"):
        return True
    return _os_path_exists_original(path)


def cleanup_excel_copies():
    """Elimina copias locales de Excel si aun existen."""
    for filename in EXCEL_TABLES.values():
        path = os.path.join("bd", filename)
        if _os_path_exists_original(path):
            try:
                os.remove(path)
            except OSError:
                pass


def install_excel_proxies():
    pd.read_excel = _read_excel_proxy
    pd.DataFrame.to_excel = _to_excel_proxy
    os.path.exists = _path_exists_proxy


def init_db():
    ensure_tables()
    bootstrap_tables_from_excel()
    cleanup_excel_copies()
    cleanup_orphans_and_add_fks()
    install_excel_proxies()
    return engine


# Inicializa al importar
init_db()

__all__ = [
    "engine",
    "init_db",
    "ensure_tables",
    "bootstrap_tables_from_excel",
    "EXCEL_TABLES",
]
