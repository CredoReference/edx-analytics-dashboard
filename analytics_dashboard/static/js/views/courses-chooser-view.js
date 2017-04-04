define(['underscore', 'backbone'],
    function(_, Backbone) {
        'use strict';

        var CoursesChooserView = Backbone.View.extend({

            initialize: function(options) {
                var self = this;

                self.selector = options.selector;
                self.selectorDropdownBtn = options.selectorDropdownBtn;
                self.selectorSubmitBtn = options.selectorSubmitBtn;
                self.onSubmitFunc = options.onSubmitFunc;

                self.options = [];
                self.checkedAll = false;
                self.numCourses = self.selector.find('a').length - 1;
                self.numSelected = 0;
                self.selectorAllCheckbox = null;

                $(self.selector).find('a').each(function() {
                    if (parseInt($(this).attr('data-all'))) {
                        self.selectorAllCheckbox = this;
                    } else {
                        if($(this).find('input').is(':checked')) {
                            self.options.push($(this).attr('data-value'));
                            self.numSelected += 1;
                        }
                    }
                });

                if (self.numSelected == self.numCourses) {
                    self.checkAll(true);
                }

                self.selectorDropdownBtn.on('click', function(event) {
                    self.selector.toggle();
                });

                self.selectorSubmitBtn.on('click', function(event) {
                    self.submitBtnDisable();
                    if (self.onSubmitFunc) {
                        self.onSubmitFunc(event, self.options);
                    }
                });

                self.selector.find('a').on('click', function(event) {
                    self.onCourseClick(event);
                    return false;
                });
            },

            check: function(el, checked)
            {
                setTimeout(function() {
                    $(el).find('input').prop('checked', checked);
                }, 0);
            },

            checkAll: function(checked)
            {
                var self = this;

                self.checkedAll = checked;
                self.check(self.selectorAllCheckbox, checked);
            },

            submitBtnChange: function()
            {
                var self = this;

                if (self.numSelected > 0) {
                    $(self.selectorSubmitBtn).removeAttr('disabled');
                } else {
                    self.submitBtnDisable();
                }
            },

            submitBtnDisable: function()
            {
                $(self.selectorSubmitBtn).attr('disabled', 'disabled');
            },

            onCourseClick: function(event)
            {
                var self = this,
                    $target = $(event.currentTarget),
                    val = $target.attr('data-value'),
                    all = parseInt($target.attr('data-all')),
                    idx;

                if (all) {
                    self.numSelected = 0;
                    self.options = [];
                    self.checkedAll = !self.checkedAll;

                    if (self.checkedAll) {
                        self.numSelected = self.numCourses;
                    }

                    $(self.selector).find('a').each(function() {
                        if (self.checkedAll) {
                            if (!parseInt($(this).attr('data-all'))) {
                                self.options.push($(this).attr('data-value'));
                            }
                            self.check(this, true);
                        } else {
                            self.check(this, false);
                        }
                    });

                    self.check($target, self.checkedAll);
                } else {
                    if ((idx = self.options.indexOf(val)) > -1) {
                        self.options.splice(idx, 1);
                        self.numSelected -= 1;

                        self.check($target, false);
                        self.checkAll(false);
                    } else {
                        self.options.push(val);
                        self.numSelected += 1;

                        self.check($target, true);
                        if (self.numSelected == self.numCourses) {
                            self.checkAll(true);
                        }
                    }
                }

                self.submitBtnChange();
                $(event.target).blur();

                return false;
            }
        });

        return CoursesChooserView;
    }
);
