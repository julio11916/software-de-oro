import os
from typing import Any, Dict, Tuple

try:
    import stripe
except ImportError:  # pragma: no cover
    stripe = None


def _strip_env(name: str) -> str:
    return str(os.getenv(name, "") or "").strip()


def stripe_secret_key() -> str:
    return _strip_env("STRIPE_SECRET_KEY")


def stripe_publishable_key() -> str:
    return _strip_env("STRIPE_PUBLISHABLE_KEY")


def stripe_currency() -> str:
    moneda = _strip_env("STRIPE_CURRENCY").lower()
    return moneda or "cop"


def stripe_disponible() -> bool:
    return bool(stripe is not None and stripe_secret_key() and stripe_publishable_key())


def stripe_estado_configuracion() -> Tuple[bool, str]:
    if stripe is None:
        return False, "Falta instalar el paquete stripe en el entorno."
    if not stripe_secret_key():
        return False, "No existe STRIPE_SECRET_KEY en variables de entorno."
    if not stripe_publishable_key():
        return False, "No existe STRIPE_PUBLISHABLE_KEY en variables de entorno."
    return True, ""


def _set_api_key() -> None:
    if stripe is None:
        raise RuntimeError("Stripe SDK no disponible.")
    stripe.api_key = stripe_secret_key()


def crear_checkout_sesion_tarjeta(
    amount_total: float,
    success_url: str,
    cancel_url: str,
    customer_email: str = "",
    descripcion: str = "Compra en tienda",
    metadata: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    ok, msg = stripe_estado_configuracion()
    if not ok:
        raise RuntimeError(msg)

    total_centavos = int(round(float(amount_total) * 100))
    if total_centavos <= 0:
        raise RuntimeError("Monto invalido para Stripe.")

    _set_api_key()
    session = stripe.checkout.Session.create(
        mode="payment",
        success_url=f"{success_url}?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=cancel_url,
        customer_email=customer_email or None,
        line_items=[
            {
                "price_data": {
                    "currency": stripe_currency(),
                    "product_data": {"name": descripcion[:120] or "Compra"},
                    "unit_amount": total_centavos,
                },
                "quantity": 1,
            }
        ],
        metadata={k: str(v) for k, v in (metadata or {}).items()},
    )
    return session


def obtener_checkout_sesion(session_id: str) -> Dict[str, Any]:
    ok, msg = stripe_estado_configuracion()
    if not ok:
        raise RuntimeError(msg)
    sid = str(session_id or "").strip()
    if not sid:
        raise RuntimeError("session_id vacio.")

    _set_api_key()
    return stripe.checkout.Session.retrieve(sid)
