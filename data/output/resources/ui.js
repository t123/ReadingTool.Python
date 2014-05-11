﻿$(function () {
    jQuery.ajaxSettings.traditional = true;
    jQuery.support.cors = true;
    window.reading = undefined;

    var webApiEndPoint = $('#reading').data('webapi');
    var lastL1 = -2, lastL2 = -2;

    $('body').tooltip({
        selector: '[rel=tooltip]',
        html: true,
        animation: false
    });

        if ($('#reading').data('mediauri') != '') {
        	$("#jquery_jplayer_1").show()
            var mediaUri = $('#reading').data('mediauri');
            
            if(mediaUri.indexOf('http://')!=0 && mediaUri.indexOf('https://')!=0) {
            	mediaUri = webApiEndPoint + '/resource/v1/media/' + $('#reading').data('itemid');
            }

            if ($('#reading').data('itemtype') == 'text') {
            	$("#jquery_jplayer_1").jPlayer({
                    ready: function () {
                        $(this).jPlayer("setMedia", {
                            mp3: mediaUri
                        });
                    },
                    swfPath: webApiEndPoint + "/resource/v1/local/Jplayer.swf",
                    supplied: "mp3",
                    //warningAlerts: true,
                    //errorAlerts: true,
                    solution: "flash",
                    wmode:"window"
                });
            } else {
                $("#jquery_jplayer_1").jPlayer({
                    ready: function () {
                        $(this).jPlayer("setMedia", {
                            m4v: mediaUri
                        });
                    },
                    swfPath: webApiEndPoint + "/resource/v1/local/Jplayer.swf",
                    supplied: "m4v",
                    //warningAlerts: true,
                    //errorAlerts: true,
                    solution: "flash",
                    size: {
                        width: "720px",
                        height: "405px"
                    }
                });
            }
        } else {
            $('#jp_container_1').hide();
        }

        var lib = new Lib({
            url: webApiEndPoint,
            languageId: $('#reading').data('languageid'),
            itemId: $('#reading').data('itemid')
        });
        
        var reading = new Reading({
            url: webApiEndPoint,
            languageId: $('#reading').data('languageid'),
            itemId: $('#reading').data('itemid')
        });

        window.reading = reading;
        window.lib = lib;
        
        $(document).trigger('pluginReady');

        $(document).on('keydown', function (e) {
            var code = (e.keyCode ? e.keyCode : e.which);

            if ($('#popup').is(':visible')) {
                if (e.ctrlKey) {
                    switch (code) {
                        case 13: //Enter
                            reading.save();
                            reading.closeModal();
                            e.preventDefault();
                            break;

                        case 82: //R
                            reading.reset();
                            e.preventDefault();
                            break;

                        case 49: //1
                            reading.setDState('known');
                            e.preventDefault();
                            break;

                        case 50: //2
                            reading.setDState('unknown');
                            e.preventDefault();
                            break;

                        case 51: //3
                            reading.setDState('ignored');
                            e.preventDefault();
                            break;

                        case 52: //4
                            reading.setDState('notseen');
                            e.preventDefault();
                            break;

                        case 81: //q
                        case 83: //s
                            reading.setFocus($('#dSentence'));
                            e.preventDefault();
                            break;

                        case 65: //a
                        case 66: //b
                            reading.setFocus($('#dBase'));
                            e.preventDefault();
                            break;

                        case 90: //z
                        case 68: //d
                            reading.setFocus($('#dDefinition'));
                            e.preventDefault();
                            break;
                    }

                    return;
                }

                switch (code) {
                    case 27: //escape
                        reading.closeModal();
                        break;

                    case 37: //left
                        if (!reading.getHasChanged()) {
                            var el = $('.__current').prevAll('.__term.__notseen,.__term.__unknown').first('span');

                            if (el.any()) {
                                reading.showModal(el);
                                return;
                            }

                            el = $('.__current').parent().prev('.__sentence').children('.__term.__notseen,.__term.__unknown').last('span');

                            if (el.any()) {
                                reading.showModal(el);
                                return;
                            }
                        }
                        break;

                    case 39: //right
                        if (!reading.getHasChanged()) {
                            var el = $('.__current').nextAll('.__term.__notseen,.__term.__unknown').first('span');

                            if (el.any()) {
                                reading.showModal(el);
                                return;
                            }

                            el = $('.__current').parent().next('.__sentence').children('.__term.__notseen,.__term.__unknown').first('span');

                            if (el.any()) {
                                reading.showModal(el);
                                return;
                            }
                        }
                        break;
                }
            } else {
                switch (code) {
                    case 32:
                        var el = reading.getCurrentSelected();

                        if (el.any()) {
                            reading.showModal(el);
                            e.preventDefault();
                            return;
                        }
                        break;

                    case 37: //left
                        var el = $('.__current').prevAll('.__term.__notseen,.__term.__unknown').first('span');

                        if (el.any()) {
                            reading.updateCurrentSelected(el);
                            return;
                        }

                        el = $('.__current').parent().prev('.__sentence').children('.__term.__notseen,.__term.__unknown').last('span');

                        if (el.any()) {
                            reading.updateCurrentSelected(el);
                            return;
                        }
                        break;

                    case 39: //right
                        var el = $('.__current').nextAll('.__term.__notseen,.__term.__unknown').first('span');

                        if (el.any()) {
                            reading.updateCurrentSelected(el);
                            return;
                        }

                        el = $('.__current').parent().next('.__sentence').children('.__term.__notseen,.__term.__unknown').first('span');

                        if (el.any()) {
                            reading.updateCurrentSelected(el);
                            return;
                        }
                        break;
                }
            }
        });

        $('input[type="text"], input[type="radio"], textarea').change(function (e) {
            $(document).trigger('preDataChanged', e, e);
            reading.changed($(e.target));
            $(document).trigger('postDataChanged', e, e);
        });

        jQuery.fn['any'] = function () {
            return (this.length > 0);
        };

        $('#reading').on('click', 'span.__term', function (e) {
            if (e.ctrlKey) {
                reading.markTemp($(this));
            } else {
                reading.showModal($(this));
            }
        });

        $('#dSave').click(function () {
            reading.save();
        });

        $('#dClose').click(function () {
            reading.closeModal();
            return false;
        });

        $('#dReset').click(function () {
            reading.reset();
        });

        $('#dCopy').click(function () {
            reading.copy();
            return false;
        });

        $('#dRefresh').click(function () {
            reading.refresh();
            return false;
        });
});

