import os
from .remind import create_app
import sys

app = create_app()

if __name__ == "__main__":
    """
    This is the entry point for starting the application.
    It reads environment variables to decide between the 
    Development (Flask) or Production (Waitress) server.
    """

    env = os.getenv("FLASK_ENV", "development")
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 4000))

    if env == "production":
        # Production Server: Waitress
        try:
            from waitress import serve

            sys.stdout.write(f"Serving REmind on http://{host}:{port}")
            sys.stdout.flush()
            serve(app, host=host, port=port)
        except ImportError:
            print(
                "Error: 'waitress' not installed. Install it via: pip install waitress"
            )
    else:
        app.run(host=host, port=port)
