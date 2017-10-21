var mirador;
$(document).ready(function() {
    mirador = Mirador({
	"id": "viewer",
	"layout": "1x1",
	"data": [{
	    "manifestUri": "https://iiif.archivelab.org/iiif/TheGeometry/manifest.json", "location": "Internet Archive"
	}],
	"windowObjects": [{
	    "viewType": "ImageView",
	    "loadedManifest": "https://iiif.archivelab.org/iiif/TheGeometry/manifest.json",
	    "annotationLayer": true,
	    "annotationCreation": true,
	    "annotationState": 'on'
	}],
	"annotationEndpoint": {

	    "name": "Local Storage",
	    "module": "PragmaEndpoint"

	}
    });
    crosslink.setup(mirador);
});
