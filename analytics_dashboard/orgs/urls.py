# pylint: disable=no-value-for-parameter
from django.conf.urls import url, include
from django.conf import settings

from courses.urls import PROBLEM_ID_PATTERN, PROBLEM_PART_ID_PATTERN, TAG_KEY_ID_PATTERN, TAG_VALUE_ID_PATTERN

from orgs import views
from orgs.views import performance

ORG_PERFORMANCE_URLS = ([
    url(r'^learning_outcomes/$',
        performance.OrgPerformanceLearningOutcomesContent.as_view(),
        name='org_learning_outcomes'),
    url(r'^learning_outcomes/(?P<courses_names>[\w;+-]+)/$',
        performance.OrgPerformanceLearningOutcomesContent.as_view(),
        name='org_learning_outcomes'),
    url(r'^learning_outcomes/(?P<courses_names>[\w;+-]+)/{}/{}/$'.format(TAG_KEY_ID_PATTERN, TAG_VALUE_ID_PATTERN),
        performance.OrgPerformanceLearningOutcomesSection.as_view(),
        name='org_learning_outcomes_section'),
    url(r'^learning_outcomes/(?P<courses_names>[\w;+-]+)/{}/{}/problems/{}/$'.format(TAG_KEY_ID_PATTERN,
                                                                                     TAG_VALUE_ID_PATTERN,
                                                                                     PROBLEM_ID_PATTERN),
        performance.OrgPerformanceLearningOutcomesAnswersDistribution.as_view(),
        name='org_learning_outcomes_answers_distribution'),
    url(r'^learning_outcomes/(?P<courses_names>[\w;+-]+)/{}/{}/problems/{}/{}/$'.format(TAG_KEY_ID_PATTERN,
                                                                                        TAG_VALUE_ID_PATTERN,
                                                                                        PROBLEM_ID_PATTERN,
                                                                                        PROBLEM_PART_ID_PATTERN),
        performance.OrgPerformanceLearningOutcomesAnswersDistribution.as_view(),
        name='org_learning_outcomes_answers_distribution_with_part'),
], 'performance')

ORG_URLS = [
    url(r'^performance/', include(ORG_PERFORMANCE_URLS)),
    url(r'^$', views.OrgHome.as_view(), name='org_home'),
]

app_name = 'orgs'
urlpatterns = [
    url('^$', views.OrgsIndex.as_view(), name='orgs_index'),
    url(r'^{}/'.format(settings.ORG_ID_PATTERN), include(ORG_URLS))
]
