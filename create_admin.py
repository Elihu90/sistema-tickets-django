from django.contrib.auth import get_user_model

User = get_user_model()

if User.objects.filter(username='admin').exists():
    print('⚠️  El usuario admin ya existe')
    user = User.objects.get(username='admin')
    print(f'Usuario: {user.username}')
    print(f'Email: {user.email}')
else:
    user = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='admin123'
    )
    print('✅ Superusuario creado exitosamente!')
    print('')
    print('Credenciales:')
    print('  Usuario: admin')
    print('  Contraseña: admin123')
    print('')
    print('Accede al admin en: http://localhost:8000/admin')
