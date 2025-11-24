# tickets/constants.py

class TicketStatus:
    ABIERTO = 'Abierto'
    EN_REPARACION = 'En Reparación'
    EN_REPARACION_SIN_TILDE = 'En Reparacion' # For compatibility if needed
    CERRADO = 'Cerrado'

    ALL = [ABIERTO, EN_REPARACION, CERRADO]

class Turno:
    PRIMERO = "1er Turno"
    SEGUNDO = "2do Turno"
    TERCERO = "3er Turno"

    ALL = [PRIMERO, SEGUNDO, TERCERO]

class ChartColors:
    # Hex colors
    ABIERTO_HEX = '#FF6384'
    EN_REPARACION_HEX = '#FFCE56'
    CERRADO_HEX = '#4BC0C0'
    DEFAULT_HEX = '#CCCCCC'

    # RGBA colors
    ABIERTO_RGBA = 'rgba(255, 99, 132, 0.7)'
    EN_REPARACION_RGBA = 'rgba(255, 206, 86, 0.7)'
    CERRADO_RGBA = 'rgba(75, 192, 192, 0.7)'

    HEX_MAP = {
        TicketStatus.ABIERTO: ABIERTO_HEX,
        TicketStatus.EN_REPARACION: EN_REPARACION_HEX,
        TicketStatus.EN_REPARACION_SIN_TILDE: EN_REPARACION_HEX,
        TicketStatus.CERRADO: CERRADO_HEX,
    }

    RGBA_MAP = {
        TicketStatus.ABIERTO: ABIERTO_RGBA,
        TicketStatus.EN_REPARACION: EN_REPARACION_RGBA,
        TicketStatus.EN_REPARACION_SIN_TILDE: EN_REPARACION_RGBA,
        TicketStatus.CERRADO: CERRADO_RGBA,
    }
