require(['vendor/domReady!', 'load/init-page'], function(doc, page) {
    'use strict';

    require(['d3', 'underscore', 'views/courses-chooser-view', 'views/data-table-view', 'views/stacked-bar-view'],
        function(d3, _, CoursesChooserView, DataTableView, StackedBarView) {
            var model = page.models.orgModel,
                graphSubmissionColumns = [
                    {
                        key: 'average_correct_submissions',
                        percent_key: 'correct_percent',
                        title: gettext('Average Correct'),
                        className: 'text-right',
                        type: 'number',
                        fractionDigits: 1,
                        color: '#4BB4FB'
                    },
                    {
                        key: 'average_incorrect_submissions',
                        percent_key: 'incorrect_percent',
                        title: gettext('Average Incorrect'),
                        className: 'text-right',
                        type: 'number',
                        fractionDigits: 1,
                        color: '#CA0061'
                    }
                ],
                tableColumns = [
                    {key: 'index', title: gettext('Order'), type: 'number', className: 'text-right'},
                    {key: 'tag_value', title: model.get('contentTableHeading'), type: 'hasNull'},
                    {key: 'tag_key_title', title: 'Outcome Type', type: 'hasNull'}
                ],
                performanceLoContentChart,
                performanceLoContentTable,
                org = model.get('org_id');

            new CoursesChooserView({
                'selector': $('.org-courses-selector'),
                'selectorDropdownBtn': $('.org-courses-selector-btn'),
                'selectorSubmitBtn': $('.generate-report'),
                'onSubmitFunc': function(event, options) {
                    window.location.href = '/orgs/' + org + '/performance/learning_outcomes/' + options.join(';') + '/';
                }
            });

            tableColumns = tableColumns.concat(graphSubmissionColumns);

            tableColumns.push({
                key: 'average_submissions',
                title: gettext('Average Submissions per Problem'),
                className: 'text-right',
                type: 'number',
                fractionDigits: 1
            });

            tableColumns.push({
                key: 'correct_percent',
                title: gettext('Percentage Correct'),
                className: 'text-right',
                type: 'percent'
            });

            if (model.get('hasData')) {
                performanceLoContentChart = new StackedBarView({
                    el: '#chart-view',
                    model: model,
                    modelAttribute: 'tagsDistribution',
                    trends: graphSubmissionColumns
                });
                performanceLoContentChart.renderIfDataAvailable();
            }

            performanceLoContentTable = new DataTableView({
                el: '[data-role=data-table]',
                model: model,
                modelAttribute: 'tagsDistribution',
                columns: tableColumns,
                sorting: ['index'],
                replaceZero: '-'
            });
            performanceLoContentTable.renderIfDataAvailable();
        });
});

