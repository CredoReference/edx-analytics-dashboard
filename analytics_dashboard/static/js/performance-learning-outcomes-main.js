require(['vendor/domReady!', 'load/init-page'], function (doc, page) {
    'use strict';

    require(['d3', 'underscore', 'views/data-table-view', 'views/stacked-bar-view', 'sample-learning-outcomes'],
        function (d3, _, DataTableView, StackedBarView, outcomes) {
            var model = page.models.courseModel,
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
                    {key: 'name', title: model.get('contentTableHeading'), type: 'hasNull'},
                    {key: 'num_modules', title: gettext('Problems'), type: 'number', className: 'text-right'}
                ];

            model.set({
                'primaryContent': outcomes.sections,
                'chartContent': outcomes.chart
            });

            tableColumns = tableColumns.concat(graphSubmissionColumns);

            tableColumns.push({
                key: 'average_submissions',
                title: gettext('Average Submissions Per Problem'),
                className: 'text-right',
                type: 'number',
                fractionDigits: 1,
                color: '#4BB4FB'
            });

            tableColumns.push({
                key: 'correct_percent',
                title: gettext('Percentage Correct'),
                className: 'text-right',
                type: 'percent'
            });

            if (model.get('hasData')) {
                new StackedBarView({
                    el: '#chart-view',
                    model: model,
                    modelAttribute: 'chartContent',
                    dataType: 'percent',
                    trends: graphSubmissionColumns
                });
            }

            new DataTableView({
                el: '[data-role=data-table]',
                model: model,
                modelAttribute: 'primaryContent',
                columns: tableColumns,
                sorting: ['index'],
                replaceZero: '-'
            });
        });

    define('sample-learning-outcomes', {
        'chart': [{
            'index': 1,
            'id': 'Critical Thinking',
            'name': 'Critical Thinking',
            'average_submissions': 0.0,
            'average_correct_submissions': 0.75,
            'average_incorrect_submissions': 0.25,
            'incorrect_submissions': 0,
            'incorrect_percent': 0.0,
            'correct_submissions': 0,
            'correct_percent': 0.0,
            'num_modules': 0
        }, {
            'index': 2,
            'id': 'Information Literacy',
            'name': 'Information Literacy',
            'average_submissions': 1.0,
            'average_correct_submissions': 0.52,
            'average_incorrect_submissions': 0.48,
            'incorrect_submissions': 0,
            'incorrect_percent': 0.0,
            'correct_submissions': 0,
            'correct_percent': 1.0,
            'num_modules': 3
        }],
        'sections': [{
            'index': 1,
            'id': 'Introduction',
            'name': 'Introduction',
            'average_submissions': 0.0,
            'average_correct_submissions': 0.0,
            'average_incorrect_submissions': 0.0,
            'incorrect_submissions': 0,
            'incorrect_percent': 0.0,
            'correct_submissions': 0,
            'correct_percent': 0.0,
            'num_modules': 0
        }, {
            'index': 2,
            'id': 'Example Week 1',
            'name': 'Example Week 1: Getting Started',
            'average_submissions': 1.0,
            'average_correct_submissions': 1.0,
            'average_incorrect_submissions': 0.0,
            'incorrect_submissions': 0,
            'incorrect_percent': 0.0,
            'correct_submissions': 0,
            'correct_percent': 1.0,
            'num_modules': 3
        }, {
            'index': 3,
            'id': 'Example Week 2',
            'name': 'Example Week 2: Get Interactive',
            'average_submissions': 0.0,
            'average_correct_submissions': 0.0,
            'average_incorrect_submissions': 0.0,
            'incorrect_submissions': 0,
            'incorrect_percent': 0.0,
            'correct_submissions': 0,
            'correct_percent': 0.0,
            'num_modules': 0
        },
        {
            'index': 4,
            'id': 'Example Week 3',
            'name': 'Example Week 3: Be Social',
            'average_submissions': 0.0,
            'average_correct_submissions': 0.0,
            'average_incorrect_submissions': 0.0,
            'incorrect_submissions': 0,
            'incorrect_percent': 0.0,
            'correct_submissions': 0,
            'correct_percent': 0.0,
            'num_modules': 0
        },
        {
            'index': 5,
            'id': 'About Exams and Certificates',
            'name': 'About Exams and Certificates',
            'average_submissions': 0.0,
            'average_correct_submissions': 0.0,
            'average_incorrect_submissions': 0.0,
            'incorrect_submissions': 0,
            'incorrect_percent': 0.0,
            'correct_submissions': 0,
            'correct_percent': 0.0,
            'num_modules': 0
        },
        {
            'index': 6,
            'id': 'Holding Section',
            'name': 'Holding Section',
            'average_submissions': 0.0,
            'average_correct_submissions': 0.0,
            'average_incorrect_submissions': 0.0,
            'incorrect_submissions': 0,
            'incorrect_percent': 0.0,
            'correct_submissions': 0,
            'correct_percent': 0.0,
            'num_modules': 0
        }]
    });
});
