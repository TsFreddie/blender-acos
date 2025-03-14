bl_info = {
    "name": "Change Active Collection on Save",
    "blender": (4, 2, 3),
    "category": "Object",
}

import bpy

def set_active_collection_by_pointer_recursive(target, layer_collection, context):
    if layer_collection.collection == target:
        context.view_layer.active_layer_collection = layer_collection
        return True
        
    for child_layer_collection in layer_collection.children:
        if set_active_collection_by_pointer_recursive(target, child_layer_collection, context):
            return True
    return False

def set_active_collection_by_name_recursive(target, layer_collection, context):
    if layer_collection.name == target:
        context.view_layer.active_layer_collection = layer_collection
        return True
        
    for child_layer_collection in layer_collection.children:
        if set_active_collection_by_name_recursive(target, child_layer_collection, context):
            return True
    return False

@bpy.app.handlers.persistent
def on_save_pre(dummy):
    context = bpy.context
    context.scene.acos_previous_active_collection = context.view_layer.active_layer_collection.name

    collection = context.scene.acos_saving_collection
    root_layer_collection = context.view_layer.layer_collection
    if collection:
        set_active_collection_by_pointer_recursive(collection, root_layer_collection, context)

@bpy.app.handlers.persistent
def on_save_post(dummy):
    context = bpy.context
    collection_name = context.scene.acos_previous_active_collection
    root_layer_collection = context.view_layer.layer_collection
    if collection_name:
        set_active_collection_by_name_recursive(collection_name, root_layer_collection, context)

@bpy.app.handlers.persistent
def on_load_post(filepath):
    if bpy.app.background or not filepath:
        return

    context = bpy.context
    collection_name = context.scene.acos_previous_active_collection
    root_layer_collection = context.view_layer.layer_collection
    if collection_name:
        set_active_collection_by_name_recursive(collection_name, root_layer_collection, context)

class SetSavingCollection(bpy.types.Operator):
    """Change Saving Collection"""
    bl_idname = "object.set_acos_saving_collection"
    bl_label = "Change Saving Collection"
    
    bl_options = {'REGISTER', 'UNDO'}
    
    target_name: bpy.props.StringProperty()

    def execute(self, context):
        collection = bpy.data.collections.get(self.target_name)
        context.scene.acos_saving_collection = collection
        return {'FINISHED'}

def menu_func(self, context):
    layout = self.layout
    collection = context.collection
    if collection:
        is_acos_saving_collection = (collection == context.scene.acos_saving_collection)
        icon = 'FILE_TICK' if not is_acos_saving_collection else 'FILE_HIDDEN'
        text = "Set as Saving Collection" if not is_acos_saving_collection else "Unset as Saving Collection"

        op = layout.operator(SetSavingCollection.bl_idname, text=text, icon=icon)
        op.target_name = collection.name if not is_acos_saving_collection else ""

class ChangeActiveCollectionPanel(bpy.types.Panel):
    bl_label = "Active Collection on Save"
    bl_idname = "SCENE_PT_active_collection"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = 'scene'

    def draw(self, context):
        layout = self.layout
        layout.use_property_decorate = False
        layout.use_property_split = True
        layout.prop(context.scene, "acos_saving_collection")

def register():
    bpy.utils.register_class(SetSavingCollection)
    bpy.utils.register_class(ChangeActiveCollectionPanel)
    bpy.types.OUTLINER_MT_collection.append(menu_func)
    
    bpy.types.Scene.acos_saving_collection = bpy.props.PointerProperty(
        name="Saving Collection",
        type=bpy.types.Collection,
        description="Collection to set as active on save"
    )
    bpy.types.Scene.acos_previous_active_collection = bpy.props.StringProperty(
        name="Previous Active Collection",
        description="The active collection before saving"
    )
    
    bpy.app.handlers.save_pre.append(on_save_pre)
    bpy.app.handlers.save_post.append(on_save_post)
    bpy.app.handlers.load_post.append(on_load_post)

def unregister():
    bpy.utils.unregister_class(SetSavingCollection)
    bpy.utils.unregister_class(ChangeActiveCollectionPanel)
    bpy.types.OUTLINER_MT_collection.remove(menu_func)
    
    del bpy.types.Scene.acos_saving_collection
    del bpy.types.Scene.acos_previous_active_collection
    
    bpy.app.handlers.save_pre.remove(on_save_pre)
    bpy.app.handlers.save_post.remove(on_save_post)
    bpy.app.handlers.load_post.remove(on_load_post)

if __name__ == "__main__":
    register()