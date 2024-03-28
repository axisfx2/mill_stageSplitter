import c4d
import re
import os
from datetime import datetime

# sorting
def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [atoi(c) for c in re.split(r'(\d+)', text)]

class stageSplitter():
    def __init__(self, doc):
        
        self.doc = doc
        self.stage = doc.GetActiveObject()
        
        self.fps = doc.GetFps()
        
        if not self.stage or self.stage.GetType() != 5136:
            c4d.gui.MessageDialog('ERROR: Please select a stage')
            return
        
        camera_track_id = c4d.DescID(c4d.DescLevel(c4d.STAGEOBJECT_CLINK))
        camera_track = self.stage.FindCTrack(camera_track_id)
        
        if not camera_track:
            c4d.gui.MessageDialog('ERROR: Please add keyframes to the camera track')
            return

        self.doc.StartUndo()

        if self.getAllRenderData() or self.getAllTakeData():
            if c4d.gui.QuestionDialog('Delete All Takes and Render Settings?'):
                self.deleteAllRenderData()
                self.deleteAllTakes()

        self.shot_specific_objs = c4d.gui.QuestionDialog(
            'Enable shot specific lights/objects?\nSupport for nulls formatted:\ncamera_name_LIGHTS\ncamera_name_BG\ncamera_name_SCENE')

        self.dataListFromKeyframes(camera_track)
        self.createRenderData()
        self.createTakeData()
        
        self.doc.EndUndo()

        self.writeLogInformation()

        c4d.gui.MessageDialog(self.prettyStats())

    def prettyStats(self):
        n_cameras = len(self.camera_dict)
        n_takes = len(self.data_list)

        if n_cameras == 1:
            camera_plural = ''
        else:
            camera_plural = 's'

        if n_takes == 1:
            take_plural = ''
        else:
            take_plural = 's'

        stats = 'Successfully Generated {} Take{} from {} Camera{}'.format(
            n_takes,
            take_plural,
            n_cameras,
            camera_plural
        )

        return stats

    def getAllRenderData(self):
        rd = self.doc.GetFirstRenderData()
        rd = rd.GetNext()
        rds = []
        
        while rd:
            rds.append(rd)
            rd = rd.GetNext()

        return rds
        
    def deleteAllRenderData(self):
        rds = self.getAllRenderData()
            
        for rd in rds:
            rd.Remove()

        c4d.EventAdd()
    
    def getAllTakeData(self):
        src_take_data = self.doc.GetTakeData()
        main_take = src_take_data.GetMainTake()
        td = main_take.GetDown()

        tds = []
        
        while td:
            tds.append(td)
            td = td.GetNext()

        return tds

    def deleteAllTakes(self):
        tds = self.getAllTakeData()
            
        for td in tds:
            td.Remove()
                
        c4d.EventAdd()

    def dataListFromKeyframes(self, camera_track):
        alphabet = 'abcdefghijklmnopqrstuvwxyz'

        camera_curve = camera_track.GetCurve()

        max_time = self.doc.GetMaxTime()
        
        # iterate over keyframes
        self.data_list = []
        self.camera_dict = {}

        keyframe_count = camera_curve.GetKeyCount()

        for k in range(keyframe_count):
            key = camera_curve.GetKey(k)
            time = key.GetTime()
            start_time = time#.GetFrame(fps)
            
            data = {
                'Enable Nulls': []
            }
            
            data['Frame Range'] = [start_time]
            
            if k > 0:
                end_time = start_time - c4d.BaseTime(1, self.fps)
                self.data_list[-1]['Frame Range'].append(end_time)
                
            if k == keyframe_count-1:
                data['Frame Range'].append(max_time)
            
            camera = key.GetGeData()
            
            camera_name = camera.GetName()
            
            if camera_name not in self.camera_dict:
                self.camera_dict[camera_name] = -1
            self.camera_dict[camera_name] += 1
            
            camera_letter = alphabet[self.camera_dict[camera_name]]
            
            take_name = camera_name
            take_name += '_{}'.format(camera_letter.upper())
            
            data['Take Name'] = take_name
            data['Camera'] = camera
            
            self.data_list.append(data)
            
        # sort alphabetically by take name
        self.data_list = sorted(
            self.data_list,key=lambda n: natural_keys(n['Take Name']))
        
    def createRenderData(self):
        src_render_data = self.doc.GetFirstRenderData()
        
        for data_dict in self.data_list:
            render_data: c4d.documents.RenderData = src_render_data.GetClone(c4d.COPYFLAGS_0)
            #data = doc.InsertRenderDataLast(clone)
            self.doc.InsertRenderDataLast(render_data)
            
            tstart, tend = data_dict['Frame Range']
            
            render_data.SetName(data_dict['Take Name'])
            render_data[c4d.RDATA_FRAMESEQUENCE] = 0
            render_data[c4d.RDATA_FRAMEFROM] = tstart
            render_data[c4d.RDATA_FRAMETO] = tend
            
            data_dict['Render Data'] = render_data

        c4d.EventAdd()

    def getNullObjects(self):
        first_scene_object = self.doc.GetFirstObject()
        all_scene_objects = IterateHierarchy(
            first_scene_object)
        all_scene_objects += [first_scene_object]

        alembic_null_id = 1028083
        null_id = 5140
        null_ids = [null_id, alembic_null_id]

        cameras = list(self.camera_dict.keys())
        cameras = sorted(cameras, key=lambda n: len(n), reverse=True)

        accepted_suffix = [
            'LIGHTS',
            'SCENE',
            'BG'
        ]

        nulls = []
        for object in all_scene_objects:
            if object.GetType() not in null_ids:
                continue
            
            object_name = object.GetName()
            # print('null', object_name)
            for camera in cameras:
                splitter = camera + '_'

                accepted_null_names = []

                for suffix in accepted_suffix:
                    accepted_null_names.append(splitter+suffix)
                
                if object_name not in accepted_null_names:
                    continue

                for data in self.getDataEquallingCamera(camera):
                    data['Enable Nulls'].append(object)

                # for data in self.getDataNotEquallingCamera(camera):
                #     data['Disable Nulls'].append(object)

                break
            
    def getDataEquallingCamera(self, camera):
        items = []
        for data in self.data_list:
            if data['Camera'].GetName() == camera:
                items.append(data)

        return items
            
    def getDataNotEquallingCamera(self, camera):
        items = []
        for data in self.data_list:
            if data['Camera'].GetName() != camera:
                items.append(data)

        return items
    
    def writeLogInformation(self):
        doc_simple = os.path.splitext(self.doc.GetDocumentName())[0]
        log_folder = os.path.expanduser('~/Documents/Stage Splitter/Logs/'+doc_simple)
        current_datetime = datetime.now()
        
        log_filename = current_datetime.strftime("%m-%d-%Y_%H-%M-%S")
        log_filename = 'split-log_{}.txt'.format(log_filename)
        # log_filename = 'qwer.txt'
        log_file = os.path.join(log_folder, log_filename).replace('/', '\\')

        if not os.path.isdir(log_folder):
            os.makedirs(log_folder)

        log_info = []
        doc_path = os.path.join(
            self.doc.GetDocumentPath(), 
            self.doc.GetDocumentName()
        )

        doc_path = doc_path.replace('/', '\\')

        log_info.append('Scene File: '+doc_path)
        
        tab = '    '

        for data in self.data_list:
            tstart, tend = data['Frame Range']
            fstart = tstart.GetFrame(self.fps)
            fend = tend.GetFrame(self.fps)

            log_info.append('')
            log_info.append('{}: {} - {}'.format(
                data['Take Name'], fstart, fend))
            
        with open(log_file, 'w') as f:
            f.write('\n'.join(log_info))

    def createTakeData(self):
        # create takes
        src_take_data = self.doc.GetTakeData()
        main_take = src_take_data.GetMainTake()
        child_take = main_take.GetDown()

        rs_light_types = [
            1036751,
            1036751,
            1036751,
            1036751,
            1036751,
            1036751,
            1036751,
            1036751
        ]
        
        self.getNullObjects()
        
        for data_dict in reversed(self.data_list):
            take_data = src_take_data.AddTake(
                '', main_take, child_take)
            
            take_data.SetName(data_dict['Take Name'])

            # object & light visibility
            if self.shot_specific_objs:
                for null in data_dict['Enable Nulls']:

                    # enable editor visibility
                    take_data.FindOrAddOverrideParam(
                        src_take_data,
                        null,
                        c4d.DescID(c4d.ID_BASEOBJECT_VISIBILITY_EDITOR),
                        False
                    )

                    # enable render visibility
                    take_data.FindOrAddOverrideParam(
                        src_take_data,
                        null,
                        c4d.DescID(c4d.ID_BASEOBJECT_VISIBILITY_RENDER),
                        False
                    )

                    for object in IterateHierarchy(null, True):
                        null_name = null.GetName()
                        
                        # ignore anything that isnt rs light
                        if object.GetType() not in rs_light_types:
                            continue
                        # # ignore cameras
                        # if object.GetType == 1057516:
                        #     continue
                        
                        # if null_name.lower().find('lights') >= 0:


                        # enable.. enable?
                        take_data.FindOrAddOverrideParam(
                            src_take_data,
                            object,
                            c4d.DescID(c4d.ID_BASEOBJECT_GENERATOR_FLAG),
                            True
                        )
                
            take_data.SetCamera(src_take_data, data_dict['Camera'])
            take_data.SetRenderData(src_take_data, data_dict['Render Data'])
            
            data_dict['Take Data'] = take_data
            #take_data.SetName(data_dict['Take Name'])

        c4d.EventAdd()

def IterateHierarchy(op, children_only=False):
    '''
    hierarchy iteration
    https://developers.maxon.net/?p=596
    '''
    def GetNextObject(op):
        if op==None:
            return None
    
        if op.GetDown():
            return op.GetDown()
    
        while not op.GetNext() and op.GetUp():
            op = op.GetUp()

        if children_only and op == src:
            return None
        
        return op.GetNext()
    
    if op is None:
        return
 
    children = []

    src = op

    while op:
        children.append(op)
        op = GetNextObject(op)
 
    return children

class CommandData(c4d.plugins.CommandData):
    def Execute(self, doc):
        stageSplitter(doc)
        return True

def main():
    # iconMTX = c4d.bitmaps.BaseBitmap()
    # iconMTX.InitWith(os.path.join(os.path.dirname(__file__), "res", "stageSplitter.png"))
    iconMTX = None
    # Register Plugin
    try:
        c4d.plugins.RegisterCommandPlugin(
            1062995, 
            'Stage Splitter', 
            0, 
            iconMTX,
            'Split stage object into takes and render settings per each keyframe', 
            CommandData()
        )
    except:
        stageSplitter(
            c4d.documents.GetActiveDocument())

if __name__ == '__main__':
    main()