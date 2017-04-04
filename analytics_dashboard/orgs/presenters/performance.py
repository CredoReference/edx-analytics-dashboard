from collections import OrderedDict
import logging
from slugify import slugify

from analyticsclient.exceptions import NotFoundError
from django.conf import settings
from django.core.cache import cache
from django.core.urlresolvers import reverse
from analyticsclient.client import Client
from core.utils import CourseStructureApiClient, sanitize_cache_key
from courses import utils
from courses.presenters import BasePresenter
from opaque_keys.edx.keys import CourseKey

logger = logging.getLogger(__name__)


class OrgTagsDistributionPresenter(BasePresenter):
    def __init__(self, access_token, org_id, course_ids=None, timeout=settings.ANALYTICS_API_DEFAULT_TIMEOUT):
        self.client = Client(base_url=settings.DATA_API_URL,
                             auth_token=settings.DATA_API_AUTH_TOKEN,
                             timeout=timeout)
        self.org_id = org_id
        self.course_ids = course_ids if course_ids else []
        self.course_api_client = CourseStructureApiClient(settings.COURSE_API_URL, access_token)

    _last_updated = None
    available_tags = None
    courses_names = ''

    def set_courses_names(self, courses_names):
        self.courses_names = courses_names

    def get_courses_names(self):
        return self.courses_names

    def get_cache_key(self, course_id=None):
        if course_id:
            return sanitize_cache_key(u'{}_{}_{}'.format(self.org_id, course_id, 'org_tags'))
        else:
            return sanitize_cache_key(u'{}_{}'.format(self.org_id, 'org_tags'))

    def _fetch_org_data(self):
        key = self.get_cache_key()
        courses_problems_tags = cache.get(key)

        if not courses_problems_tags:
            try:
                courses_problems_tags = self.client.orgs(self.org_id).problems_and_tags()
            except NotFoundError as e:
                logger.warning("There is no tags distribution info for %s: %s", self.org_id, e)
                return []
            cache.set(key, courses_problems_tags)

        return courses_problems_tags

    @property
    def last_updated(self):
        """ Returns when data was last updated according to the data api. """
        if not self._last_updated:
            self.get_available_tags()
        return self._last_updated

    def get_available_tags(self):
        """
        This function is used to return dict with all emitted unique tag values.
        The return dict format is:
        {
            'tag_name_1': set('tag_value_11', 'tag_value_12',  ... , 'tag_value_1n'),
            'tag_name_2': set('tag_value_21', 'tag_value_22',  ... , 'tag_value_2n'),
            ...
        }
        """
        if not self.available_tags:
            tags_distribution_data = self._fetch_org_data()
            self.available_tags = {}

            for item in tags_distribution_data:
                if item['course_id'] in self.course_ids:
                    for tag_key, tag_values in item['tags'].iteritems():
                        if tag_key not in self.available_tags:
                            self.available_tags[tag_key] = set()
                        for tag_value in tag_values:
                            self.available_tags[tag_key].add(tag_value)
                created = item.pop('created', None)
                if created:
                    created = self.parse_api_datetime(created)
                    self._last_updated = max(self._last_updated, created) if self._last_updated else created
        return self.available_tags

    def get_tags_content_nav(self, key_lst, selected_key=None, selected_value=None):
        """
        This function is used to create dropdown list with all available values
        for some particular tag. The first argument is the tag key.
        The second argument is the selected tag value.
        """
        result = []
        selected_item = None
        tags = self.get_available_tags()

        for key in key_lst:
            if key in tags:
                for item in tags[key]:
                    val = {
                        'id': item,
                        'name': self._tag_name(key, item),
                        'url': reverse('orgs:performance:org_learning_outcomes_section',
                                       kwargs={'org_id': self.org_id,
                                               'courses_names': self.get_courses_names(),
                                               'tag_key': slugify(key),
                                               'tag_value': slugify(item)})}
                    if selected_key == slugify(key) and selected_value == slugify(item):
                        selected_item = val
                    result.append(val)
        return result, selected_item

    def _get_structure(self, course_id):
        """ Retrieves course structure from the course API. """
        key = self.get_cache_key(course_id)
        structure = cache.get(key)
        if not structure:
            logger.debug('Retrieving structure for course: %s', course_id)
            blocks_kwargs = {
                'course_id': course_id,
                'depth': 'all',
                'all_blocks': 'true',
                'requested_fields': 'children,format,graded',
            }
            structure = self.course_api_client.blocks().get(**blocks_kwargs)
            cache.set(key, structure)

        return structure

    def _get_course_structure(self, course_id):
        def _update_node(updated_structure, origin_structure, node_id, parent_id=None):
            """
            Helper function to get proper course structure.
            Updates the dict that passed as the first argument (adds the parent to each node)
            """
            updated_structure[node_id] = origin_structure[node_id]
            updated_structure[node_id]['parent'] = parent_id if parent_id else None
            for child_id in origin_structure[node_id].get('children', []):
                _update_node(updated_structure, origin_structure, child_id, origin_structure[node_id]['id'])

        updated_structure = OrderedDict()
        origin_structure = self._get_structure(course_id)
        if origin_structure:
            _update_node(updated_structure, origin_structure["blocks"], origin_structure['root'])
        return updated_structure

    def _tag_name(self, key, value=None):
        k = key.replace('_', ' ').title()
        return ': '.join([k, value]) if value else k

    def get_tags_distribution(self, key_lst):
        tags_distribution_data = self._fetch_org_data()

        result = OrderedDict()
        index = 0

        for item in tags_distribution_data:
            for tag_key in key_lst:
                if tag_key in item['tags'] and item['course_id'] in self.course_ids:
                    tag_values = item['tags'][tag_key]
                    for tag_value in tag_values:
                        tag_name = self._tag_name(tag_key, tag_value)
                        if tag_name not in result:
                            index += 1
                            result[tag_name] = {
                                'id': tag_name,
                                'index': index,
                                'name': tag_name,
                                'tag_key': tag_key,
                                'tag_key_title': self._tag_name(tag_key),
                                'tag_value': tag_value,
                                'num_modules': 0,
                                'total_submissions': 0,
                                'correct_submissions': 0,
                                'incorrect_submissions': 0
                            }

                        incorrect_submissions = item['total_submissions'] - item['correct_submissions']
                        result[tag_name]['num_modules'] += 1
                        result[tag_name]['total_submissions'] += item['total_submissions']
                        result[tag_name]['correct_submissions'] += item['correct_submissions']
                        result[tag_name]['incorrect_submissions'] += incorrect_submissions

        for _, item in result.iteritems():
            item.update({
                'average_submissions': (item['total_submissions'] * 1.0) / item['num_modules'],
                'average_correct_submissions': (item['correct_submissions'] * 1.0) / item['num_modules'],
                'average_incorrect_submissions': (item['incorrect_submissions'] * 1.0) / item['num_modules'],
                'correct_percent': utils.math.calculate_percent(item['correct_submissions'],
                                                                item['total_submissions']),
                'incorrect_percent': utils.math.calculate_percent(item['incorrect_submissions'],
                                                                  item['total_submissions']),
                'url': reverse('orgs:performance:org_learning_outcomes_section',
                               kwargs={'org_id': self.org_id,
                                       'courses_names': self.get_courses_names(),
                                       'tag_key': slugify(item['tag_key']),
                                       'tag_value': slugify(item['tag_value'])})
            })
        return result.values()

    def get_modules_marked_with_tag(self, tag_key, tag_value):
        tags_distribution_data = self._fetch_org_data()
        available_tags = self.get_available_tags()
        intermediate = OrderedDict()

        courses = {}

        for item in tags_distribution_data:
            if item['course_id'] not in self.course_ids:
                continue

            item_tags = {}
            for k, v in item['tags'].iteritems():
                item_tags[slugify(k)] = v

            if tag_key in item_tags:
                for tag_val in item_tags[tag_key]:
                    if tag_value == slugify(tag_val):
                        course_name = CourseKey.from_string(item['course_id']).course
                        course_run = CourseKey.from_string(item['course_id']).run
                        incorrect_submissions = item['total_submissions'] - item['correct_submissions']
                        val = {
                            'id': item['module_id'],
                            'name': item['module_id'],
                            'course_id': item['course_id'],
                            'course_name': course_name,
                            'course_run': course_run,
                            'total_submissions': item['total_submissions'],
                            'correct_submissions': item['correct_submissions'],
                            'incorrect_submissions': incorrect_submissions,
                            'correct_percent': utils.math.calculate_percent(item['correct_submissions'],
                                                                            item['total_submissions']),
                            'incorrect_percent': utils.math.calculate_percent(incorrect_submissions,
                                                                              item['total_submissions']),
                            'url': reverse('orgs:performance:org_learning_outcomes_answers_distribution',
                                           kwargs={'org_id': self.org_id,
                                                   'courses_names': self.get_courses_names(),
                                                   'tag_key': tag_key,
                                                   'tag_value': tag_value,
                                                   'problem_id': item['module_id']})
                        }
                        if available_tags:
                            for av_tag_key in available_tags:
                                if av_tag_key in item['tags']:
                                    val[av_tag_key] = item['tags'][av_tag_key]
                                else:
                                    val[av_tag_key] = None
                        intermediate[item['module_id']] = val

                        if item['course_id'] not in courses:
                            courses[item['course_id']] = {
                                'name': course_name,
                                'run': course_run,
                                'structure': self._get_course_structure(item['course_id'])
                            }

        result = []
        index = 0

        for course_id, course_data in courses.iteritems():
            course_name = course_data['name']
            course_run = course_data['run']
            course_structure = course_data['structure']

            for key, val in course_structure.iteritems():
                if key in intermediate:
                    first_parent = course_structure[val['parent']]
                    second_parent = course_structure[first_parent['parent']]

                    index += 1
                    intermediate[key]['index'] = index
                    intermediate[key]['name'] = course_name + u' ' + course_run + u': ' + u', '.join([
                        second_parent['display_name'], first_parent['display_name'], val['display_name']])
                    result.append(intermediate[key])

        return result
