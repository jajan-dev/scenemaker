$(document).ready(function(){

	// Current Scene loaded in the Client Browser
	scene = {};
	var scenes = [];
	var backgrounds = [];
	var props = [];

	// Save New Background to Server
	function newBackground(formData){
		$.ajax({
			type : "POST",
			url : "/api/backgrounds/",
			data : formData,
			processData : false,
			contentType : false,
			enctype : 'multiplart/form-data',
			success : function(result){
				// Show that New Background Was Uploaded to Server
				newBackgroundView(result.background)
			},
			error : function(error){
				// BAD
				console.log(error.statusText);
			}
		});
	}

	// Show that New Background Was Uploaded to Server
	function newBackgroundView(background){

		// Create a Thumbnail
		var thumb = new Image();
		thumb.src = background.url || "/media/default/question-mark.jpg";
		$(thumb).addClass("img-thumbnail").addClass("background-thumbnail");

		// Create a New Row in the Background Collection
		var thumbRow = $("<div></div>").append(thumb);
		
		// Add Thumbnail to Backgrounds
		$("#backgrounds").append(thumbRow);

		// Event Listener for Background Thumbnail - Selection / Set
		$(thumb).dblclick(function(event){
			if (!scene.hasOwnProperty("id")){
				// Scene Must be Set First
				return false;
			}
			// Set Current Scene Background using Background Data Model Representation
			setBackground(background);
		});
	}

	// Set Current Scene Background using Background Dat Model Representation
	function setBackground(background){
		$.ajax({
			type : "POST",
			url : "/api/scenes/" + scene.id + "/background/set",
			data : JSON.stringify({ background : background.id }),
			success : function(result){
				
				// Set Client Model Scene's Background
				var background = result.background;
				scene.background = background;

				// Set Current Scene's Background in the DOM
				setBackgroundView(background);

				// Update Client Scene Thumbnail
				changeSceneThumbnail(scene);
			},
			error : function(error){
				// BAD
				console.log(error.statusText);
			}
		});
	}

	// Set Current Scene's Background in the DOM
	function setBackgroundView(background){
		$("#scene-background-image").attr("src", background.url || "")
			.css("display", "block")
			.attr("draggable", false);
		changeEditorMenu();
	}

	// Save New Prop to Server
	function newProp(formData){
		$.ajax({
			type : "POST",
			url : "/api/props/",
			data : formData,
			processData : false,
			contentType : false,
			enctype : 'multiplart/form-data',
			success : function(result){
				newPropView(result.prop);
			},
			error : function(error){
				// BAD
				console.log(error.statusText);
			}
		});
	}

	// Show that New Prop was Uploaded to Server
	function newPropView(prop){

		var thumb = new Image();
		thumb.src = prop.url || "/media/default/question-mark.jpg";
		$(thumb).addClass("img-thumbnail").addClass("prop-thumbnail");
		var thumbRow = $("<div></div>").append(thumb);
		$("#props").append(thumbRow);

		$(thumb).dblclick(function(event){
			if (!scene.hasOwnProperty("id")){
				// Scene Must be Set First
				return false;
			}
			addProp(prop);
		});
	}

	// Add Prop to Current Scene on Server
	function addProp(prop){
		$.ajax({
			type : "POST",
			url : "/api/scenes/" + scene.id + "/props/add",
			data : JSON.stringify({ prop : prop.id }),
			success : function(result){
				addPropView(result.prop)
			},
			error : function(error){
				console.log(error.statusText);
			}
		});
	}

	// Add Prop to Current Scene in the DOM
	function addPropView(prop){
		scene.props[prop.scene_prop_id] = prop;
		var image = new Image();
		image.src = prop.url || "";
		$(image).data("scene-prop-id", prop.scene_prop_id);
		image.draggable = true;
		$(image).addClass("prop");
		$(".scene-props").append(image);
		image.style.left = prop.position_x ? prop.position_x + "px" : "0px";
		image.style.top = prop.position_y ? prop.position_y + "px" : "0px";
	}

	// Update Prop Position on Server
	function moveProp(id, update){
		$.ajax({
			type : "PUT",
			url : "/api/scenes/" + scene.id,
			data : JSON.stringify(update),
			success : function(result){
				// Saved
				scene.props[id].position_x = update.update.position_x;
				scene.props[id].position_y = update.update.position_y;
				changeSceneThumbnail(scene);
				changeEditorMenu();
			},
			error : function(error){
				console.log(error.statusText);
			}
		});
	}

	// Save New Scene on Server
	function newScene(name, description){
		$.ajax({
			type : "POST",
			url : "/api/scenes",
			data : JSON.stringify({
				name : name,
				description : description
			}),
			success : function(result){
				newSceneView(result.scene);
			},
			error : function(error){
				console.log(error.statusText);
			}
		});
	}

	// Show that New Scene was Created on Server
	function newSceneView(new_scene){

		// Close Modal
		$("#new-scene-modal").modal("hide");
		$("#new-scene-form .form-control").val("");

		// Model
		scene = {
			id : new_scene.id,
			name : new_scene.name,
			description : new_scene.description,
			version : new_scene.version,
			background : {},
			background_scale : 1.0,
			props : {}
		}

		// View
		clearSceneView();

		// Thumbnail
		addSceneThumbnail(new_scene);

	}

	function addSceneThumbnail(scene){

		// Create Thumbnail
		var thumb = createSceneThumbnailImage(scene);

		// Create a New Row in the Background Collection
		var thumbRow = $("<div></div>").addClass("scene-thumbnail-row").append(thumb);
		$(thumbRow).data("scene-id", scene.id);
		
		// Add Thumbnail to Backgrounds
		$("#scenes").append(thumbRow);

		// Event Listener for Background Thumbnail - Selection / Set
		$(thumb).dblclick(function(event){
			// Set Current Scene using Scene Data Model Representation
			changeScene(scene);
		});
	}

	function changeSceneThumbnail(scene){

		var newThumbnailData = createSceneThumbnailImage(scene).src;

		// Change Thumbnail
		var sceneThumbnail = $(".scene-thumbnail-row").filter(function(){
			return $(this).data("scene-id") === scene.id;
		}).find(".scene-thumbnail")[0];
		sceneThumbnail.src = newThumbnailData;
	}

	function createSceneThumbnailImage(scene){
		
		// Create Temporary Canvas
		var canvas = $("<canvas></canvas>")[0];
		var ctx = canvas.getContext('2d');

		// Create a Thumbnail
		var thumb = new Image();
		$(thumb).addClass("img-thumbnail").addClass("scene-thumbnail");

		// Draw Background
		var backgroundImage = new Image();
		backgroundImage.src = scene.background.url || "";
		canvas.width = 1920 || backgroundImage.width;
		canvas.height = 1080 || backgroundImage.height;
		ctx.drawImage(backgroundImage, 0, 0, backgroundImage.width, backgroundImage.height);

		// Draw Props
		for (var i in scene.props){
			var prop = scene.props[i];
			var propImage = new Image();
			propImage.src = prop.url;
			var left = prop["position_x"];
			var top = prop["position_y"];

			ctx.drawImage(propImage,left,top);
		}

		// Return Image
		var imageDataURL = canvas.toDataURL();
		thumb.src = imageDataURL;
		return thumb;
	}

	// Change Scene Client Model
	function changeScene(new_scene){
		scene = new_scene;
		changeSceneView();
	}

	// Change Scene in the DOM
	function changeSceneView(){
		background = scene.background;
		props = scene.props;
		clearSceneView();
		setBackgroundView(background);
		for (var i in props){
			var prop = props[i];
			addPropView(prop);
		}

		// Update Editor
		changeEditorMenu();
		return true;
	}

	// Resets Scene to Empty View
	function clearSceneView(){
		$("#scene-background-image").attr("src", "");
		$(".scene-props").html("");
		return true;
	}

	// Update Editor Menu With Current Scene
	function changeEditorMenu(){

		// Change Metadata
		$("#editor-scene-name-value").text(scene.name);
		$("#editor-scene-description-value").text(scene.description);
		$("#editor-scene-version-value").text(scene.version);
		
		// Change Background
		$("#editor-background .background-thumbnail").attr("src", scene.background.url || "");
		
		// Change Props
		$("#editor-props").html("");
		$.each(scene.props, function(i,prop){
			if (!prop.url){
				return false;
			}
			var propImage = new Image();
			propImage.src = prop.url;
			$(propImage).addClass("img-thumbnail").addClass("prop-thumbnail");
			$("#editor-props").append(propImage);
		});
	}

	// CLIENT EVENTS //

	// Drag Event Listener
	window.onload = function() {
		document.onmousedown = startDrag;
		document.onmouseup = stopDrag;
	}

	// Drag Event Listener Helpers

	// Drag Event Variables
	var drag = false;
	var targ, coordX, coordY, offsetX, offsetY;
	var left, top, maxLeft, maxTop;

	// Start Drag Event Hanlder
	function startDrag(e) {
		// determine event object
		if (!e) {
			var e = window.event;
		}
		// if(e.preventDefault) e.preventDefault();

		// IE uses srcElement, others use target
		targ = e.target ? e.target : e.srcElement;

		if (targ.className != 'prop') {return true;};
		// calculate event X, Y coordinates
		offsetX = e.clientX;
		offsetY = e.clientY;

		// assign default values for top and left properties
		if (!targ.style.left) { targ.style.left='0px'};
		if (!targ.style.top) { targ.style.top='0px'};

		// calculate integer values for top and left 
		// properties
		coordX = parseInt(targ.style.left);
		coordY = parseInt(targ.style.top);
		drag = true;

		// move div element
		document.onmousemove = dragDiv;
		return false;
	}

	// Draggig Event Handler
	function dragDiv(e) {
		if (!drag) { return; }
		if (!e) { var e = window.event; }
		// var targ=e.target?e.target:e.srcElement;
		// move div element
		left = coordX + e.clientX - offsetX;
		maxLeft = ($("#scene-background-image")[0].width || 1920) - targ.width;
		top = coordY + e.clientY - offsetY;
		maxTop = ($("#scene-background-image")[0].height || 1080) - targ.height;
		if (left < 0){
			targ.style.left = '0px';
		} else if (left > maxLeft){
			targ.style.left = maxLeft + 'px'
		} else {
			targ.style.left = left + 'px';
		}
		if (top < 0){
			targ.style.top = '0px';
		} else if (top > maxTop){
			targ.style.top = maxTop + 'px';
		} else {
			targ.style.top = top + 'px';
		}
		return false;
	}

	// Stop Drag Event Handler
	function stopDrag(e) {
		drag = false;

		if (!e) {  var e = window.event; }
		if (targ.className != 'prop') {return true;};
		var propLeft = parseInt(targ.style.left,10);
		var propTop = parseInt(targ.style.top,10);
		var scenePropId = $(targ).data("scene-prop-id");
		var update_data = {
			update : {
				type : "PROP",
				scene_prop : scenePropId,
				position_x : propLeft,
				position_y : propTop
			}
		};
		moveProp(scenePropId, update_data);
	}

	// New Scene Event Listener
	$("#create-new-scene-btn").click(function(event){
		
		// Get Metadata
		var name = $("#new-scene-name").val();
		var description = $("#new-scene-description").val()
		
		// Create New Scene on Server
		newScene(name, description);
	});

	// Background Image Uploaded Event Listener
	$("#new-background").on('change.bs.fileinput', function(){

		// Get File
		var files = [this.files[0]];
		var file = files[0];

		// Read File
		var backgroundFr = new FileReader();
		backgroundFr.readAsDataURL(file);

		// Reset Upload Tool (Blank)
		$("#new-background").replaceWith($("#new-background").val('').clone(true));
		$(".fileinput-filename").html("");
		
		// Create New Form with Background Image
		var data = new FormData();
		$.each(files, function(key,value){
			data.append("background",value);
		});

		// Background Image Metadata - TODO
		data.append("name", "testing the backgrond upload");
		data.append("description", "");
		
		// Save New Background to Server
		newBackground(data);
	});

	// Prop Image Uploaded Event Listener
	$("#new-prop").on('change.bs.fileinput', function(){
		
		// Get File
		var files = [this.files[0]];
		var file = files[0];

		// Read File
		var propFr = new FileReader();
		propFr.readAsDataURL(file);

		// Reset Upload Tool (Blank)
		$("#new-prop").replaceWith($("#new-prop").val('').clone(true));
		$(".fileinput-filename").html("");

		// Create New Form with Prop Image
		var data = new FormData();
		$.each(files, function(key,value){
			data.append("prop",value);
		});

		// Prop Image Metadata - TODO
		data.append("name", "testing the prop upload");
		data.append("description", "");

		newProp(data);
	});

	// Initializtion

	// Load All Scenes
	$.ajax({
		type: "GET",
		url: "/api/scenes",
		success: function(result){
			scenes = result.scenes;
			for (var i in scenes){
				var load_scene = scenes[i];
				var props_array = load_scene.props;
				load_scene.props = {};
				for (var j in props_array){
					var prop = props_array[j];
					load_scene.props[prop.scene_prop_id] = prop;
				}
				scenes[load_scene.id] = load_scene;
				addSceneThumbnail(load_scene);
			}
		}
	});

	// Load All Backgrounds
	$.ajax({
		type: "GET",
		url: "/api/backgrounds",
		success: function(result){
			backgrounds = result.backgrounds;
			for (var i in backgrounds){
				var background = backgrounds[i];
				newBackgroundView(background);
			}
		}
	});

	// Load All Props
	$.ajax({
		type: "GET",
		url: "/api/props",
		success: function(result){
			props = result.props;
			for (var i in props){
				var prop = props[i];
				newPropView(prop);
			}
		}
	});
});