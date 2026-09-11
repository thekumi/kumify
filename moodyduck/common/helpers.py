import uuid


def get_upload_path(instance, filename):
    return f"usermedia/{instance.user.id}/{uuid.uuid4()!s}/{filename}"
