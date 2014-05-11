function Lib(options) {
	var self = this;
	self.options = options;
	self.currentElement = null;
	
	self.getOptions = function () {
        return self.options;
    };
    
    //MANIPULATION OF CURRENT ELEMENT
    
    /**
     * Returns the current element
     * @method getCurrentElement
     * @return {element}
     */
    self.getCurrentElement = function() {
    	return self.currentElement;
    }
    
    /**
     * Sets the current element
     * @method setCurrentElement
     * @param {element} current element
    */
    self.setCurrentElement = function(element) {
    	$.event.trigger("preSetCurrentElement", [element]);
    	self.currentElement = element;
    	$.event.trigger("postSetCurrentElement", [element]);
    };
    
    /**
     * Gets the element marked with __current
     * @method getCurrentSelected
     * @return {element}
    */
    self.getCurrentSelected = function () {
        return $('.__current');
    };
    
    /**
     * Sets __current on given element
     * @method setCurrentSelected
     * @param {element} element to add __current to
    */
    self.setCurrentSelected = function (element) {
        if (element.any()) {
        	$.event.trigger("preSetCurrentSelected", [element]);
            var current = self.getCurrentSelected();
            current.removeClass('__current');
            element.addClass('__current');
            $.event.trigger("postSetCurrentSelected", [element]);
        }
    };
    
    /**
     * Gets the text from the currently selected element 
     * @method getCurrentElementAsText
     * @return {element}
    */
    self.getCurrentWordAsText = function () {
    	current = self.getCurrentElement();
        
    	if (current!=null && current.any()) {
    		if (current[0].childNodes[0].nodeType == 3) {
                return current[0].childNodes[0].nodeValue;
            } else {
                return current[0].childNodes[0].innerText;
            }
        }

        return '';
    };
    
    /**
     * Gets the current sentence of the currently selected element 
     * @method getSentence
     * @return {sentence}
    */
    self.getSentence = function () {
        if (!self.getCurrentElement().any()) {
            return '';
        }

        var sentence = '';
        var children = self.getCurrentElement().parent('p.__sentence').children('span');

        for (var i = 0; i < children.length; i++) {
            sentence += $(children[i]).text();
        }

        return sentence;
    };
    
    //AJAX calls
    self.find = function(phrase, languageId, doneCallback, failCallback) {
    	$.event.trigger("preFetchPhrase", [phrase, languageId]);
    	
    	$.ajax({
            url: self.getWebAPI() + '/internal/v1/term',
            type: 'GET',
            data: {
            	phrase: phrase,
            	languageId: languageId
            }
        }).done(function (data, status, xhr) {
        	$.event.trigger("preFetchPhraseDone", [phrase, languageId, data]);
        	
        	if(doneCallback!=null) {
        		doneCallback(phrase, languageId, data, status, xhr);
        	}
        	
        	$.event.trigger("postFetchPhraseDone", [phrase, languageId, data]);
        }).fail(function (data, status, xhr) {
        	$.event.trigger("preFetchPhraseFail", [phrase, languageId, data]);
        	
        	if(failCallback!=null) {
        		failCallback(phrase, languageId, data, status, xhr);
        	}
        	
        	$.event.trigger("postFetchPhraseFail", [phrase, languageId, data]);
        }).always(function (data, status, xhr) {
        	$.event.trigger("postFetchPhrase", [phrase, languageId, data, status, xhr]);
        });
    };
    
    self.save = function(
    		obj,
    		previousClass,
    		doneCallback,
    		failCallback
    		) {
    	$.event.trigger("preSaveTerm", [obj, previousClass]);
    	
        $.ajax({
            url: self.getWebAPI() + "/internal/v1/term",
            type: 'POST',
            data: {
                phrase: obj.phrase,
                basePhrase: obj.basePhrase,
                sentence: obj.sentence,
                definition: obj.definition,
                languageId: obj.languageId,
                itemId: obj.itemId,
                state: obj.state
            }
        }).done(function (data, status, xhr) {
        	$.event.trigger("preSaveTermDone", [obj, previousClass, data]);
        	
            if(doneCallback!=null) {
            	doneCallback(obj, data, status, xhr);
            }
            
            $.event.trigger("postSaveTermDone", [obj, previousClass, data]);
        }).fail(function (data, status, xhr) {
        	$.event.trigger("preSaveTermFail", [obj, previousClass, data]);
        	
        	if(failCallback!=null) {
        		failCallback(obj, previousClass, data, status, xhr);
            }
        	
        	$.event.trigger("postSaveTermFail", [obj, previousClass, data]);
        }).always(function (data, status, xhr) {
        	$.event.trigger("postSaveTerm");
        });
    };
    
    self.reset = function(phrase, languageId, doneCallback, failCallback) {
    	$.event.trigger("preResetTerm", [phrase, languageId]);
    	
    	$.ajax({
            url: self.getWebAPI() + "/internal/v1/deleteterm",
            type: 'POST',
            data: {
                phrase: phrase,
                languageId: languageId 
            }
        }).done(function (data, status, xhr) {
        	$.event.trigger("preResetTermDone", [phrase, languageId, data]);
        	
        	if(doneCallback!=null) {
            	doneCallback(phrase, data, status, xhr);
            }
        	
        	$.event.trigger("postResetTermDone", [phrase, languageId, data]);
        }).fail(function (data, status, xhr) {
        	if(failCallback!=null) {
        		$.event.trigger("preResetTermFail", [phrase, languageId, data]);
        		
        		failCallback(data, status, xhr);
        		
        		$.event.trigger("postResetTermDone", [phrase, languageId, data]);
            }
        }).always(function (data) {
        	$.event.trigger("postReset", [phrase, languageId, data]);
        });
    };
    
    self.markRemainingAsKnown = function(data, doneCallback, failCallback) {
    	$.event.trigger("preMarkRemainingAsKnown");
    	
    	$.ajax({
            url: self.getWebAPI() + "/internal/v1/markallknown",
            type: 'POST',
            dataType: 'text',
            contentType: "application/json",
            data: data
        }).done(function (data, status, xhr) {
        	if(doneCallback!=null) {
        		doneCallback(data, status, xhr);
        	}
        }).fail(function (data, status, xhr) {
        	if(failCallback!=null) {
        		failCallback(data, status, xhr);
        	}
        }).always(function (data, status, xhr) {
        	$.event.trigger("postMarkRemainingAsKnown");            
        });
    };

    //COMMON DATA
    self._getItemData = function(name) {
    	return $('#reading').data(name);
    };
    
    self.getItemType = function () {
        return self._getItemData('itemtype');
    };
    
    self.getLanguageId = function () {
    	return self._getItemData('languageid');
    };
    
    self.getItemId = function () {
    	return self._getItemData('itemid');
    };
    
    self.getWebAPI = function() { 
    	return self._getItemData('webapi');    	
    };
    
    self.getMediaUri = function() {
    	return self._getItemData('mediauri');    	
    };
    
    self.getL1Code = function() {
    	return self._getItemData('l1code');    	
    };
    
    self.getL2Code = function() {
    	return self._getItemData('l2code');    	
    };
    
    self.getCollectionName = function() {
    	return self._getItemData('collectionname');
    };
    
    self.getCollectionNo = function() {
    	return self._getItemData('collectionno');
    };
    
    self.getDateCreated = function() {
    	return self._getItemData('datecreated');
    };
    
    self.getDateModified = function() {
    	return self._getItemData('datemodified');
    };
    
    self.getLastRead = function() {
    	return self._getItemData('lastread');
    };
    
    self.getL1Title = function() {
    	return self._getItemData('l1title');
    };
    
    self.getL2Title = function() {
    	return self._getItemData('l2title');
    };
    
    self.getLanguage1Id= function() {
    	return self._getItemData('l1id');
    };
    
    self.getLanguage2Id= function() {
    	return self._getItemData('l2id');
    };
    
    self.getL1Direction = function() {
    	return self._getItemData('l1Direction');
    };
    
    self.getL2Direction = function() {
    	return self._getItemData('l2Direction');
    };
    
    self.getCommonness = function () {
    	ce = self.getCurrentElement();
    	
    	if(!ce.any()) {
    		return ''
    	}
    	
        if (ce.hasClass('__high')) return ' high';
        if (ce.hasClass('__medium')) return ' medium';
        if (ce.hasClass('__low')) return ' low';

        return '';
    };

    self.getFrequency = function () {
    	ce = self.getCurrentElement();
        if (ce.any()) {
            return ce.data('frequency');
        }

        return 0;
    };

    self.getOccurrences = function () {
    	ce = self.getCurrentElement();
    	
        if (ce.any()) {
            return ce.data('occurrences');
        }

        return 0;
    };
    
    self.getLowerPhrase = function () {
    	ce = self.getCurrentElement();
    	
        if (ce.any()) {
            return ce.data('lower');
        }

        return 0;
    };
    
    //FUNCTIONS
    self.copyToClipboard = function (toCopy) {
    	$.event.trigger("preCopyToClipboard");

        if(typeof rtjscript==='undefined') {
        	console.log("rtjscript undefined");
        	return;
        } 
        
        rtjscript.copyToClipboard(toCopy);

        $.event.trigger("postCopyToClipboard", [toCopy]);
    };

    self.selectText = function (element) {
    	$.event.trigger("preSelectText");
    	
    	if (element==null || !element.any()) {
            return;
        }

        setTimeout(function () {
            var range = document.createRange();
            var selection = window.getSelection();
            selection.removeAllRanges();
            range.selectNodeContents(element[0]);
            selection.addRange(range);
            
            $.event.trigger("postSelectText");
        }, 125);
    };
    
    self.phraseToClass = function (phrase) {
        return phrase.toLowerCase().replace("'", "_").replace('"', "_");
    };
    
    self.updateElementState = function(phrase, state, definition) {
    	lower = self.phraseToClass(phrase)
    	elements = $('.__' + lower);
    	
    	state = state.toLowerCase();
    	elements.removeClass('__notseen __known __ignored __unknown __kd __id __ud __temp').addClass("__" + state);
    	
    	if(state=="notseen") {
    		$(elements).each(function (index) {
                $(this).html(phrase);
            });
    	} else {
    		if (definition.length > 0) {
                elements.each(function (index) {
                    $(this).html(
                        (definition.length > 0 ? '<a rel="tooltip" title="' + definition + '">' : '') + phrase + (definition.length > 0 ? '</a>' : '')
                    );

                    if (state == 'known') {
                        $(this).addClass("__kd");
                    } else if (state == 'unknown') {
                        $(this).addClass("__ud");
                    } else if (state == 'ignored') {
                        $(this).addClass("__id");
                    }
                });
            }
    	}
    };
}