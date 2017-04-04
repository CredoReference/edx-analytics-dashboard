require(['vendor/domReady!', 'load/init-page'], function(doc, page) {
    'use strict';

    require(['d3', 'underscore', 'views/data-table-view'],
        function(d3, _, DataTableView) {
            var model = page.models.orgModel,
                tableColumns = [
                    {key: 'course_link', title: gettext('Course'), type: 'hasNull'},
                    {key: 'course', title: gettext('Number'), type: 'hasNull'},
                    {key: 'run', title: gettext('Run'), type: 'hasNull'},
                    {key: 'start_date', title: 'Start Date', type: 'hasNull'},
                    {key: 'end_date', title: 'End Date', type: 'hasNull'},
                    {key: 'status', title: 'Status', type: 'hasNull'}
                ],
                orgTable;

            orgTable = new DataTableView({
                el: '[data-role=data-table]',
                model: model,
                modelAttribute: 'courses',
                columns: tableColumns,
                sorting: ['course_link'],
                replaceZero: '-',
                onClick: true
            });
            orgTable.renderIfDataAvailable();
        });
});

