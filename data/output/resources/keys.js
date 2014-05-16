(function(){
	$(document).on('keyEvent', function(e, source) {
		var code = source.keyCode ? source.keyCode : source.which;
		console.log(code)

		if (window.reading.isModalVisible()) {
			if (source.ctrlKey) { //Modal visible, ctrl
				switch (code) {
					case 13: // Enter
						reading.save(true);
						source.preventDefault();
						break;
	
					case 82: // R
						reading.reset();
						source.preventDefault();
						break;
	
					case 75: // k
						reading.setDState('known');
						source.preventDefault();
						break;
	
					case 85: // u
						reading.setDState('unknown');
						source.preventDefault();
						break;
	
					case 73: // i
						reading.setDState('ignored');
						source.preventDefault();
						break;
				}
	
				return;
			}  //Modal visible, ctrl

			switch (code) {  //Modal visible, not ctrl
				case 27: // escape
					reading.closeModal();
					break;
	
				case 37: // left
					if (!reading.getHasChanged()) {
						var el = window.lib.currentLeft();
						
						if(el!=null) {
							reading.showModal(el);
							return;
						}
					}
					break;
	
				case 39: // right
					if (!reading.getHasChanged()) {
						var el = window.lib.currentRight();
						
						if(el!=null) {
							reading.showModal(el);
							return;
						}
					}
					break;
			}
		} else { //Modal not visible
			switch (code) {
				case 32:
					var el = window.lib.getCurrentSelected();
	
					if (el.any()) {
						reading.showModal(el);
						source.preventDefault();
						return;
					}
					break;
	
				case 37: // left
					var el = window.lib.currentLeft();
					
					if(el!=null) {
						window.lib.setCurrentSelected(el);
						return;
					}
					break;
	
				case 39: // right
					var el = window.lib.currentRight();
					
					if(el!=null) {
						window.lib.setCurrentSelected(el);
						return;
					}
					break;
			}
		}
	});
})();