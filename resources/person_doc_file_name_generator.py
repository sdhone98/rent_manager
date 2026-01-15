def aadhaar_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    return f"documents/aadhaar/{instance.person_id}.{ext}"


def pan_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    return f"documents/pan/{instance.person_id}.{ext}"
