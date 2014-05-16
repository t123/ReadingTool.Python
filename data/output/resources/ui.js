﻿window.onerror = function(msg, url, line) {
		console.error(line, msg);
		//alert('An unhandled error has occurred. You might want to reload the page. See the console for more information.')
		return false;
	};
	
$(function() {
	cl = function() {
		return console.log.apply(console, arguments); 
	};
	
	jQuery.ajaxSettings.traditional = true;
	jQuery.support.cors = true;
	window.reading = undefined;

	jQuery.fn['any'] = function() {
		return (this.length > 0);
	};

	var lib = new Lib({});
	window.lib = lib;

	if(window.lib.getL1Code()=='ja') {
		$('.__whitespace').hide();
	}

	var lastL1 = -2, lastL2 = -2;

	$('body').tooltip({
		selector : '[rel=tooltip]',
		html : true,
		animation : false
	});

	if (window.lib.getMediaUri() != '') {
		$("#jquery_jplayer_1").show()
		var mediaUri = window.lib.getMediaUri();
		var webApiEndPoint = window.lib.getWebAPI();

		if (mediaUri.indexOf('http://') != 0 && mediaUri.indexOf('https://') != 0) {
			mediaUri = webApiEndPoint + '/resource/v1/media/' + window.lib.getItemId(); 
		}

		if (window.lib.getItemType() == 'text') {
			$("#jquery_jplayer_1").jPlayer({
				ready : function() {
					$(this).jPlayer("setMedia", {
						mp3 : mediaUri
					});
				},
				swfPath : webApiEndPoint + "/resource/v1/local/Jplayer.swf",
				supplied : "mp3",
				//warningAlerts: true,
				//errorAlerts: true,
				solution : "flash",
				wmode : "window"
			});
		} else {
			$("#jquery_jplayer_1").jPlayer({
				ready : function() {
					$(this).jPlayer("setMedia", {
						m4v : mediaUri
					});
				},
				swfPath : webApiEndPoint + "/resource/v1/local/Jplayer.swf",
				supplied : "m4v",
				// warningAlerts: true,
				// errorAlerts: true,
				solution : "flash",
				size : {
					width : "720px",
					height : "405px"
				}
			});
		}
	} else {
		$('#jp_container_1').hide();
	}

	var reading = new Reading({});

	window.reading = reading;

	$.event.trigger("pluginReady");
	
	$(document).on('keydown', function(e) {
		$.event.trigger("preKeyEvent", [$(this)]);
		$.event.trigger("keyEvent", [e, $(this)]);
		$.event.trigger("postKeyEvent", [$(this)]);
	});

	$('input[type="text"], input[type="radio"], textarea').change(function(e) {
		$.event.trigger("preDialogDataChanged", [$(e.target)]);
		reading.changed($(e.target));
		$.event.trigger("postDialogDataChanged", [$(e.target)]);
	});
	
	var mouseTrack = {};
	mouseTrack.dragged = false;
	mouseTrack.mouseDown = false;
	mouseTrack.originalSpan = null;
	
	$('#reading').on('click', '', function(e) {
		if(!$(e.target).hasClass('__term') && window.reading.isModalVisible() && !window.reading.getHasChanged()) {
			window.reading.closeModal();
		}
	});

	$('#reading').on('mousedown', 'span.__term', function(e) {
		mouseTrack.dragged = false;
		mouseTrack.mouseDown = true;
		mouseTrack.originalSpan = null;
	});
		
	$('#reading').on('mousemove', 'span.__term', function(e) {
		if(mouseTrack.mouseDown) {
			mouseTrack.dragged = true;
			$('body').css('cursor', 'copy');
			
			if(mouseTrack.originalSpan==null) {
				mouseTrack.originalSpan = $(this);
			}
		}
	});
	
	$('#reading').on('mouseup', 'span.__term', function(e) {
		mouseTrack.mouseDown = false;
		$('body').css('cursor', 'auto');
		element = $(this);
		
		if(mouseTrack.dragged && element[0]!==mouseTrack.originalSpan[0]) {
			fragment = window.lib.createFragment(mouseTrack.originalSpan, element);
			
			if(fragment==null) {
				return;
			}
			
			element = fragment;
		} else {
			if(element.closest('.__fragment').any()) {
				element = element.closest('.__fragment');
			}
		}
		
		$.event.trigger("preTermClick", [e, $(this)]);
		
		if(!e.shiftKey && !e.ctrlKey && !e.altKey && !e.metaKey) {
			reading.showModal(element);
		}
		
		$.event.trigger("postTermClick", [e, $(this)]);
		
		mouseTrack.dragged = false;
		mouseTrack.originalSpan = null;
	});
	
	$('#dSave').click(function() {
		reading.save();
	});

	$('#dClose').click(function() {
		reading.closeModal();
		return false;
	});

	$('#dReset').click(function() {
		reading.reset();
	});

	$('#dCopy').click(function() {
		reading.copy();
		return false;
	});

	$('#dRefresh').click(function() {
		reading.refresh();
		return false;
	});
});