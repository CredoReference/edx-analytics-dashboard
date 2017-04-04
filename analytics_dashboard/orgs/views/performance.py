import copy

from django.conf import settings
from django.utils.translation import ugettext_lazy as _, ugettext_noop
from waffle import switch_is_active

from courses import permissions
from core.utils import translate_dict_values
from courses.presenters.performance import CoursePerformancePresenter
from orgs.presenters.performance import OrgTagsDistributionPresenter

from opaque_keys.edx.keys import CourseKey, UsageKey
from orgs.views import OrgContextMixin, OrgNavBarMixin, OrgView


class OrgPerformanceTemplateView(OrgNavBarMixin, OrgContextMixin, OrgView):
    """
    Base view for course performance pages.
    """
    presenter = None
    problem_id = None
    part_id = None
    no_data_message = None

    # Translators: Do not translate UTC.
    update_message = _('Problem submission data was last updated %(update_date)s at %(update_time)s UTC.')

    secondary_nav_items_base = []
    secondary_nav_items = None

    active_primary_nav_item = 'performance'

    def get_context_data(self, **kwargs):
        self.secondary_nav_items = copy.deepcopy(self.secondary_nav_items_base)
        if switch_is_active('enable_performance_learning_outcome'):
            if not any(d['name'] == 'learning_outcomes' for d in self.secondary_nav_items):
                self.secondary_nav_items.append({
                    'name': 'learning_outcomes',
                    'text': ugettext_noop('Learning Outcomes'),
                    'label': _('Learning Outcomes'),
                    'view': 'orgs:performance:org_learning_outcomes',
                    'scope': 'org',
                    'lens': 'performance',
                    'report': 'outcomes',
                    'depth': ''
                })
                translate_dict_values(self.secondary_nav_items, ('text',))

        context_data = super(OrgPerformanceTemplateView, self).get_context_data(**kwargs)
        context_data['no_data_message'] = self.no_data_message

        return context_data


class OrgPerformanceLearningOutcomesMixin(OrgPerformanceTemplateView):
    active_secondary_nav_item = 'learning_outcomes'
    tags_presenter = None
    selected_tag_key = None
    selected_tag_value = None
    update_message = _('Tags distribution data was last updated %(update_date)s at %(update_time)s UTC.')
    no_data_message = _('No submissions received for these exercises.')
    tags_nav_lst = ['learning_outcome', 'learning_outcome_custom']
    chosen_courses = []

    def get_context_data(self, **kwargs):
        context = super(OrgPerformanceLearningOutcomesMixin, self).get_context_data(**kwargs)

        self.selected_tag_key = kwargs.get('tag_key', None)
        self.selected_tag_value = kwargs.get('tag_value', None)
        self.chosen_courses = []

        courses_names = kwargs.get('courses_names', '')
        if courses_names:
            courses_names_lst = courses_names.split(';')
            course_ids = permissions.get_user_course_permissions(self.request.user)

            for course_id in course_ids:
                course_key = CourseKey.from_string(course_id)
                if course_key.org == self.org_id:
                    course_match = course_key.course + '+' + course_key.run
                    if course_match in courses_names_lst:
                        self.chosen_courses.append(course_id)

        self.tags_presenter = OrgTagsDistributionPresenter(self.access_token, self.org_id, self.chosen_courses)

        if courses_names:
            self.tags_presenter.set_courses_names(courses_names)

            first_level_content_nav, first_selected_item = self.tags_presenter.get_tags_content_nav(
                self.tags_nav_lst, self.selected_tag_key, self.selected_tag_value)

            context['selected_tag_key'] = self.selected_tag_key
            context['selected_tag_value'] = self.selected_tag_value
            context['js_data'].update({
                'first_level_content_nav': first_level_content_nav,
                'first_level_selected': first_selected_item
            })

        context['update_message'] = self.get_last_updated_message(self.tags_presenter.last_updated)
        context['chosen_courses'] = self.chosen_courses
        context['courses_names'] = courses_names
        context['org_courses'] = self.get_org_courses()

        return context


