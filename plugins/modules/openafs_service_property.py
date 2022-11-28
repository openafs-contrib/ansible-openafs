#!/usr/bin/python
# Copyright (c) 2022, Sine Nomine Associates
# BSD 2-Clause License

ANSIBLE_METADATA = {
    'metadata_version': '1.1.',
    'status': ['preview'],
    'supported_by': 'community',
}

DOCUMENTATION = r'''
---
module: openafs_service_properties

short_description: Manage Solaris service properties.

description:
  - Set service properties using the Solaris svc commands.

options:

  state:
    description:
      - If C(present) the C(property) will be set to the given C(value).
      - If C(absent) the C(property) will be deleted.

  service:
    description: The SMF service name.
    required: True

  instance:
    description: The SMF service instance name.
    default: "default"

  property:
    description: The property name.
    required: True

  value:
    description: The property value. Requiried when C(state) is C(present).

  single:
    description:
      - If True, the value is a single string.
      - If False, the value is a space separated list of strings.
    type: bool
    default: True

author:
  - Michael Meffie
'''

EXAMPLES = r'''
- name: Set client startup arguments.
  openafs_service_property:
    state: present
    service: network/openafs/client
    instance: default
    property: afsd/arguments
    value: -dynroot -fakestat -afsd
    single: no
'''

RETURN = r'''
service:
  description: SMF service name
  type: str
  returned: always
instance:
  description: SMF service instance
  type: str
  returned: always
property:
  description: SMF service property name
  type: str
  returned: always
value:
  description: SMF service property value
  type: str
  returned: on success
single:
  description: Value is a single string
  type: bool
  returned: always
'''

from ansible.module_utils.basic import AnsibleModule   # noqa: E402


class ServiceProperty(object):
    """
    Manage Solaris service properties.
    """

    def __init__(self, module):
        self.module = module
        self.state = module.params['state']
        self.service = module.params['service']
        self.instance = module.params['instance']
        self.property = module.params['property']
        self.value = module.params['value']
        self.single = module.params['single']
        self.changed = False

    def get_property(self):
        """
        Retreive the value of an existing property.
        """
        cmd = [self.module.get_bin_path('svcprop', required=True)]
        cmd.append('-p')
        cmd.append(self.property)
        cmd.append(':'.join([self.service, self.instance]))
        rc, out, err = self.module.run_command(cmd)
        if rc != 0:
            self.module.fail_json(
                msg='Failed to get property',
                cmd=cmd, rc=rc, out=out, err=err)
        return out.rstrip()

    def set_property(self):
        """
        Set the value for an existing property.
        """
        cmd = [self.module.get_bin_path('svccfg', required=True)]
        cmd.append('-s')
        cmd.append(':'.join([self.service, self.instance]))
        cmd.append('setprop')
        cmd.append(self.property)
        cmd.append('=')
        if self.single:
            cmd.append(self.value)
        else:
            cmd.append('(')
            if ' ' in self.value:
                cmd.extend(self.value.split())
            else:
                cmd.append(self.value)
            cmd.append(')')
        rc, out, err = self.module.run_command(cmd)
        if rc != 0:
            self.module.fail_json(
                msg='Failed to set property',
                cmd=cmd, rc=rc, out=out, err=err)
        self._refresh()
        self.changed = True

    def clear_property(self):
        """
        Delete the property.
        """
        cmd = [self.module.get_bin_path('svccfg', required=True)]
        cmd.append('-s')
        cmd.append(':'.join([self.service, self.instance]))
        cmd.append('delprop')
        cmd.append(self.property)
        rc, out, err = self.module.run_command(cmd)
        if rc != 0:
            self.module.fail_json(
                msg='Failed to set property',
                cmd=cmd, rc=rc, out=out, err=err)
        self._refresh()
        self.changed = True

    def _refresh(self):
        """
        Refresh the service to apply the new property value.
        """
        cmd = [self.module.get_bin_path('svcadm')]
        cmd.append('refresh')
        cmd.append(':'.join([self.service, self.instance]))
        rc, out, err = self.module.run_command(cmd)
        if rc != 0:
            self.module.fail_json(
                msg='Failed to refresh service',
                cmd=cmd, rc=rc, out=out, err=err)


def main():
    module = AnsibleModule(
            argument_spec=dict(
                state=dict(type='str',
                           choices=['present', 'absent'],
                           default='present'),
                service=dict(required=True),
                instance=dict(required=False, default='default'),
                property=dict(required=True),
                value=dict(required=False),
                single=dict(type='bool', default=True),
            ),
            supports_check_mode=False,
    )

    prop = ServiceProperty(module)
    if prop.state == 'present':
        if prop.value is None:
            module.fail_json(msg='Value is mandatory with state "present"')
        value = prop.get_property()
        if value != prop.value:
            prop.set_property()
        value = prop.get_property()
    elif prop.state == 'absent':
        prop.clear_property()
        value = prop.get_property()
    else:
        raise AssertionError('Invalid state: %s' % prop.state)

    results = {
        'changed': prop.changed,
        'service': prop.service,
        'instance': prop.instance,
        'property': prop.property,
        'value': value,
        'single': prop.single,
    }
    module.exit_json(**results)


if __name__ == '__main__':
    main()
