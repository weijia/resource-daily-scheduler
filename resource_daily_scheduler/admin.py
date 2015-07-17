from djangoautoconf.auto_conf_admin_tools.admin_register import AdminRegister

import models
factory = AdminRegister()

factory.register_all_model(models)
from reversion.helpers import patch_admin

patch_admin(models.BookingRequest)
patch_admin(models.BookableResource)


from reversion import models

factory.register_all_model(models)