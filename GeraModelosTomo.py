import bpy
import platform
import tempfile
import subprocess
import multiprocessing
import os
import pydicom
import shutil
import numpy as np
from os.path import expanduser

from .ImportaObjMat import *

# MENSAGENS

class MessageFaltaDICOM(bpy.types.Operator):
    bl_idname = "object.dialog_operator_informe_dicom"
    bl_label = "Doesn't have DICOM path!"
  
    def execute(self, context):
        message = ("Doesn't have DICOM path!")
        self.report({'INFO'}, message)
        return {'FINISHED'}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

bpy.utils.register_class(MessageFaltaDICOM)


'''
def ERROruntimeDICOMDef(self, context):
    self.UILayout.label("Doesn't have DICOM path!")
#    self.layout.label("Doesn't have DICOM path!")

def ERROTermDICOM():
     CRED = '\033[91m'
     CEND = '\033[0m'
     print(CRED + "Doesn't have DICOM path!" + CEND)
'''

# GERA MODELOS TOMO

def GeraModelosTomoDef(self, context):

    context = bpy.context
    obj = context.object
    scn = context.scene


    if scn.my_tool.path == "":
            bpy.ops.object.dialog_operator_informe_dicom('INVOKE_DEFAULT')
            return {'FINISHED'}
    
#    scene = context.scene
#    rd = scene.render

    else:
        interesseOssos = bpy.context.scene.interesse_ossos
        interesseMole = bpy.context.scene.interesse_mole
        interesseDentes = bpy.context.scene.interesse_dentes

        # Calcula número de CPUs

        CpuNum = multiprocessing.cpu_count()

        if CpuNum >= 8:
            DecimFactor = '0.90'

        if CpuNum == 4:
            DecimFactor = '0.95'

        if CpuNum == 2:
            DecimFactor = '0.98'

        if CpuNum == 1:
            DecimFactor = '0.99'

        ReconTomo(scn.my_tool.path, interesseOssos, 'Bones', DecimFactor)
        ReconTomo(scn.my_tool.path, interesseMole, 'SoftTissue', DecimFactor)
        ReconTomo(scn.my_tool.path, interesseDentes, 'Teeth', DecimFactor)


        a = bpy.data.objects['Bones']
        b = bpy.data.objects['SoftTissue']
        c = bpy.data.objects['Teeth']


        bpy.ops.object.select_all(action='DESELECT')
        a.select_set(True)
        context.view_layer.objects.active = a
        #bpy.context.scene.objects.active = a
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')
    #    bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')
    #    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')

        
        bpy.ops.object.select_all(action='DESELECT')
        b.select_set(True)
    #    bpy.context.scene.objects.active = b
        context.view_layer.objects.active = b
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')


        bpy.ops.object.select_all(action='DESELECT')
        c.select_set(True)
    #    bpy.context.scene.objects.active = c
        context.view_layer.objects.active = c
        bpy.ops.object.shade_smooth()
        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

        bpy.ops.object.select_all(action='DESELECT')
        a.select_set(True)
        b.select_set(True) 
        c.select_set(True)
    #    bpy.context.scene.objects.active = a
        context.view_layer.objects.active = a
        bpy.ops.object.parent_set()

        #bpy.ops.transform.rotate(value=3.14159)

        bpy.ops.transform.rotate(value=3.14159, orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(True, False, False), mirror=True, proportional='DISABLED', proportional_edit_falloff='SMOOTH', proportional_size=1)


                                     
        a.location[0] = 0
        a.location[1] = 0
        a.location[2] = 0

        bpy.ops.view3d.view_all(center=False)

        impMaterial = 'SCATTER_bone'
        SelObj = 'Bones'
        ImportaMaterial(impMaterial, SelObj)

        impMaterial = 'SCATTER_skin'
        SelObj = 'SoftTissue'
        ImportaMaterial(impMaterial, SelObj)

        impMaterial = 'SCATTER_teeth'
        SelObj = 'Teeth'
        ImportaMaterial(impMaterial, SelObj)

        bpy.ops.object.select_all(action='DESELECT')
        a.select_set(True)
     #   bpy.context.scene.objects.active = a
        context.view_layer.objects.active = a



