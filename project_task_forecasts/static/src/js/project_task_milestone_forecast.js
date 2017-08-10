odoo.define('project_task_forecast.update_kanban', function (require) {
'use strict';

var core = require('web.core');
var data = require('web.data');
var Dialog = require('web.Dialog');
var Model = require('web.Model');
var session = require('web.session');

var KanbanView = require('web_kanban.KanbanView');
var KanbanRecord = require('web_kanban.Record');

var QWeb = core.qweb;
var _t = core._t;

    KanbanRecord.include({
        on_card_clicked: function () {
            if (this.model === 'project.backlog.cw' || this.model === 'project.backlog.sa' || this.model === 'project.backlog.sran') {
                var obj = $(this.$el).find('a').first().click();
            } else {
                this._super.apply(this, arguments);
            }
        },

    });
});
