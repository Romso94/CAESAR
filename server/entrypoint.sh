#!/bin/sh

echo "========================================"
echo " Initialisation du serveur"
echo "========================================"

# Génération du mot de passe admin si absent
if [ -z "$ADMIN_PASSWORD" ]; then
  ADMIN_PASSWORD=$(python3 - << 'EOF'
import secrets
import string

alphabet = (
    string.ascii_lowercase +
    string.ascii_uppercase +
    string.digits +
    "!@#$%^&*()-_=+[]{}:,.?"
)

password = ''.join(secrets.choice(alphabet) for _ in range(20))
print(password)
EOF
)
  export ADMIN_PASSWORD
fi

export ADMIN_USERNAME=admin

echo "Utilisateur admin créé :"
echo "  ➤ Username : $ADMIN_USERNAME"
echo "  ➤ Password : $ADMIN_PASSWORD"
echo "⚠️  Note ce mot de passe, il ne sera plus affiché"
echo "========================================"

exec "$@"
