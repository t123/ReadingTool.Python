function Reading(options) {
    var self = this;
    self.hasChanged = false;
    self.modal = $('#popup');
    self.currentElement = null;
    self.options = options;
    self.wasPlaying = false;
    self.jplayer = $('#jquery_jplayer_1');

    self.getOptions = function () {
        return self.options;
    };

    self._getWordFromSpan = function (element) {
        if (element[0].childNodes[0].nodeType == 3) {
            return element[0].childNodes[0].nodeValue;
        } else {
            return element[0].childNodes[0].innerText;
        }
    };

    self.setFocus = function (element) {
        if (element.any()) {
            element.focus();
        }
    };

    self.updateCurrentSelected = function (element) {
        if (element.any()) {
            var current = self.getCurrentSelected();
            current.removeClass('__current');
            element.addClass('__current');
        }

        $(document).trigger('postUpdateCurrentSelected');
    };

    self.getCurrentSelected = function () {
        return $('.__current');
    };

    self.getCurrentWordAsText = function () {
    	current = self.getCurrent();
        if (current!=null && current.any()) {
            return self._getWordFromSpan(self.currentElement);
        }

        return '';
    };

    self.getCurrent = function () {
        return self.currentElement;
    };

    self.getCurrentSentence = function () {
        if (!self.currentElement.any()) {
            return '';
        }

        var sentence = '';
        var children = self.currentElement.parent('p.__sentence').children('span');

        for (var i = 0; i < children.length; i++) {
            sentence += $(children[i]).text();
        }

        return sentence;
    };

    self._removeChanged = function () {
        $('#dSentence').removeClass('changed');
        $('#dBase').removeClass('changed');
        $('#dDefinition').removeClass('changed');
    };

    self.copyToClipboard = function (toCopy) {
        $(document).trigger('preCopyToClipboard');

        if(typeof rtjscript==='undefined') {
        	console.log("rtjscript undefined");
        	return;
        } 
        
        rtjscript.copyToClipboard(toCopy);

        $(document).trigger('postCopyToClipboard');
    };

    self.log = function (message) {
        var date = new Date();
        var d = date.getDate();
        var m = date.getMonth() + 1;
        var y = date.getFullYear();
        var h = date.getHours();
        var mn = date.getMinutes();
        var s = date.getSeconds();
        var f = date.getMilliseconds();

        console.log((d < 10 ? '0' + d : d) + '/' + (m < 10 ? '0' + m : m) + y + ' ' + (h < 10 ? '0' + h : h) + ':' + (mn < 10 ? '0' + mn : mn) + ':' + (s < 10 ? '0' + s : s) + '.' + f + ":-> " + message);
    };

    self.updateModal = function () {
        $(document).trigger('preUpdateModal');

        var text = self.getCurrentWordAsText();

        self.setDMessage('');
        self._removeChanged();

        $.ajax({
            url: self.options.url + '/internal/v1/term',
            type: 'GET',
            data: {
            	phrase: text,
            	languageId: self.options.languageId
            }
        }).done(function (data) {
            self.setDPhrase(data.phrase);
            self.setDState(data.state);
            self.setDBase(data.basePhrase);
            self.setDDefinition(data.definition);
            self.setDSentence(data.sentence);

            self.setHasChanged(false);
        }).fail(function (data, status, error) {
            if (data.status == 404) {
                self.setDPhrase(text);
                self.setDState('unknown');
                self.setDBase('');
                self.setDDefinition('');
                self.setDSentence(self.getCurrentSentence());
                self.changed($('#dSentence'));

                self.setDMessage('New word, defaulting to unknown');

                self.setHasChanged(false);
            } else {
                self.setDPhrase(text);
                self.setDMessage('Failed to lookup word');
            }

        }).always(function (data) {
            $(document).trigger('postUpdateModalFetched');
        });

        $(document).trigger('postUpdateModal');
    };

    self._selectText = function (element) {
        if (!element.any()) {
            return;
        }

        setTimeout(function () {
            var range = document.createRange();
            var selection = window.getSelection();
            selection.removeAllRanges();
            range.selectNodeContents($('#dPhrase')[0]);
            selection.addRange(range);
        }, 125);
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
        return self.options.languageId;
    };

    self.getItemId = function () {
        return self.options.itemId;
    };

    self.setDState = function (state) {
        if (state) {
            state = state.toLowerCase();
            $('[name=State][value=' + state + ']').prop('checked', 'true');
            self.changed();
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
    };

    self.setDSentence = function (val) {
        $('#dSentence').val(val);
        self.changed();
    };

    self.setDDefinition = function (val) {
        $('#dDefinition').val(val);
        self.changed();
    };

    self.setDMessage = function (val) {
        $('#dMessage').html(val);
        self.changed();
    };

    self.save = function () {
        $(document).trigger('preSave');

        var phrase = self.getCurrentWordAsText();
        
        if(phrase=='') {
        	return;
        }
        
        var state = self.getDState();

        $.ajax({
            url: self.options.url + "/internal/v1/term",
            type: 'POST',
            data: {
                phrase: phrase,
                basePhrase: self.getDBase(),
                sentence: self.getDSentence(),
                definition: self.getDDefinition(),
                languageId: self.getLanguageId(),
                itemId: self.getItemId(),
                state: state,
            }
        }).done(function (data, status, xhr) {
            if (xhr.status == 200) {
                self.setDMessage('Term updated');
            } else if (xhr.status == 201) {
                self.setDMessage('New term saved');
            } else {
                self.setDMessage('Saved');
            }

            self._removeChanged();
            self.setHasChanged(false);
            var lower = self.phraseToClass(phrase);
            $('.__' + lower).removeClass('__notseen __known __ignored __unknown __temp').addClass('__' + state.toLowerCase());

            var tempDef = self.getDBase().length > 0 ? self.getDBase() + "<br/>" : '';
            if (self.getDDefinition().length > 0) tempDef += self.getDDefinition().replace(/\n/g, '<br />');

            if (tempDef.length > 0) {
                $('.__' + lower).each(function (index) {
                    $(this).html(
                        (tempDef.length > 0 ? '<a rel="tooltip" title="' + tempDef + '">' : '') + phrase + (tempDef.length > 0 ? '</a>' : '')
                    );

                    var stateLower = state.toLowerCase();

                    if (stateLower == 'known') {
                        $(this).addClass("__kd");
                    } else if (stateLower == 'unknown') {
                        $(this).addClass("__ud");
                    } else if (stateLower == 'ignored') {
                        $(this).addClass("__id");
                    }
                });
            }
        }).fail(function (data) {
            self.setDMessage('Save failed');
        }).always(function (data) {
            $(document).trigger('postSave');
        });
    };

    self.phraseToClass = function (phrase) {
        return phrase.toLowerCase().replace("'", "_").replace('"', "_");
    };

    self.reset = function () {
        $(document).trigger('preReset');

        var phrase = self.getCurrentWordAsText();

        $.ajax({
            url: self.options.url + "/internal/v1/deleteterm",
            type: 'POST',
            data: {
                phrase: phrase,
                languageId: self.getLanguageId()
            }
        }).done(function (data, status, xhr) {
            if (xhr.status == 200) {
                self.setDMessage('Term reset, use save to keep data.');
            } else {
                self.setDMessage('Term reset');
            }

            var lower = self.phraseToClass(phrase);
            $('.__' + lower).removeClass('__notseen __known __ignored __unknown __kd __id __ud __temp').addClass('__notseen');
            $('.__' + lower).each(function (index) {
                $(this).html(phrase);
            });

        }).fail(function (data) {
            self.setDMessage('Reset failed');
        }).always(function (data) {
            $(document).trigger('postReset');
        });
    };

    self.changed = function (element) {
        if (element && element.any()) {
            element.addClass('changed');
        }

        self.setHasChanged(true);
    };

    self.setHasChanged = function (value) {
        self.hasChanged = value;
    };

    self.getHasChanged = function () {
        return self.hasChanged;
    };

    self.hasPlayer = function() {
    	if(self.jplayer==undefined || self.jplayer==null) {
    		return false;
    	}
    	
    	if(self.jplayer.data()==null || self.jplayer.data().jPlayer==undefined) {
    		return false;
    	}
    	
    	return true;
    };
    
    self.setWasPlaying = function () {
    	self.wasPlaying = false;
    	
    	if(self.hasPlayer() && !self.jplayer.data().jPlayer.status.paused) {
    		self.wasPlaying = true;
    	}
    };

    self.getWasPlaying = function () {
        return self.wasPlaying;
    };

    self.copy = function () {
        $(document).trigger('preWordCopy');

        self.setDBase(self.getCurrentWordAsText());
        self.changed($('#dBase'));
        $('#dBase').trigger('change');
        self.setFocus($('#dBase'));

        $(document).trigger('postWordCopy');
    };

    self.refresh = function () {
        $(document).trigger('preSentenceRefreshed');

        self.setDSentence(self.getCurrentSentence());
        self.changed($('#dSentence'));
        $('#dSentence').trigger('change');
        self.setFocus($('#dSentence'));

        $(document).trigger('postSentenceRefreshed');
    };

    self.getCommonness = function () {
        if (self.currentElement.hasClass('__high')) return ' high';
        if (self.currentElement.hasClass('__medium')) return ' medium';
        if (self.currentElement.hasClass('__low')) return ' low';

        return '';
    };

    self.getFrequency = function () {
        if (self.currentElement.any()) {
            return self.currentElement.data('frequency');
        }

        return 0;
    };

    self.getOccurrences = function () {
        if (self.currentElement.any()) {
            return self.currentElement.data('occurrences');
        }

        return 0;
    };

    self.displayModal = function () {
        var c = self.currentElement[0].getBoundingClientRect();

        var dh = $(window).height();
        var dw = $(window).width();

        var o = self.currentElement.offset();
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
        self.modal.offset({ top: nt, left: nl });
    };

    self._clearInputs = function () {
        self.setDBase('');
        self.setDSentence('');
        self.setDDefinition('');
        self.setDState('unknown');
        self.setHasChanged(false);
    };

    self.markTemp = function (element) {
        if (element.hasClass('__temp')) {
            $(element).removeClass('__temp');
        } else {
            $(element).addClass('__temp');
        }
    };

    self.showModal = function (element) {
        if (self.modal.is(':visible') && self.hasChanged) {
            return;
        }

        self._clearInputs();
        self.currentElement = element;

        $(document).trigger('preShowModal');

        self.updateCurrentSelected(self.getCurrent());
        self.updateModal();
        self.displayModal();

        $(document).trigger('postShowModal');
    };

    self.closeModal = function () {
        $(document).trigger('preCloseModal');

        self.hasChanged = false;
        self.modal.hide();

        $(document).trigger('postCloseModal');
    };

    self.getItemType = function () {
        return $('#reading').data('itemtype');
    };

    self.getPlayer = function () {
        if ($('#reading').data('mediauri') == '') {
            return null;
        }

        return self.jplayer;
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
        $(document).trigger('preMarkRemainingAsKnown');

        var termArray = Array();
        var languageId = self.getLanguageId();
        var itemId = self.getItemId();

        $('.__notseen').each(function (index, x) {
            var word = self._getWordFromSpan($(x));

            termArray.push({
                languageId: languageId,
                phrase: word,
                definition: '',
                basePhrase: '',
                sentence: '',
                itemId: itemId,
                state: 'Known'
            });
        });

        self._showOverlayModal('Please wait, sending <strong>' + termArray.length + '</strong> terms');

        $.ajax({
            url: self.options.url + "/internal/v1/markallknown",
            type: 'POST',
            dataType: 'json',
            headers: { "content-type": "application/json" },
            data: JSON.stringify(termArray)
        }).done(function (data, status, xhr) {
            self._setOverlayModalContent('Marked <strong>' + data + '</strong> words as known.<br/><button href="#" onclick="window.reading._hideOverlayModal()">OK</button>');

            $('.__notseen').each(function (index, x) {
                $(x).removeClass('__notseen').addClass('__known');
            });
        }).fail(function (data) {
            self._setOverlayModalContent('Operation failed.<br/><button href="#" onclick="window.reading._hideOverlayModal()">OK</button>');
        }).always(function (data) {
            $(document).trigger('postMarkRemainingAsKnown');
        });
    };

    if (self.getItemType() == 'video' && self.hasPlayer()) {
    	lastL1 = -2
    	lastL2 = -2
    	
        self.jplayer.bind($.jPlayer.event.timeupdate, function (event) {
            l1 = rtjscript.getSrtL1(event.jPlayer.status.currentTime);
            l2 = rtjscript.getSrtL2(event.jPlayer.status.currentTime);
            
            if(l1!=lastL1) {
            	if(l1==-1) {
            		$('#l1Main').html('');
            	} else {
            		$('#l1Main').html($('#l1_' + l1).html());
            	}
            	
            	lastL1 = l1;
            }
            
            if(l2!=lastL2) {
            	if(l2==-1) {
            		$('#l2Main').html('');
            	} else {
            		$('#l2Main').html($('#l2_' + l2).html());
            	}
            	
            	lastL2 = l2;
            }
        });
    }
}