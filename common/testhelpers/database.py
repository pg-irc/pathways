
def validate_save_and_reload(instance):
    instance.save()
    instance.refresh_from_db()
    return instance
