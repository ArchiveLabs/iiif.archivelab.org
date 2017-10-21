/*
 * All Endpoints need to have at least the following:
 * annotationsList - current list of OA Annotations
 * dfd - Deferred Object
 * init()
 * search(options, successCallback, errorCallback)
 * create(oaAnnotation, successCallback, errorCallback)
 * update(oaAnnotation, successCallback, errorCallback)
 * deleteAnnotation(annotationID, successCallback, errorCallback) (delete is a reserved word)
 * TODO:
 * read() //not currently used
 *
 * Optional, if endpoint is not OA compliant:
 * getAnnotationInOA(endpointAnnotation)
 * getAnnotationInEndpoint(oaAnnotation)
 */

var pragma_url, Annotation;
(function($){
    pragma_url = 'https://pragma.archivelab.org/annotations';
    Annotation = {
	get: function(annotation_id, successCallback) {
            jQuery.ajax({
                url: annotation_id,
                type: 'GET',
                dataType: 'json',
                contentType: "application/json; charset=utf-8",
                success: function(data) {
                    var annotation = data.annotation;
                    if (typeof successCallback === "function") {
                        successCallback(annotation);
                    }
		}
	    });
	},
	update: function(oaAnnotation, successCallback, errorCallback) {
	    var annotation = jQuery.extend({}, oaAnnotation);
	    if(annotation.on.length) {
		annotation.on = annotation.on[0];
	    }
	    if (annotation.endpoint) {
		delete annotation.endpoint;
	    }

	    jQuery.ajax({
		url: pragma_url,
                type: 'POST',
                dataType: 'json',
                headers: { },
		data: JSON.stringify(annotation),
                processData: false,
                contentType: "application/json; charset=utf-8",
                success: function(data) {
                    var annotation = data.annotation;
		    if (typeof successCallback === "function") {
			successCallback(annotation)
		    }
		},
		error: function() {
		    if (typeof errorCallback === "function") {
			errorCallback();
		    }
		}
	    });
	}
    }


    $.PragmaEndpoint = function(options) {

        jQuery.extend(this, {
            dfd:             null,
            annotationsList: [],        //OA list for Mirador use
            windowID:        null,
            eventEmitter:    null
        }, options);

        this.init();
    };

    $.PragmaEndpoint.prototype = {
        init: function() {
            //whatever initialization your endpoint needs
        },

        //Search endpoint for all annotations with a given URI in options
        search: function(options, successCallback, errorCallback) {
            var _this = this;

            //use options.uri
            jQuery.ajax({
                url: pragma_url + '?canvas_id=' +  options.uri,
                type: 'GET',
                dataType: 'json',
                headers: { },
                data: {
                    canvas_id: options.uri
                },
                contentType: "application/json; charset=utf-8",
                success: function(data) {
                    var annotations = data.annotations
		    _this.annotationsList = [];

                    jQuery.each(annotations, function(index, value) {
                        value.annotation.on = [value.annotation.on];
                        value.annotation.endpoint = _this;
			if (!value.annotation['@id']) {
			    value.annotation['@id'] = $.genUUID();
			}

			_this.annotationsList.push(value.annotation);
                    });

		    //check if a function has been passed in, otherwise, treat it as a normal search
                    if (typeof successCallback === "function") {
                        successCallback(_this.annotationsList);
                    } else {
                        _this.dfd.resolve(true);
                    }
                },
                error: function() {
                    if (typeof errorCallback === "function") {
                        errorCallback();
                    }
                }
            });
        },

        //Delete an annotation by endpoint identifier
        deleteAnnotation: function(annotationID, successCallback, errorCallback) {
            var _this = this;
            jQuery.ajax({
                url: pragma_url,
                type: 'DELETE',
                dataType: 'json',
                headers: { },
                contentType: "application/json; charset=utf-8",
                success: function(data) {
                    if (typeof successCallback === "function") {
                        successCallback();
                    }
                },
                error: function() {
                    if (typeof errorCallback === "function") {
                        errorCallback();
                    }
                }
            });
        },

        //Update an annotation given the OA version
        update: function(oaAnnotation, successCallback, errorCallback) {
	    var _this = this;

	    Annotation.update(oaAnnotation, function(annotation) {
                if (typeof successCallback === "function") {
		    annotation.endpoint = _this;
                    successCallback(_this.getAnnotationInOA(annotation));
                }
	    }, errorCallback);

        },

        //takes OA Annotation, gets Endpoint Annotation, and saves
        //if successful, MUST return the OA rendering of the annotation
        create: function(oaAnnotation, successCallback, errorCallback) {
            var _this = this;
            oaAnnotation.on = oaAnnotation.on[0];
            jQuery.ajax({
                url: pragma_url,
                type: 'POST',
                dataType: 'json',
                headers: { },
                data: JSON.stringify(oaAnnotation),
                processData: false,
                contentType: "application/json; charset=utf-8",
                success: function(data) {
                    var annotation = data.annotation;
                    annotation.endpoint = _this;
                    if (typeof successCallback === "function") {
                        successCallback(_this.getAnnotationInOA(annotation));
                    }
                },
                error: function() {
                    if (typeof errorCallback === "function") {
                        errorCallback();
                    }
                }
            });
        },

        userAuthorize: function(){
            return true;
        },

        set: function(prop, value, options) {
            if (options) {
                this[options.parent][prop] = value;
            } else {
                this[prop] = value;
            }
        },

        //Convert Endpoint annotation to OA
        getAnnotationInOA: function(annotation) {
            annotation.on = [annotation.on];
            return annotation;
        },

        // Converts OA Annotation to endpoint format
        getAnnotationInEndpoint: function(oaAnnotation) {
            return oaAnnotation;
        }
    };
}(Mirador));
