import bpy
from .operators import AddCraftItem_OT_Operator, ExportCraft_OT_Operator, RemoveCraftItem_OT_Operator
from ..icons_load import get_icon
from ..preferences import get_addon_prefs

class CRAFT_UL_list(bpy.types.UIList):
    bl_idname = "CRAFT_UL_list"
    
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        prefs = get_addon_prefs()
        scene = context.scene
        row = layout.row()
        row.label(text=f"{item.title} by {prefs.detected_author}", icon_value=get_icon("sofa_outline"))
        match item.type:
            case 'Build':
                row.label(text="Build", icon_value=get_icon("wall"))
            case 'Character':
                row.label(text="Character", icon_value=get_icon("hanger"))


class InzoiderCraftExport_PT_Panel(bpy.types.Panel):
    bl_label = "3D Printer"
    bl_idname = "INZOIDER_PT_craft_export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Inzoider'
    bl_options = {'DEFAULT_CLOSED'}
        
    def draw_header(self, context):
        self.layout.label(text="", icon_value=get_icon("printer_3d"))
    
    def draw(self, context):
        scene = context.scene
        layout = self.layout
        prefs = get_addon_prefs()
        if prefs.is_printed_file_loaded:
            row = layout.row()
            col = row.column()
            col.operator(AddCraftItem_OT_Operator.bl_idname, text="", icon='ADD')
            col.operator(RemoveCraftItem_OT_Operator.bl_idname, text="", icon='REMOVE')
            col.separator()
            col.operator(ExportCraft_OT_Operator.bl_idname, text="", icon_value=get_icon("export"))
            col.separator()
            row = row.row()
            col = row.column(align=False)
            col.template_list(CRAFT_UL_list.bl_idname, "", scene, "obj_craft_list", scene, "obj_craft_index")
            col.prop(scene, "inzoider_export_all", text="Export All Crafts")
            row = layout.row()
            selected_item = scene.obj_craft_list[scene.obj_craft_index] if scene.obj_craft_list else None
            if selected_item:
                header, panel = layout.panel("_selectedcraft", default_closed=True)
                icon_state = 'CHECKBOX_HLT' if selected_item.enable_editing else 'CHECKBOX_DEHLT'
                header.alignment = 'LEFT'
                header.label(text="Selected Craft", icon_value=get_icon("sofa_outline"))
                header.prop(selected_item, "enable_editing", text="Edit Mode", icon=icon_state, expand=False)
                if panel:
                    col_panel = panel.column(align=False)
                    col_panel.enabled = selected_item.enable_editing
                    col_panel.prop(selected_item, "title", icon_value=get_icon("format_title"))
                    col_panel.prop(selected_item, "description", icon_value=get_icon("text_long"))
                    type_icon = "wall" if selected_item.type == 'Build' else "hanger"
                    col_panel.prop(selected_item, "type", icon_value=get_icon(type_icon))
                    col_panel.separator()
                    col_panel.label(text="Thumbnail and linked object cannot be edited.", icon='ERROR')
        else:
            layout.label(text="No printed.dat file has been loaded, check extension's preferences.", icon='ERROR')