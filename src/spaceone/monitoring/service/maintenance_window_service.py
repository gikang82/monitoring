import logging

from spaceone.core.service import *
from spaceone.monitoring.model.maintenance_window_model import MaintenanceWindow
from spaceone.monitoring.manager.identity_manager import IdentityManager
from spaceone.monitoring.manager.maintenance_window_manager import MaintenanceWindowManager

_LOGGER = logging.getLogger(__name__)


@authentication_handler
@authorization_handler
@mutation_handler
@event_handler
class MaintenanceWindowService(BaseService):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.maintenance_window_mgr: MaintenanceWindowManager = self.locator.get_manager('MaintenanceWindowManager')

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['title', 'projects', 'start_time', 'end_time', 'domain_id'])
    @change_timestamp_value(['start_time', 'end_time'], timestamp_format='iso8601')
    def create(self, params):
        """Create maintenance window

        Args:
            params (dict): {
                'title': 'str',
                'projects': 'list',
                'start_time': 'datetime',
                'end_time': 'datetime',
                'tags': 'dict',
                'domain_id': 'str'
            }

        Returns:
            maintenance_window_vo (object)
        """

        domain_id = params['domain_id']
        projects = params['projects']

        params['created_by'] = self.transaction.get_meta('user_id')

        identity_mgr: IdentityManager = self.locator.get_manager('IdentityManager')

        # Check projects and user permissions

        return self.maintenance_window_mgr.create_maintenance_window(params)

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['maintenance_window_id', 'domain_id'])
    @change_timestamp_value(['start_time', 'end_time'], timestamp_format='iso8601')
    def update(self, params):
        """Update maintenance window

        Args:
            params (dict): {
                'maintenance_window_id': 'str',
                'title': 'str',
                'projects': 'list',
                'start_time': 'datetime',
                'end_time': 'datetime',
                'tags': 'dict',
                'domain_id': 'str'
            }

        Returns:
            maintenance_window_vo (object)
        """

        maintenance_window_id = params['maintenance_window_id']
        domain_id = params['domain_id']
        projects = params.get('projects')

        maintenance_window_vo = self.maintenance_window_mgr.get_maintenance_window(maintenance_window_id, domain_id)

        if projects:
            identity_mgr: IdentityManager = self.locator.get_manager('IdentityManager')

            # Check projects and user permissions

        return self.maintenance_window_mgr.update_maintenance_window_by_vo(params, maintenance_window_vo)

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['maintenance_window_id', 'domain_id'])
    def close(self, params):
        """Delete maintenance window

        Args:
            params (dict): {
                'maintenance_window_id': 'str',
                'domain_id': 'str'
            }

        Returns:
            None
        """

        return self.maintenance_window_mgr.close_maintenance_window(params['maintenance_window_id'],
                                                                    params['domain_id'])

    @transaction(append_meta={'authorization.scope': 'PROJECT'})
    @check_required(['maintenance_window_id', 'domain_id'])
    def get(self, params):
        """ Get maintenance window

        Args:
            params (dict): {
                'maintenance_window_id': 'str',
                'domain_id': 'str',
                'only': 'list
            }

        Returns:
            maintenance_window_vo (object)
        """

        return self.maintenance_window_mgr.get_maintenance_window(params['maintenance_window_id'],
                                                                  params['domain_id'], params.get('only'))

    @transaction(append_meta={
        'authorization.scope': 'PROJECT',
        'mutation.append_parameter': {'user_projects': 'authorization.projects'}
    })
    @check_required(['domain_id'])
    @append_query_filter(['maintenance_window_id', 'title', 'state', 'project_id', 'created_by', 'domain_id',
                          'user_projects'])
    @append_keyword_filter(['maintenance_window_id', 'title'])
    def list(self, params):
        """ List maintenance windows

        Args:
            params (dict): {
                'maintenance_window_id': 'str',
                'title': 'str',
                'state': 'str',
                'project_id': 'str',
                'created_by': 'str',
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.Query)',
                'user_projects': 'list', // from meta
            }

        Returns:
            maintenance_window_vos (object)
            total_count
        """

        query = params.get('query', {})
        return self.maintenance_window_mgr.list_maintenance_windows(query)

    @transaction(append_meta={
        'authorization.scope': 'PROJECT',
        'mutation.append_parameter': {'user_projects': 'authorization.projects'}
    })
    @check_required(['query', 'domain_id'])
    @append_query_filter(['domain_id', 'user_projects'])
    @append_keyword_filter(['maintenance_window_id', 'title'])
    def stat(self, params):
        """
        Args:
            params (dict): {
                'domain_id': 'str',
                'query': 'dict (spaceone.api.core.v1.StatisticsQuery)',
                'user_projects': 'list', // from meta
            }

        Returns:
            values (list) : 'list of statistics data'

        """

        query = params.get('query', {})
        return self.maintenance_window_mgr.stat_maintenance_windows(query)
