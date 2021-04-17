#! /bin/bash
gunicorn --name recommand_back --timeout "40" -t 3000 -b 0.0.0.0:5000 -w 5 wsgi:app &
