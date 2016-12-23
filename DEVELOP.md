# How to develop

Build and run backend:

```bash
./build_backend.sh
./backend.sh
```

Handle i18n:

```bash
# backend
./exec.sh ./makemessages.sh
# frontend
./exec.sh ./makemessages.sh --domain=djangojs
./exec.sh ./compilemessages.sh
```
