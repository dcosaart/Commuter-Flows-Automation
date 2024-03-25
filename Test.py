import arcpy



def main():
    #set folder to the parent folder of the project you wish to automate
    arcpy.env.workspace = r"T:\Staff Folders\Dylan\2023 Commuter flows\Python Test 2024 commuter flows"
    
    #set project path, input the path to the porject itself for the code to work correctly, minus the ".aprx" at the end
    project_path=r"T:\Staff Folders\Dylan\2023 Commuter flows\Python Test 2024 commuter flows\Python Test 2024 commuter flows"

    
    #copy the path to the project's goedatabase
    geodatabase=r"T:\Staff Folders\Dylan\2023 Commuter flows\Python Test 2024 commuter flows\Python Test 2024 commuter flows.gdb"
    
    
    #set the default map name you wish input the layers into, map in the project
    #set the path to the default layer file path
    #already made default map and heat map layer file is saved here:"G:\Population\Commuter Flows Data\Default map and heat map symbology" 
    default_map_name="default_map"
    def_heat_sym=r"G:\Population\Commuter Flows Data\Default map, layout, sym\default_symbology.lyrx"
    def_layout_path=r"G:\Population\Commuter Flows Data\Default map, layout, sym\default_layout.pagx"
    
    #Set the reference layer where you want the lyers to be inserted below
    sel_ref_lyr_name="WAMPO_StateSystem Medium"      #WARNING: cannot be a sublayer to a group layer
    pts_ref_lyr_name="Boundary Layers"
    
    #set the clipping layer, what you want the points to be inside of , will also be the layer that is zoomed to in the layout 
    clip_lyr_name="Boundary Layers/WAMPO Planning Boundary"     #if in group layer it will be (group layer name)/layer name WARNING: cannot be a grouplayer/sub-grouplayer/layer, 


    #SET THE FOLDER for the jpgs
    jpg_ex_path=r"G:\Population\Commuter Flows Data\Python test jpegs"
    #jpg_ex_path=rf"G:\Population\Commuter Flows Data\2024\SourceData\Cities\{city}"    

    project=arcpy.mp.ArcGISProject(f"{project_path}.aprx")
    def_map=project.listMaps(default_map_name)[0]

    
    
    
    
    


    cities=["Andale","Andover","Bel Aire","Bentley","Cheney","Clearwater","Colwich","Derby","Eastborough","Garden Plain","Goddard","Haysville","Kechi","Maize","Mt. Hope","Mulvane","Park City",
            "Rose Hill","Sedgwick","Valley Center","Viola","Wichita"]          #list of cities to iterate through to make each inflow/outflow maps

    for city in cities:
        syntax_f_city=city.lower().replace('.','').replace(' ','_')
        map_lww=project.copyItem(def_map,f"Where Workers Live Who Work in {city}")

    
        #SET THE PATHS TO THE SHAPE FILES YOU WISH TO IMPORT, put {index} every time the city is mentioned, it will be added in the loop. no more setting after these cases
        live_who_work_pts_shp=rf"G:\Population\Commuter Flows Data\2023\SourceData\Cities\{city}\shape_files\where_workers_live_who_work_in_{syntax_f_city}\points_2020.shp"
        work_who_live_pts_shp=rf"G:\Population\Commuter Flows Data\2023\SourceData\Cities\{city}\shape_files\where_workers_work_who_live_in_{syntax_f_city}\points_2020.shp"
        sel_shp=rf"G:\Population\Commuter Flows Data\2023\SourceData\Cities\{city}\shape_files\where_workers_live_who_work_in_{syntax_f_city}\selection.shp"




        #START OF FUNCTIONS
        
        #function returns the points layer and selection layer object
        pts_lyr, sel_lyr =import_data(map_lww, live_who_work_pts_shp, sel_shp)
        
        make_map(project,syntax_f_city,map_lww, pts_lyr, clip_lyr_name, def_heat_sym, pts_ref_lyr_name, sel_ref_lyr_name, geodatabase, sel_lyr, True)
        #we can reuse these functions for the work who live maps
    
        map_wwl=project.copyItem(def_map,f"Where Workers Work Who Live in {city}")
        
        
        pts_lyr, sel_lyr= import_data(map_wwl, work_who_live_pts_shp, sel_shp)
        make_map(project,syntax_f_city,map_wwl, pts_lyr, clip_lyr_name, def_heat_sym, pts_ref_lyr_name, sel_ref_lyr_name, geodatabase, sel_lyr)

        make_layout_export(project, city, syntax_f_city, def_layout_path, map_lww, map_wwl,clip_lyr_name, jpg_ex_path)
    
    #save all changes made to another copy
        
    project.saveACopy(f"{project_path} - Updated.aprx")                                
    del project
        




