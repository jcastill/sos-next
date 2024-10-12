# Copyright (C) 2024 Red Hat, Inc., Jose Castillo <jcastillo@redhat.com>

# This file is part of the sos project: https://github.com/sosreport/sos
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# version 2 of the GNU General Public License.
#
# See the LICENSE file in the source distribution for further information.

from sos.report.plugins import Plugin, IndependentPlugin, PluginOpt


class Instructlab(Plugin, IndependentPlugin):

    short_desc = 'Instructlab'
    plugin_name = 'instructlab'
    profiles = ('ai',)
    containers = ('instructlab', 'ilab',)
    commands = ('ilab',)

    option_list = [
        PluginOpt('ilab_user', default='', val_type=str,
                  desc='user that runs instructlab'),
        PluginOpt('ilab_conf_dir', default='', val_type=str,
                  desc='instructlab data directory'),
        PluginOpt('get-cache', default=False,
                  desc='Capture models and osci cached data')
    ]

    def setup(self):
        cont_share_conf_path = "/usr/share/instructlab/config"
        cont_opt_path = "/opt/app-root/src"
        # .cache dir contains the models and oci directories
        # which can be quite big. We'll gather this only if
        # specifying it via command line option
        cache_dir = "/.cache/instructlab"
        # .config is where the configuration yaml files can
        # be found. We gather this always.
        config_dir = "/.config/instructlab"
        # In the .local directory we can find datasets,
        # chat logs, taxonomies, and other very useful data
        # We gather this always.
        local_share_dir = "/.local/share/instructlab"

        # container paths
        cont_cache_path = f"{cont_opt_path}{cache_dir}"
        cont_config_path = f"{cont_opt_path}{config_dir}"
        cont_local_path = f"{cont_opt_path}{local_share_dir}"

        self.add_forbidden_path([
            f"{cont_local_path}/taxonomy/.git",
            f"{cont_local_path}/taxonomy/.github",
            f"{cont_opt_path}/src/.local/share/instructlab/taxonomy/.git",
            f"{cont_opt_path}/src/.local/share/instructlab/taxonomy/.github",
            ])

        subcmds = [
            'taxonomy diff',
            'taxonomy diff --taxonomy-base=empty',
            'system info',
            'model list',
            'config show',
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

        ilab_con = None
        for con in self.containers:
            if self.get_container_by_name(con):
                ilab_con = con
                break

        self.add_copy_spec(
            [f"{cont_share_conf_path}/rhel_ai_config.yaml",
             f"{cont_config_path}/config.yaml"],
            container=ilab_con)
        self.add_copy_spec(
            [f"{cont_local_path}/{data_dir}"
             for data_dir in data_dirs],
            container=ilab_con)
        self.add_cmd_output(
            [f"ilab {sub}" for sub in subcmds],
            container=ilab_con)
        self.add_dir_listing(cont_cache_path,
                             recursive=True,
                             container=ilab_con)
        if self.get_option('get-cache'):
            self.add_copy_spec(
                f"{cont_cache_path}",
                container=ilab_con)
        self.add_container_logs(list(self.containers))

        ilab_user = self.get_option("ilab_user")
        if ilab_user:
            ilab_dir = f"/home/{ilab_user}"
            if self.get_option("ilab_conf_dir"):
                ilab_dir = f"{ilab_dir}{self.get_option('ilab_conf_dir')}"
            data_dirs_base = f"{ilab_dir}{local_share_dir}"

            self.add_copy_spec(f"{ilab_dir}{config_dir}")
            self.add_copy_spec([
                f"{data_dirs_base}/{data_dir}" for data_dir in data_dirs
            ])
            self.add_dir_listing(f"{ilab_dir}/{cache_dir}",
                                 recursive=True)

            if self.get_option("get-cache"):
                self.add_copy_spec(
                    f'{ilab_dir}/{cache_dir}')

# vim: set et ts=4 sw=4 :
