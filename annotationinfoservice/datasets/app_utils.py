import flask
from middle_auth_client.decorators import dataset_from_table_id


def user_has_permission(permission, table_id, resource_namespace, service_token=None):
    token = (
        service_token
        if service_token
        else flask.current_app.config.get("AUTH_TOKEN", "")
    )

    dataset = dataset_from_table_id(resource_namespace, table_id, token)

    has_permission = permission in flask.g.auth_user.get("permissions_v2", {}).get(
        dataset, []
    )
    return has_permission
