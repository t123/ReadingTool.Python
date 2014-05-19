function Abbreviations() {
	var self = this;

	self.get = function(languageCode) {
		switch(languageCode) {
			case "en":
				return ['dr','mr','mrs','mr', 'etc'];
		}
		
		return [];
	};
}