class GeraModelosTomo(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.gera_modelos_tomo"
    bl_label = "Prepara Impressao"
    
    def execute(self, context):
        GeraModelosTomoDef(self, context)
        return {'FINISHED'}

# GERA MODELO ARCADA

def GeraModelosTomoArcDef(self, context):
    
    context = bpy.context
    obj = context.object
    scn = context.scene

    if scn.my_tool.path == "":
            bpy.ops.object.dialog_operator_informe_dicom('INVOKE_DEFAULT')
            return {'FINISHED'}

    else:
    #    scene = context.scene
    #    rd = scene.render

        ReconTomo(scn.my_tool.path, '226', 'Arcada','0.90')

        obj = context.object

        bpy.ops.object.select_all(action='DESELECT')
        obj.select_set(True)
        context.view_layer.objects.active = obj
        bpy.ops.object.shade_smooth()
        bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')


def ReconTomo(pathdir, interes, saida, simplif):

    context = bpy.context
    obj = context.object
    scn = context.scene

#    scene = context.scene
#    rd = scene.render
    
    tmpdir = tempfile.mkdtemp()
    tmpSTL = tmpdir+'/'+saida+'.stl'

    homeall = expanduser("~")

#    capturaEndereco = bpy.data.scenes['Scene'].my_tool['path']
#    dirAtual = os.getcwd()
#    print("DIRETÓRIO ATUAL:", dirAtual)
#    os.chdir(dirAtual)    


    if scn.my_tool.path == "":
            bpy.ops.object.dialog_operator_informe_dicom('INVOKE_DEFAULT')
            return {'FINISHED'}

    else:


        if platform.system() == "Linux":


            dicom2DtlPath = homeall+'/Programs/OrtogOnBlender/Dicom2Mesh/dicom2mesh'
    


        if platform.system() == "Windows":

            dicom2DtlPath = 'C:/OrtogOnBlender/DicomToMeshWin/dicom2mesh.exe'



        if platform.system() == "Darwin":

            dicom2DtlPath = '/OrtogOnBlender/DicomToMeshMAC/dicom2mesh'


        subprocess.call([dicom2DtlPath, '-i',  pathdir, '-r', simplif, '-s', '-t', interes, '-o', tmpSTL])
        bpy.ops.import_mesh.stl(filepath=tmpSTL, filter_glob="*.stl",  files=[{"name":saida+".stl", "name":saida+".stl"}], directory=tmpdir)

 
#        bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN')
#        bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
#        bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='MEDIAN')
        bpy.ops.view3d.view_all(center=False)


def CopiaTomoDir(Origem):

    context = bpy.context
    scn = context.scene

    homeDir = expanduser("~")

    NomePaciente = bpy.context.scene.nome_paciente
    SobrenomePaciente = bpy.context.scene.sobrenome_paciente

    NomePacienteDir = homeDir+"/OrtogOnBlenderDir/"+NomePaciente+"_"+SobrenomePaciente

#        if found == False:
    if not os.path.exists(NomePacienteDir):
        print("Patience Dir does not exist!")
    else:
        if os.path.exists(NomePacienteDir):
            shutil.copytree(Origem, NomePacienteDir+"/CT-Scan")


def ReduzDimDICOMDef():

    context = bpy.context
    scn = context.scene

    print("FATIAAAAAAAAA222")

    ListaArquivos = sorted(os.listdir(scn.my_tool.path))

    os.chdir(scn.my_tool.path)

    for fatia in range(len(ListaArquivos)):
        ds = pydicom.dcmread(str(ListaArquivos[fatia]), force=True)
        ArquivoAtual = str(ListaArquivos[fatia])
        DimPixelsX = ds.Rows
        DimPixelsY = ds.Columns

        print("FATIAAAAAAAAA222")
        print("DimPixelsX", DimPixelsX)
        print("DimPixelsY", DimPixelsY)

        if DimPixelsX > 512 or DimPixelsY > 512:

            ListaDim = [ DimPixelsX, DimPixelsY ]
            ElementoFator = float(max(ListaDim))

            Fator = str( 512 / ElementoFator )

#            DimPixelsXFinal = str(int(DimPixelsX * Fator))
#            DimPixelsYFinal = str(int(DimPixelsY * Fator))

#            print("DimPixelsX", DimPixelsX)
#            print("DimPixelsY", DimPixelsY)
#            print("Fator:", Fator)
#            print("DimPixelsXFinal", DimPixelsXFinal)
#            print("DimPixelsYFinal", DimPixelsYFinal)


            if not os.path.exists("REDUC"):
                os.mkdir("REDUC")
                print("Diretorio REDUC criado")

            if platform.system() == "Linux" or platform.system() == "Darwin": 
                    subprocess.call('dcmscale -v +Sxf '+Fator+' +Syf '+Fator+' '+ArquivoAtual+' REDUC/'+ArquivoAtual, shell=True)

            if platform.system() == "Windows": 
                    subprocess.call('C:/OrtogOnBlender/dcmtk/dcmscale.exe -v +Sxf '+Fator+' +Syf '+Fator+' '+ArquivoAtual+' REDUC/'+ArquivoAtual, shell=True)

    scn.my_tool.path = os.getcwd()+"/REDUC/"

class ReduzDimDICOM(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.reduz_dimensao_dicom"
    bl_label = "Reduz Dimensao DICOM"
    
    def execute(self, context):
        ReduzDimDICOMDef()
        return {'FINISHED'}

bpy.utils.register_class(ReduzDimDICOM)


def IdentificaTomografo(Arquivo):

    context = bpy.context
    scn = context.scene

    # Lê arquivo DICOM
    ds = pydicom.dcmread(Arquivo)

    # Separa Manufacturer
    ManufacturerComplete = ds.data_element("Manufacturer")
    ManufacturerLimpa1 = str(ManufacturerComplete).split('LO: ')
    ManufacturerLimpo = str(ManufacturerLimpa1[1]).strip('"')

    print("ManufacturerComplete:", ManufacturerComplete)
    print("ManufacturerLimpa1:", ManufacturerLimpa1)
    print("ManufacturerLimpo:", ManufacturerLimpo)


    try:
        # Separa StationName
        StationNameComplete = ds.data_element("StationName")
        StationNameLimpa1 = str(StationNameComplete).split('SH: ')
        StationNameLimpo = str(StationNameLimpa1[1]).strip('"')

        print("StationNameComplete:", StationNameComplete)
        print("StationNameLimpa1:", StationNameLimpa1)
        print("StationNameLimpo:", StationNameLimpo)
    except:
        print("Sem StationNam")


    
    try:
        # Separa ManufacturerModelName
        ManufacturerModelNameComplete = ds.data_element("ManufacturerModelName")
        ManufacturerModelNameLimpa1 = str(ManufacturerModelNameComplete).split('LO: ')
        ManufacturerModelNameLimpo = str(ManufacturerModelNameLimpa1[1]).strip('"')

        print("ManufacturerModelName:", ManufacturerModelNameComplete)
        print("ManufacturerModelNameLimpa1:", ManufacturerModelNameLimpa1)
        print("ManufacturerModelNameLimpo:", ManufacturerModelNameLimpo)
        return ManufacturerModelName
    except:
        print("Sem ManufacturerModelName")


    if ManufacturerLimpo == "'TOSHIBA'" and StationNameLimpo == "'ACTIVION_16'":
        print("USA FIXED!")
        print("SÉRIE 3")
        print("Bone: 200")
        print("SoftTissue: -300")
        print("Teeth: 1430")
        print("Condylus: 655")

        # Seleciona diretório e corrige biblio
        os.chdir(scn.my_tool.path+"/3")
        scn.my_tool.path = os.getcwd()
        bpy.ops.object.corrige_dicom()

        #bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D        
        bpy.context.scene.interesse_ossos = "200"
        bpy.context.scene.interesse_mole = "-300"
        bpy.context.scene.interesse_dentes = "1430"

        bpy.ops.object.gera_modelos_tomo() 

    if ManufacturerLimpo == "'Imaging Sciences International'" and StationNameLimpo == "'IMAGING-53246DF'":
        print("SÉRIE 0")
        print("Bone: 200")
        print("SoftTissue: -600")
        print("Teeth: 800")
        print("Condylus: 655")

        os.chdir(scn.my_tool.path+"/0")
        scn.my_tool.path = os.getcwd()
        bpy.ops.object.corrige_dicom()

        #bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "200"
        bpy.context.scene.interesse_mole = "-600"
        bpy.context.scene.interesse_dentes = "800"

        bpy.ops.object.gera_modelos_tomo()
        
    if ManufacturerLimpo == "'Imaging Sciences International'" and StationNameLimpo == "'ICAT-6BHI1BTQFF'":
        print("USA FIXED!")
        print("SÉRIE 0")
        print("Bone: 200")
        print("SoftTissue: -600")
        print("Teeth: 1000")
        print("Condylus: 655")

        os.chdir(scn.my_tool.path+"/0")
        scn.my_tool.path = os.getcwd()
        bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "200"
        bpy.context.scene.interesse_mole = "-600"
        bpy.context.scene.interesse_dentes = "1000"

        bpy.ops.object.gera_modelos_tomo()        


    if ManufacturerLimpo == "'Imaging Sciences International'" and StationNameLimpo == "'CONEPEAM'":
        print("SÉRIE 0")
        print("Bone: 250")
        print("SoftTissue: -950")
        print("Teeth: 711")
        print("Condylus: MODELO LIMITADO")

        os.chdir(scn.my_tool.path+"/0")
        scn.my_tool.path = os.getcwd()
#        bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "250"
        bpy.context.scene.interesse_mole = "-950"
        bpy.context.scene.interesse_dentes = "711"

        bpy.ops.object.gera_modelos_tomo()


    if ManufacturerLimpo == "'Imaging Sciences International'" and StationNameLimpo == "'ICAT_TOMO'":
        print("SÉRIE 1")
        print("Bone: 485")
        print("SoftTissue: -480")
        print("Teeth: 1030")
        print("Condylus: MODELO LIMITADO")
        os.chdir(scn.my_tool.path+"/1")
        scn.my_tool.path = os.getcwd()
        bpy.ops.object.corrige_dicom()

        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "485"
        bpy.context.scene.interesse_mole = "-480"
        bpy.context.scene.interesse_dentes = "1030"

        bpy.ops.object.gera_modelos_tomo()
        

    if ManufacturerLimpo == "'NIM'" and StationNameLimpo == "'NT'":
        print("Modifica o FIXED! Usar o 67821")
        print("SÉRIE 67821")
        print("Bone: 1300")
        print("SoftTissue: -1")
        print("Teeth: 1260")
        print("Condylus: 1260")

        os.chdir(scn.my_tool.path+"/67821")
        scn.my_tool.path = os.getcwd()
        bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "1300"
        bpy.context.scene.interesse_mole = "-1"
        bpy.context.scene.interesse_dentes = "1260"

        bpy.ops.object.gera_modelos_tomo() 
        
    if ManufacturerLimpo == "'PreXion'" and StationNameLimpo == "'CT-02'":
        print("SÉRIE 1000")
        print("Bone: 287")
        print("SoftTissue: 724")
        print("Teeth: 1807")
        print("Condylus: APENAS DENTES, ÁREA LIMITADA.")

    if ManufacturerLimpo == "'TOSHIBA'" and StationNameLimpo == "'Alexion 16'":
        print("USA FIXED!")
        print("SÉRIE 3")
        print("Bone: 593")
        print("SoftTissue: -562")
        print("Teeth: 1862")
        print("Condylus: 655")
        
        print("----")
        
        print("USA FIXED!")
        print("SÉRIE 4")
        print("Bone: 200")
        print("SoftTissue: -300")
        print("Teeth: 1340")
        print("Condylus: 655")

        os.chdir(scn.my_tool.path+"/4")
        scn.my_tool.path = os.getcwd()
        bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "200"
        bpy.context.scene.interesse_mole = "-300"
        bpy.context.scene.interesse_dentes = "1340"

        bpy.ops.object.gera_modelos_tomo()

    if ManufacturerLimpo == "'GE MEDICAL SYSTEMS'" and StationNameLimpo == "'CTGE'":
        print("SÉRIE 3")
        print("Bone: 200")
        print("SoftTissue: -300")
        print("Teeth: 1430")
        print("Condylus: 655")

        os.chdir(scn.my_tool.path+"/3")
        scn.my_tool.path = os.getcwd()
 #       bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "200"
        bpy.context.scene.interesse_mole = "-300"
        bpy.context.scene.interesse_dentes = "1430"

        bpy.ops.object.gera_modelos_tomo()

    if ManufacturerLimpo == "'GE MEDICAL SYSTEMS'" and StationNameLimpo == "'Optima'":
        print("SÉRIE 303")
        print("Bone: 200")
        print("SoftTissue: -300")
        print("Teeth: 1430")
        print("Condylus: 655")

        os.chdir(scn.my_tool.path+"/303")
        scn.my_tool.path = os.getcwd()
 #       bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "200"
        bpy.context.scene.interesse_mole = "-300"
        bpy.context.scene.interesse_dentes = "1430"

        bpy.ops.object.gera_modelos_tomo()

    if ManufacturerLimpo == "'GE MEDICAL SYSTEMS'" and StationNameLimpo == "'CT99'":
        print("SÉRIE 3")
        print("Bone: 200")
        print("SoftTissue: -300")
        print("Teeth: 1430")
        print("Condylus: 655")

        os.chdir(scn.my_tool.path+"/3")
        scn.my_tool.path = os.getcwd()
 #       bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "200"
        bpy.context.scene.interesse_mole = "-300"
        bpy.context.scene.interesse_dentes = "1430"

        bpy.ops.object.gera_modelos_tomo()

    if ManufacturerLimpo == "'SIEMENS'" and StationNameLimpo == "'CT3SQ'":
        print("SÉRIE 3")
        print("Bone: 200")
        print("SoftTissue: -300")
        print("Teeth: 1430")
        print("Condylus: 655")
        
    if ManufacturerLimpo == "'SIEMENS'" and StationNameLimpo == "'CT54551'":
        print("USA FIXED!")
        print("SÉRIE ")
        print("Bone: 200")
        print("SoftTissue: -300")
        print("Teeth: 1430")
        print("Condylus: 655")

        print("----")

        print("USA FIXED!")
        print("SÉRIE 4")
        print("Bone: 200")
        print("SoftTissue: -300")
        print("Teeth: 1430")
        print("Condylus: 655")

        os.chdir(scn.my_tool.path+"/4")
        scn.my_tool.path = os.getcwd()
        bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")          

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "200"
        bpy.context.scene.interesse_mole = "-300"
        bpy.context.scene.interesse_dentes = "1430"

        bpy.ops.object.gera_modelos_tomo()

    if ManufacturerLimpo == "'GE MEDICAL SYSTEMS'" and StationNameLimpo == "'PETCT'":
#        print("USA FIXED!")
        print("SÉRIE 3")
        print("Bone: 200")
        print("SoftTissue: -300")
        print("Teeth: 1430")
        print("Condylus: 655")

        print("----")

#        print("USA FIXED!")
        print("SÉRIE 4")
        print("Bone: 400")
        print("SoftTissue: -300")
        print("Teeth: 1665")
        print("Condylus: 655")

        os.chdir(scn.my_tool.path+"/3")
        scn.my_tool.path = os.getcwd()
 #       bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        CopiaTomoDir(scn.my_tool.path)           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "200"
        bpy.context.scene.interesse_mole = "-300"
        bpy.context.scene.interesse_dentes = "1430"

        bpy.ops.object.gera_modelos_tomo()

    if ManufacturerLimpo == "'SIEMENS'" and StationNameLimpo == "'CTAWP92145'":
        print("USA FIXED!")
        print("SÉRIE 3")
        print("Bone: 710")
        print("SoftTissue: -460")
        print("Teeth: 1430")
        print("Condylus: 655")

        os.chdir(scn.my_tool.path+"/3")
        scn.my_tool.path = os.getcwd()
        bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "710"
        bpy.context.scene.interesse_mole = "-460"
        bpy.context.scene.interesse_dentes = "1430"

        bpy.ops.object.gera_modelos_tomo()

    if ManufacturerLimpo == "'SIEMENS'" and StationNameLimpo == "'CTAWP65585'":
#        print("USA FIXED!")
        print("SÉRIE 2")
        print("Bone: 200")
        print("SoftTissue: -300")
        print("Teeth: 1430")
        print("Condylus: 655")

        print("----")

#        print("USA FIXED!")
        print("SÉRIE 3")
        print("Bone: 613")
        print("SoftTissue: -230")
        print("Teeth: 1320")
        print("Condylus: 655")

        os.chdir(scn.my_tool.path+"/2")
        scn.my_tool.path = os.getcwd()
#        bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        CopiaTomoDir(scn.my_tool.path)           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "200"
        bpy.context.scene.interesse_mole = "-300"
        bpy.context.scene.interesse_dentes = "1430"

        bpy.ops.object.gera_modelos_tomo()

    if ManufacturerLimpo == "'Xoran Technologies ®'" and StationNameLimpo == "'TOMOGRAFIA'":
        print("SÉRIE 1")
        print("Bone: 545")
        print("SoftTissue: -960")
        print("Teeth: 1230")
        print("Condylus: 655")

        os.chdir(scn.my_tool.path+"/1")
        scn.my_tool.path = os.getcwd()
 #       bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "545"
        bpy.context.scene.interesse_mole = "-960"
        bpy.context.scene.interesse_dentes = "1230"

        bpy.ops.object.gera_modelos_tomo()

    if ManufacturerLimpo == "'Xoran Technologies ®'" and StationNameLimpo == "'FEN-TOMO07'":
        print("SÉRIE 1")
        print("Bone: 450")
        print("SoftTissue: -700")
        print("Teeth: 1440")

        os.chdir(scn.my_tool.path+"/1")
        scn.my_tool.path = os.getcwd()
 #       bpy.ops.object.corrige_dicom()

        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "450"
        bpy.context.scene.interesse_mole = "-700"
        bpy.context.scene.interesse_dentes = "1440"

        bpy.ops.object.gera_modelos_tomo()

    if ManufacturerLimpo == "'Xoran Technologies'" and StationNameLimpo == "'WS_ICAT'":
        print("SÉRIE 0")
        print("Bone: 580")
        print("SoftTissue: -811")
        print("Teeth: 1235")
        print("Condylus: 655")

        os.chdir(scn.my_tool.path+"/0")
        scn.my_tool.path = os.getcwd()
 #       bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "580"
        bpy.context.scene.interesse_mole = "-811"
        bpy.context.scene.interesse_dentes = "1235"

        bpy.ops.object.gera_modelos_tomo()

    if ManufacturerLimpo == "'Xoran Technologies ®'" and StationNameLimpo == "'SERVER2'":
        print("SÉRIE 1")
        print("Bone: 320")
        print("SoftTissue: -680")
        print("Teeth: 1800")


        os.chdir(scn.my_tool.path+"/1")
        scn.my_tool.path = os.getcwd()
 #       bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "320"
        bpy.context.scene.interesse_mole = "-680"
        bpy.context.scene.interesse_dentes = "1800"

        bpy.ops.object.gera_modelos_tomo()

    if ManufacturerLimpo == "'Xoran Technologies ®'" and StationNameLimpo == "'FEN-TOMO05'":
        print("SÉRIE 1")
        print("Bone: 335")
        print("SoftTissue: -925")
        print("Teeth: 1070")
        print("Condylus: 525")

        os.chdir(scn.my_tool.path+"/1")
        scn.my_tool.path = os.getcwd()
 #       bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "335"
        bpy.context.scene.interesse_mole = "-925"
        bpy.context.scene.interesse_dentes = "1070"

        bpy.ops.object.gera_modelos_tomo()

    if ManufacturerLimpo == "'Xoran Technologies ®'" and StationNameLimpo == "'ISI'":
        print("SÉRIE 1")
        print("Bone: 462")
        print("SoftTissue: 1688")
        print("Teeth: 4591")


        os.chdir(scn.my_tool.path+"/1")
        scn.my_tool.path = os.getcwd()
 #       bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "462"
        bpy.context.scene.interesse_mole = "1688"
        bpy.context.scene.interesse_dentes = "4591"

        bpy.ops.object.gera_modelos_tomo()


    if ManufacturerLimpo == "'Philips'" and StationNameLimpo == "'INGENUITY'":
        print("SÉRIE 202")
        print("Bone: 200")
        print("SoftTissue: -300")
        print("Teeth: 1430")
        print("Condylus: 800")

        # TAMBÉM FUNCIONA O 201
        os.chdir(scn.my_tool.path+"/202")
        scn.my_tool.path = os.getcwd()
 #       bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "200"
        bpy.context.scene.interesse_mole = "-300"
        bpy.context.scene.interesse_dentes = "1430"

        bpy.ops.object.gera_modelos_tomo()

    if ManufacturerLimpo == "'SIEMENS'" and StationNameLimpo == "'CTHSL06'":
        print("SÉRIE 2")
        print("Bone: 250")
        print("SoftTissue: -300")
        print("Teeth: 1430")
        print("FIX!")

        print("SÉRIE 3")
        print("Bone: 200")
        print("SoftTissue: -300")
        print("Teeth: 1430")

        # TAMBÉM FUNCIONA O 201
        os.chdir(scn.my_tool.path+"/3")
        scn.my_tool.path = os.getcwd()
#        bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "200"
        bpy.context.scene.interesse_mole = "-300"
        bpy.context.scene.interesse_dentes = "1430"

        bpy.ops.object.gera_modelos_tomo()

    if ManufacturerLimpo == "'SIEMENS'" and StationNameLimpo == "'CTAWP75938'":
        print("SÉRIE 2")
        print("Bone: 200")
        print("SoftTissue: -300")
        print("Teeth: 1430")

        print("SÉRIE 3")
        print("Bone: 323")
        print("SoftTissue: -668")
        print("Teeth: 1850")

        # TAMBÉM FUNCIONA O 201
        os.chdir(scn.my_tool.path+"/2")
        scn.my_tool.path = os.getcwd()
#        bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "200"
        bpy.context.scene.interesse_mole = "-300"
        bpy.context.scene.interesse_dentes = "1430"

        bpy.ops.object.gera_modelos_tomo()

    if ManufacturerLimpo == "'Philips'" and StationNameLimpo == "'HOST-6163'":
        print("SÉRIE 2")
        print("Bone: 200")
        print("SoftTissue: -300")
        print("Teeth: 1430")
        print("Condylus: 655")

        # TAMBÉM FUNCIONA O 201
        os.chdir(scn.my_tool.path+"/2")
        scn.my_tool.path = os.getcwd()
 #       bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "200"
        bpy.context.scene.interesse_mole = "-300"
        bpy.context.scene.interesse_dentes = "1430"

        bpy.ops.object.gera_modelos_tomo()

    if ManufacturerLimpo == "'SIEMENS'" and StationNameLimpo == "'SNDS_CT'":
        print("SÉRIE 4")
        print("Bone: 260")
        print("SoftTissue: -400")
        print("Teeth: 1270")

        print("USA FIXED!")
        print("SÉRIE 5")
        print("Bone: 200")
        print("SoftTissue: -300")
        print("Teeth: 1430")
        print("Condylus: 655")

        # TAMBÉM FUNCIONA O 201
        os.chdir(scn.my_tool.path+"/5")
        scn.my_tool.path = os.getcwd()
        bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "200"
        bpy.context.scene.interesse_mole = "-300"
        bpy.context.scene.interesse_dentes = "1430"

    if ManufacturerLimpo == "'GE MEDICAL SYSTEMS'" and StationNameLimpo == "'ct99'":
        print("SÉRIE 3")
        print("Bone: 200")
        print("SoftTissue: -300")
        print("Teeth: 1430")
        print("Condylus: 655")

        print("SÉRIE 4")
        print("Bone: 480")
        print("SoftTissue: -300")
        print("Teeth: 1430")
        print("Condylus: 655")

        print("SÉRIE 5")
        print("Bone: 200")
        print("SoftTissue: -300")
        print("Teeth: 1430")
        print("Condylus: 655")

        # TAMBÉM FUNCIONA O 201
        os.chdir(scn.my_tool.path+"/3")
        scn.my_tool.path = os.getcwd()
#        bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "200"
        bpy.context.scene.interesse_mole = "-300"
        bpy.context.scene.interesse_dentes = "1430"

        bpy.ops.object.gera_modelos_tomo()

    if ManufacturerLimpo == "'SIEMENS'" and StationNameLimpo == "'CT4SQ'":
        print("SÉRIE 4")
        print("Bone: 200")
        print("SoftTissue: -300")
        print("Teeth: 1430")
        print("Condylus: 655")

        # TAMBÉM FUNCIONA O 201
        os.chdir(scn.my_tool.path+"/4")
        scn.my_tool.path = os.getcwd()
#        bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "200"
        bpy.context.scene.interesse_mole = "-300"
        bpy.context.scene.interesse_dentes = "1430"

        bpy.ops.object.gera_modelos_tomo()

    if ManufacturerLimpo == "'SIEMENS'" and StationNameLimpo == "'CT29290'":
        print("SÉRIE 3")
        print("Bone: 275")
        print("SoftTissue: -300")
        print("Teeth: 1430")
        print("Condylus: 655")

        # TAMBÉM FUNCIONA O 201
        os.chdir(scn.my_tool.path+"/3")
        scn.my_tool.path = os.getcwd()
        bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "275"
        bpy.context.scene.interesse_mole = "-300"
        bpy.context.scene.interesse_dentes = "1430"

        bpy.ops.object.gera_modelos_tomo()

    if ManufacturerLimpo == "'SIEMENS'" and StationNameLimpo == "'ct32571'":
        print("SÉRIE 3")
        print("Bone: 200")
        print("SoftTissue: -300")
        print("Teeth: 1430")
        print("Condylus: 655")

        # TAMBÉM FUNCIONA O 201
        os.chdir(scn.my_tool.path+"/3")
        scn.my_tool.path = os.getcwd()
#        bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "200"
        bpy.context.scene.interesse_mole = "-300"
        bpy.context.scene.interesse_dentes = "1430"

        bpy.ops.object.gera_modelos_tomo()

    
    if ManufacturerLimpo == "'TOSHIBA'" and StationNameLimpo == "'ID_STATION'":
        print("SÉRIE 3")
        print("Bone: 200")
        print("SoftTissue: -300")
        print("Teeth: 976")
        print("Condylus: 917")

        # ManufacturerModelNameLimpo: 'Aquilion ONE'
        print("SÉRIE 4")
        print("Bone: 200")
        print("SoftTissue: -300")
        print("Teeth: 1430")
        print("Condylus: 655")

        print("SÉRIE 5")
        print("Bone: 200")
        print("SoftTissue: -300")
        print("Teeth: 1430")
        print("Condylus: 655")

        print("SÉRIE 7")
        print("Bone: 395")
        print("SoftTissue: -300")
        print("Teeth: 1140")
        print("Condylus: 851")

        # TAMBÉM FUNCIONA O 201

        os.chdir(scn.my_tool.path+"/4")
        scn.my_tool.path = os.getcwd()
#        bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "200"
        bpy.context.scene.interesse_mole = "-300"
        bpy.context.scene.interesse_dentes = "1430"

        bpy.ops.object.gera_modelos_tomo()

    if ManufacturerLimpo == "'Philips'" and StationNameLimpo == "'HOST-9121'":
        print("SÉRIE 2")
        print("Bone: 280")
        print("SoftTissue: -300")
        print("Teeth: 1430")
        print("Condylus: 655")

        # TAMBÉM FUNCIONA O 201
        os.chdir(scn.my_tool.path+"/2")
        scn.my_tool.path = os.getcwd()
#        bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "280"
        bpy.context.scene.interesse_mole = "-300"
        bpy.context.scene.interesse_dentes = "1430"

        bpy.ops.object.gera_modelos_tomo()


    if ManufacturerLimpo == "'Philips'" and StationNameLimpo == "'HOST-10703'":
        print("SÉRIE 80328")
        print("Bone: 200")
        print("SoftTissue: -300")
        print("Teeth: 1430")
        print("Condylus: 655")

        # TAMBÉM FUNCIONA O 201
        os.chdir(scn.my_tool.path+"/80328")
        scn.my_tool.path = os.getcwd()
#        bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "200"
        bpy.context.scene.interesse_mole = "-300"
        bpy.context.scene.interesse_dentes = "1430"

        bpy.ops.object.gera_modelos_tomo()

    if ManufacturerLimpo == "'GE MEDICAL SYSTEMS'" and StationNameLimpo == "'CT'":
        print("SÉRIE 2")
        print("Bone: 200")
        print("SoftTissue: -300")
        print("Teeth: 1430")
        print("Condylus: 655")

        # TAMBÉM FUNCIONA O 201
        os.chdir(scn.my_tool.path+"/2")
        scn.my_tool.path = os.getcwd()
#        bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "200"
        bpy.context.scene.interesse_mole = "-300"
        bpy.context.scene.interesse_dentes = "1430"

        bpy.ops.object.gera_modelos_tomo()

    if ManufacturerLimpo == "'Imaging Sciences International'" and StationNameLimpo == "'ICAT'":
        print("SÉRIE 2")
        print("Bone: 360")
        print("SoftTissue: -600")
        print("Teeth: 992")
        print("Condylus: 655")

        # TAMBÉM FUNCIONA O 201
        os.chdir(scn.my_tool.path+"/0")
        scn.my_tool.path = os.getcwd()
        bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "360"
        bpy.context.scene.interesse_mole = "-600"
        bpy.context.scene.interesse_dentes = "992"

        bpy.ops.object.gera_modelos_tomo()

    if ManufacturerLimpo == "'SIEMENS'" and StationNameLimpo == "'CT79409'":
        print("SÉRIE 607")
        print("Bone: 200")
        print("SoftTissue: -300")
        print("Teeth: 1430")
        print("Condylus: 655")

        # TAMBÉM FUNCIONA O 201
        os.chdir(scn.my_tool.path+"/607")
        scn.my_tool.path = os.getcwd()
        bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "200"
        bpy.context.scene.interesse_mole = "-300"
        bpy.context.scene.interesse_dentes = "1430"

        bpy.ops.object.gera_modelos_tomo()    

    if ManufacturerLimpo == "'Planmeca'" and ManufacturerModelNameLimpo == "'ProMax'":
        print("SÉRIE 453970")
        print("Bone: 200")
        print("SoftTissue: -580")
        print("Teeth: 460")
        print("Condylus: 145")

        # TAMBÉM FUNCIONA O 201
        try:
            os.chdir(scn.my_tool.path+"/453970")
            scn.my_tool.path = os.getcwd()
#           bpy.ops.object.corrige_dicom()
        except:
            print("Não conta com diretório 453970")

        try:
            os.chdir(scn.my_tool.path+"/456750")
            scn.my_tool.path = os.getcwd()
#           bpy.ops.object.corrige_dicom()
        except:
            print("Não conta com diretório 456750")

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "200"
        bpy.context.scene.interesse_mole = "-580"
        bpy.context.scene.interesse_dentes = "460"

        bpy.ops.object.gera_modelos_tomo()


    if ManufacturerLimpo == "'Carestream Health'" and ManufacturerModelNameLimpo == "'CS 9300'":
        print("SÉRIE 1")
        print("Bone: 452")
        print("SoftTissue: -580")
        print("Teeth: 1080")

        os.chdir(scn.my_tool.path+"/1")
        scn.my_tool.path = os.getcwd()
        bpy.ops.object.corrige_dicom()

#        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "200"
        bpy.context.scene.interesse_mole = "-580"
        bpy.context.scene.interesse_dentes = "1080"

        bpy.ops.object.gera_modelos_tomo()

    if ManufacturerLimpo == "'Dabi Atlante'" and ManufacturerModelNameLimpo == "'Eagle 3D'":
        print("SÉRIE 1")
        print("Bone: 575")
        print("SoftTissue: -377")
        print("Teeth: 1080")

        os.chdir(scn.my_tool.path+"/1")
        scn.my_tool.path = os.getcwd()
#        bpy.ops.object.corrige_dicom()

        bpy.ops.object.reduz_dimensao_dicom()

        # Copia para o diretório
        try:
            CopiaTomoDir(scn.my_tool.path)
        except:
            print("Doesn't have Patient Dir")           

        # Gera o 3D 
        bpy.context.scene.interesse_ossos = "575"
        bpy.context.scene.interesse_mole = "-377"
        bpy.context.scene.interesse_dentes = "1080"

        bpy.ops.object.gera_modelos_tomo()

    
def GeraModeloTomoAutoDef(self, context):

    context = bpy.context
    scn = context.scene

    bpy.ops.object.ajusta_tomo()

    print("Original:", scn.my_tool.path)
    
    try:
        os.chdir(scn.my_tool.path+"/1")
    except:
        print("Dir 1 doesn't exist")

    try:
        os.chdir(scn.my_tool.path+"/2")
    except:
        print("Dir 2 doesn't exist")

    try:
        os.chdir(scn.my_tool.path+"/3")
    except:
        print("Dir 3 doesn't exist")

    try:
	    os.chdir(scn.my_tool.path+"/4")
    except:
        print("Dir 4 doesn't exist")
	  
    try:
	    os.chdir(scn.my_tool.path+"/0")
    except:
        print("Dir 0 doesn't exist")

    try:
	    os.chdir(scn.my_tool.path+"/202")
    except:
        print("Dir 202 doesn't exist")

    try:
	    os.chdir(scn.my_tool.path+"/67821")
    except:
        print("Dir 67821 doesn't exist")
    try:
	    os.chdir(scn.my_tool.path+"/5")
    except:
        print("Dir 5 doesn't exist")

    try:
	    os.chdir(scn.my_tool.path+"/453970")
    except:
        print("Dir 453970 doesn't exist")

    try:
	    os.chdir(scn.my_tool.path+"/456750")
    except:
        print("Dir 453970 doesn't exist")


    try:
	    os.chdir(scn.my_tool.path+"/303")
    except:
        print("Dir 303 doesn't exist")

	  
    # Não usar o 1, dá erro!
	  
    print("Atual:", os.getcwd())
    print (os.listdir(os.getcwd())[0])

    ArquivoAtual = os.listdir(os.getcwd())[0]

    IdentificaTomografo(ArquivoAtual)

class GeraModeloTomoAuto(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.gera_modelos_tomo_auto"
    bl_label = "Gera Modelo Tomo"
    
    def execute(self, context):
        GeraModeloTomoAutoDef(self, context)
        return {'FINISHED'}

bpy.utils.register_class(GeraModeloTomoAuto)

def DesagrupaTomoDef(self, context):

    context = bpy.context
    scn = context.scene

    a = bpy.data.objects['Bones']
    b = bpy.data.objects['SoftTissue']
    c = bpy.data.objects['Teeth']


    bpy.ops.object.select_all(action='DESELECT')

    a.hide_set(False)
    b.hide_set(False)
    c.hide_set(False)

    a.select_set(True)
    b.select_set(True)
    c.select_set(True)

    context.view_layer.objects.active = a

    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')

    bpy.ops.object.select_all(action='DESELECT')

class DesagrupaTomo(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.desagrupa_tomo"
    bl_label = "Desagrupa Tomo"
    
    def execute(self, context):
        DesagrupaTomoDef(self, context)
        return {'FINISHED'}

bpy.utils.register_class(DesagrupaTomo)
   
