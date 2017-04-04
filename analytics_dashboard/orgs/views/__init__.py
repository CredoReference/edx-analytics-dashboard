import logging
from datetime import datetime

from braces.views import LoginRequiredMixin
from ccx_keys.locator import CCXLocator
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.http import Http404
from django.views.generic import TemplateView
from django.utils import dateformat
from django.utils.translation import ugettext_lazy as _, ugettext_noop
from opaque_keys.edx.keys import CourseKey
from waffle import switch_is_active

from analyticsclient.exceptions import (ClientError, NotFoundError)

from core.utils import CourseStructureApiClient, translate_dict_values
from courses import permissions
from courses.views import CourseAPIMixin, CourseNavBarMixin, LazyEncoderMixin, TrackedViewMixin
from courses.utils import is_feature_enabled


logger = logging.getLogger(__name__)


class OrgContextMixin(CourseAPIMixin, TrackedViewMixin, LazyEncoderMixin):
    """
    Adds default org context data.

    Use primarily with templated views where data needs to be passed to Javascript.
    """
    # Title displayed on the page
    page_title = None
    page_subtitle = None

    def dispatch(self, request, *args, **kwargs):
        self.course_api_enabled = switch_is_active('enable_course_api')
        self.access_token = None

        if self.course_api_enabled and request.user.is_authenticated():
            self.access_token = settings.COURSE_API_KEY or request.user.access_token

        return super(OrgContextMixin, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(OrgContextMixin, self).get_context_data(**kwargs)
        context.update(self.get_default_data())

        user = self.request.user
        context['js_data'] = context.get('js_data', {})
        context['js_data'].update({
            'org': {
                'org_id': self.org_id
            },
            'user': {
                'username': user.get_username(),
                'name': user.get_full_name(),
                'email': user.email
            },
        })

        return context

    def get_default_data(self):
        """
        Returns default data for the pages (context and javascript data).
        """
        context = {
            'org_id': self.org_id,
            'org_name': self.org_id.replace('-', ' ').title(),
            'page_title': self.page_title,
            'page_subtitle': self.page_subtitle,
        }

        return context

    def get_org_courses(self):
        course_ids = permissions.get_user_course_permissions(self.request.user)

        # ccx courses are hidden on the course listing page unless enabled
        if not switch_is_active('enable_ccx_courses'):
            # filter ccx courses
            course_ids = [course_id for course_id in course_ids
                          if not isinstance(CourseKey.from_string(course_id), CCXLocator)]

        result = []
        if self.course_api_enabled:
            courses = self.get_courses()
            data = [course for course in courses if course['id'] in course_ids and
                    self.org_id.lower() == course['org'].lower()]
            for item in data:
                course_key = CourseKey.from_string(item['id'])
                item['course'] = course_key.course
                item['run'] = course_key.run
                result.append(item)
            return result
        else:
            for course_id in course_ids:
                course_key = CourseKey.from_string(course_id)
                if self.org_id.lower() == course_key.org.lower():
                    result.append({
                        "id": course_id,
                        "name": course_key.course + ' ' + course_key.run,
                        "category": "course",
                        "run": course_key.run,
                        "course": course_key.course,
                        "start": None,
                        "end": None
                    })
            return result


class OrgView(LoginRequiredMixin, TemplateView):
    """
    Base org view.
    """
    client = None
    org_id = None
    user = None
    update_message = None

    def get_last_updated_message(self, last_updated):
        if last_updated:
            return self.update_message % self.format_last_updated_date_and_time(last_updated)
        else:
            return None

    @staticmethod
    def format_last_updated_date_and_time(d):
        return {'update_date': dateformat.format(d, settings.DATE_FORMAT),
                'update_time': dateformat.format(d, settings.TIME_FORMAT)}

    def dispatch(self, request, *args, **kwargs):
        self.user = request.user
        self.org_id = kwargs.get('org_id', None)

        # some views will catch the NotFoundError to set data to a state that
        # the template can rendering a loading error message for the section
        try:
            return super(OrgView, self).dispatch(request, *args, **kwargs)
        except NotFoundError as e:
            logger.error('The requested data from the Analytics Data API was not found: %s', e)
            raise Http404
        except ClientError as e:
            logger.error('An error occurred while retrieving data from the Analytics Data API: %s', e)
            raise


class OrgsIndex(CourseAPIMixin, LazyEncoderMixin, LoginRequiredMixin, TrackedViewMixin, TemplateView):
    template_name = 'orgs/index.html'
    page_name = {
        'scope': 'insights',
        'lens': 'orgs_index',
        'report': '',
        'depth': ''
    }

    def get_context_data(self, **kwargs):
        context = super(OrgsIndex, self).get_context_data(**kwargs)

        courses = permissions.get_user_course_permissions(self.request.user)

        if not courses:
            # The user is probably not a course administrator and should not be using this application.
            raise PermissionDenied

        orgs_list = self._create_orgs_list(courses)
        context['orgs'] = orgs_list
        context['page_data'] = self.get_page_data(context)

        return context

    def _create_orgs_list(self, course_ids):
        info = {}

        # ccx courses are hidden on the course listing page unless enabled
        if not switch_is_active('enable_ccx_courses'):
            # filter ccx courses
            course_ids = [course_id for course_id in course_ids
                          if not isinstance(CourseKey.from_string(course_id), CCXLocator)]

        for course_id in course_ids:
            org_id = CourseKey.from_string(course_id).org
            if org_id not in info:
                info[org_id] = {'key': org_id, 'name': org_id.replace('-', ' ').title()}

        result = info.values()
        result.sort(key=lambda org: (org.get('name', '') or org.get('key', '') or '').lower())

        return result


class OrgNavBarMixin(CourseNavBarMixin):

    def get_primary_nav_items(self, request):
        """
        Return the primary nav items.
        """
        items = []

        if switch_is_active('enable_performance_learning_outcome'):
            items.append({
                'name': 'performance',
                'label': _('Performance'),
                'text': ugettext_noop('Performance'),
                'view': 'orgs:performance:org_learning_outcomes',
                'icon': 'fa-check-square-o',
                'switch': 'enable_course_api',
                'fragment': ''
            })

        # Remove disabled items
        items = [item for item in items if is_feature_enabled(item, request)]

        translate_dict_values(items, ('text',))

        # Clean each item
        map(self.clean_item, items)

        return items

    def clean_item(self, item):
        """
        Remove extraneous keys from item and set the href value.
        """
        # Prevent page reload if user clicks on the active navbar item, otherwise navigate to the new page.
        if item.get('active', False):
            href = '#'
        else:
            href = reverse(item['view'], kwargs={'org_id': self.org_id})

        item['href'] = href

        # Delete entries that are no longer needed
        item.pop('view', None)
        item.pop('switch', None)


class OrgHome(OrgNavBarMixin, OrgContextMixin, OrgView):
    template_name = 'orgs/home.html'
    page_title = _('Organization Home')
    page_name = {
        'scope': 'orgs',
        'lens': 'org_home',
        'report': '',
        'depth': ''
    }

    def get_table_items(self, request):
        items = []

        if self.course_api_enabled:
            subitems = []

            if switch_is_active('enable_performance_learning_outcome'):
                subitems.append({
                    'title': _('What is the breakdown for learning outcomes across courses?'),
                    'view': 'orgs:performance:org_learning_outcomes',
                    'breadcrumbs': [_('Learning Outcomes')],
                    'fragment': ''
                })

            items.append({
                'name': _('Performance'),
                'icon': 'fa-check-square-o',
                'heading': _('How are students doing on courses assignments?'),
                'items': subitems
            })

        return items

    def _parse_course_date(self, date_str):
        return datetime.strptime(date_str, CourseStructureApiClient.DATETIME_FORMAT) if date_str else None

    def _format_date(self, date):
        return dateformat.format(date, settings.DATE_FORMAT) if date else "--"

    # pylint: disable=redefined-variable-type
    def get_context_data(self, **kwargs):
        context = super(OrgHome, self).get_context_data(**kwargs)
        context.update({
            'table_items': self.get_table_items(self.request)
        })

        data = self.get_org_courses()

        for i, course in enumerate(data):
            start_date = self._parse_course_date(course.get('start'))
            end_date = self._parse_course_date(course.get('end'))
            todays_date = datetime.now()
            status_str = '--'

            if start_date:
                if todays_date >= start_date:
                    in_progress = (end_date is None or end_date > todays_date)
                    # Translators: 'In Progress' and 'Ended' refer to whether students are
                    # actively using the course or it is over.
                    status_str = _('In Progress') if in_progress else _('Ended')
                else:
                    # Translators: This refers to a course that has not yet begun.
                    status_str = _('Not Started Yet')

            course_key = CourseKey.from_string(data[i]['id'])

            data[i]['status'] = status_str
            data[i]['start_date'] = self._format_date(start_date)
            data[i]['end_date'] = self._format_date(end_date)
            data[i]['course'] = course_key.course
            data[i]['run'] = course_key.run

            course_url = reverse('courses:home', kwargs={'course_id': data[i]['id']})
            data[i]['course_link'] = '<a href="' + course_url + '">' + data[i]['name'] + '</a>'

        context['js_data']['org'].update({
            'courses': data,
            'hasData': bool(data),
            'contentTableHeading': "Courses List"
        })
        context['page_data'] = self.get_page_data(context)
        return context
