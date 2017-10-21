var crosslink;
var loaded = false;
$(document).ready(function() {
    crosslink = {
	setup: function(mirador) {
	    mirador.viewer.eventEmitter.subscribe('manifestReceived', function(event, manifest) {
		if (!loaded) {
		    $('.mirador-main-menu').prepend(
			'<li><a href="javascript:;" class="xannotate-activate"><i class="fa fa-columns fa-lg fa-fw"></i> xAnnotate</a></li>');
		    $('.mirador-main-menu').prepend('<div class="xannotate-widget"><form><button type="reset" id="xannotate-reset">Reset</button><input class="xannotate-text" value="" placeholder="Text"/><input class="xannotate-source" value="" placeholder="Source annotation"/><input class="xannotate-target" placeholder="Target annotation"/><button type="button" id="xannotate-submit">Cross-link</button></form></div>');
		    loaded = true;
		}
	    });

	    mirador.viewer.eventEmitter.subscribe('manifestReceived', function(event, manifest) {

		var isManifestLoaded = function(manifestUri) {
		    for (var m in mirador.viewer.data) {
			if (mirador.viewer.data[m].manifestUri == manifestUri) {
			    return true;
			}
		    }
		    return false;
		}

		var splitAndLoad = function(manifest, canvas) {
		    mirador.viewer.eventEmitter.publish('SPLIT_RIGHT', mirador.viewer.workspace.slots[0]);
		    console.log(manifest)
		    var _config = {
			manifest: manifest,
			slotAddress: mirador.viewer.workspace.slots[1].getAddress(),
			canvasID: canvas,
			viewType: 'ImageView',
			annotationLayer: true,
			annotationCreation: true,
			annotationState: 'on'
		    };
		    mirador.reload();
		    mirador.viewer.eventEmitter.publish('ADD_WINDOW', _config);
		    // load the manifest in the right slot
		}

		mirador.reload = function() {
		    for (var i in mirador.viewer.workspace.windows) {
			var window = mirador.viewer.workspace.windows[i];
			window.update();
		    }
		}

		$('.mirador-viewer').on('click', '.text-viewer a', function(event) {
		    var link = $(this).attr('href'),
			canvas,
			manifest;

		    event.preventDefault();
		    event.stopImmediatePropagation;

		    $.get(link, function(anno) {
			canvas = anno.annotation.on.full;
			manifest = anno.annotation.on.within['@id'];

			// XXX this is breaking if manifest is the same
			// check if manifest loadad


			if (isManifestLoaded(manifest)) {
			    splitAndLoad(manifest, canvas);
			} else {
			    mirador.viewer.addManifestFromUrl(manifest);
			}
		    });
		    mirador.viewer.eventEmitter.subscribe('manifestReceived', function(event, manifest) {
			splitAndLoad(manifest, canvas);
		    });

		    return false;
		});

	    });
	}
    }

    var insertCrosslinks = function(source_id, target_id, link_text) {
	var hyperlink = function(annotation_id) {
	    return '<p><a href="' + annotation_id + '" target="_blank" title="' + link_text + '">' + link_text + '</a></p>';
	}

	console.log('attempting crosslink');
	console.log('fetching target:');
	Annotation.get(target_id, function(target_annotation) {
	    target_annotation.resource[0]['chars'] += hyperlink(source_id);
	    console.log('target, before update:');
	    console.log(target_annotation);
	    Annotation.update(target_annotation, function(x) {
		console.log('updated target:');
		console.log(x);
		console.log('fetching source:');
		Annotation.get(source_id, function(source_annotation) {
		    console.log('source, before update:');
		    console.log(source_annotation);
		    source_annotation.resource[0]['chars'] += hyperlink(target_id);
		    Annotation.update(source_annotation, function(y) {
			console.log('updated source:');
			console.log(y);
			//mirador.reload();
		    });
		});
	    });
	});
    }

    $(document).on('click', '#xannotate-submit', function(e) {
	var source_annotation_id = $('.xannotate-source').val();
	var target_annotation_id = $('.xannotate-target').val();
	var link_text = $('.xannotate-text').val();
	insertCrosslinks(source_annotation_id, target_annotation_id, link_text);
	e.stopImmediatePropagation();
	e.preventDefault();
	return false;
    });

    $(document).on('click', '.xannotate-activate', function() {
	$('.xannotate-widget').toggle();
    });

    $('.button-container').append(
		'<a href="#xannotate" class="xannotate">' +
	    '<i class="fa fa-link-o fa-fw"></i>crosslink</a>');

    $(document).on('click', '.annotation-tooltip', function(e) {
	var anno_id = $(this).data('anno-id');
	console.log(anno_id);
	if (anno_id) {
	    if (!$('.xannotate-source').val()) {
		$('.xannotate-source').val(anno_id);
	    } else {
		$('.xannotate-target').val(anno_id);
	    }
	}
    });

    $('.xannotate-widget .xannotate-source').focus(function(e) {
	$('.xannotate-target').removeClass('selected');
	$('.xannotate-source').addClass('selected');
	// change mouse cursor to crosshairs
    })

    $('.xannotate-widget .xannotate-target').focus(function(e) {
	$('.xannotate-source').removeClass('selected');
	$('.xannotate-target').addClass('selected');
	// change mouse cursor to crosshairs
    });

    $(document).click(function() {
	var selected = $('.xannotate-widget .selected');
    });

});
