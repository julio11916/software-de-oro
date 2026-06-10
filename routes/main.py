from flask import Blueprint, jsonify

main_bp = Blueprint("main", __name__)


@main_bp.get("/health")
def healthcheck():
    """Endpoint tecnico para verificar disponibilidad basica del servidor."""
    return jsonify({"ok": True, "module": "main"})

