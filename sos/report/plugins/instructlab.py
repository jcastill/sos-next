# Copyright (C) 2024 Red Hat, Inc., Jose Castillo <jcastillo@redhat.com>

# This file is part of the sos project: https://github.com/sosreport/sos
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# version 2 of the GNU General Public License.
#
# See the LICENSE file in the source distribution for further information.

from sos.report.plugins import (Plugin, IndependentPlugin, PluginOpt)


class Instructlab(Plugin, IndependentPlugin):

    short_desc = 'Instructlab'
    plugin_name = 'instructlab'
    profiles = ('ai',)
    containers = ('instructlab', 'ilab',)

    option_list = [
        PluginOpt('ilab_user', default='root', val_type=str,
                  desc='user that runs instructlab'),
        PluginOpt('ilab_conf_dir', default='', val_type=str,
                  desc='instructlab data directory'),
        PluginOpt('get-cache', default=False,
                  desc='Capture models and osci cached data')
    ]

    def setup(self):
        cont_share_conf_path = '/usr/share/instructlab/config/'
        cont_opt_path = '/opt/app-root/src'
        # .cache dir contains the models and oci directories
        # which can be quite big. We'll gather this only if
        # specifying it via command line option
        cache_dir = '/.cache/instructlab'
        # .config is where the configuration yaml files can
        # be found. We gather this always.
        config_dir = '/.config/instructlab'
        # In the .local directory we can find datasets,
        # chat logs, taxonomies, and other very useful data
        # We gather this always.
        local_share_dir = '/.local/share/instructlab'

        # container paths
        cont_cache_path = f'{cont_opt_path}{cache_dir}'
        cont_config_path = f'{cont_opt_path}{config_dir}'
        cont_local_path = f'{cont_opt_path}{local_share_dir}'

        self.add_forbidden_path([
            f"{cont_local_path}/taxonomy/.git",
            f"{cont_local_path}/taxonomy/.github",
            ])

        subcmds = [
            'taxonomy diff',
            'taxonomy diff --taxonomy-base=empty',
            'system info',
            'model list',
            'config show'
        ]

        data_dirs = [
            'data',
            'generated',
            'taxonomy',
            'taxonomy_data',
            'chatlogs',
            'checkpoints',
            'datasets',
            'internal',
            'phased',
        ]

        in_container = False
        container_names = []
        _containers = self.get_containers()

        for _con in _containers:
            if _con[1].startswith('instructlab'):
                in_container = True
                container_names.append(_con[1])

        if in_container:
            for cont in container_names:
                self.add_copy_spec(
                    [f'{cont_share_conf_path}rhel_ai_config.yaml',
                     f'{cont_config_path}/config.yaml'],
                    container=cont)
                self.add_copy_spec(
                    [f"{cont_local_path}/{data_dir}"
                     for data_dir in data_dirs],
                    container=cont
                    )
                self.add_cmd_output(
                    [f"ilab {sub}" for sub in subcmds],
                    container=cont
                )
                self.add_cmd_output(f"ls -laR {cont_cache_path}",
                                    container=cont)
                if self.get_option("get-cache"):
                    self.add_copy_spec(
                        f'{cont_cache_path}',
                        container=cont
                        )
                self.add_container_logs(cont)

        if self.get_option("ilab_user"):
            ilab_dir = f'/home/{self.get_option("ilab_user")}'
            if self.get_option("ilab_conf_dir"):
                ilab_dir = f'{ilab_dir}{self.get_option("ilab_conf_dir")}'
            data_dirs_base = f'{ilab_dir}{local_share_dir}'

            self.add_copy_spec(f"{ilab_dir}{config_dir}")
            self.add_copy_spec([
                f"{data_dirs_base}/{data_dir}" for data_dir in data_dirs
            ])
            self.add_cmd_output(
                [f"ilab {sub}" for sub in subcmds]
            )
        self.add_cmd_output(f"ls -laR {ilab_dir}/{cache_dir}")

        if self.get_option("get-cache"):
            self.add_copy_spec(
                f'{ilab_dir}/{cache_dir}'
            )
# vim: set et ts=4 sw=4 :
