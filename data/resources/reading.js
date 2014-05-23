/*global $:false */
/*global MediaPlayerFactory:false */
/*jslint devel:true */
/*jslint browser:true */

function Reading(options) {
    "use strict";
    
    var self = this;
    self.hasChanged = false;
    self.modal = $('#popup');
    self.currentElement = null;
    self.options = options;
    self.mediaPlayer = new MediaPlayerFactory(window.lib.getMediaPlugin());

    self.getOptions = function () {
        return self.options;
    };

    self.setFocus = function (element) {
        if (element.any()) {
            element.focus();
        }
    };

    self._removeChanged = function () {
        $('#dSentence').removeClass('changed');
        $('#dBase').removeClass('changed');
        $('#dDefinition').removeClass('changed');
    };

    self.updateModal = function () {
        var text = window.lib.getCurrentWordAsText();

        self.setDMessage('');
        self._removeChanged();

        window.lib.find(text, self.getLanguageId(), self._findDone, self._findFail);
    };

    self._findDone = function (phrase, languageId, data, status, xhr) {
        if (data.state == "known" && data.sentence === "") {
            self.setDSentence(window.lib.getSentence());
        } else {
            self.setDSentence(data.sentence);
        }

        self.setDPhrase(data.phrase);
        self.setDState(data.state);
        self.setDBase(data.basePhrase);
        self.setDDefinition(data.definition);
        self.setFocus($('#dDefinition'));

        self.setHasChanged(false);
    };

    self._findFail = function (phrase, languageId, data, status, xhr) {
        if (data.status == 404) {
            self.setDPhrase(phrase);
            self.setDState('unknown');
            self.setDDefinition('');
            self.setDSentence(window.lib.getSentence());
            self.changed($('#dSentence'));

            self.setDMessage('New word, defaulting to unknown');

            if (window.lib.isCurrentFragment()) {
                self.setDBase(phrase);
                self.setFocus($('#dDefinition'));
            } else {
                self.setFocus($('#dBase'));
                self.setDBase('');
            }

            self.setHasChanged(false);
        } else {
            self.setDPhrase(phrase);
            self.setDMessage('Failed to lookup word');
        }
    };

    self.getDState = function () {
        return $('input[name="State"]:checked').val();
    };

    self.getDBase = function () {
        return $('#dBase').val();
    };

    self.getDSentence = function () {
        return $('#dSentence').val();
    };

    self.getDDefinition = function () {
        return $('#dDefinition').val();
    };

    self.getLanguageId = function () {
        return window.lib.getLanguageId();
    };

    self.getItemId = function () {
        return window.lib.getItemId();
    };

    self.setDState = function (state) {
        if (state) {
            state = state.toLowerCase();
            $('[name=State][value=' + state + ']').prop('checked', 'true');
            self.changed();
            $.event.trigger("dialogStateElementChanged");
        } else {
            alert('state value is unknown: ' + state);
        }
    };

    self.setHeaderText = function (val) {
        $('#dHeader').html(val);
    };

    self.setDPhrase = function (val) {
        $('#dPhrase').html(val);
    };

    self.setDBase = function (val) {
        $('#dBase').val(val);
        self.changed();
        $.event.trigger("dialogBaseElementChanged");
    };

    self.setDSentence = function (val) {
        $('#dSentence').val(val);
        self.changed();
        $.event.trigger("dialogSentenceElementChanged");
    };

    self.setDDefinition = function (val) {
        $('#dDefinition').val(val);
        self.changed();
        $.event.trigger("dialogDefinitionElementChanged");
    };

    self.setDMessage = function (val) {
        $('#dMessage').html(val);
        self.changed();
    };

    self.save = function (close) {
        var phrase = window.lib.getCurrentWordAsText();

        if (phrase === '') {
            return;
        }

        if (close === null) {
            close = false;
        }

        var state = self.getDState();

        window.lib.save({
                "phrase": phrase,
                "basePhrase": self.getDBase(),
                "sentence": self.getDSentence(),
                "definition": self.getDDefinition(),
                "languageId": self.getLanguageId(),
                "itemId": self.getItemId(),
                "state": state
            },
            window.lib.getCurrentElement(), {
                "close": close
            },
            self._saveDone,
            self._saveFail
        );
    };

    self._saveFail = function (obj, element, optional, data, status, xhr) {
        self.setDMessage('Save failed');
    };

    self._saveDone = function (obj, element, optional, data, status, xhr) {
        if (xhr.status == 200) {
            self.setDMessage('Term updated');
        } else if (xhr.status == 201) {
            self.setDMessage('New term saved');
        } else {
            self.setDMessage('Saved');
        }

        self._removeChanged();
        self.setHasChanged(false);

        if (optional.close) {
            self.closeModal();
        }
    };

    self.reset = function () {
        var element = window.lib.getCurrentElement();

        window.lib.reset(element, null, self._resetDone, self._resetFail);
    };

    self._resetDone = function (element, optional, data, status, xhr) {
        if (xhr.status == 200) {
            self.setDMessage('Term reset, use save to keep data.');
        } else {
            self.setDMessage('Term reset');
        }
    };

    self._resetFail = function (optional, data, status, xhr) {
        self.setDMessage('Reset failed');
    };

    self.changed = function (element) {
        if (element && element.any()) {
            element.addClass('changed');
            $.event.trigger("dialogDataElementChanged", [element]);
        }

        self.setHasChanged(true);
    };

    self.setHasChanged = function (value) {
        $.event.trigger("dialogDataHasChanged", [value]);
        self.hasChanged = value;
    };

    self.getHasChanged = function () {
        return self.hasChanged;
    };

    self.copy = function () {
        $.event.trigger("preDialogWordCopy");

        self.setDBase(window.lib.getCurrentWordAsText());
        self.changed($('#dBase'));
        $('#dBase').trigger('change');
        self.setFocus($('#dBase'));

        $.event.trigger("postDialogWordCopy");
    };

    self.refresh = function () {
        $.event.trigger("preDialogSentenceRefresh");

        self.setDSentence(window.lib.getSentence());
        self.changed($('#dSentence'));
        $('#dSentence').trigger('change');
        self.setFocus($('#dSentence'));

        $.event.trigger("postDialogSentenceRefresh");
    };

    self.displayModal = function () {
        var c = window.lib.getCurrentElement();
        
        if(c===null || typeof c==='undefined') {
            return;
        }
        
        c = c[0].getBoundingClientRect();

        var dh = $(window).height();
        var dw = $(window).width();

        var o = window.lib.getCurrentElement().offset();
        var nt, nl;

        var popupH = $('#popup').height();
        var popupW = $('#popup').width();

        if (c.top + 21 + popupH + 70 > dh) {
            nt = o.top - popupH - 5;
        } else {
            nt = o.top + 23;
        }

        if (o.left + popupW + 10 < dw) {
            nl = o.left;
        } else {
            nl = o.left - popupW + 70;
        }

        self.modal.css('display', 'inline-block');
        self.modal.offset({
            top: nt,
            left: nl
        });
    };

    self._clearInputs = function () {
        self.setDBase('');
        self.setDSentence('');
        self.setDDefinition('');
        self.setDState('unknown');
        self.setHasChanged(false);
    };

    self.isModalVisible = function () {
        return self.modal.is(':visible');
    };

    self.showModal = function (element) {
        if (self.isModalVisible() && self.hasChanged) {
            return;
        }

        self._clearInputs();
        window.lib.setCurrentElement(element);

        $.event.trigger("preShowModal");

        window.lib.setCurrentSelected(window.lib.getCurrentElement());
        self.updateModal();
        self.displayModal();

        $.event.trigger("postShowModal");
    };

    self.closeModal = function () {
        $.event.trigger("preCloseModal");

        self.hasChanged = false;
        self.modal.hide();

        if (window.lib.isCurrentFragment()) {
            var current = window.lib.getCurrentElement();

            if (!current.hasClass('__known') && !current.hasClass('__unknown') && !current.hasClass('__ignored')) {
                window.lib.deleteFragment(current);
            }
        }

        $.event.trigger("postCloseModal");
    };

    self.getMediaPlayer = function () {
        return self.mediaPlayer;
    };

    self._showOverlayModal = function (content) {
        self._setOverlayModalContent(content);
        $('#modalOverlay').show();
        $('#modalContent').show();
    };

    self._setOverlayModalContent = function (content) {
        $('#modalContent').html(content);
    };

    self._hideOverlayModal = function () {
        $('#modalOverlay').hide();
        $('#modalContent').hide();
    };

    self.markRemainingAsKnown = function () {
        if (self.isModalVisible()) {
            self.closeModal();
        }

        var termArray = [];
        var languageId = self.getLanguageId();
        var itemId = self.getItemId();

        $('.__notseen').each(function (index, x) {
            var word = $(x).data('lower');

            if (termArray.indexOf(word) > -1)
                return;

            termArray.push(word);
        });

        var data = JSON.stringify({
            "languageId": languageId,
            "itemId": itemId,
            "phrases": termArray
        });

        self._showOverlayModal('Please wait, sending <strong>' + termArray.length + '</strong> terms.<br/>This may take a few seconds.');
        $('body').css('cursor', 'wait');
        window.lib.markRemainingAsKnown(data, self._doneMarkRemainingAsKnown, self._failMarkRemainingAsKnown);
    };

    self._doneMarkRemainingAsKnown = function (data, status, xhr) {
        $('body').css('cursor', 'auto');
        self._setOverlayModalContent('Marked <strong>' + data + '</strong> words as known.<br/><button href="#" onclick="window.reading._hideOverlayModal()">OK</button>');
    };

    self._failMarkRemainingAsKnown = function (data, status, xhr) {
        $('body').css('cursor', 'auto');
        self._setOverlayModalContent('Operation failed.<br/><button href="#" onclick="window.reading._hideOverlayModal()">OK</button>');
    };
}