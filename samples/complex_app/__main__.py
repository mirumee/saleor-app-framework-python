import sys

import uvicorn

from .db import configuration, get_db, get_domain_config


def add_domain(saleor_domain):
    db = next(get_db())
    db_config = get_domain_config(db, saleor_domain)
    if not db_config:
        query = configuration.insert().values(
            saleor_domain=saleor_domain,
        )
        db.execute(query)
        db.commit()


def main():
    uvicorn.run(
        "complex_app.app:app", host="0.0.0.0", port=5000, debug=True, reload=True
    )


if __name__ == "__main__":
    if len(sys.argv) == 3:
        if sys.argv[1] == "add-domain":
            add_domain(sys.argv[2])

    main()