##############################################
###############################################








def import_data(map, points_shp, sel_shp):

    


    pts_lyr=map.addDataFromPath(points_shp)
    sel_lyr=map.addDataFromPath(sel_shp)

    return pts_lyr, sel_lyr
  


    

def make_map(project,city,map, pts_lyr,clip_lyr_name, heat_sym, pts_ref_lyr_name, sel_ref_lyr_name, gdb, sel_lyr, is_lww=False):
    pts_ref_lyr=map.listLayers(pts_ref_lyr_name)[0]
    sel_ref_lyr=map.listLayers(sel_ref_lyr_name)[0]



    if '/' in clip_lyr_name:
        group_lyr, clip_lyr= clip_lyr_name.split('/')
        clipping_lyr=map.listLayers(group_lyr)[0].listLayers(clip_lyr)[0]         #clip the ptrs layer with the inputted clip layer
    else:
        clipping_lyr=map.listLayers(clip_lyr_name)[0]

    if is_lww:
        clip_feature=arcpy.analysis.Clip(pts_lyr, clipping_lyr, rf"{gdb}\livewhoworkin{city}_clip")
    else:
        clip_feature=arcpy.analysis.Clip(pts_lyr, clipping_lyr, rf"{gdb}\workwholivein{city}_clip")

    clip_lyr=map.addDataFromPath(clip_feature)

    map.removeLayer(pts_lyr)

   
    #changing symbology of the points and selection layer
    #lyr.symbology.renderer.symbol for selection layer
    sym=sel_lyr.symbology
    sym.renderer.symbol.color={"RGB":[0,0,0,0]}
    sym.renderer.symbol.outlineColor={"RGB":[0,0,0]}
    sym.renderer.symbol.outlineWidth= 1.5
    sel_lyr.symbology=sym


    arcpy.management.ApplySymbologyFromLayer(clip_lyr, heat_sym)

    #move selection, then heatmap below the reference layer

    map.moveLayer(sel_ref_lyr, sel_lyr, "AFTER")
    map.moveLayer(pts_ref_lyr, clip_lyr, "AFTER")



    

def make_layout_export(project, city,syntax_f_city, layout_path, map_lww, map_wwl,z_lyr_name, jpg_ex_path):
    lyt=project.importDocument(layout_path)
    lyt.name=f"{city} Layout"
    lww_mf,wwl_mf=lyt.listElements("MAPFRAME_ELEMENT")

    
    lww_mf.map=map_lww
    
    if '/' in z_lyr_name:
        group_lyr, zoom_lyr= z_lyr_name.split('/')
        z_lyr=lww_mf.map.listLayers(group_lyr)[0].listLayers(zoom_lyr)[0]         
    else:
        z_lyr=lww_mf.map.listLayers(z_lyr_name)[0]
    
    lww_mf.camera.setExtent(lww_mf.getLayerExtent(z_lyr))
    lww_mf.camera.scale=lww_mf.camera.scale * 1.1

    wwl_mf.map=map_wwl
    if '/' in z_lyr_name:
        group_lyr, zoom_lyr= z_lyr_name.split('/')
        z_lyr=wwl_mf.map.listLayers(group_lyr)[0].listLayers(zoom_lyr)[0]         
    else:
        z_lyr=wwl_mf.map.listLayers(z_lyr_name)[0]
    
    wwl_mf.camera.setExtent(wwl_mf.getLayerExtent(z_lyr))
    wwl_mf.camera.scale=wwl_mf.camera.scale * 1.1

    legend= lyt.listElements("LEGEND_ELEMENT")[0]
    ref_lyr=legend.items[0]
    for item in legend.items:
        if  item.name==f"workwholivein{syntax_f_city}_clip":
            break
        else:
            item.visible=False;

    
    
    lyt.exportToJPEG(jpg_ex_path+rf"\{city} Layout",300)
    
    

    

    

    
    




if __name__=="__main__":
    main()
    
