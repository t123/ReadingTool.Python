/*global $:false */
/*global rtjscript:false */
/*jslint devel:true */
/*jslint browser:true */

function MediaPlayerFactory(type) {
    "use strict";

    var mp = null;

    if (type == 'jplayer') {
        mp = new JPlayerMediaPlayer();
    } else if (type == 'vlc') {
        mp = new VlcMediaPlayer();
    } else {
        mp = null;
    }

    if (mp === null || !mp.hasPlayer()) {
        return new NullMediaPlayer();
    }

    return mp;
}

function NullMediaPlayer() {
    "use strict";
    var self = this;

    self.hasPlayer = function () {
        return false;
    };

    self.isPlaying = function () {
        return false;
    };

    self.isPaused = function () {
        return false;
    };

    self.isStopped = function () {
        return false;
    };

    self.getDuration = function () {
        return 0;
    };
    
    self.setWasPlaying = function() {
        return;  
    };
    
    self.getWasPlaying = function() {
        return false;
    };

    self.mute = function () {};

    self.unmute = function () {};

    self.volumeUp = function () {};

    self.volumeDown = function () {};

    self.getVolume = function () {};

    self.setVolume = function (volume) {};

    self.play = function (fromTime) {};

    self.pause = function () {};

    self.stop = function () {};

    self.getCurrentTime = function () {
        return 0;
    };
}

function VlcMediaPlayer() {
    "use strict";
    var self = this;
    self.player = document.getElementById('vlc');
    self.lastL1 = -2;
    self.lastL2 = -2;

    self.hasPlayer = function () {
        if (self.player === null) {
            return false;
        }

        try { //Crashes if no permission to run yet
            if (typeof self.player.versionInfo !== 'function') {
                return false;
            }
        } catch (error) {
            return false;
        }

        return true;
    };

    self.isPaused = function () {
        return self.player.input.state == 4;
    };

    self.isPlaying = function () {
        return self.player.input.state == 3;
    };

    self.isStopped = function () {
        return self.player.input.state == 5 || self.player.input.state == 6;
    };

    self.getDuration = function () {
        return self.player.input.length / 1000;
    };

    self.mute = function () {
        self.player.audio.mute = true;
    };

    self.unmute = function () {
        self.player.audio.mute = false;
    };

    self.volumeUp = function () {
        self.setVolume(self.getVolume() + 10);
    };

    self.volumeDown = function () {
        self.setVolume(self.getVolume() - 10);
    };

    self.getVolume = function () {
        return self.player.audio.volume;
    };

    self.setVolume = function (volume) {
        if (volume < 0) {
            volume = 0;
        } else if (volume > 100) {
            volume = 100;
        }

        self.player.audio.volume = volume;
    };

    self.play = function (fromTime) {
        fromTime = fromTime || null;
        
        if (fromTime !== null) {
            if (fromTime < 0) {
                fromTime = 0;
            } else if (fromTime > self.getDuration()) {
                fromTime = self.getDuration();
            }

            self.player.input.time = fromTime * 1000;
            self.player.playlist.play();
        } else {
            self.player.playlist.play();
        }
    };

    self.pause = function () {
        self.player.playlist.pause();
    };

    self.stop = function () {
        self.player.playlist.stop();
    };

    self.getCurrentTime = function () {
        return self.player.input.time / 1000;
    };

    if (self.hasPlayer()) {
        self.setVolume(0);
        self.play();

        setTimeout(function () {
            self.setVolume(75);
            self.stop();
        }, 150);
    }

    self._updateSubs = function (e) {
        if (!window.lib.hasEmbeddedScript()) {
            $('#l1Main').html('Missing rtjscript');
            $('#l2Main').html('Missing rtjscript');
            return;
        }

        var l1 = rtjscript.getSrtL1(e * 1000);
        var l2 = rtjscript.getSrtL2(e * 1000);

        if (l1 != self.lastL1) {
            if (l1 == -1) {
                $('#l1Main').html('');
            } else {
                $('#l1Main').html($('#l1_' + l1).html());
            }

            self.lastL1 = l1;
        }

        if (l2 != self.lastL2) {
            if (l2 == -1) {
                $('#l2Main').html('');
            } else {
                $('#l2Main').html($('#l2_' + l2).html());
            }

            self.lastL2 = l2;
        }
    };

    if (window.lib.getItemType() == 'video' && self.hasPlayer()) {
        self.player.addEventListener("MediaPlayerPositionChanged", self._updateSubs, false);
    }
}

function JPlayerMediaPlayer() {
    var self = this;
    self.player = $('#jquery_jplayer_1');
    self.lastL1 = -2;
    self.lastL2 = -2;

    self.hasPlayer = function () {
        return self.player !== null;
    };
    
    self.isPaused = function () {
        return self.player.data().jPlayer.status.paused;
    };

    self.isPlaying = function () {
        return !self.player.data().jPlayer.status.paused;
    };

    self.isStopped = function () {
        return self.isPaused() && self.getCurrentTime() <= 0; //Close enough
    };

    self.getDuration = function () {
        return self.player.data().jPlayer.status.duration;
    };

    self.mute = function () {
        self.player.jPlayer("mute");
    };

    self.unmute = function () {
        self.player.jPlayer("unmute");
    };

    self.volumeUp = function () {
        self.setVolume(self.getVolume() + 10);
    };

    self.volumeDown = function () {
        self.setVolume(self.getVolume() - 10);
    };

    self.getVolume = function () {
        return self.player.data().jPlayer.options.volume * 100;
    };

    self.setVolume = function (volume) {
        if (volume < 0) {
            volume = 0;
        } else if (volume > 100) {
            volume = 100;
        }

        self.player.jPlayer("volume", volume / 100);
    };

    self.play = function (fromTime) {
        fromTime = fromTime || null;
        
        if (fromTime !== null) {
            if (fromTime < 0) {
                fromTime = 0;
            } else if (fromTime > self.duration) {
                fromTime = self.duration;
            }

            self.player.jPlayer('play', fromTime);
        } else {
            self.player.jPlayer('play');
        }
    };

    self.pause = function () {
        self.player.jPlayer('pause');
    };

    self.stop = function () {
        self.player.jPlayer('stop');
    };

    self.getCurrentTime = function () {
        return self.player.data().jPlayer.status.currentTime;
    };

    if (self.player === undefined || self.player === null) {
        self.player = null;
    }

    if (self.player.data() === null || self.player.data().jPlayer === undefined) {
        self.player = null;
    }

    if (self.hasPlayer() && window.lib.getItemType() == 'video') {
        self.player.bind($.jPlayer.event.timeupdate, function (event) {
            if (!window.lib.hasEmbeddedScript()) {
                $('#l1Main').html('Missing rtjscript');
                $('#l2Main').html('Missing rtjscript');
                return;
            }

            var l1 = rtjscript.getSrtL1(event.jPlayer.status.currentTime);
            var l2 = rtjscript.getSrtL2(event.jPlayer.status.currentTime);

            if (l1 != self.lastL1) {
                if (l1 == -1) {
                    $('#l1Main').html('');
                } else {
                    $('#l1Main').html($('#l1_' + l1).html());
                }

                self.lastL1 = l1;
            }

            if (l2 != self.lastL2) {
                if (l2 == -1) {
                    $('#l2Main').html('');
                } else {
                    $('#l2Main').html($('#l2_' + l2).html());
                }

                self.lastL2 = l2;
            }
        });
    }
}