import os
import sys
from waitress import serve
from sgtr.wsgi import application

def main():
    # Asegurar que el directorio actual está en el path
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

    # Obtener puerto de variable de entorno o usar 8000 por defecto
    port = int(os.environ.get('PORT', 8000))
    
    print(f"Iniciando servidor Waitress en el puerto {port}...")
    print(f"Accede a la aplicación en http://localhost:{port}")
    
    # Iniciar servidor
    serve(application, host='0.0.0.0', port=port, threads=4)

if __name__ == "__main__":
    main()
