from src.applications.boe_app import BOEApplication, PermissionsEnum


def main():
    app = BOEApplication()

    app.create_new_parent(
        first_name='test',
        last_name='test',
        email='test@gmail.com',
        role_name='test_role',
        permissions=[PermissionsEnum.ADMIN]
    )




if __name__ == "__main__":
    main()
