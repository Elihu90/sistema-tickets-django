# tickets/views/__init__.py

from .crud import (
    crear_ticket,
    lista_tickets,
    detalles_ticket,
    editar_ticket,
    eliminar_ticket,
)

from .dashboard import (
    dashboard_service_line,
    ticket_estado_data,
    exportar_tickets_excel,
    detalles_filtrados_modal,
)

from .api import (
    actualizar_estado_ticket,
    buscar_herramientas,
    verificar_ticket_duplicado,
)

from .notificaciones import (
    ver_notificaciones,
    contar_notificaciones_sin_leer,
    marcar_leida_y_redirigir,
)