class OrgPerformanceLearningOutcomesContent(OrgPerformanceLearningOutcomesMixin):
    template_name = 'orgs/performance_learning_outcomes_content.html'
    page_title = _('Performance: Learning Outcomes')
    page_name = {
        'scope': 'orgs',
        'lens': 'performance',
        'report': 'outcomes',
        'depth': ''
    }

    def get_context_data(self, **kwargs):
        context = super(OrgPerformanceLearningOutcomesContent, self).get_context_data(**kwargs)

        if kwargs.get('courses_names', ''):
            tags_distribution = self.tags_presenter.get_tags_distribution(self.tags_nav_lst)

            org_tags_data = {'tagsDistribution': tags_distribution,
                             'hasData': bool(tags_distribution),
                             'org_id': self.org_id,
                             'contentTableHeading': "Outcome Name"}

            context['js_data']['org'].update(org_tags_data)

        context.update({
            'page_data': self.get_page_data(context)
        })

        return context


class OrgPerformanceLearningOutcomesSection(OrgPerformanceLearningOutcomesMixin):
    template_name = 'orgs/performance_learning_outcomes_section.html'
    page_title = _('Performance: Learning Outcomes')
    has_part_id_param = False
    page_name = {
        'scope': 'orgs',
        'lens': 'performance',
        'report': 'outcomes',
        'depth': 'section'
    }

    def get_context_data(self, **kwargs):
        context = super(OrgPerformanceLearningOutcomesSection, self).get_context_data(**kwargs)

        modules_marked_with_tag = self.tags_presenter.get_modules_marked_with_tag(self.selected_tag_key,
                                                                                  self.selected_tag_value)
        course_data = {'tagsDistribution': modules_marked_with_tag,
                       'hasData': bool(modules_marked_with_tag),
                       'org_id': self.org_id,
                       'contentTableHeading': "Problem Name"}

        context['js_data'].update({
            'org': course_data,
            'second_level_content_nav': modules_marked_with_tag
        })

        context.update({
            'page_data': self.get_page_data(context),
        })

        return context


class OrgPerformanceLearningOutcomesAnswersDistribution(OrgPerformanceLearningOutcomesSection):
    template_name = 'orgs/performance_learning_outcomes_answer_distribution.html'
    page_title = _('Performance: Problem Submissions')
    has_part_id_param = True
    page_name = {
        'scope': 'orgs',
        'lens': 'performance',
        'report': 'outcomes',
        'depth': 'problem'
    }

    def get_context_data(self, **kwargs):
        context = super(OrgPerformanceLearningOutcomesAnswersDistribution, self).get_context_data(**kwargs)

        self.problem_id = kwargs.get('problem_id', None)
        self.part_id = kwargs.get('problem_part_id', None)

        usage_key = UsageKey.from_string(self.problem_id)

        course_id = str(usage_key.course_key)

        context['course_key'] = course_id
        context['course_id'] = course_id

        presenter = CoursePerformancePresenter(self.access_token, course_id)

        if self.has_part_id_param and self.part_id is None and self.problem_id:
            assignments = presenter.course_module_data()
            if self.problem_id in assignments and len(assignments[self.problem_id]['part_ids']) > 0:
                self.part_id = assignments[self.problem_id]['part_ids'][0]

        answer_distribution_entry = presenter.get_answer_distribution(self.problem_id, self.part_id)

        if 'course' not in context['js_data']:
            context['js_data']['course'] = {}

        context['js_data']['course'].update({
            'answerDistribution': answer_distribution_entry.answer_distribution,
            'answerDistributionLimited': answer_distribution_entry.answer_distribution_limited,
            'isRandom': answer_distribution_entry.is_random,
            'answerType': answer_distribution_entry.answer_type
        })

        context.update({
            'problem': presenter.block(self.problem_id),
            'questions': answer_distribution_entry.questions,
            'active_question': answer_distribution_entry.active_question,
            'problem_id': self.problem_id,
            'problem_part_id': self.part_id,
            'problem_part_description': answer_distribution_entry.problem_part_description,
            'view_live_url': presenter.build_view_live_url(settings.LMS_COURSE_SHORTCUT_BASE_URL, self.problem_id),
        })

        second_level_selected_item = None
        for nav_item in context['js_data']['second_level_content_nav']:
            if nav_item['id'] == self.problem_id:
                second_level_selected_item = nav_item
                break

        context['js_data'].update({
            'second_level_selected': second_level_selected_item
        })

        context.update({
            'page_data': self.get_page_data(context)
        })

        return context
