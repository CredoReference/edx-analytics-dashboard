/**
 * Initializes standard models with data from the page.
 *
 * Returns the model.
 */
define(['jquery', 'models/course-model', 'models/tracking-model', 'models/user-model', 'models/org-model'],
    function($, CourseModel, TrackingModel, UserModel, OrgModel) {
        'use strict';
        var courseModel = new CourseModel(),
            trackingModel = new TrackingModel(),
            userModel = new UserModel(),
            orgModel = new OrgModel();

        /* eslint-disable no-undef */
        // initModelData is set by the Django template at render time.
        courseModel.set(initModelData.course);
        trackingModel.set(initModelData.tracking);
        userModel.set(initModelData.user);
        orgModel.set(initModelData.org);
        /* eslint-enable no-undef */

        return {
            courseModel: courseModel,
            trackingModel: trackingModel,
            userModel: userModel,
            orgModel: orgModel
        };
    }
);
