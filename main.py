#!/usr/bin/env python3

from app import app
import views  # noqa isort:skip


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000', debug=True)
