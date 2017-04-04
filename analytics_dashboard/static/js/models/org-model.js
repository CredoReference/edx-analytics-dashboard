define(['backbone'], function(Backbone) {
    'use strict';

    /**
     * Stores our user logic and information.
     */
    var OrgModel = Backbone.Model.extend({
        defaults: {
            ignoreInReporting: false
        }
    });

    return OrgModel;
});
