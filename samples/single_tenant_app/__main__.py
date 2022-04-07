import uvicorn


def main():
    uvicorn.run(
        "single_tenant_app.app:app", host="0.0.0.0", port=5000, debug=True, reload=True
    )


if __name__ == "__main__":
    main()
