# Copyright (C) 2024 Red Hat Inc., Jose Castillo <jcastillo@redhat.com>

# This file is part of the sos project: https://github.com/sosreport/sos
#
# This copyrighted material is made available to anyone wishing to use,
# modify, copy, or redistribute it subject to the terms and conditions of
# version 2 of the GNU General Public License.
#
# See the LICENSE file in the source distribution for further information.

import json

from sos.collector.clusters import Cluster


class aap(Cluster):
    """
    This cluster profile is for Ansible Automation Platform clusters.

    By default, all nodes in the cluster will be returned for collection. This
    may not be desirable, so users are encouraged to use the `labels` option
    to specify a colon-delimited set of AAP node labels to restrict the list
    of nodes to.

    """

    cluster_name = 'Ansible Automation Platform Cluster'
    sos_plugins = [
        'aap_controller',
        'aap_eda',
        'aap_gateway',
        'aap_hub',
        'aap_receptor',
    ]
    sos_options = {'log-size': 50}
    packages = (
        'automation-controller-venv-tower',
        'automation-controller-server',
        'automation-controller-ui',
        'automation-eda-controller',
        'automation-eda-controller-server',
        'automation-gateway',
        'automation-gateway-config',
        'automation-hub',
        'receptor',
        'receptorctl',
        )
    option_list = [
        ('labels', '', 'Colon delimited list of labels to select nodes with')
    ]

    def get_nodes(self):
        self.nodes = []
        awx_out = self.exec_primary_cmd(
            'awx-manage list_instances',
            need_root=True
        )

        if not awx_out['status'] == 0:
            self.log_error(
                "Could not enumerate nodes via awx-manage: "
                f"{awx_out['output']}"
            )
            return self.nodes

        nodes = json.loads(awx_out['output'].splitlines()[-1])
        _labels = [lab for lab in self.get_option('labels').split(':') if lab]
        for node in nodes:
            if _labels and not any(_l in node['labels'] for _l in _labels):
                self.log_debug(f"{node} filtered from list due to labels")
                continue
            self.nodes.append(node['hostname'])

        return self.nodes

# vim: set et ts=4 sw=4 :
