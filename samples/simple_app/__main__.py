import os

import uvicorn


def main():
    os.environ["APP_SETTINGS"] = "simple_app.app.settings"
    uvicorn.run(
        "simple_app.app:app", host="0.0.0.0", port=5000, debug=True, reload=True
    )


if __name__ == "__main__":
    main()
