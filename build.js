/* eslint-disable no-unused-expressions */
({
    mainConfigFile: 'analytics_dashboard/static/js/config.js',
    baseUrl: 'analytics_dashboard/static',
    dir: 'analytics_dashboard/static/dist',
    removeCombined: true,
    findNestedDependencies: true,

    // Disable all optimization. django-compressor will handle that for us.
    optimizeCss: false,
    optimize: 'none',
    normalizeDirDefines: 'all',
    skipDirOptimize: true,

    preserveLicenseComments: true,
    modules: [
        {
            name: 'js/common'
        },
        {
            name: 'js/config'
        },
        {
            name: 'js/engagement-content-main',
            exclude: ['js/common']
        },
        {
            name: 'js/engagement-video-content-main',
            exclude: ['js/common']
        },
        {
            name: 'js/engagement-videos-main',
            exclude: ['js/common']
        },
        {
            name: 'js/engagement-video-timeline-main',
            exclude: ['js/common']
        },
        {
            name: 'js/enrollment-activity-main',
            exclude: ['js/common']
        },
        {
            name: 'js/enrollment-geography-main',
            exclude: ['js/common']
        },
        {
            name: 'js/enrollment-demographics-age-main',
            exclude: ['js/common']
        },
        {
            name: 'js/enrollment-demographics-education-main',
            exclude: ['js/common']
        },
        {
            name: 'js/enrollment-demographics-gender-main',
            exclude: ['js/common']
        },
        {
            name: 'js/performance-content-main',
            exclude: ['js/common']
        },
        {
            name: 'js/performance-problems-main',
            exclude: ['js/common']
        },
        {
            name: 'js/performance-answer-distribution-main',
            exclude: ['js/common']
        },
        {
            name: 'apps/learners/app/learners-main',
            exclude: ['js/common']
        },
        {
            name: 'js/performance-learning-outcomes-content-main',
            exclude: ['js/common']
        },
        {
            name: 'js/performance-learning-outcomes-section-main',
            exclude: ['js/common']
        },
        {
            name: 'js/orgs-home',
            exclude: ['js/common']
        },
        {
            name: 'js/orgs-performance-learning-outcomes-content-main',
            exclude: ['js/common']
        },
        {
            name: 'js/orgs-performance-learning-outcomes-section-main',
            exclude: ['js/common']
        },
        {
            name: 'apps/course-list/app/course-list-main',
            exclude: ['js/common']
        }
    ]
});
