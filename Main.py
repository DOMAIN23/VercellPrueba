from app import create_app

try:
    app = create_app()
except Exception as e:
    print(f"Error al crear la app: {e}")
    import sys
    sys.exit(1)

if __name__ == '__main__':
    app.run(debug=True)

