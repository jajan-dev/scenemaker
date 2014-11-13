$(document).ready(function(){

	// Current Scene loaded in the Client Browser
	scene = {};

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
		thumb.crossOrigin = "Anonymous";
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
				renderBackgroundView(background);

				// Update Client Scene Thumbnail
				changeSceneThumbnail(scene);

				// Update Editor Menu
				changeEditorMenu();
			},
			error : function(error){
				// BAD
				console.log(error.statusText);
			}
		});
	}

	// Set Current Scene's Background in the DOM
	function renderBackgroundView(background){
		$("#scene-background-image").attr("src", background.url || "")
			.css("display", "block")
			.attr("draggable", false);
		var tempBackground = new Image();
		tempBackground.crossOrigin = "Anonymous";
		tempBackground.onload = function(){
			var width = tempBackground.width;
			var height = tempBackground.height;
			$("#scene-background-image")[0].width = scene.background_scale * width;
			$("#scene-background-image")[0].height = scene.background_scale * height;
		}
		tempBackground.src = background.url || "";
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
		thumb.crossOrigin = "Anonymous";
		thumb.src = prop.url || "/media/default/question-mark.jpg";
		$(thumb).addClass("img-thumbnail").addClass("prop-thumbnail");
		var thumbRow = $("<div></div>").append(thumb);
		$("#props").append(thumbRow);

		$(thumb).dblclick(function(event){
			if (!scene.hasOwnProperty("id") || scene.background.url === ""){
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
				scene.props[result.prop.scene_prop_id] = result.prop;
				renderPropView(result.prop)
				changeSceneThumbnail(scene);
			},
			error : function(error){
				console.log(error.statusText);
			}
		});
	}

	// Add Prop to Current Scene in the DOM
	function renderPropView(prop){
		var image = new Image();
		image.crossOrigin = "Anonymous";
		image.src = prop.url || "";
		$(image).data("scene-prop-id", prop.scene_prop_id);
		image.draggable = true;
		$(image).addClass("prop");

		// Position
		image.style.left = prop.position_x ? prop.position_x + "px" : "0px";
		image.style.top = prop.position_y ? prop.position_y + "px" : "0px";

		// Scaling
		image.width *= prop.scale;
		image.height *= prop.scale;

		// Index
		image.style.zIndex = 4000 - prop.index;

		$(".scene-props").append(image);

		changeEditorMenu();
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

		// Update Editor Menu
		changeEditorMenu();

		// Switch to Editor Menu
		$("#editor-tab").tab("show");

	}

	function addSceneThumbnail(scene){

		// Create Thumbnail
		createSceneThumbnailImage(scene, function(thumb){
			// Create a New Row in the Background Collection
			$(thumb).addClass("img-thumbnail").addClass("scene-thumbnail");
			var thumbRow = $("<div></div>").addClass("scene-thumbnail-row").append(thumb);
			$(thumb).data("scene-id", scene.id);
			
			// Add Thumbnail to Backgrounds
			$("#scenes").append(thumbRow);

			// Event Listener for Background Thumbnail - Selection / Set
			$(thumb).dblclick(function(event){
				// Set Current Scene using Scene Data Model Representation
				changeScene(scene);
			});
		});
	}

	function changeSceneThumbnail(scene){

		createSceneThumbnailImage(scene, function(thumb){
			// Change Thumbnail
			var sceneThumbnail = $(".scene-thumbnail").filter(function(){
				return $(this).data("scene-id") === scene.id;
			}).attr("src", thumb.src);
		});
	}

	function createSceneThumbnailImage(scene, callback){
		
		// Create Temporary Canvas
		var canvas = $("<canvas></canvas>")[0];
		canvas.width = 1920;
		canvas.height = 1080;
		var ctx = canvas.getContext('2d');

		// Create a Thumbnail
		var thumb = new Image();
		thumb.crossOrigin = "Anonymous";

		// Draw Background
		var backgroundImage = new Image();
		backgroundImage.crossOrigin = "Anonymous";
		backgroundImage.onload = function(){
			backgroundImage.width *= scene.background_scale;
			backgroundImage.height *= scene.background_scale;
			ctx.drawImage(this, 0, 0, backgroundImage.width, backgroundImage.height);
			multiplePropThumbnailLoader(scene.props, propsLoaded);
		}
		backgroundImage.src = scene.background.url || "/static/editor/img/undefined.png";

		function propsLoaded(propImages){
			for (var i in propImages){
				var prop = propImages[i].prop;
				var image = propImages[i].image;
				var left = prop["position_x"];
				var top = prop["position_y"];
				image.width *= prop["scale"];
				image.height *= prop["scale"];
				ctx.drawImage(image, left, top, image.width, image.height);
			}
			var imageDataURL = canvas.toDataURL();
			var onLoad = function(e){
				thumb.removeEventListener("load", onLoad);
				callback(thumb);
			}
			thumb.addEventListener("load", onLoad, false);
			thumb.src = imageDataURL;
		}
	}

	// Change Scene Client Model
	function changeScene(new_scene){
		scene = new_scene;
		renderSceneView();
	}

	// Change Scene in the DOM
	function renderSceneView(){
		var background = scene.background;
		var props = scene.props;
		clearSceneView();
		renderBackgroundView(background);
		for (var i in props){
			var prop = props[i];
			scene.props[prop.scene_prop_id] = prop;
			renderPropView(prop);
		}

		// Update Editor
		changeEditorMenu();
		return true;
	}

	// Resets Scene to Empty View
	function clearSceneView(){
		$("#scene-background-image")[0].width = 0;
		$("#scene-background-image")[0].height = 0;
		$("#scene-background-image").attr("src", null);
		$(".scene-props").html("");
		return true;
	}

	// Update Editor Menu With Current Scene
	function changeEditorMenu(){

		// Change Metadata
		$("#editor-scene-name-value").text(scene.name);
		$("#editor-scene-description-value").text(scene.description);
		$("#editor-scene-version-value").text(scene.version);
		$("#edit-scene-btn").removeClass("disabled");
		
		// Change Background
		$("#editor-background .background-thumbnail")
			.attr("src", scene.background.url || "/static/editor/img/undefined.png")
			.removeClass("disabled")
			.attr("data-toggle", "modal")
			.attr("data-target", "#background-modal")
			.click(function(event){
				if (!scene.background || !scene.background.url || scene.background.url === ""){
					return false;
				}
			});
		
		// Change Props
		$("#editor-props").html("");
		$.each(scene.props, function(i,prop){
			if (!prop.url){
				return false;
			}
			var propImage = new Image();
			propImage.crossOrigin = "Anonymous";
			propImage.src = prop.url;
			$(propImage).addClass("img-thumbnail")
				.addClass("prop-thumbnail")
				.attr("data-toggle", "modal")
				.attr("data-target", "#prop-modal")
				.data("prop", prop)
				.removeClass("disabled");
			$("#editor-props").append(propImage);
		});
	}

	function updateMetadata(data){
		$.ajax({
			type : "PUT",
			url : "/api/scenes/" + scene.id,
			data : JSON.stringify(data),
			success : function(result){
				updateMetadataModel(data.update)
			},
			error : function(error){
				console.log(error);
			}
		});
	}

	function updateMetadataModel(update){
		if (update.hasOwnProperty("name")){
			scene.name = update["name"]; // Model
			$("#editor-scene-name-value").text(update["name"]); // View
		}
		if (update.hasOwnProperty("description")){
			scene.description = update["description"]; // Model
			$("#editor-scene-description-value").text(update["description"]); // View
		}
		if (update.hasOwnProperty("version")){
			scene.version = update["version"]; // Model
			$("#editor-scene-version-value").text(update["version"]); // View
		}
	}

	function updateBackground(data){
		$.ajax({
			type : "PUT",
			url : "/api/scenes/" + scene.id,
			data : JSON.stringify(data),
			success : function(result){
				updateBackgroundModel(data.update);
			},
			error : function(error){
				console.log(error);
			}
		});
	}

	function updateBackgroundModel(update){
		if (update.hasOwnProperty("background_scale")){
			
			// Update Client Model
			scene.background_scale = update["background_scale"];

			// Get Original Dimensions
			var tempBackground = new Image();
			tempBackground.crossOrigin = "Anonymous";
			tempBackground.src = scene.background.url || "/static/editor/img/undefined.png";
			var width = tempBackground.width;
			var height = tempBackground.height;

		}
		renderSceneView();
		changeSceneThumbnail(scene);
	}

	function updateSceneProp(data){
		$.ajax({
			type : "PUT",
			url : "/api/scenes/" + scene.id,
			data : JSON.stringify(data),
			success : function(result){
				updateScenePropModel(data.update);
			},
			error : function(error){
				console.log(error);
			}
		});
	}

	function updateScenePropModel(update){
		if (!update.hasOwnProperty("scene_prop")){
			return false;
		}
		var sceneProp = scene.props[update["scene_prop"]];
		if (update.hasOwnProperty("scale")){
			sceneProp.scale = update["scale"];
		}
		if (update.hasOwnProperty("index")){
			sceneProp.index = update["index"];
		}
		if (update.hasOwnProperty("rotation")){
			sceneProp.rotation = update["rotation"];
		}
		renderSceneView();
		changeSceneThumbnail(scene);
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

	// Modal Event Listeners
	$("#metadata-modal").on("show.bs.modal", function(event){
		$("#edit-metadata-name").val(scene.name);
		$("#edit-metadata-description").val(scene.description);
		$("#edit-metadata-version").val(scene.version);
	});

	$("#background-modal").on("show.bs.modal", function(event){
		$("#edit-background-scale").val(scene["background_scale"]);
	});

	$("#prop-modal").on("show.bs.modal", function(event){
		var element = event.relatedTarget;
		var prop = $(element).data("prop");
		$("#update-prop-btn").data("prop", prop);
		// Load Modal Based on Prop
		$("#edit-prop-scale").val(prop.scale);
		$("#edit-prop-index").val(prop.index);
		$("#edit-prop-index-value").text($("#edit-prop-index").val());
	});

	$("#update-metadata-btn").click(function(event){
		var data = {
			"update" : {
				"type" : "META",
				"name" : $("#edit-metadata-name").val(),
				"description" : $("#edit-metadata-description").val(),
				"version" : $("#edit-metadata-version").val()
			}
		}
		updateMetadata(data);
	});

	$("#update-background-btn").click(function(event){
		var data = {
			"update" : {
				"type" : "BACKGROUND",
				"background_scale" : parseFloat($("#edit-background-scale").val())
			}
		}
		updateBackground(data);
	});

	$("#update-prop-btn").click(function(event){
		var prop = $(this).data("prop");
		var data = {
			"update" : {
				"type" : "PROP",
				"scene_prop" : prop.scene_prop_id,
				"scale" : parseFloat($("#edit-prop-scale").val()),
				"index" : parseInt($("#edit-prop-index").val(), 10),
				"rotation" : parseFloat($("#edit-prop-rotation").val() || "0.0"),
			}
		}
		updateSceneProp(data);
	});

	// Helper Functions and Event Listeners
	$('.float-input').keypress(function(event) {
		if ((event.which != 46 || $(this).val().indexOf('.') != -1) && 
			(event.which < 48 || event.which > 57) || 
			(event.which == 46 && $(this).caret().start == 0)) {
			event.preventDefault();
			return false;
		}

		// this part is when left part of number is deleted and leaves a . in the leftmost position. For example, 33.25, then 33 is deleted
		$('.float-input').keyup(function(event) {
			if ($(this).val().indexOf('.') == 0) {
				$(this).val($(this).val().substring(1));
			}
		});
	});

	function multiplePropThumbnailLoader(props, callback){
		if (!props){
			return;
		}
		if ("undefined" === Object.keys(props).length){
			props = [props];
		}
		var count = Object.keys(props).length;
		var propImages = [];
		if (count === 0){
			return callback(propImages);
		}
		$.each(props, function(i,prop){
			var img = new Image();
			img.crossOrigin = "Anonymous";
			var propImage = {
				prop : prop,
				image : img
			};

			img.onload = function(){
				propImages.push(propImage);
				count--;
				if (count === 0){
					callback(propImages);
				}
			}
			img.src = prop.url || "";
		});
	}

	// Slider Displays Value
	$(".slider").on("input", function(event){
		var self = this;
		$(".slider-value").text($(self).val());
	});

	// Initializtion

	// Load All Scenes
	$.ajax({
		type: "GET",
		url: "/api/scenes",
		success: function(result){
			var scenes = result.scenes;
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
			var backgrounds = result.backgrounds;
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
			var props = result.props;
			for (var i in props){
				var prop = props[i];
				newPropView(prop);
			}
		}
	});
});