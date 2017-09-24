var crosslink = {};
var loaded = false;
$(document).ready(function() {
    crosslink.setup = function(mirador) {
        mirador.viewer.eventEmitter.subscribe('manifestReceived', function(event, manifest) {
	    if (!loaded) {
		$('.mirador-main-menu').prepend(
	            '<li><a href="javascript:;" class="xannotate-activate"><i class="fa fa-columns fa-lg fa-fw"></i> xAnnotate</a></li>');
		$('.mirador-main-menu').prepend('<div class="xannotate-widget"><form><input class="xannotate-source" value="" placeholder="Source"/><input class="xannotate-target" placeholder="Target"/><button id="xannotate-submit">Link</button></form></div>');
		loaded = true;
	    }
	});
	mirador.viewer.eventEmitter.subscribe('manifestReceived', function(event, manifest) {
	    $('.mirador-viewer').on('click', '.text-viewer a', function(event) {
		var link = $(this).attr('href'),
		canvas,
		manifest;

		event.preventDefault();
		event.stopImmediatePropagation;
		$.get(link, function(anno) {
		    canvas = anno.annotation.on.full;
		    manifest = anno.annotation.on.within['@id'];
		    mirador.viewer.addManifestFromUrl(manifest);
		});
		mirador.viewer.eventEmitter.subscribe('manifestReceived', function(event, manifest) {
		    mirador.viewer.eventEmitter.publish('SPLIT_RIGHT', mirador.viewer.workspace.slots[0]);
		    var _config = {
			manifest: manifest,
			slotAddress: mirador.viewer.workspace.slots[1].getAddress(),
			canvasID: canvas,
			viewType: 'ImageView',
			annotationLayer: true,
			annotationCreation: true,
			annotationState: 'on'
		    };
		    mirador.viewer.eventEmitter.publish('ADD_WINDOW', _config);
		    // load the manifest in the right slot
		});

		return false;
	    });
	});
    }

    $(document).on('click', '.xannotate-activate', function() {
	console.log('?');
	$('.xannotate-widget').toggle();
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
	if (selected.length){
	    selected.val('lol');
	}
    });

    //https://pragma.archivelab.org/annotations/39

    $('#xannotate-submit').click(function() {
	var source_annotation = null;
	var target_annotation = null;

	console.log('creating xannotation');
	//backref
	//ref
    });
});
