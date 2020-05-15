import { parseJSON, create3dForceObject } from "./../src/utils.js";

function displayGraph(object){
  const Graph = ForceGraph3D()
    (document.getElementById('p3d-graph'))
    .nodeAutoColorBy('group')
      .graphData(object)
        .linkDirectionalArrowLength(3.5)
        .linkDirectionalArrowRelPos(1)
        .linkCurvature(0.25)
      .onNodeDragEnd(node => {
          node.fx = node.x;
          node.fy = node.y;
          node.fz = node.z;
        });
}

export function loadFileAsText(){
  var fileToLoad = document.getElementById("files").files[0];
  var fileReader = new FileReader();
  fileReader.onload = function(fileLoadedEvent){
      var textFromFileLoaded = fileLoadedEvent.target.result;
      // Create the graph
      jsonFileToGraph(textFromFileLoaded);
  };
  fileReader.readAsText(fileToLoad, "UTF-8");
}


// Read and parse the JSON file to display the graph
export function jsonFileToGraph(data){
  var jsonObject = stringToJSON(data);
  var pathwayCreatedByParseJSON = parseJSON(jsonObject);
  var object = create3dForceObject(pathwayCreatedByParseJSON);
  displayGraph(object);
}


/*
fetch('./ecoli_e_coli_core.json')
  .then (function(response){
      return response.json();
  })
  .then(function(data){
      console.log(data);
      var pathwayCreatedByParseJSON = parseJSON(data);

      console.log("\n\n\n PATHWAY CREATED \n\n");
      console.log(pathwayCreatedByParseJSON);
      var object = create3dForceObject(pathwayCreatedByParseJSON);
      console.log(object);
      displayGraph(object);
      
  })
  .catch(function(err){
      console.log("ERROR");
  }
  );*/