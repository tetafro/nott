var Backbone = require('backbone');
var App = require('../app');
var Notepad = require('../models/Notepad');

module.exports = Backbone.Collection.extend({
    model: Notepad,
    url: '/ajax/notepads/',
    active: null,

    parse: function (response) {
        return response.notepads;
    },

    createOne: function (title, folderId) {
        var that = this;
        var notepad = new Notepad();

        notepad.save(
            {
                title: title,
                folder_id: folderId
            },
            {
                success: function (model, response) {
                    that.add(model);
                }
            }
        );

        return notepad;
    },

    editOne: function (notepad, title, folderId) {
        notepad.save({
            title: title,
            folder_id: folderId
        });
    },

    deleteOne: function (notepad) {
        notepad.destroy({wait: true});
    },

    setActive: function (activeNotepad) {
        var notepad;
        this.each(function (notepad) {
            notepad.set('active', false);
        });
        activeNotepad.set('active', true);
        this.active = activeNotepad;

        $('#search-form').hide();
    }
});
