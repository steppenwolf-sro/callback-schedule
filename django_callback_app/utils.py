from rest_framework import permissions


class ProtectedPermission(permissions.DjangoModelPermissions):
    def __init__(self):
        super().__init__()
        self.perms_map['GET'] = ['%(app_label)s.change_%(model_name)s']
