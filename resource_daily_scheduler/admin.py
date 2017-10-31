from djangoautoconf.auto_conf_admin_tools.admin_register import AdminRegister

import models
factory = AdminRegister()

factory.register_all_model(models)
# from reversion.helpers import patch_admin
#
# patch_admin(models.BookingRequest)
# patch_admin(models.BookableResource)

# import eav
# eav.register(models.BookableResource)


# from south.modelsinspector import add_ignored_fields
# add_ignored_fields(["^eav\.fields\.EavDatatypeField"])
# add_ignored_fields(["^eav\.fields\.EavSlugField"])
