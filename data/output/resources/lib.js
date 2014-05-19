function Lib(options) {
	var self = this;
	self.options = options;
	self.currentElement = null;
	self.sentenceMarkers = new RegExp(/[\.\?!。]/);
	self.navTerms = { }
    self.abbrs = ['dr','mr','mrs','mr', 'etc'];
	
	self.getOptions = function () {
        return self.options;
    };
    
    //MANIPULATION OF CURRENT ELEMENT
    /**
     * Caches the previous/next element in case the current element changes state and can't be found
     * @method setNextPrev
     */
    self.setNextPrev = function() {
    	var elements = $('span.__term.__notseen,span.__term.__unknown');
		var current = self.getCurrentElement();
		var lower = current.data('lower');
		
		if(!current.any()) {
			return;
		}
		
		if(elements.length<=1) {
			return;
		} 
		
    	self.navTerms.left = null;
    	self.navTerms.right = null;
    	
		for(var i=0; i<elements.length; i++) {
			var el = $(elements[i]);
			
			if(el.hasClass('__current')) {
				j = i;
				
				while(j-1>0) {
					prev = $(elements[j-1]);
					
					if(prev.data('lower')!=lower) {
						self.navTerms.left = prev;
						j = -999;
					}
					
					j--;
				}
				
				j = i;
				
				while(j+1<elements.length) {
					next = $(elements[j+1]);
					
					if(next.data('lower')!=lower) {
						self.navTerms.right = next;
						j = elements.length+999;
					}
					
					j++;
				}
				
				return;
			}
		}
    };
    
    /**
     * Returns the first unknown or unseen element to the left of the current element
     * @method currentLeft
     * @return {element}
     */
    self.currentLeft = function() {
    	var elements = $('span.__term.__notseen,span.__term.__unknown');
		
		for(var i=0; i<elements.length; i++) {
			var el = $(elements[i]);
			
			if(el.hasClass('__current') && i>0) {
				return $(elements[i-1]);
			}
		}
		
    	if(self.navTerms.left!=null) {
    		return self.navTerms.left;
    	}
    };

    /**
     * Returns the first unknown or unseen element to the right of the current element
     * @method currentRight
     * @return {element}
     */
    self.currentRight = function() {
		var elements = $('span.__term.__notseen,span.__term.__unknown');
		
		for(var i=0; i<elements.length; i++) {
			var el = $(elements[i]);
			
			if(el.hasClass('__current') && i+1<elements.length) {
				return $(elements[i+1]);
			}
		}
		
		if(self.navTerms.right!=null) {
    		return self.navTerms.right;
    	}
    };
    
    /**
     * Returns the current element
     * @method getCurrentElement
     * @return {element}
     */
    self.getCurrentElement = function() {
    	return self.currentElement;
    };
    
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
    
    self.isCurrentFragment = function() {
        return self.isFragment(self.getCurrentElement());
    };

    self.isFragment = function(element) {
        if(element==null || !element.any())
             return false;

        return element.hasClass('__fragment');
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
            self.setNextPrev();
            $.event.trigger("postSetCurrentSelected", [element]);
        }
    };
    
    /**
     * Gets the text from the currently selected element 
     * @method getCurrentElementAsText
     * @return text of currently selected element
    */
    self.getCurrentWordAsText = function () {
        return self.getCurrentElementAsText(self.getCurrentElement());
    };

    self.getCurrentElementAsText = function (element) {
        if(element==null || !element.any()) {
            return '';
        }
        
        if(self.isFragment(element)) {
            fragment = '';
            children = element.find('.__term,.__nt');
            for(var i=0; i<children.length; i++) {
                child = $(children[i]);
                
                if (child[0].childNodes[0].nodeType == 3) {
                    fragment += child[0].childNodes[0].nodeValue;
                } else {
                    fragment += child[0].childNodes[0].innerText;
                }
            }
            
            return fragment;
        } else {
            if (element[0].childNodes[0].nodeType == 3) {
                return element[0].childNodes[0].nodeValue;
            } else {
                return element[0].childNodes[0].innerText;
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
    	current = self.getCurrentElement();
    	
        if (!current.any()) {
            return '';
        }

        if(self.isFragment(current)) {
            startNode = current.find('span.__term,span.__nt').first();
            endNode = current.find('span.__term,span.__nt').last();
        } else {
            startNode = current;
            endNode = current;
        }

        searchableNodes = $(current).parents('td.__active').find('span.__term,span.__nt');
        var startIndex = -1, endIndex = -1;

        for(var i=0; i<searchableNodes.length; i++) {
            if(searchableNodes[i]===startNode[0]) {
                startIndex = i;
            }

            if(searchableNodes[i]===endNode[0]) {
                endIndex = i;
            }

            if(startIndex>=0 && endIndex>=0) {
                break;
            }
        }

        var sentence  = '';
        var fromNode = self._backwards(searchableNodes, startIndex);
        var toNode = self._forwards(searchableNodes, endIndex);
        
        counter = 0;
        var node = fromNode;

        if(node.hasClass('__punctuation') && self.sentenceMarkers.test(node.text())) {
            node = node.next();
        }

        while(node[0]!==toNode[0] && counter<100) {
            counter++;

            if(self.getL1Code()=='ja' && !node.hasClass("__whitespace")) {
                sentence += node.text();
            } else if(self.getL1Code()!='ja') {
                sentence += node.text();
            }

            node = node.next();
        }

        sentence += node.text();

        return sentence.replace(/\s+/g, ' ').trim();
    };

    self._forwards = function(searchableNodes, index) {
        for(var i=index+1; i<searchableNodes.length; i++) {
            node = $(searchableNodes[i]);

            if(node.hasClass('__punctuation') && self.sentenceMarkers.test(node.text())) {
                if(i>0 && self.abbrs.indexOf($(searchableNodes[i-1]).text().toLowerCase())<0) {
                    return node;
                }
            }
        }

        return $(searchableNodes[searchableNodes.length-1]);
    };

    self._backwards = function(searchableNodes, index) {
        for(var i=index-1; i>=0; i--) {
            node = $(searchableNodes[i]);

            if(node.hasClass('__punctuation') && self.sentenceMarkers.test(node.text())) {
                if(i>0 && self.abbrs.indexOf($(searchableNodes[i-1]).text().toLowerCase())<0) {
                    return node;
                }
            }
        }

        return $(searchableNodes[0]);
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
            element,
    		optional,
    		doneCallback,
    		failCallback
    		) {
    	$.event.trigger("preSaveTerm", [obj, element, optional]);
    	
        var previousClass = element.attr('class');
        element.removeClass('__notseen __known __ignored __unknown __temp').addClass('__' + state.toLowerCase());

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
        	$.event.trigger("preSaveTermDone", [obj, element, optional, data]);
        	
            self.updateState(element, data);

            if(doneCallback!=null) {
            	doneCallback(obj, element, optional, data, status, xhr);
            }
            
            $.event.trigger("postSaveTermDone", [obj, element, optional, data]);
        }).fail(function (data, status, xhr) {
        	$.event.trigger("preSaveTermFail", [obj, element, optional, data]);
        	
            element.attr('class', previousClass);

        	if(failCallback!=null) {
        		failCallback(obj, element, optional, data, status, xhr);
            }
        	
        	$.event.trigger("postSaveTermFail", [obj, element, optional, data]);
        }).always(function (data, status, xhr) {
        	$.event.trigger("postSaveTerm", [obj, element, optional, data]);
        });
    };
    
    self.reset = function(element, optional, doneCallback, failCallback) {
    	phrase = self.getCurrentElementAsText(element);
        $.event.trigger("preResetTerm", [element, optional]);
    	
    	$.ajax({
            url: self.getWebAPI() + "/internal/v1/delete",
            type: 'POST',
            data: {
                phrase: phrase,
                languageId: self.getLanguageId() 
            }
        }).done(function (data, status, xhr) {
        	$.event.trigger("preResetTermDone", [element, optional, data]);
        	
            if(self.isFragment(element)) {
                element.removeClass('__unknown __known __ignored');
            } else{
                self._updateElementState(phrase, 'notseen', '')
            }

        	if(doneCallback!=null) {
            	doneCallback(element, optional, data, status, xhr);
            }
        	
        	$.event.trigger("postResetTermDone", [element, optional, data]);
        }).fail(function (data, status, xhr) {
        	if(failCallback!=null) {
        		$.event.trigger("preResetTermFail", [element, optional, data]);
        		
        		failCallback(element, optional, data, status, xhr);
        		
        		$.event.trigger("postResetTermDone", [element, optional, data]);
            }
        }).always(function (data) {
        	$.event.trigger("postReset", [element, optional, data]);
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
            $('.__notseen').each(function () {
                $(this).removeClass('__notseen').addClass('__known');
            });

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
    self.hasEmbeddedScript = function() {
    	if(typeof rtjscript==='undefined') {
        	console.log("rtjscript undefined");
        	return false;
        }
    	
    	return true;
    };
    
    self.copyToClipboard = function (toCopy) {
    	$.event.trigger("preCopyToClipboard");

        if(self.hasEmbeddedScript()) {
        	rtjscript.copyToClipboard(toCopy);
        }

        $.event.trigger("postCopyToClipboard", [toCopy]);
    };
    
    self.sendMessage = function(message) {
    	if(self.hasEmbeddedScript()) {
        	rtjscript.setMessage(message);
        }
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
    	if(phrase==null) {
    		console.log('Phrase is null.');
    		return '__';
    	}
    	
    	if(typeof phrase !== 'string') {
    		console.log('Phrase is not a string.');
    		return '__';
    	}
    	
        return phrase.toLowerCase().replace("'", "_").replace('"', "_");
    };
    
    /**
     * Updates all the element states with correct definition and classes
     * @param  {[type]} The element currently selected. Required for fragment only.
     * @param  {[type]} An object representing a term.
     */
    self.updateState = function(element, data) {
        var tempDef = data.basePhrase.length > 0 ? data.basePhrase + "<br/>" : '';
        if (data.definition.length > 0) tempDef += data.definition.replace(/\n/g, '<br />');

        if(self.isFragment(element)) {
            self._updateFragmentState(element, data.phrase, data.state, tempDef);
        } else {
            self._updateElementState(data.phrase, data.state, tempDef);
        }
    };

    self._updateElementState = function(phrase, state, definition) {
    	lower = self.phraseToClass(phrase)
    	elements = $('.__' + lower).filter(function() {
    		return !$(this).closest('.__fragment').any()
    	});

        elementsInFragments = $('.__' + lower).filter(function() {
            return $(this).closest('.__fragment').any()
        });
    	
    	state = state.toLowerCase();
    	
    	elements.removeClass('__notseen __known __ignored __unknown __kd __id __ud __temp').addClass("__" + state);
        elementsInFragments.removeClass('__notseen __known __ignored __unknown __kd __id __ud __temp').addClass("__" + state + "_t");
    	
    	if(state=="notseen") {
    		elements.each(function (index) {
    			var phrase = $(this).text();
                $(this).html(phrase);
            });
    	} else {
    		if (definition.length > 0) {
                elements.each(function (index) {
                	phrase = $(this).text();
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
    
    self._updateFragmentState = function(element, phrase, state, definition) {
    	if(element.data('termid')!=null) {
    		termId = element.data('termid');
    		$('.__' + termId).removeClass('__known __unknown __ignored').addClass('__' + state);
    		
    		if(definition.length>0) {
	    		$('.__' + termId).each(function() {
	    			element = $(this);
	    			if(element.children('a').any()) {
		    			var tooltip = element.children('a').first();
		    			element.html(tooltip.contents());
		    		}
	    			
	    			element.html('<a rel="tooltip" title="' + definition + '">' + element.html() + '</a>');    			
	    		});
    		}
    	} else {
	    	if(definition.length>0) {
	    		if(element.children('a').any()) {
	    			var tooltip = element.children('a').first();
	    			tooltip.prop('title', definition);
	    		} else {
	    			element.html('<a rel="tooltip" title="' + definition + '">' + element.html() + '</a>');    			
	    		}
	    	}
	    	
	    	element.removeClass('__known __unknown __ignored').addClass('__' + state);
    	}
    };
    
    self.createFragment = function(startElement, stopElement) {
		if(!startElement.hasClass("__term") || !stopElement.hasClass("__term")) { //Only terms
			return null;
		}
		
		if(startElement[0]===stopElement[0]) { //On the same node
			return null;
		}
		
		if(startElement.parent()[0]!==stopElement.parent()[0]) { //Different sentences
			return null;
		}
		
		if( (startElement[0].offsetTop==stopElement[0].offsetTop && startElement[0].offsetLeft>stopElement[0].offsetLeft) || 
			stopElement[0].offsetTop<startElement[0].offsetTop
			) { //Selected backwards, same height, further on OR anywhere above
			var temp = startElement;
			startElement = stopElement;
			stopElement = temp;
		}
		
		startElement.addClass("__temp_fragment");
		startElement.nextUntil(stopElement).addClass("__temp_fragment");
		stopElement.addClass("__temp_fragment");
		
		var inFragment = false;
		$('.__temp_fragment').each(function() { //Piece is already in a fragment
			if(element.closest('.__fragment').any()) {
				inFragment = true;
			}
		});
		
		if(inFragment) {
			$('.__temp_fragment').removeClass('__temp_fragment');
			return null;
		}
		
		$('.__temp_fragment').wrapAll('<span class="__fragment"> </span>')
		$('.__temp_fragment').each(function() {
			if($(this).hasClass('__known')) {
				$(this).removeClass('__known').addClass('__known_t');
			}
			
			if($(this).hasClass('__unknown')) {
				$(this).removeClass('__unknown').addClass('__unknown_t');
			}
			
			if($(this).hasClass('__ignored')) {
				$(this).removeClass('__ignored').addClass('__ignored_t');
			}
			
			if($(this).hasClass('__notseen')) {
				$(this).removeClass('__notseen').addClass('__notseen_t');
			}
			
			if($(this).hasClass('__current')) {
				$(this).removeClass('__current');
			}
		});
		
		$('.__temp_fragment').removeClass('__temp_fragment');
		
		return startElement.parent();
	};
	
	self.deleteFragment = function(element) {
		if(!element.hasClass('__fragment')) {
			return;
		}
		
		element.find('.__term,.__nt').each(function() {
			if($(this).hasClass('__known_t')) {
				$(this).addClass('__known').removeClass('__known_t');
			}
			
			if($(this).hasClass('__unknown_t')) {
				$(this).addClass('__unknown').removeClass('__unknown_t');
			}
			
			if($(this).hasClass('__ignored_t')) {
				$(this).addClass('__ignored').removeClass('__ignored_t');
			}
			
			if($(this).hasClass('__notseen_t')) {
				$(this).addClass('__notseen').removeClass('__notseen_t');
			}
			
			if($(this).hasClass('__current')) {
				$(this).removeClass('__current');
			}		
		});
		
    	
		if(element.prev().any()) {
			element.prev().after(element.find('.__term,.__nt'));
		} else {
			element.parent().prepend(element.find('.__term,.__nt'));
		}
		
		element.remove();
	};
}