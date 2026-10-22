# Fake the package manager modules which are run by the normal action plugin,
# such as community.general.zypper, with the fake_package module. All the
# other modules are run as usual.
#
# This replaces the ansible.builtin.normal action plugin, which can not be
# imported here, since this plugin is loaded with the same name.

from ansible import constants as C
from ansible.plugins.action import ActionBase
from ansible.utils.vars import merge_hash

FAKE_MODULES = (
    "apt",
    "ansible.builtin.apt",
    "zypper",
    "community.general.zypper",
    "community.general.pkgng",
    "community.general.pkg5",
)


class ActionModule(ActionBase):

    _supports_check_mode = True
    _supports_async = True

    def run(self, tmp=None, task_vars=None):
        result = super().run(tmp, task_vars)
        wrap_async = self._task.async_val
        module_name = None
        if self._task.action in FAKE_MODULES:
            module_name = "ansible.legacy.fake_package"
        result = merge_hash(
            result,
            self._execute_module(module_name=module_name, task_vars=task_vars, wrap_async=wrap_async),
        )
        if self._task.action in C._ACTION_SETUP:
            result["_ansible_verbose_override"] = True
        if not wrap_async:
            self._remove_tmp_path(self._connection._shell.tmpdir)
        return result
