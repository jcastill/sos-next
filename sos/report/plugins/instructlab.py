# Copyright (C) 2024 Red Hat, Inc., Jose Castillo <jcastillo@redhat.com>

# This file is part of the sos project: https://github.com/sosreport/sos
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# version 2 of the GNU General Public License.
#
# See the LICENSE file in the source distribution for further information.

from sos.report.plugins import Plugin, IndependentPlugin


class Instructlab(Plugin, IndependentPlugin):

    short_desc = 'Instructlab'
    plugin_name = 'instructlab'
    profiles = ('ai',)
    containers = ('instructlab', 'ilab',)

    def setup(self):
        config_dir = '/usr/share/instructlab/config/'
        opt_dir = '/opt/app-root/src/.config/instructlab/'

        instructlab_con = None

        subcmds = [
            'taxonomy diff',
            'taxonomy diff --taxonomy-base=empty',
            'system info',
            'model list',
            'config show'
        ]

        for con in self.containers:
            if self.get_container_by_name(con):
                instructlab_con = con
                self.add_copy_spec([f'{config_dir}rhel_ai_config.yaml',
                                    f'{opt_dir}config.yaml'],
                                   container=instructlab_con)
                self.add_cmd_output(
                    [f"ilab {sub}" for sub in subcmds],
                    container=instructlab_con
                )
                self.add_container_logs(instructlab_con)


# vim: set et ts=4 sw=4 :
