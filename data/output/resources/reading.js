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
        var text = window.lib.getCurrentWordAsText();

        self.setDMessage('');
        self._removeChanged();

        window.lib.find(text, self.getLanguageId(), self._findDone, self._findFail);
    };
    
    self._findDone = function(phrase, languageId, data, status, xhr) {
    	if(data.state=="known" && data.sentence=="") {
    		self.setDSentence(window.lib.getSentence());
    	} else {
    		self.setDSentence(data.sentence);    		
    	}
    	
    	self.setDPhrase(data.phrase);
        self.setDState(data.state);
        self.setDBase(data.basePhrase);
        self.setDDefinition(data.definition);
        
        self.setHasChanged(false);
    };
    
    self._findFail = function(phrase, languageId, data, status, xhr) {
    	if (data.status == 404) {
            self.setDPhrase(phrase);
            self.setDState('unknown');
            self.setDBase('');
            self.setDDefinition('');
            self.setDSentence(window.lib.getSentence());
            self.changed($('#dSentence'));

            self.setDMessage('New word, defaulting to unknown');

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

    self.save = function (close) {
        var phrase = window.lib.getCurrentWordAsText();
        
        if(phrase=='') {
        	return;
        }
        
        if(close==null) {
        	close = false;
        }
        
        state = self.getDState();
        var previousClass = window.lib.getCurrentElement().attr('class');
        $('.__current').removeClass('__notseen __known __ignored __unknown __temp').addClass('__' + state.toLowerCase());
        
        window.lib.save( {
        			"phrase": phrase,
        			"basePhrase": self.getDBase(),
        			"sentence": self.getDSentence(),
        			"definition": self.getDDefinition(),
        			"languageId": self.getLanguageId(),
        			"itemId": self.getItemId(),
        			"state": state
        		}, {
            		"close": close,
            		"previousClass": previousClass
        		}, 
        		self._saveDone, 
        		self._saveFail
        		);
    };
    
    self._saveFail = function(obj, optional, data, status, xhr) {
    	window.lib.getCurrentElement().attr('class', optional.previousClass);
        self.setDMessage('Save failed');
    };
    
    self._saveDone = function(obj, optional, data, status, xhr) {
    	if (xhr.status == 200) {
            self.setDMessage('Term updated');
        } else if (xhr.status == 201) {
            self.setDMessage('New term saved');
        } else {
            self.setDMessage('Saved');
        }

        self._removeChanged();
        self.setHasChanged(false);

        var tempDef = data.basePhrase.length > 0 ? data.basePhrase + "<br/>" : '';
        if (data.definition.length > 0) tempDef += data.definition.replace(/\n/g, '<br />');
        
        if(window.lib.getIsFragment()) {
        	window.lib.updateFragmentState(data.phrase, data.state, tempDef);
        } else {
        	window.lib.updateElementState(data.phrase, data.state, tempDef);
        }
        
        if(optional.close) {
        	self.closeModal();
        }
    };

    self.reset = function () {
        var phrase = window.lib.getCurrentWordAsText();
        var languageId = self.getLanguageId();
        
        window.lib.reset(phrase, languageId, self._resetDone, self._resetFail);
    };
    
    self._resetDone = function(phrase, data, status, xhr) {
    	if (xhr.status == 200) {
            self.setDMessage('Term reset, use save to keep data.');
        } else {
            self.setDMessage('Term reset');
        }

        if(window.lib.getIsFragment()) {
        	var current = window.lib.getCurrentElement();
        	current.removeClass('__unknown __known __ignored');
        } else {
        	window.lib.updateElementState(phrase, 'notseen', '');
        }
    };
    
    self._resetFail = function(data, status,xhr) {
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
        var c = window.lib.getCurrentElement()[0].getBoundingClientRect();

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
        self.modal.offset({ top: nt, left: nl });
    };

    self._clearInputs = function () {
        self.setDBase('');
        self.setDSentence('');
        self.setDDefinition('');
        self.setDState('unknown');
        self.setHasChanged(false);
    };

    self.isModalVisible = function() {
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
        
        if(window.lib.getIsFragment()) {
        	var current = window.lib.getCurrentElement();
        	
        	$('.__known_t').removeClass('__known_t').addClass('__known');
        	$('.__unknown_t').removeClass('__unknown_t').addClass('__unknown');
        	$('.__ignored_t').removeClass('__ignored_t').addClass('__ignored');
        	$('.__notseen_t').removeClass('__notseen_t').addClass('__notseen');
        	
        	if(!current.hasClass('__known') && !current.hasClass('__unknown') && !current.hasClass('__ignored')) {
        		window.lib.deleteFragment(current);
        	}
        }

        $.event.trigger("postCloseModal");
    };

    self.getPlayer = function () {
    	if(window.lib.getMediaUri()=='') {
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
    	if(self.isModalVisible()) {
    		self.closeModal();
    	}
    	
        var termArray = Array();
        var languageId = self.getLanguageId();
        var itemId = self.getItemId();

        $('.__notseen').each(function (index, x) {
            var word = $(x).data('lower')

            if(termArray.indexOf(word) > -1)
            	return;
            
            termArray.push(word);
        });
        
        data = JSON.stringify({
        		"languageId": languageId,
        		"itemId": itemId,
        		"phrases": termArray
        });
        
        self._showOverlayModal('Please wait, sending <strong>' + termArray.length + '</strong> terms');
        window.lib.markRemainingAsKnown(data, self._doneMarkRemainingAsKnown, self._failMarkRemainingAsKnown);
    };
    
    self._doneMarkRemainingAsKnown = function(data, status, xhr) {
    	self._setOverlayModalContent('Marked <strong>' + data + '</strong> words as known.<br/><button href="#" onclick="window.reading._hideOverlayModal()">OK</button>');

        $('.__notseen').each(function (index, x) {
            $(x).removeClass('__notseen').addClass('__known');
        });
    };
    
    self._failMarkRemainingAsKnown = function(data, status, xhr) {
    	self._setOverlayModalContent('Operation failed.<br/><button href="#" onclick="window.reading._hideOverlayModal()">OK</button>');
    };

    if (window.lib.getItemType() == 'video' && self.hasPlayer()) {
    	lastL1 = -2;
    	lastL2 = -2;
    	
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