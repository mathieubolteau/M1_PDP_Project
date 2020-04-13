
import { Pathway } from "./Pathway.js";
import { Metabolite } from "./Metabolite.js";
import { json } from "./loadJSONfs.js";


function parseJSON(json){
    var pathway = new Pathway(json.id, json.compartments, json.version, "NAME_OF_THE_PATHWAY");
    for(let m of json.metabolites){
        var metabolite = new Metabolite(m.id, m.name, [0,0,0], m.compartment, m.charge, m.formula);
        pathway.addNode(metabolite);
    }
    return pathway;
}


var p = parseJSON(json);
console.log(p);