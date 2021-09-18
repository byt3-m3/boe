from src.applications.boe_app import BOEApplication, PermissionsEnum, query_table_dao
from bson import decode


def main():
    app = BOEApplication()

    app.create_new_parent(
        first_name='liam',
        last_name='baxter',
        email='liam.baxter@gmail.com',
        role_name='test_role',
        permissions=[PermissionsEnum.ADMIN]
    )

    app.create_new_parent(
        first_name='john',
        last_name='baxter',
        email='john.baxter@gmail.com',
        role_name='test_role',
        permissions=[PermissionsEnum.ADMIN]
    )
    items = query_table_dao.scan_adult_aggregates()
    print(items)


if __name__ == "__main__":
    main()
