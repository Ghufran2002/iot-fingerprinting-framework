from src.dashboard.app import app
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8050))
    app.run(debug=False, port=port, host="0.0.0.0")
